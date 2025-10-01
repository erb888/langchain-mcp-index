import asyncio
from agent import chat_once

def main():
  print('Docs-QA + Email Agent (langl + llindx + MCP server running separately)')
  print('Ask questions like: Whats up?\n')
  print('Or: Email ops.@example.com about failed HVAC appointment with a brief summary')

  while True:
    try:
      q = input('You> ')
      if not q:
        continue
      if q.lower() in {'q', 'quit', 'exit'}:
        break

      res = asyncio.run(chat_once(q))
      print('\nAgent>', res.content, '\n')

    except (KeyBoardInterrupt, EOFError):
      break

if __name__ == '__main':
  main()
  