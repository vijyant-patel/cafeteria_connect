import requests

def send_push(device_id, message):
    server_key = "your_firebase_server_key"
    url = "https://fcm.googleapis.com/fcm/send"

    payload = {
        "to": device_id,
        "notification": {
            "title": "Cafeteria Update",
            "body": message
        }
    }

    headers = {
        "Authorization": f"key={server_key}",
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)
    print(f"✅ Push sent: {response.json()}")
