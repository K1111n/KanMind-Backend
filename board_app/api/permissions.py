from rest_framework.permissions import BasePermission


class IsBoardOwner(BasePermission):
    """Only the board owner can perform this action."""

    def has_object_permission(self, request, view, obj):
        return obj.created_by == request.user


class IsBoardOwnerOrMember(BasePermission):
    """Board owner or members can access this board."""

    def has_object_permission(self, request, view, obj):
        if obj.created_by == request.user:
            return True
        return obj.members.filter(id=request.user.id).exists()
