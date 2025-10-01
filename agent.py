import os, json
from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from rag_index import get_retriever

# ---------- RAG tool (LlamaIndex) ----------
retriever = get_retriever()

@tool
def ask_docs(question:str) -> str:
  '''Search company docs and return the most relevant answer'''
  nodes = retriever.retrieve(question)
  return '\n\n'.join(n.get_content() for n in nodes)

# ---------- Email tool (direct SMTP for MVP) ----------
import smtplib, ssl
from email.message import EmailMessage

@tool
def smtp_send(to: str, subject: str, body: str) -> dict:
  """Send an email. MVP uses SMTP directly."""
  host = os.environ.get('SMTP_HOST')
  port = int(os.environ.get('SMTP_PORT', '587'))
  user = os.environ.get('SMTP_USER')
  pwd = os.environ.get('SMTP_PASS')
  from_addr = os.environ.get('SMTP_FROM', user)

  msg = EmailMessage()
  msg['From'] = from_addr
  msg['To'] = to
  msg['Subject'] = subject
  msg.set_content(body)

  ctx = ssl.create_default_context()
  with smtplib.SMTP(host, port) as s:
    s.starttls(context=ctx)
    s.login(user, pwd)
    s.send_message(msg)

  return {'ok': True, 'to': to, 'subject': subject}

@tool
def send_email(to: str, subject: str, body: str) -> str:
  """Send an email. MVP uses SMTP directly. See ?? to switch to MCP."""
  try:
    res = smtp_send(to, subject, body)
    return json.dumps(res)
  except Exception as e:
    return json.dumps({
      'ok': False,
      'error': str(e)
    })

# ---------- Model & routing ----------
llm = ChatOpenAI(model='gpt-4o-mini', temperature=0) #any chat model really

system = """You are a helpful assistant for a small field services company.
- If the user asks policy/handbook/FAQ questions, use ask_docs first.
- If the user asks to email someone, call send_email with a concise subject and body.
- Always explain what you did and include brief citations or quoted snippets when you used the docs.
"""
prompt = ChatPromptTemplate.from_messages([('system', system), ('human', '{input}')])
tools = [ask_docs, send_email]
chain = prompt | llm.bind_tools(tools) # tool aware model

async def chat_once(msg: str):
  return await chain.ainvoke({'input': msg})