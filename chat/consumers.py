import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from chat.models import Chat, ChatMember, Message
from chat.utils import rate_limit


from loguru import logger

from uuid import UUID

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.chat_id = self.scope["url_route"]["kwargs"]["chat_id"]
        self.group_name = f"chat_{self.chat_id}"

        if not self.user.is_authenticated:
            logger.error(f"Anonymous user tried to connect to chat {self.chat_id}.")
            await self.close()
            return

        if self.channel_layer is None:
            logger.error("Channel layer is not configured.")
            await self.close()
            return
        
        if not await self.chat_exists(self.chat_id):
            logger.error(f"Chat {self.chat_id} does not exist.")
            await self.close()
            return

        if not await self.is_user_member(self.chat_id, self.user.id):
            logger.error(f"User is not a member of chat {self.chat_id}.")
            await self.close()
            return

        await self.channel_layer.group_add(
            self.group_name, 
            self.channel_name
        )

        logger.info(f"User {self.user.get_full_name()} connected to chat {self.chat_id}.")
        await self.accept()


    async def disconnect(self, close_code):
        if self.channel_layer is not None:
            await self.channel_layer.group_discard(
                self.group_name, 
                self.channel_name
            )

        logger.info(f"User {self.user.get_full_name()} disconnected from chat {self.chat_id}.")

    async def receive(self, text_data):
        data = json.loads(text_data)
        
        msg_type = data.get("type")
        
        match msg_type:
            case "typing":
                is_typing = data.get("is_typing", False)
                await self.handle_typing(is_typing)
                
            case "chat_message":
                await self.handle_chat_message(
                data.get("content", ""),
                data.get("reply_to_id")
            )
            case _:
                logger.warning(f"Unknown message type: {msg_type} from user {self.user.id}")
                
                
    @rate_limit("typing_event", 2)  
    async def handle_typing(self, is_typing):
        if self.channel_layer is not None:
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "typing_status",
                    "user_id": self.user.id,
                    "username": self.user.get_full_name(),
                    "is_typing": is_typing,
                }
            )
            
    async def handle_chat_message(self, content, reply_to_id=None):
        if not content.strip():
            await self.send_error("Message content cannot be empty.", event_type="validation_error")
            return

        try:
            if reply_to_id:
                reply_to_id = UUID(reply_to_id)
        except (ValueError, TypeError):
            await self.send_error("Invalid Message Reply Id.", event_type="validation_error")
            return

        message = await self.create_message(
            content=content,
            sender=self.user,
            chat_id=self.chat_id,
            reply_to_id=reply_to_id
        )

        if self.channel_layer is not None:
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "chat_message_event",
                    "message": {
                        "type": "chat_message",
                        "id": str(message.id),
                        "content": message.content,
                        "sender": self.user.get_full_name(),
                        "chat_id": str(message.chat_id),
                        "reply_to_id": str(message.reply_to_id) if message.reply_to_id else None,
                        "created_at": message.created_at.isoformat(),
                        "updated_at": message.updated_at.isoformat(),
                    }
                }
            )

            
    async def chat_message_event(self, event):
        await self.send(text_data=json.dumps(event["message"]))

    @database_sync_to_async
    def chat_exists(self, chat_id):
        return Chat.objects.filter(id=chat_id).exists()

    @database_sync_to_async
    def is_user_member(self, chat_id, user_id):
        return ChatMember.objects.filter(chat_id=chat_id, user_id=user_id).exists()

    @database_sync_to_async
    def create_message(self, content, sender, chat_id, message_type="text", reply_to_id=None):
        kwargs = {
            "content": content,
            "sender": sender,
            "chat_id": chat_id,
            "type": message_type, 
        }
        if reply_to_id:
            kwargs["reply_to_id"] = reply_to_id
        return Message.objects.create(**kwargs)

    async def send_error(self, error_message, event_type="error"):
        """
        Helper to send error response over WebSocket.
        """
        payload = {
            "message": error_message,
            "type": event_type,
        }
        await self.send(text_data=json.dumps(payload))
