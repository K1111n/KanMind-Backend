from rest_framework.permissions import BasePermission


class IsBoardMemberForTask(BasePermission):
    """User must be a member or owner of the task's board."""

    def has_object_permission(self, request, view, obj):
        board = obj.board
        if board.created_by == request.user:
            return True
        return board.members.filter(id=request.user.id).exists()


class IsTaskCreatorOrBoardOwner(BasePermission):
    """Only the task creator or board owner can delete a task."""

    def has_object_permission(self, request, view, obj):
        if obj.created_by == request.user:
            return True
        return obj.board.created_by == request.user


class IsCommentAuthor(BasePermission):
    """Only the comment author can delete the comment."""

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user
