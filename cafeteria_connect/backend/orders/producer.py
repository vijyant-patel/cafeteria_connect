from kafka import KafkaProducer
import json

producer = KafkaProducer(
    bootstrap_servers='192.168.80.5:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def send_order_event(data):
    producer.send('order-events', value=data)
    producer.flush()
