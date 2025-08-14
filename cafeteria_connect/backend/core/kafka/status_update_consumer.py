# core/kafka/status_update_consumer.py

import os
import sys
import json
import django
from kafka import KafkaConsumer
from datetime import datetime
import redis
from notifications.redis_connection import redis_client

# Django setup
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from orders.models import Order

# Kafka config
KAFKA_TOPIC = 'orders.status_updated'
KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BROKER', '192.168.80.5:9092')
KAFKA_GROUP_ID = 'order-status-update-consumers'

consumer = KafkaConsumer(
    KAFKA_TOPIC,
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
    group_id=KAFKA_GROUP_ID,
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

# Redis client

REDIS_CHANNEL = 'order_updates'

print(f"🚀 Listening to Kafka topic '{KAFKA_TOPIC}' for order status updates...")

for message in consumer:
    data = message.value
    order_id = data.get('order_id')
    new_status = data.get('new_status')

    if not order_id or not new_status:
        print(f"⚠️ Invalid message data: {data}")
        continue

    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        print(f"❌ Order {order_id} not found")
        continue

    if order.status != new_status:
        old_status = order.status
        order.status = new_status
        order.save()
        print(f"🟢 Updated Order {order_id} status: {old_status} -> {new_status}")
    else:
        print(f"ℹ️ Order {order_id} status already {new_status}")

    # Publish update to Redis channel for websocket
    redis_message = {
        'order_id': order_id,
        'new_status': new_status,
        'timestamp': str(datetime.now()),
        'user_id': order.user.id if order.user else None
    }

    redis_client.publish(REDIS_CHANNEL, json.dumps(redis_message))
    print(f"🔔 Published to Redis channel '{REDIS_CHANNEL}': {redis_message}")
