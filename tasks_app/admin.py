from django.contrib import admin

from tasks_app.models import Comment, Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "status", "priority", "board", "assignee"]
    search_fields = ["title"]
    list_filter = ["status", "priority"]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ["id", "author", "task", "created_at"]
    list_filter = ["created_at"]
