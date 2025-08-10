from django.db import models
from django.utils.translation import gettext_lazy as _

from users.models import User
from .message import Message

import uuid


class MessageReaction(models.Model):
    class ReactionType(models.TextChoices):
        LIKE = 'like', _('Like')
        LOVE = 'love', _('Love')
        LAUGH = 'laugh', _('Laugh')
        WOW = 'wow', _('Wow')
        SAD = 'sad', _('Sad')
        ANGRY = 'angry', _('Angry')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='reactions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reactions')
    type = models.CharField(max_length=50, choices=ReactionType.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('message', 'user')
        indexes = [
            models.Index(fields=['message']),
            models.Index(fields=['user']),
            models.Index(fields=['created_at']),
        ]
