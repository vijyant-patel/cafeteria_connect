from twilio.rest import Client

def send_sms(to, message):
    account_sid = "your_twilio_sid"
    auth_token = "your_twilio_auth_token"
    client = Client(account_sid, auth_token)

    client.messages.create(
        body=message,
        from_="+1234567890",  # Twilio number
        to=to
    )
    print(f"✅ SMS sent to {to}")
