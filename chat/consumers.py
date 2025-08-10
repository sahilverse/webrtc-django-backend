import json 
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from chat.models import Chat, ChatMember, Message


from loguru import logger

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
            await self.close()
            return

        if not await self.is_user_member(self.chat_id, self.user.id):
            await self.close()
            return

        await self.channel_layer.group_add(
            self.group_name, 
            self.channel_name
        )
        
        logger.info(f"User {self.user.first_name + " " + self.user.last_name} connected to chat {self.chat_id}.")
        await self.accept()


    async def disconnect(self, close_code):
        if self.channel_layer is not None:
            await self.channel_layer.group_discard(
                self.group_name, 
                self.channel_name
            )

        logger.info(f"User {self.user.first_name + " " + self.user.last_name} disconnected from chat {self.chat_id}.")
        
    
    
    @database_sync_to_async
    def chat_exists(self, chat_id):
        return Chat.objects.filter(id=chat_id).exists()

    @database_sync_to_async
    def is_user_member(self, chat_id, user_id):
        return ChatMember.objects.filter(chat_id=chat_id, user_id=user_id).exists()

    @database_sync_to_async
    def create_message(self, content, sender, chat_id, reply_to_id=None):
        kwargs = {"content": content, "sender": sender, "chat_id": chat_id}
        if reply_to_id:
            kwargs["reply_to_id"] = reply_to_id
        return Message.objects.create(**kwargs)
      
