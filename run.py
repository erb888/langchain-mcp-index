import asyncio
from agent import chat_once

if __name__ == '__main':
  while True:
    q = input('You: ')
    out = asyncio.run(chat_once(q))
    print('\nAgent: ', out.content, '\n')
  