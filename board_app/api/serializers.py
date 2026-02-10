from django.contrib.auth.models import User
from rest_framework import serializers

from auth_app.api.serializers import UserDetailsSerializer
from board_app.models import Board


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
