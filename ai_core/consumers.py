# ai_core/consumers.py
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from .models import FeatureRequest
import json

class AISystemConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.channel_layer.group_add(
            f"user_{self.scope['user'].id}",
            self.channel_name
        )

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            f"user_{self.scope['user'].id}",
            self.channel_name
        )

    async def receive_json(self, content):
        """Handle incoming WebSocket messages"""
        message_type = content.get('type')
        if message_type == 'feature_status':
            await self.send_feature_status(content['feature_id'])

    async def feature_update(self, event):
        """Send feature implementation updates to connected clients"""
        await self.send_json({
            'type': 'feature_update',
            'feature_id': event['feature_id'],
            'status': event['status'],
            'details': event['details']
        })

    async def send_feature_status(self, feature_id):
        """Send current feature status"""
        try:
            feature = await self.get_feature(feature_id)
            await self.send_json({
                'type': 'feature_status',
                'feature_id': feature_id,
                'status': feature.status,
                'details': feature.implementation_details
            })
        except FeatureRequest.DoesNotExist:
            await self.send_json({
                'type': 'error',
                'message': f'Feature {feature_id} not found'
            })