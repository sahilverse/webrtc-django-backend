from django.db import models
from django.utils.translation import gettext_lazy as _

from users.models import User
from .chat import Chat

import uuid

class Call(models.Model):

    class CallType(models.TextChoices):
        AUDIO = 'AUDIO', _('Audio')
        VIDEO = 'VIDEO', _('Video')

    class CallStatus(models.TextChoices):
        ONGOING = 'ONGOING', _('Ongoing')
        COMPLETED = 'COMPLETED', _('Completed')
        MISSED = 'MISSED', _('Missed')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='calls')
    initiator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='calls_initiated')
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    call_type = models.CharField(max_length=10, choices=CallType.choices)
    call_status = models.CharField(max_length=10, choices=CallStatus.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('chat', 'initiator', 'started_at')
        ordering = ['-started_at']
