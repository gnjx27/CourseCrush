import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from .models import ChatMessage, CustomUser
from .serializers import ChatMessageSerializer

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_group_name = "chat_global"  # Hardcoded room name

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )

        self.accept()
        
        # Send chat history to the newly connected user
        self.send_chat_history()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    def send_chat_history(self):
        # Get the last 50 messages from the database
        messages = ChatMessage.objects.all().order_by('-created_at')[:50]
        # Use the serializer for consistent data format
        serializer = ChatMessageSerializer(reversed(messages), many=True)
        
        # Send history to the WebSocket
        self.send(text_data=json.dumps({'history': serializer.data}))

    def save_message(self, username, message):
        # Get the user and save the message
        try:
            user = CustomUser.objects.get(username=username)
            message_obj = ChatMessage.objects.create(
                user=user,
                message=message
            )
            return message_obj  # Return the saved message object
        except CustomUser.DoesNotExist:
            # Handle the case where user doesn't exist
            return None

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        
        # Get the username from the scope
        username = self.scope['user'].username
        
        # Save the message to the database and get the saved message object
        saved_message = self.save_message(username, message)
        
        if saved_message:
            # Use the serializer to format the message data
            serializer = ChatMessageSerializer(saved_message)
            message_data = serializer.data
            
            # Send message to room group
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name, {
                    "type": "chat.message", 
                    "message": message_data["message"],
                    "username": message_data["username"],
                    "created_at": message_data["created_at"]
                }
            )

    def chat_message(self, event):
        message = event["message"]
        username = event["username"]
        created_at = event["created_at"]

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            "message": message,
            "username": username,
            "created_at": created_at
        }))