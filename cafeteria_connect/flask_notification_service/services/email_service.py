import smtplib
from email.mime.text import MIMEText

def send_email(to, message):
    msg = MIMEText(message)
    msg["Subject"] = "Cafeteria Notification"
    msg["From"] = "no-reply@cafeteria.com"
    msg["To"] = to

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login("your_email@gmail.com", "your_password")
            server.sendmail("your_email@gmail.com", [to], msg.as_string())
        print(f"✅ Email sent to {to}")
    except Exception as e:
        print(f"❌ Email failed: {e}")
