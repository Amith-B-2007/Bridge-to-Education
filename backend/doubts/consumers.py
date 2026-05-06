"""
WebSocket consumer for real-time doubts chat.

This is a placeholder for local-dev mode (channels not installed).
The frontend falls back to REST API for messages, so chat still works.

To enable real-time WebSockets:
1. pip install channels daphne
2. Uncomment 'channels' and 'daphne' in settings.py INSTALLED_APPS
3. Restore the channels-based consumer below.
"""

# Channels-based code preserved as comments for future use:
#
# from channels.generic.websocket import AsyncWebsocketConsumer
# from channels.db import database_sync_to_async
# import json
# from .models import DoubtSession, DoubtMessage
#
# class DoubtConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.session_id = self.scope['url_route']['kwargs']['session_id']
#         self.room_group_name = f'doubt_{self.session_id}'
#         await self.channel_layer.group_add(self.room_group_name, self.channel_name)
#         await self.accept()
#
#     async def disconnect(self, close_code):
#         await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
#
#     async def receive(self, text_data):
#         data = json.loads(text_data)
#         message = await self.create_message(self.session_id, self.scope['user'], data['message'])
#         await self.channel_layer.group_send(self.room_group_name, {
#             'type': 'doubt_message',
#             'message_id': str(message.id),
#             'sender': self.scope['user'].username,
#             'text': data['message'],
#             'timestamp': message.created_at.isoformat()
#         })
#
#     async def doubt_message(self, event):
#         await self.send(text_data=json.dumps({**event, 'type': 'message'}))
#
#     @database_sync_to_async
#     def create_message(self, session_id, user, message_text):
#         session = DoubtSession.objects.get(id=session_id)
#         return DoubtMessage.objects.create(session=session, sender=user, message=message_text)

DoubtConsumer = None
