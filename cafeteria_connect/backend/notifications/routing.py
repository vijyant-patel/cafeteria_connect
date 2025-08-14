# notifications/routing.py
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/notifications/order/(?P<order_id>\d+)/$', consumers.NotificationConsumer.as_asgi()),
    re_path(r'ws/notifications/user/(?P<user_id>\d+)/$', consumers.NotificationConsumer.as_asgi()),

]
