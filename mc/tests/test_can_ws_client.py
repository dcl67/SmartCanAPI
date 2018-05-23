"""Tests for the CanWsClient"""
import asyncio
import asynctest
import sys
import websockets
sys.path.append("..") # Adds higher directory to python modules path

from mc.scpi.can_ws_client import CanWsClient


class CanWsClientTest(asynctest.TestCase):
    async def test_echo_handler(self):
        """Echo sends back the message it receives"""
        cws = CanWsClient(None, None, None, None)
        w_s_mock = asynctest.CoroutineMock(websockets.WebSocketClientProtocol)
        content = {'message': 'test'}
        await cws._echo_handler(w_s_mock, content)
        w_s_mock.send.assert_awaited_once_with(content['message'])
