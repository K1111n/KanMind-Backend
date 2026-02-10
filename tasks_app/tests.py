from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from board_app.models import Board
from tasks_app.models import Comment, Task


class TaskSetupMixin:
    """Shared setup for task tests."""

    def setUp(self):
        self.owner = User.objects.create_user(
            username="owner@test.com",
            email="owner@test.com",
            password="testpass123",
            first_name="Owner",
        )
        self.member = User.objects.create_user(
            username="member@test.com",
            email="member@test.com",
            password="testpass123",
            first_name="Member",
        )
        self.outsider = User.objects.create_user(
            username="outsider@test.com",
            email="outsider@test.com",
            password="testpass123",
        )
        self.board = Board.objects.create(
            title="Board", created_by=self.owner
        )
        self.board.members.add(self.member)
        self.task = Task.objects.create(
            title="Test Task",
            description="A test task",
            board=self.board,
            created_by=self.owner,
            status="to-do",
            priority="high",
            assignee=self.member,
            reviewer=self.owner,
        )
        self.token = Token.objects.create(user=self.owner)
        self.client.credentials(
            HTTP_AUTHORIZATION="Token " + self.token.key
        )


class AssignedToMeTestCase(TaskSetupMixin, APITestCase):
    """Tests for GET /api/tasks/assigned-to-me/"""

    def test_assigned_to_me(self):
        """Returns tasks assigned to current user."""
        token = Token.objects.create(user=self.member)
        self.client.credentials(
            HTTP_AUTHORIZATION="Token " + token.key
        )
        response = self.client.get("/api/tasks/assigned-to-me/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Test Task")
        self.assertIn("comments_count", response.data[0])

    def test_assigned_to_me_empty(self):
        """Returns empty list if no tasks assigned."""
        response = self.client.get("/api/tasks/assigned-to-me/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

    def test_assigned_to_me_unauthenticated(self):
        """Unauthenticated returns 401."""
        self.client.credentials()
        response = self.client.get("/api/tasks/assigned-to-me/")
        self.assertEqual(response.status_code, 401)


class ReviewingTestCase(TaskSetupMixin, APITestCase):
    """Tests for GET /api/tasks/reviewing/"""

    def test_reviewing(self):
        """Returns tasks where user is reviewer."""
        response = self.client.get("/api/tasks/reviewing/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_reviewing_empty(self):
        """Returns empty list if no tasks to review."""
        token = Token.objects.create(user=self.outsider)
        self.client.credentials(
            HTTP_AUTHORIZATION="Token " + token.key
        )
        response = self.client.get("/api/tasks/reviewing/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)


class TaskCreateTestCase(TaskSetupMixin, APITestCase):
    """Tests for POST /api/tasks/"""

    def test_create_task_success(self):
        """Board member can create a task."""
        data = {
            "board": self.board.id,
            "title": "New Task",
            "description": "Description",
            "status": "to-do",
            "priority": "medium",
        }
        response = self.client.post("/api/tasks/", data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["title"], "New Task")

    def test_create_task_with_assignee(self):
        """Task can be created with assignee and reviewer."""
        data = {
            "board": self.board.id,
            "title": "Assigned Task",
            "status": "in-progress",
            "priority": "high",
            "assignee_id": self.member.id,
            "reviewer_id": self.owner.id,
            "due_date": "2025-12-31",
        }
        response = self.client.post("/api/tasks/", data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.data["assignee"]["id"], self.member.id
        )

    def test_create_task_as_outsider(self):
        """Non-member cannot create task."""
        token = Token.objects.create(user=self.outsider)
        self.client.credentials(
            HTTP_AUTHORIZATION="Token " + token.key
        )
        data = {
            "board": self.board.id,
            "title": "Fail Task",
            "status": "to-do",
            "priority": "low",
        }
        response = self.client.post("/api/tasks/", data, format="json")
        self.assertEqual(response.status_code, 403)

    def test_create_task_missing_title(self):
        """Missing title returns 400."""
        data = {"board": self.board.id, "status": "to-do"}
        response = self.client.post("/api/tasks/", data, format="json")
        self.assertEqual(response.status_code, 400)

    def test_create_task_unauthenticated(self):
        """Unauthenticated returns 401."""
        self.client.credentials()
        data = {"board": self.board.id, "title": "Fail"}
        response = self.client.post("/api/tasks/", data, format="json")
        self.assertEqual(response.status_code, 401)


class TaskUpdateTestCase(TaskSetupMixin, APITestCase):
    """Tests for PATCH /api/tasks/{id}/"""

    def test_update_task(self):
        """Board member can update task."""
        data = {"title": "Updated Title", "status": "done"}
        response = self.client.patch(
            f"/api/tasks/{self.task.id}/", data, format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["title"], "Updated Title")
        self.assertEqual(response.data["status"], "done")

    def test_update_task_change_board_forbidden(self):
        """Changing board is not allowed."""
        other_board = Board.objects.create(
            title="Other", created_by=self.owner
        )
        data = {"board": other_board.id}
        response = self.client.patch(
            f"/api/tasks/{self.task.id}/", data, format="json"
        )
        self.assertEqual(response.status_code, 400)

    def test_update_task_as_outsider(self):
        """Non-member cannot update task."""
        token = Token.objects.create(user=self.outsider)
        self.client.credentials(
            HTTP_AUTHORIZATION="Token " + token.key
        )
        data = {"title": "Hacked"}
        response = self.client.patch(
            f"/api/tasks/{self.task.id}/", data, format="json"
        )
        self.assertEqual(response.status_code, 403)

    def test_update_nonexistent_task(self):
        """Non-existent task returns 404."""
        response = self.client.patch(
            "/api/tasks/9999/", {"title": "Nope"}, format="json"
        )
        self.assertEqual(response.status_code, 404)


class TaskDeleteTestCase(TaskSetupMixin, APITestCase):
    """Tests for DELETE /api/tasks/{id}/"""

    def test_delete_as_creator(self):
        """Task creator can delete."""
        response = self.client.delete(f"/api/tasks/{self.task.id}/")
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Task.objects.filter(id=self.task.id).exists())

    def test_delete_as_board_owner(self):
        """Board owner can delete any task."""
        task = Task.objects.create(
            title="Member Task",
            board=self.board,
            created_by=self.member,
        )
        response = self.client.delete(f"/api/tasks/{task.id}/")
        self.assertEqual(response.status_code, 204)

    def test_delete_as_member_not_creator(self):
        """Member who didn't create task gets 403."""
        token = Token.objects.create(user=self.member)
        self.client.credentials(
            HTTP_AUTHORIZATION="Token " + token.key
        )
        response = self.client.delete(f"/api/tasks/{self.task.id}/")
        self.assertEqual(response.status_code, 403)

    def test_delete_as_outsider(self):
        """Outsider gets 403."""
        token = Token.objects.create(user=self.outsider)
        self.client.credentials(
            HTTP_AUTHORIZATION="Token " + token.key
        )
        response = self.client.delete(f"/api/tasks/{self.task.id}/")
        self.assertEqual(response.status_code, 403)


class CommentListCreateTestCase(TaskSetupMixin, APITestCase):
    """Tests for GET/POST /api/tasks/{id}/comments/"""

    def test_list_comments(self):
        """Board member can list comments."""
        Comment.objects.create(
            task=self.task,
            author=self.owner,
            content="First comment",
        )
        response = self.client.get(
            f"/api/tasks/{self.task.id}/comments/"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["content"], "First comment")
        self.assertEqual(response.data[0]["author"], "Owner")

    def test_create_comment(self):
        """Board member can create comment."""
        data = {"content": "New comment"}
        response = self.client.post(
            f"/api/tasks/{self.task.id}/comments/",
            data,
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["content"], "New comment")
        self.assertEqual(response.data["author"], "Owner")

    def test_create_comment_empty_content(self):
        """Empty content returns 400."""
        data = {"content": ""}
        response = self.client.post(
            f"/api/tasks/{self.task.id}/comments/",
            data,
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_comments_as_outsider(self):
        """Non-member gets 403."""
        token = Token.objects.create(user=self.outsider)
        self.client.credentials(
            HTTP_AUTHORIZATION="Token " + token.key
        )
        response = self.client.get(
            f"/api/tasks/{self.task.id}/comments/"
        )
        self.assertEqual(response.status_code, 403)

    def test_comments_nonexistent_task(self):
        """Non-existent task returns 404."""
        response = self.client.get("/api/tasks/9999/comments/")
        self.assertEqual(response.status_code, 404)


class CommentDeleteTestCase(TaskSetupMixin, APITestCase):
    """Tests for DELETE /api/tasks/{id}/comments/{id}/"""

    def setUp(self):
        super().setUp()
        self.comment = Comment.objects.create(
            task=self.task,
            author=self.owner,
            content="Delete me",
        )

    def test_delete_own_comment(self):
        """Author can delete their comment."""
        response = self.client.delete(
            f"/api/tasks/{self.task.id}/comments/{self.comment.id}/"
        )
        self.assertEqual(response.status_code, 204)

    def test_delete_others_comment_forbidden(self):
        """Non-author cannot delete comment."""
        token = Token.objects.create(user=self.member)
        self.client.credentials(
            HTTP_AUTHORIZATION="Token " + token.key
        )
        response = self.client.delete(
            f"/api/tasks/{self.task.id}/comments/{self.comment.id}/"
        )
        self.assertEqual(response.status_code, 403)

    def test_delete_nonexistent_comment(self):
        """Non-existent comment returns 404."""
        response = self.client.delete(
            f"/api/tasks/{self.task.id}/comments/9999/"
        )
        self.assertEqual(response.status_code, 404)
