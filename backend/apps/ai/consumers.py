# PATH: apps/ai/consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):

        self.session_key = self.scope['url_route']['kwargs']['session_key']

        self.room_group_name = f"chat_{self.session_key}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        await self.send(text_data=json.dumps({
            "type": "connected",
            "message": "WebSocket connected successfully",
            "session_key": self.session_key
        }))


    async def disconnect(self, close_code):

        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )


    async def receive(self, text_data):

        data = json.loads(text_data)

        user_message = data.get("message", "")


        response = (
            f'(AI not connected yet) I received your message: "{user_message}". '
            'Backend 2 AI Coordinator will be connected here later.'
        )


        await self.send(text_data=json.dumps({
            "type": "message",
            "sender": "ai",
            "message": response
        }))