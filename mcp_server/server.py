import asyncio, os, smtplib, ssl
from email.message import EmailMessage
from mcp.server.fastmcp import FastMCP

app = FastMCP('email-mcp')

def send_email_smtp(to: str, subject: str, body: str) -> dict:
  host = os.environ.get('SMTP_HOST')
  port = int(os.environ.get('SMTP_PORT', '587'))
  user = os.environ.get('SMTP_USER')
  pwd = os.environ.get('SMTP_PASS')
  from_addr = os.environ.get('SMTP_FROM', user)

  if not all([host, port, user, pwd, from_addr]):
    return {'ok': False, 'error': 'SMTP env vars missing'}

  msg = EmailMessage()
  msg['FROM'] = from_addr
  msg['To'] = to
  msg['Subject'] = subject
  msg.set_content(body)

  ctx = ssl.create_default_context()
  with smtplib.SMTP(host, port) as s:
    s.starttls(context=ctx)
    s.login(user, pwd)
    s.send_message(msg)

  return {'ok': True, 'to': to, 'subject': subject}

@app.tool()
def send_email(to: str, subject: str, body: str) -> dict:
  try:
    return send_email_smtp(to, subject, body)
  except:
    return {'ok': False, 'error': str(e)}

def main():
  print('Starting MCP server')
  asyncio.run(app.run(transport='stdio')) # stdio transport

if __name__ == '__main__':
  main()