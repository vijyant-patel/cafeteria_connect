# notifications/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Notification

class NotificationListView(APIView):
    def get(self, request):
        user = request.user
        notifs = Notification.objects.filter(recipient=user).order_by("-created_at")
        data = [{
            "id": n.id,
            "message": n.message,
            "type": n.type,
            "is_read": n.is_read,
            "created_at": n.created_at,
        } for n in notifs]
        return Response(data)
