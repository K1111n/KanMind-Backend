from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from board_app.api.permissions import IsBoardOwner, IsBoardOwnerOrMember
from board_app.api.serializers import (
    BoardDetailSerializer,
    BoardListSerializer,
    BoardUpdateSerializer,
)
from board_app.models import Board


class BoardViewSet(ModelViewSet):
    """ViewSet for board CRUD operations."""

    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "patch", "delete"]

    def get_queryset(self):
        """Return boards filtered by action type."""
        if self.action == "list":
            user = self.request.user
            return Board.objects.filter(
                Q(created_by=user) | Q(members=user)
            ).distinct()
        return Board.objects.all()

    def get_serializer_class(self):
        """Return different serializer per action."""
        if self.action == "retrieve":
            return BoardDetailSerializer
        if self.action == "partial_update":
            return BoardUpdateSerializer
        return BoardListSerializer

    def get_permissions(self):
        """Add object-level permissions for detail actions."""
        permissions = [IsAuthenticated()]
        if self.action == "destroy":
            permissions.append(IsBoardOwner())
        elif self.action in ["retrieve", "partial_update"]:
            permissions.append(IsBoardOwnerOrMember())
        return permissions
