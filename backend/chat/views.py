import datetime

from django.db.models import Count, Q
from django.db.models.functions import TruncDate
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ChatSession, LegalQuery
from .serializers import (
    ChatSessionSerializer,
    CreateLegalQuerySerializer,
    LegalQuerySerializer,
)
from .rag_setup import get_legal_catalog
from .tasks import process_legal_query


class CreateSessionView(APIView):
    def post(self, request):
        session = ChatSession.objects.create()
        return Response({'session_id': session.id}, status=status.HTTP_201_CREATED)


class SubmitQueryView(APIView):
    def post(self, request):
        serializer = CreateLegalQuerySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        session = ChatSession.objects.get(id=serializer.validated_data['session_id'])
        legal_query = LegalQuery.objects.create(
            session=session,
            user_query=serializer.validated_data['user_query'],
            status='pending',
        )
        process_legal_query.delay(legal_query.id)
        return Response({'query_id': legal_query.id, 'status': legal_query.status}, status=status.HTTP_202_ACCEPTED)


class SessionMessagesView(APIView):
    def get(self, request, session_id: int):
        session = get_object_or_404(ChatSession, id=session_id)
        queries = session.queries.order_by('created_at')

        return Response(
            {
                'session': ChatSessionSerializer(session).data,
                'messages': LegalQuerySerializer(queries, many=True).data,
            },
            status=status.HTTP_200_OK,
        )


class LegalCatalogView(APIView):
    def get(self, request):
        search = request.query_params.get('search', '')
        catalog = get_legal_catalog(search=search)
        return Response(
            {
                'count': len(catalog),
                'results': catalog,
            },
            status=status.HTTP_200_OK,
        )


class AllSessionsView(APIView):
    """Return every session with aggregated query counts."""

    def get(self, request):
        sessions = (
            ChatSession.objects
            .annotate(
                query_count=Count('queries'),
                completed_count=Count('queries', filter=Q(queries__status='completed')),
                pending_count=Count('queries', filter=Q(queries__status='pending')),
            )
            .order_by('-created_at')
        )

        data = []
        for s in sessions:
            last_query = s.queries.order_by('-created_at').first()
            data.append({
                'id': s.id,
                'created_at': s.created_at,
                'query_count': s.query_count,
                'completed_count': s.completed_count,
                'pending_count': s.pending_count,
                'last_query': last_query.user_query if last_query else None,
                'last_status': last_query.status if last_query else None,
            })

        return Response({'sessions': data}, status=status.HTTP_200_OK)


class AnalyticsView(APIView):
    """Aggregated analytics for the dashboard."""

    def get(self, request):
        total_sessions = ChatSession.objects.count()
        total_queries = LegalQuery.objects.count()
        completed = LegalQuery.objects.filter(status='completed').count()
        pending = LegalQuery.objects.filter(status='pending').count()

        # Daily queries (last 7 days)
        seven_days_ago = timezone.now() - datetime.timedelta(days=7)
        daily = (
            LegalQuery.objects
            .filter(created_at__gte=seven_days_ago)
            .annotate(date=TruncDate('created_at'))
            .values('date')
            .annotate(count=Count('id'))
            .order_by('date')
        )

        # Intent distribution (top 10) from recent completed queries
        from .query_understanding import understand_user_query
        recent_queries = LegalQuery.objects.filter(
            status='completed',
        ).values_list('user_query', flat=True)[:100]

        intent_counts: dict[str, int] = {}
        for q in recent_queries:
            understanding = understand_user_query(q)
            for intent in understanding.intents:
                intent_counts[intent] = intent_counts.get(intent, 0) + 1

        intent_distribution = sorted(
            [{'intent': k.replace('_', ' ').title(), 'count': v} for k, v in intent_counts.items()],
            key=lambda x: x['count'],
            reverse=True,
        )[:10]

        # Recent queries
        recent = LegalQuery.objects.order_by('-created_at')[:10]
        recent_data = LegalQuerySerializer(recent, many=True).data

        return Response({
            'total_sessions': total_sessions,
            'total_queries': total_queries,
            'completed_queries': completed,
            'pending_queries': pending,
            'completion_rate': round(completed / total_queries * 100, 1) if total_queries > 0 else 0,
            'daily_queries': [{'date': str(d['date']), 'count': d['count']} for d in daily],
            'intent_distribution': intent_distribution,
            'recent_queries': recent_data,
        }, status=status.HTTP_200_OK)
