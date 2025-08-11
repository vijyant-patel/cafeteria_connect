import json
import threading
import redis
from .redis_connection import redis_client
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import asyncio


# Initialize Redis client (same as your Docker Redis service name)

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = "order_updates"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        print(f"WebSocket connected: {self.channel_name}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        print(f"WebSocket disconnected: {self.channel_name}")

    async def send_notification(self, event):
        print("Sending notification to client:", event["message"])
        await self.send(text_data=json.dumps(event["message"]))
