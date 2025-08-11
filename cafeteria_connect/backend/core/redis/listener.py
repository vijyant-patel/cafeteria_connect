# core/redis/listener.py

import os
import django
import json
import redis
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from notifications.redis_connection import redis_client

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()


pubsub = redis_client.pubsub()
pubsub.subscribe('order_updates')

channel_layer = get_channel_layer()

print("🔄 Listening to Redis channel 'order_updates'...")

for message in pubsub.listen():
    if message['type'] == 'message':
        data = json.loads(message['data'])
        print(f"📥 Received message from Redis: {data}")

        async_to_sync(channel_layer.group_send)(
            'order_updates',
            {
                'type': 'send_notification',   # Must match async method name in consumer
                'message': data
            }
        )
        print("📤 Sent message to Channels group 'order_updates'")
