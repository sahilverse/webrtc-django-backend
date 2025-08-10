from django.db import models
from django.utils.translation import gettext_lazy as _

from users.models import User
from .chat import Chat

import uuid

class ChatMember(models.Model):
    class ChatRoles(models.TextChoices):
        ADMIN = "admin", _("Admin")
        MEMBER = "member", _("Member")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    chat = models.ForeignKey(Chat, related_name='members', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_members')
    role = models.CharField(max_length=20, choices=ChatRoles.choices, blank=True, null=True, default=ChatRoles.MEMBER)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('chat', 'user')
        ordering = ['joined_at']

    def save(self, *args, **kwargs):
        if not self.chat.is_group:
            self.role = None
        super().save(*args, **kwargs)

    def __str__(self):
        if self.chat.is_group:
            return f"{self.user.get_full_name()} - {self.role} in {self.chat.name}"
        
        other_member = self.chat.members.exclude(user=self.user).first() # type: ignore
        if other_member:
            return f"{self.user.get_full_name()} in private chat with {other_member.user.get_full_name()}"
        return f"{self.user.get_full_name()} in private chat"

