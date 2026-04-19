import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


class LiveClassConsumer(AsyncWebsocketConsumer):
    """
    Handles:
      - Real-time chat messages
      - WebRTC signaling (offer / answer / ice-candidate)
      - raise-hand events
      - participant join / leave broadcasts
    """

    async def connect(self):
        self.live_class_id = self.scope['url_route']['kwargs']['live_class_id']
        self.room_group = f'live_class_{self.live_class_id}'
        self.user = self.scope['user']

        if self.user.is_anonymous:
            await self.close()
            return

        await self.channel_layer.group_add(self.room_group, self.channel_name)
        await self.accept()
        await self.add_participant()

        # Notify everyone else
        await self.channel_layer.group_send(self.room_group, {
            'type': 'user_joined',
            'username': self.user.username,
            'user_id': str(self.user.id),
        })
        logger.info(f"User {self.user.id} joined room {self.live_class_id}")

    async def disconnect(self, close_code):
        await self.record_leave()
        await self.channel_layer.group_send(self.room_group, {
            'type': 'user_left',
            'username': self.user.username,
            'user_id': str(self.user.id),
        })
        await self.channel_layer.group_discard(self.room_group, self.channel_name)
        logger.info(f"User {self.user.id} left room {self.live_class_id}")

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            msg_type = data.get('type')

            if msg_type == 'chat':
                await self.save_chat(data['message'])
                await self.channel_layer.group_send(self.room_group, {
                    'type': 'chat_message',
                    'message': data['message'],
                    'username': self.user.username,
                    'user_id': str(self.user.id),
                })

            # ---------- WebRTC signaling ----------
            elif msg_type == 'webrtc_offer':
                await self.channel_layer.group_send(self.room_group, {
                    'type': 'webrtc_offer',
                    'offer': data['offer'],
                    'from_user': str(self.user.id),
                })

            elif msg_type == 'webrtc_answer':
                await self.channel_layer.group_send(self.room_group, {
                    'type': 'webrtc_answer',
                    'answer': data['answer'],
                    'from_user': str(self.user.id),
                })

            elif msg_type == 'ice_candidate':
                await self.channel_layer.group_send(self.room_group, {
                    'type': 'ice_candidate',
                    'candidate': data['candidate'],
                    'from_user': str(self.user.id),
                })

            elif msg_type == 'raise_hand':
                await self.channel_layer.group_send(self.room_group, {
                    'type': 'raise_hand',
                    'username': self.user.username,
                    'user_id': str(self.user.id),
                    'raised': data.get('raised', True),
                })

        except Exception as e:
            logger.error(f"WebSocket receive error: {e}")

    # --------- Group message handlers ---------

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'chat',
            'message': event['message'],
            'username': event['username'],
            'user_id': event['user_id'],
        }))

    async def user_joined(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user_joined',
            'username': event['username'],
            'user_id': event['user_id'],
        }))

    async def user_left(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user_left',
            'username': event['username'],
            'user_id': event['user_id'],
        }))

    async def webrtc_offer(self, event):
        await self.send(text_data=json.dumps({
            'type': 'webrtc_offer',
            'offer': event['offer'],
            'from_user': event['from_user'],
        }))

    async def webrtc_answer(self, event):
        await self.send(text_data=json.dumps({
            'type': 'webrtc_answer',
            'answer': event['answer'],
            'from_user': event['from_user'],
        }))

    async def ice_candidate(self, event):
        await self.send(text_data=json.dumps({
            'type': 'ice_candidate',
            'candidate': event['candidate'],
            'from_user': event['from_user'],
        }))

    async def raise_hand(self, event):
        await self.send(text_data=json.dumps({
            'type': 'raise_hand',
            'username': event['username'],
            'user_id': event['user_id'],
            'raised': event['raised'],
        }))

    # --------- DB helpers ---------

    @database_sync_to_async
    def add_participant(self):
        from .models import LiveClass, LiveClassParticipant
        try:
            lc = LiveClass.objects.get(id=self.live_class_id)
            LiveClassParticipant.objects.get_or_create(live_class=lc, student=self.user)
        except LiveClass.DoesNotExist:
            pass

    @database_sync_to_async
    def record_leave(self):
        from .models import LiveClassParticipant
        LiveClassParticipant.objects.filter(
            live_class_id=self.live_class_id,
            student=self.user,
            left_at=None,
        ).update(left_at=timezone.now())

    @database_sync_to_async
    def save_chat(self, message):
        from .models import LiveClassChat
        LiveClassChat.objects.create(
            live_class_id=self.live_class_id,
            user=self.user,
            message=message,
        )
