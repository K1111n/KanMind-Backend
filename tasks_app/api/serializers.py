from django.contrib.auth.models import User
from rest_framework import serializers

from auth_app.api.serializers import UserDetailsSerializer
from tasks_app.models import Comment, Task


class TaskSerializer(serializers.ModelSerializer):
    """Serializer for task list, create and update."""

    assignee = UserDetailsSerializer(read_only=True)
    reviewer = UserDetailsSerializer(read_only=True)
    assignee_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source="assignee",
        write_only=True,
        required=False,
        allow_null=True,
    )
    reviewer_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source="reviewer",
        write_only=True,
        required=False,
        allow_null=True,
    )
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            "id",
            "board",
            "title",
            "description",
            "status",
            "priority",
            "assignee",
            "reviewer",
            "assignee_id",
            "reviewer_id",
            "due_date",
            "comments_count",
        ]

    def get_comments_count(self, obj):
        return obj.comments.count()

    def _validate_board_member(self, user, board):
        """Check that user is a member or creator of the board."""
        if not board:
            return
        is_member = board.created_by == user or board.members.filter(id=user.id).exists()
        if not is_member:
            raise serializers.ValidationError(
                "User is not a member of this board."
            )

    def validate(self, attrs):
        board = attrs.get("board") or getattr(self.instance, "board", None)
        if attrs.get("assignee"):
            self._validate_board_member(attrs["assignee"], board)
        if attrs.get("reviewer"):
            self._validate_board_member(attrs["reviewer"], board)
        return attrs


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for task comments."""

    author = serializers.CharField(
        source="author.first_name", read_only=True
    )

    class Meta:
        model = Comment
        fields = ["id", "created_at", "author", "content"]
        read_only_fields = ["id", "created_at", "author"]
