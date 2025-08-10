from django.db import models
from django.utils.translation import gettext_lazy as _

from users.models import User
from .chat import Chat

import uuid

class Message(models.Model):
    class MessageType(models.TextChoices):
        TEXT = 'text', _('Text')
        EMOJI = 'emoji', _('Emoji')
        PHOTO = 'photo', _('Photo')
        VIDEO = 'video', _('Video')
        AUDIO = 'audio', _('Audio')


    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.CharField(max_length=10, choices=MessageType.choices, default=MessageType.TEXT)
    content = models.TextField(null=True, blank=True)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages_sent')
    reply_to = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)


    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['chat']),
            models.Index(fields=['sender']),
            models.Index(fields=['created_at']),
        ]
