from django.db import models

import uuid

class Chat(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, blank=True, null=True)
    is_group = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    
    def __str__(self):
        return f"{self.name} ({'Group' if self.is_group else 'Private'})"
    
    class Meta:
        verbose_name = "Chat"
        verbose_name_plural = "Chats"
        ordering = ['-created_at']