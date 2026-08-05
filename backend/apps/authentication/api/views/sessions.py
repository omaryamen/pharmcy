"""Session management endpoints."""

from __future__ import annotations

from rest_framework.response import Response

from apps.common.api.viewsets import BaseAPIView

from ...serializers import LoginSessionSerializer
from ...services import SessionService


class SessionListView(BaseAPIView):
    """List the authenticated user's active sessions."""

    def get(self, request):
        sessions = SessionService().list_sessions(user=request.user)
        return Response(LoginSessionSerializer(sessions, many=True).data)


class SessionRevokeView(BaseAPIView):
    """Revoke one of the user's own sessions."""

    def post(self, request, pk):
        session = SessionService().revoke_session(
            user=request.user,
            session_id=pk,
            request=request,
        )
        return Response(LoginSessionSerializer(session).data)


class SessionRevokeAllView(BaseAPIView):
    """Revoke every session of the authenticated user (sign out everywhere)."""

    def post(self, request):
        count = SessionService().revoke_all_sessions(user=request.user, request=request)
        return Response({"revoked": count})
