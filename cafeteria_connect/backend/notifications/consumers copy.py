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
        print("📩 Message connected by WebSocket:")

        # Start Redis listener thread
        threading.Thread(target=self.listen_to_redis_and_send, daemon=True).start()
        print("🔁 Subscribed to Redis: order_updates\n🧵 Redis thread started")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        print("📩 Message disconnect by WebSocket:", close_code)

    def listen_to_redis_and_send(self):
        pubsub = redis_client.pubsub()
        pubsub.subscribe('order_updates')

        for message in pubsub.listen():
            print("📥 Redis raw message:", message)

            if message and message['type'] == 'message':
                try:
                    data = json.loads(message['data'])
                except json.JSONDecodeError:
                    print("⚠️ Failed to decode message:", message['data'])
                    continue

                print("📣 Sending to group:", self.group_name)
                # Use group_send to push message to all WebSocket clients
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    self.group_name,
                    {
                        "type": "send.notification",
                        "message": {"text": "🔥 Test message from shell (web socket)"},
                    }
                )

                # loop = asyncio.get_event_loop()
                # asyncio.run_coroutine_threadsafe(
                #     self.channel_layer.group_send(
                #         self.group_name,
                #         {
                #             "type": "send.notification",
                #             "message": data,
                #         }
                #     ),
                #     loop
                # )

    # def listen_to_redis_and_send(self):

    #     # Create and set event loop for this thread
    #     loop = asyncio.new_event_loop()
    #     asyncio.set_event_loop(loop)

    #     pubsub = redis_client.pubsub()
    #     pubsub.subscribe('order_updates')

    #     for message in pubsub.listen():
    #         print("📥 Redis raw message:", message)

    #         if message and message['type'] == 'message':
    #             try:
    #                 data = json.loads(message['data'])
    #             except json.JSONDecodeError:
    #                 print("⚠️ Failed to decode message:", message['data'])
    #                 continue

    #             print("📣 Sending to group:", self.group_name)

    #             # Schedule the coroutine on this thread's loop
    #             asyncio.run_coroutine_threadsafe(
    #                 self.channel_layer.group_send(
    #                     self.group_name,
    #                     {
    #                         "type": "send.notification",
    #                         "message": data,
    #                     }
    #                 ),
    #                 loop
    #             )

    async def send_notification(self, event):
        print("📤 Sending to WebSocket:", event["message"])
        await self.send(text_data=json.dumps(event["message"]))
