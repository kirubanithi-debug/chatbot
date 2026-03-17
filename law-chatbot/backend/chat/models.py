from django.db import models


class ChatSession(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)


class LegalQuery(models.Model):
    status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('completed', 'Completed')],
        default='pending',
    )
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='queries')
    user_query = models.TextField()
    ai_response = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
