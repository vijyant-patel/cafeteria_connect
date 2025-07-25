from kafka import KafkaConsumer

print('test_01')

consumer = KafkaConsumer(
    'test-topic',
    bootstrap_servers=['192.168.80.5:9092'],  # ✅ List, not string
    auto_offset_reset='earliest',
    group_id='test-group',
)
print('test_02')
print("🕹 Listening for messages on 'test-topic'...\n")

for message in consumer:
    # print(f"📥 Received: {message.value.decode('utf-8')}")
    print(f"📥 Received Order Data: {message.value}")

