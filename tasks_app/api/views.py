from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from board_app.models import Board
from tasks_app.api.permissions import (
    IsBoardMemberForTask,
    IsCommentAuthor,
    IsTaskCreatorOrBoardOwner,
)
from tasks_app.api.serializers import CommentSerializer, TaskSerializer
from tasks_app.models import Comment, Task


class AssignedToMeListView(generics.ListAPIView):
    """GET /api/tasks/assigned-to-me/"""

    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(assignee=self.request.user)


class ReviewingListView(generics.ListAPIView):
    """GET /api/tasks/reviewing/"""

    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(reviewer=self.request.user)


class TaskCreateView(generics.CreateAPIView):
    """POST /api/tasks/"""

    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        board_id = request.data.get("board")
        board = get_object_or_404(Board, id=board_id)
        user = request.user
        is_member = (
            board.created_by == user
            or board.members.filter(id=user.id).exists()
        )
        if not is_member:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You must be a board member.")
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class TaskDetailView(generics.GenericAPIView):
    """PATCH and DELETE /api/tasks/{task_id}/"""

    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    lookup_url_kwarg = "task_id"

    def get_queryset(self):
        return Task.objects.all()

    def get_permissions(self):
        permissions = [IsAuthenticated()]
        if self.request.method == "PATCH":
            permissions.append(IsBoardMemberForTask())
        elif self.request.method == "DELETE":
            permissions.append(IsTaskCreatorOrBoardOwner())
        return permissions

    def patch(self, request, *args, **kwargs):
        task = self.get_object()
        serializer = self.get_serializer(
            task, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        if "board" in serializer.validated_data:
            return Response(
                {"board": "Changing the board is not allowed."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, *args, **kwargs):
        task = self.get_object()
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CommentListCreateView(generics.ListCreateAPIView):
    """GET and POST /api/tasks/{task_id}/comments/"""

    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_task(self):
        task = get_object_or_404(Task, id=self.kwargs["task_id"])
        user = self.request.user
        board = task.board
        is_member = (
            board.created_by == user
            or board.members.filter(id=user.id).exists()
        )
        if not is_member:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You must be a board member.")
        return task

    def get_queryset(self):
        task = self.get_task()
        return Comment.objects.filter(task=task)

    def perform_create(self, serializer):
        task = self.get_task()
        serializer.save(author=self.request.user, task=task)


class CommentDeleteView(generics.DestroyAPIView):
    """DELETE /api/tasks/{task_id}/comments/{comment_id}/"""

    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsCommentAuthor]
    lookup_url_kwarg = "comment_id"

    def get_queryset(self):
        return Comment.objects.filter(
            task_id=self.kwargs["task_id"]
        )
