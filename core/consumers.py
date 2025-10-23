import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import Booking, ChatMessage

User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time chat between customer and delivery partner"""
    
    async def connect(self):
        """Handle WebSocket connection"""
        self.booking_id = self.scope['url_route']['kwargs']['booking_id']
        self.room_group_name = f'chat_{self.booking_id}'
        
        # Get user from scope
        self.user = self.scope['user']
        
        # Check if user is authenticated
        if not self.user.is_authenticated:
            await self.close()
            return
        
        # Verify user has access to this booking
        has_access = await self.verify_booking_access()
        if not has_access:
            await self.close()
            return
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Receive message from WebSocket"""
        try:
            text_data_json = json.loads(text_data)
            message = text_data_json.get('message', '')
            
            if not message.strip():
                return
            
            # Save message to database
            chat_message = await self.save_message(message)
            
            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'sender_id': self.user.id,
                    'sender_name': self.user.get_full_name(),
                    'timestamp': chat_message.created_at.isoformat(),
                    'message_id': chat_message.id,
                }
            )
        except Exception as e:
            print(f"Error in receive: {e}")
    
    async def chat_message(self, event):
        """Receive message from room group"""
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender_id': event['sender_id'],
            'sender_name': event['sender_name'],
            'timestamp': event['timestamp'],
            'message_id': event['message_id'],
        }))
    
    @database_sync_to_async
    def verify_booking_access(self):
        """Verify that the user has access to this booking"""
        try:
            booking = Booking.objects.get(id=self.booking_id)
            # Check if user is customer or delivery partner for this booking
            if self.user.id == booking.customer_id or self.user.id == booking.delivery_partner_id:
                return True
            # Admin can access all chats
            if self.user.role == 'admin':
                return True
            return False
        except Booking.DoesNotExist:
            return False
    
    @database_sync_to_async
    def save_message(self, message):
        """Save chat message to database"""
        try:
            booking = Booking.objects.get(id=self.booking_id)
            
            # Determine receiver
            if self.user.id == booking.customer_id:
                receiver = booking.delivery_partner
            else:
                receiver = booking.customer
            
            # Create message
            chat_message = ChatMessage.objects.create(
                booking=booking,
                sender=self.user,
                receiver=receiver,
                message=message
            )
            
            return chat_message
        except Exception as e:
            print(f"Error saving message: {e}")
            return None

