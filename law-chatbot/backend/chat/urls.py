from django.urls import path

from .views import (
    AllSessionsView,
    AnalyticsView,
    CreateSessionView,
    LegalCatalogView,
    SessionMessagesView,
    SubmitQueryView,
)

urlpatterns = [
    path('sessions/', CreateSessionView.as_view(), name='create-session'),
    path('sessions/all/', AllSessionsView.as_view(), name='all-sessions'),
    path('query/', SubmitQueryView.as_view(), name='submit-query'),
    path('analytics/', AnalyticsView.as_view(), name='analytics'),
    path('<int:session_id>/', SessionMessagesView.as_view(), name='session-messages'),
    path('catalog/', LegalCatalogView.as_view(), name='legal-catalog'),
]
