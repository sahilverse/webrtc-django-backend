from django.db import models
from django.utils.translation import gettext_lazy as _

from users.models import User
from .message import Message

import uuid

class MessageStatusEntry(models.Model):
    class Status(models.TextChoices):
        SENT = 'sent', _('Sent')
        DELIVERED = 'delivered', _('Delivered')
        READ = 'read', _('Read')


    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='statuses')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='message_statuses')
    status = models.CharField(max_length=20, choices=Status.choices)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('message', 'user')

