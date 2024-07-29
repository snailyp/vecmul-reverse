import asyncio
import json
import websockets
import base64
import os
import uuid
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def receive_message(websocket):
    while True:
        try:
            response = await websocket.recv()
            data = json.loads(response)
            # print(data)
            if data.get("type") == "HELLO":
                continue
            if data.get("type") == "AI_STREAM_MESSAGE" and data["data"]["role"] == "assistant":
                return data["data"]["content"]
            elif data.get("type") == "RELATED_LINKS":
                continue
            elif data.get("type") == "ERROR":
                logger.error(f"Received error message: {data}")
                return None
            elif data.get("type") == "NEW_CHAT_CREATED":
                return None
            else:
                None

        except websockets.exceptions.ConnectionClosed:
            logger.warning("Connection closed")
            return None
        except json.JSONDecodeError:
            logger.error(f"Failed to decode JSON: {response}")
            continue
        except Exception as e:
            logger.error(f"Unexpected error in receive_message: {str(e)}")
            return None


class VecmulWebSocket:
    def __init__(self):
        self.uri = "wss://api.vecmul.com/ws"
        self.websocket = None

    async def __aenter__(self):
        self.websocket = await self.connect()
        return self.websocket

    async def __aexit__(self, exc_type, exc, tb):
        if self.websocket:
            await self.websocket.close()

    async def connect(self):
        headers = self._get_headers()
        try:
            return await websockets.connect(
                self.uri,
                extra_headers=headers,
                ping_interval=1,
                ping_timeout=3
            )
        except Exception as e:
            logger.error(f"Connection failed: {str(e)}")
            raise

    async def send_message(self, websocket, content, model="GPT-4o", language="zh-CN"):
        root_msg_id = str(uuid.uuid4())
        message = self._create_message(content, root_msg_id, model, language)
        await websocket.send(json.dumps(message))
        return root_msg_id

    def _get_headers(self):
        sec_websocket_key = self._generate_sec_websocket_key()
        return {
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'Upgrade',
            'Host': 'api.vecmul.com',
            'Origin': 'https://www.vecmul.com',
            'Pragma': 'no-cache',
            'Sec-WebSocket-Extensions': 'permessage-deflate; client_max_window_bits',
            'Sec-WebSocket-Key': sec_websocket_key,
            'Sec-WebSocket-Version': '13',
            'Upgrade': 'websocket',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
        }

    @staticmethod
    def _generate_sec_websocket_key():
        return base64.b64encode(os.urandom(16)).decode('utf-8')

    @staticmethod
    def _create_message(content, root_msg_id, model, language):
        return {
            "type": "CHAT",
            "spaceName": "Free Space",
            "message": {
                "isAnonymous": True,
                "rootMsgId": root_msg_id,
                "public": False,
                "model": model,
                "order": 0,
                "role": "user",
                "content": content,
                "fileId": None,
                "relatedLinkInfo": None,
                "messageType": "MESSAGE",
                "fileKey": None,
                "language": language
            }
        }
