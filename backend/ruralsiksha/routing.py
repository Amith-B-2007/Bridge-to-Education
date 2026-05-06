from django.urls import re_path
from doubts.consumers import DoubtConsumer

websocket_urlpatterns = [
    re_path(r'ws/doubts/(?P<session_id>[\w-]+)/$', DoubtConsumer.as_asgi()),
]
