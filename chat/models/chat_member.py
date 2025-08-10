from django.db import models

from users.models import User
from .chat import Chat

import uuid


class ChatMember(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    chat = models.ForeignKey(Chat, related_name='members', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_members')
    joined_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('chat', 'user')
        ordering = ['joined_at']
        