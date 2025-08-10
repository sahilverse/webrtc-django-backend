from django.contrib import admin

import chat.models

# Register your models here.
admin.site.register(chat.models.Chat)
admin.site.register(chat.models.ChatMember)
admin.site.register(chat.models.Message)
admin.site.register(chat.models.MessageReaction)
admin.site.register(chat.models.MessageStatusEntry)
admin.site.register(chat.models.Call)
admin.site.register(chat.models.CallParticipant)
