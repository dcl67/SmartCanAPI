import asyncio
import json

import websockets

async def can_client(hostname):
    async with websockets.connect(f'ws://{hostname}') as ws:
        await ws.send('{"some":"data"}')
        async for msg in ws:
            try:
                json_data = json.loads(msg)
            except json.JSONDecodeError:
                print('failed to parse json')
            print(json_data['some'])
        print('Connection has closed due to timeout.')


def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(can_client('demos.kaazing.com/echo'))
    loop.run_forever()

if __name__ == '__main__':
    main()
