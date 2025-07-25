# notifications/utils.py
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Notification

def notify_user(user, message, notif_type="info"):
    # Save to DB
    notif = Notification.objects.create(
        recipient=user,
        message=message,
        type=notif_type
    )

    # Push via WebSocket
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"user_{user.id}",
        {
            "type": "send_notification",
            "data": {
                "id": notif.id,
                "message": notif.message,
                "type": notif.type,
                "created_at": notif.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            }
        }
    )
