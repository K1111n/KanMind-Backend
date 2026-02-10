from django.contrib import admin

from board_app.models import Board


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "created_by", "created_at"]
    search_fields = ["title"]
    list_filter = ["created_at"]
