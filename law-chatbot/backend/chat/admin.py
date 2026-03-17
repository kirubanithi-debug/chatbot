from django.contrib import admin

from .models import ChatSession, LegalQuery

admin.site.register(ChatSession)
admin.site.register(LegalQuery)
