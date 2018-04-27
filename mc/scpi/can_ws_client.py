import asyncio
import json
import typing
from async_generator import asynccontextmanager, async_generator

import websockets


@asynccontextmanager
@async_generator
class CanWsClient():
    def __init__(self, bin_q: asyncio.Queue, config: dict,
                 add_to_queue_coro: typing.Coroutine,
                 hostname: str = 'localhost:8000',
                 w_s: websockets.WebSocketClientProtocol = None):
        self.bin_q = bin_q
        self.config = config
        self.hostname = hostname
        self.add_to_queue_coro = add_to_queue_coro
        self.w_s = w_s

    async def __aenter__(self):
        if self.w_s is None:
            self.w_s = await websockets.connect(f'ws://{self.hostname}')
        # Needs to return what they will be using
        return self

    async def __aexit__(self, exc_type, exc, tb):
        print('Client closed.')
        await self.w_s.close()

    async def handler(self):
        async for msg in self.w_s:
            try:
                json_data = json.loads(msg)
            except json.JSONDecodeError:
                print(f"Failed to parse json content in msg: '{msg}'")
            else:
                print(json_data)
                command = json_data.get('command')
                if command == 'identify':
                    await self._identify_handler()
                elif command == 'echo':
                    await self._echo_handler(msg)
                elif command == 'rotate':
                    await self._rotate_handler(msg)
        print('Connection closed.')

    async def send_echo(self, message):
        data = {'command':'echo', 'message': message}
        json_data = json.dumps(data)
        await self.w_s.send(json_data)


    async def send_identity(self, username: str, password: str):
        data = {
            'command': 'identify',
            'username': username,
            'password': password
        }
        json_data = json.dumps(data)
        await self.w_s.send(json_data)

    ##### Handlers

    async def _echo_handler(self, msg):
        message = msg.get('message')
        await self.w_s.send(message)

    async def _identify_handler(self):
        await self.send_identity(self.config['uuid'], self.config['password'])

    async def _rotate_handler(self, msg):
        pos = msg.get('position')
        await self.add_to_queue_coro(self.bin_q, pos)
