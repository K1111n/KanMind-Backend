from django.urls import path

from tasks_app.api.views import (
    AssignedToMeListView,
    CommentDeleteView,
    CommentListCreateView,
    ReviewingListView,
    TaskCreateView,
    TaskDetailView,
)

urlpatterns = [
    path(
        "tasks/assigned-to-me/",
        AssignedToMeListView.as_view(),
        name="tasks-assigned-to-me",
    ),
    path(
        "tasks/reviewing/",
        ReviewingListView.as_view(),
        name="tasks-reviewing",
    ),
    path(
        "tasks/",
        TaskCreateView.as_view(),
        name="task-create",
    ),
    path(
        "tasks/<int:task_id>/",
        TaskDetailView.as_view(),
        name="task-detail",
    ),
    path(
        "tasks/<int:task_id>/comments/",
        CommentListCreateView.as_view(),
        name="comment-list-create",
    ),
    path(
        "tasks/<int:task_id>/comments/<int:comment_id>/",
        CommentDeleteView.as_view(),
        name="comment-delete",
    ),
]
