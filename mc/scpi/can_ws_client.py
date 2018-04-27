import asyncio
import json
import typing

import websockets


class CanWsClient():
    def __init__(self, bin_q: asyncio.Queue, config: dict,
                 add_to_queue_coro: typing.Coroutine,
                 hostname: str = 'localhost:8000'):
        self.bin_q = bin_q
        self.config = config
        self.cooldown = 1
        self.hostname = hostname
        self.add_to_queue_coro = add_to_queue_coro

    async def handler(self):
        async with websockets.connect(f'ws://{self.hostname}') as w_s:
            self._reset_cooldown()
            async for msg in w_s:
                try:
                    json_data = json.loads(msg)
                except json.JSONDecodeError:
                    print(f"Failed to parse json content in msg: '{msg}'")
                else:
                    print(f'DEBUG: Server sent: {json_data}')
                    command = json_data.get('command')
                    if command == 'identify':
                        await self._identify_handler(w_s)
                    elif command == 'info':
                        self._info_helper(json_data)
                    elif command == 'echo':
                        await self._echo_handler(w_s, json_data)
                    elif command == 'rotate':
                        await self._rotate_handler(json_data)
                    else:
                        self._unknown_helper(json_data)

    ##### Handlers

    async def _echo_handler(self, w_s, content):
        message = content.get('message')
        await w_s.send(message)

    async def _identify_handler(self, w_s):
        # Be sure to strip the hyphens from the uuid to make the username
        data = {
            'command': 'identify',
            'username': self.config['uuid'].replace('-', ''),
            'password': self.config['password']
        }
        json_data = json.dumps(data)
        await w_s.send(json_data)

    async def _rotate_handler(self, content):
        pos = content.get('position')
        await self.add_to_queue_coro(self.bin_q, pos)

    ##### Other funcs
    def _info_helper(self, content):
        message = content.get('message')
        print(f'INFO from server: {message}')

    def _reset_cooldown(self):
        self.cooldown = 1

    def _unknown_helper(self, json_data):
        print(f'Unknown command in msg: {json_data}')
