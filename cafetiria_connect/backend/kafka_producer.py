# kafka_producer.py
from kafka import KafkaProducer
import time
import json

producer = KafkaProducer(bootstrap_servers='192.168.80.5:9092',value_serializer=lambda v: json.dumps(v).encode('utf-8'))

for i in range(1):
    message = f'Hello Kafka! Message {i}'
    message = {
        "order_id": 202,
        "items": [
            {"product_id": 1, "quantity": 2},
            {"product_id": 3, "quantity": 1}
        ]
        }
    producer.send('test-topic', message)
    
    # producer.send('test-topic', message.encode('utf-8'))
    # print(f"✅ Sent: {message}")
    # time.sleep(1)

producer.flush()
