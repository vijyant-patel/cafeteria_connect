# core/redis/listener.py

import os
import django
import json
import redis
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from notifications.redis_connection import redis_client
import requests
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()


pubsub = redis_client.pubsub()
pubsub.subscribe('order_updates')

channel_layer = get_channel_layer()

print("🔄 Listening to Redis channel 'order_updates'...")

for message in pubsub.listen():
    if message['type'] == 'message':
        data = json.loads(message['data'])
        order_id = data.get('order_id')
        print(f"📥 Received message from Redis: {data}")
        # if order_id:
        #     group_name = f'order_updates_{order_id}'
        #     async_to_sync(channel_layer.group_send)(
        #         group_name,
        #         {
        #             'type': 'send_notification',   # Must match async method name in consumer
        #             'message': data
        #         }
        #     )
        #     print("📤 Sent message to Channels group 'order_updates'")
        
        if order_id:
            group_name_order = f'order_updates_{order_id}'
            group_name_user = f'user_{data.get("user_id")}'  # Add user_id in Redis message

            # Send to order-specific group
            async_to_sync(channel_layer.group_send)(
                group_name_order,
                {
                    'type': 'send_notification',
                    'message': data
                }
            )
            print(f"📤 Sent message to Channels group '{group_name_order}'")

            # Send to user-specific group
            if data.get("user_id"):
                async_to_sync(channel_layer.group_send)(
                    group_name_user,
                    {
                        'type': 'send_notification',
                        'message': data
                    }
                )
                print(f"📤 Sent message to Channels group '{group_name_user}'")
            url = "http://localhost:5002/notify/push"
            SECRET_TOKEN = "MY_SUPER_SECRET_KEY"
            headers = {
                    "Authorization": f"Bearer {SECRET_TOKEN}",
                    "Content-Type": "application/json"
                }
            payload = {
                "user_id": 1,
                "message": {'status':True},
                "type": "push"  # ya sms / push
            }
            requests.post(url, json=payload, headers=headers)
