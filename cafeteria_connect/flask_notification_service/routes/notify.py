from flask import Blueprint, request, jsonify
from services.email_service import send_email
from services.sms_service import send_sms
from services.push_service import send_push

notify_bp = Blueprint("notify", __name__)

# Shared Secret (same key Django & Flask dono ke paas hoga)
SECRET_TOKEN = "MY_SUPER_SECRET_KEY"   # <-- isko .env file me rakho

def require_auth(func):
    """Decorator to check Authorization header"""
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Unauthorized"}), 401

        token = auth_header.split(" ")[1]
        if token != SECRET_TOKEN:
            return jsonify({"error": "Invalid Token"}), 401

        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper


@notify_bp.route("/email", methods=["POST"])
def notify_email():
    data = request.json
    result = send_email(data["to"], data["subject"], data["body"])
    return jsonify(result)

@notify_bp.route("/sms", methods=["POST"])
def notify_sms():
    data = request.json
    result = send_sms(data["phone"], data["message"])
    return jsonify(result)

@notify_bp.route("/push", methods=["POST"])
@require_auth
def notify_push():
    print("notify_push")
    data = request.json
    print(f'{data=}')
    # result = send_push(data["device_token"], data["title"], data["body"])
    result = {'status':True}
    return jsonify(result)
