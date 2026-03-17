from rest_framework import serializers

from .models import ChatSession, LegalQuery


class ChatSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatSession
        fields = ['id', 'created_at']


class LegalQuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = LegalQuery
        fields = ['id', 'status', 'user_query', 'ai_response', 'created_at', 'updated_at']


class CreateLegalQuerySerializer(serializers.Serializer):
    session_id = serializers.IntegerField()
    user_query = serializers.CharField()

    def validate_session_id(self, value):
        if not ChatSession.objects.filter(id=value).exists():
            raise serializers.ValidationError('Invalid session_id')
        return value
