import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import StudyGroup, GroupMessage
from django.contrib.auth.models import User

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Use the group name from the URL path, converted back from slug
        self.group_name_slug = self.scope['url_route']['kwargs']['group_name']
        self.group_name = self.group_name_slug.replace('_', ' ')
        self.group_channel_name = 'chat_%s' % self.group_name_slug

        # 1. Join room group
        await self.channel_layer.group_add(
            self.group_channel_name,
            self.channel_name
        )

        # 2. Accept the connection
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.group_channel_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        user = self.scope['user']
        if user.is_anonymous:
             return # Reject messages from anonymous users

        # 3. Save the message to the database asynchronously
        await self.save_message(user, self.group_name, message)

        # 4. Send message to room group
        await self.channel_layer.group_send(
            self.group_channel_name,
            {
                'type': 'chat.message',
                'message': message,
                'username': user.username
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        username = event['username']

        # 5. Send message back to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'username': username
        }))

    @sync_to_async
    def save_message(self, user, group_name, content):
        """Helper function to save the message in the database."""
        # Note: Must use exact name for lookup
        group = StudyGroup.objects.get(name=group_name)
        GroupMessage.objects.create(
            group=group,
            user=user,
            content=content
        )
