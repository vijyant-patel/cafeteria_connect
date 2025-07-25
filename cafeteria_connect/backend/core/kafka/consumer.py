# core/kafka/consumer.py

import redis
from kafka import KafkaConsumer
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from datetime import datetime
from notifications.redis_connection import redis_client
import django

# ✅ Setup Django properly
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from shops.models import Product
from orders.models import Order
from orders.tasks import start_preparing  # ✅ Import Celery task



# Connect to Redis (adjust host/port if needed)

def send_ws_notification(order, status):
    print(" send_ws_notification")
    data = {
        'type': 'order_update',
        'order_id': order.id,
        'status': status,
        'timestamp': str(datetime.now())
    }
    print(" send_ws_notification --> Publishing to Redis:", data)
    redis_client.publish('order_updates', json.dumps(data))
    print(" send_ws_notification --> Published to Redis:", data)


KAFKA_TOPIC = 'orders.placed'
KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BROKER', '192.168.80.5:9092')
KAFKA_GROUP_ID = 'cofe-order-consumers'

consumer = KafkaConsumer(
    KAFKA_TOPIC,
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
    group_id=KAFKA_GROUP_ID,
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

print("📡 Listening to Kafka topic: orders.placed")

for message in consumer:
    order_data = message.value
    print(f"\n✅ Order received: {order_data}")
    order_id = order_data.get("order_id")
    items = order_data.get("items", [])

    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        print(f"❌ Order ID {order_id} not found in DB")
        continue

    success = True
    print("🛒 Updating inventory...")

    for item in items:
        product_id = item["product_id"]
        quantity = item["quantity"]

        try:
            product = Product.objects.get(id=product_id)

            if product.stock >= quantity:
                old_stock = product.stock
                product.stock -= quantity
                product.save()
                print(f"✅ Product ID {product_id}: stock {old_stock} → {product.stock}")
            else:
                print(f"⚠️ Product ID {product_id}: insufficient stock ({product.stock})")
                success = False

        except Product.DoesNotExist:
            print(f"❌ Product ID {product_id} does not exist")
            success = False

    if success:
        order.status = 'confirmed'
        order.save()
        print(f"🟢 Order #{order.id} marked as CONFIRMED")
        send_ws_notification(order, 'confirmed')
        start_preparing.delay(order.id)  # ⏩ trigger async move to 'preparing'
    else:
        order.status = 'cancelled'
        order.save()
        send_ws_notification(order, 'cancelled')
        print(f"🔴 Order #{order.id} CANCELLED due to stock issues")
