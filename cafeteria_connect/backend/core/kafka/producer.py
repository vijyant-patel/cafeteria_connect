# core/kafka/producer.py

from kafka import KafkaProducer
import json
import os

KAFKA_TOPIC = 'orders.placed'
KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BROKER', '192.168.80.5:9092')

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def publish_order_placed(order_data):
    producer.send(KAFKA_TOPIC, order_data)
    producer.flush()


STATUS_UPDATE_TOPIC = 'orders.status_updated'

def publish_order_status_update(order_data):
    producer.send(STATUS_UPDATE_TOPIC, order_data)
    producer.flush()