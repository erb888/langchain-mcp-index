from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from rag_index import get_retriever

# RAG tool (wrap llamaindex retriever as a langchain tool)

retriever = get_retriever()

@tool
def ask_docs(question:str) -> str:
  '''Search company docs and return the most relevant answer'''
  nodes = retriever.retrieve(question)
  return '\n\n'.join(n.get_content() for n in nodes)

# === MCP client tool (call your MCP server over stdio) ===
# For MVP, just shell out to the MCP process; in production, use a proper MCP client.
import json, subprocess, sys, os

@tool
def create_ticket(title: str, description: str) -> str:
  '''Create a support ticket via MCP tool'''
  # Example: send a tool invocation to MCP over stdio using a helper script/binary.
  # For MVP: call a tiny Python client that invokes server via stdio (omitted details).
  # Here we simulate the MCP-call:
  return json.dumps({'id': f'TCK-{title[:6].upper()}', 'status': 'OPEN'})

llm = ChatOpenAI(model='gpt-4o-mini') #any chat model really
system = """You are a helpful agent. 
- If the user asks factual questions about our docs, use ask_docs first.
- If the user wants to file/raise/open a ticket, call create_ticket with a concise title and description.
- Always summarize what you did."""
prompt = ChatPromptTemplate.from_messages([('system', system), ('human', '{input}')])
tools = [ask_docs, create_ticket]
chain = prompt | llm.bind_tools(tools) # tool aware model

async def chat_once(msg: str):
  res = await chain.ainvoke({'input': msg})
  return res