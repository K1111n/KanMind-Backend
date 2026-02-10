from django.contrib.auth.models import User
from rest_framework import serializers

from auth_app.api.serializers import UserDetailsSerializer
from board_app.models import Board
from tasks_app.models import Task


class BoardListSerializer(serializers.ModelSerializer):
    """Serializer for board list and creation."""

    owner_id = serializers.IntegerField(
        source="created_by_id", read_only=True
    )
    member_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()
    members = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        many=True,
        write_only=True,
        required=False,
    )

    class Meta:
        model = Board
        fields = [
            "id",
            "title",
            "member_count",
            "ticket_count",
            "tasks_to_do_count",
            "tasks_high_prio_count",
            "owner_id",
            "members",
        ]

    def get_member_count(self, obj):
        return obj.members.count()

    def get_ticket_count(self, obj):
        return obj.tasks.count()

    def get_tasks_to_do_count(self, obj):
        return obj.tasks.filter(status="to-do").count()

    def get_tasks_high_prio_count(self, obj):
        return obj.tasks.filter(priority="high").count()

    def create(self, validated_data):
        members = validated_data.pop("members", [])
        validated_data["created_by"] = self.context["request"].user
        board = Board.objects.create(**validated_data)
        board.members.set(members)
        return board


class BoardTaskSerializer(serializers.ModelSerializer):
    """Task representation nested inside board detail."""

    assignee = UserDetailsSerializer(read_only=True)
    reviewer = UserDetailsSerializer(read_only=True)
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "status",
            "priority",
            "assignee",
            "reviewer",
            "due_date",
            "comments_count",
        ]

    def get_comments_count(self, obj):
        return obj.comments.count()


class BoardDetailSerializer(serializers.ModelSerializer):
    """Serializer for board detail view."""

    owner_id = serializers.IntegerField(
        source="created_by_id", read_only=True
    )
    members = UserDetailsSerializer(many=True, read_only=True)
    tasks = BoardTaskSerializer(many=True, read_only=True)

    class Meta:
        model = Board
        fields = ["id", "title", "owner_id", "members", "tasks"]


class BoardUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating a board."""

    owner_data = UserDetailsSerializer(
        source="created_by", read_only=True
    )
    members_data = UserDetailsSerializer(
        source="members", many=True, read_only=True
    )
    members = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        many=True,
        write_only=True,
        required=False,
    )

    class Meta:
        model = Board
        fields = ["id", "title", "owner_data", "members_data", "members"]

    def update(self, instance, validated_data):
        members = validated_data.pop("members", None)
        instance.title = validated_data.get("title", instance.title)
        instance.save()
        if members is not None:
            instance.members.set(members)
        return instance
