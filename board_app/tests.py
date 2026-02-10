from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from board_app.models import Board
from tasks_app.models import Task


class BoardListTestCase(APITestCase):
    """Tests for GET /api/boards/"""

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
            title="Test Board", created_by=self.owner
        )
        self.board.members.add(self.member)
        self.token = Token.objects.create(user=self.owner)
        self.client.credentials(
            HTTP_AUTHORIZATION="Token " + self.token.key
        )

    def test_list_boards_as_owner(self):
        """Owner sees their boards."""
        response = self.client.get("/api/boards/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Test Board")

    def test_list_boards_as_member(self):
        """Member sees boards they belong to."""
        token = Token.objects.create(user=self.member)
        self.client.credentials(
            HTTP_AUTHORIZATION="Token " + token.key
        )
        response = self.client.get("/api/boards/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_list_boards_as_outsider(self):
        """Outsider sees no boards."""
        token = Token.objects.create(user=self.outsider)
        self.client.credentials(
            HTTP_AUTHORIZATION="Token " + token.key
        )
        response = self.client.get("/api/boards/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

    def test_list_boards_unauthenticated(self):
        """Unauthenticated request returns 401."""
        self.client.credentials()
        response = self.client.get("/api/boards/")
        self.assertEqual(response.status_code, 401)

    def test_list_boards_contains_counts(self):
        """Board list contains correct count fields."""
        Task.objects.create(
            title="Task 1",
            board=self.board,
            created_by=self.owner,
            status="to-do",
            priority="high",
        )
        Task.objects.create(
            title="Task 2",
            board=self.board,
            created_by=self.owner,
            status="done",
            priority="medium",
        )
        response = self.client.get("/api/boards/")
        board_data = response.data[0]
        self.assertEqual(board_data["ticket_count"], 2)
        self.assertEqual(board_data["tasks_to_do_count"], 1)
        self.assertEqual(board_data["tasks_high_prio_count"], 1)
        self.assertEqual(board_data["member_count"], 1)
        self.assertIn("owner_id", board_data)


class BoardCreateTestCase(APITestCase):
    """Tests for POST /api/boards/"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="user@test.com",
            email="user@test.com",
            password="testpass123",
            first_name="Test User",
        )
        self.member = User.objects.create_user(
            username="member@test.com",
            email="member@test.com",
            password="testpass123",
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION="Token " + self.token.key
        )

    def test_create_board_success(self):
        """Create board returns 201."""
        data = {
            "title": "New Board",
            "members": [self.member.id],
        }
        response = self.client.post("/api/boards/", data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["title"], "New Board")
        self.assertEqual(response.data["owner_id"], self.user.id)
        self.assertEqual(response.data["member_count"], 1)

    def test_create_board_without_members(self):
        """Create board without members returns 201."""
        data = {"title": "Solo Board"}
        response = self.client.post("/api/boards/", data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["member_count"], 0)

    def test_create_board_missing_title(self):
        """Missing title returns 400."""
        response = self.client.post("/api/boards/", {}, format="json")
        self.assertEqual(response.status_code, 400)

    def test_create_board_unauthenticated(self):
        """Unauthenticated request returns 401."""
        self.client.credentials()
        response = self.client.post(
            "/api/boards/", {"title": "Fail"}, format="json"
        )
        self.assertEqual(response.status_code, 401)


class BoardDetailTestCase(APITestCase):
    """Tests for GET /api/boards/{id}/"""

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
            title="Detail Board", created_by=self.owner
        )
        self.board.members.add(self.member)
        Task.objects.create(
            title="Task A",
            board=self.board,
            created_by=self.owner,
            status="to-do",
            priority="high",
        )
        self.token = Token.objects.create(user=self.owner)
        self.client.credentials(
            HTTP_AUTHORIZATION="Token " + self.token.key
        )

    def test_detail_as_owner(self):
        """Owner can access board detail with tasks."""
        response = self.client.get(f"/api/boards/{self.board.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["title"], "Detail Board")
        self.assertEqual(len(response.data["members"]), 1)
        self.assertEqual(len(response.data["tasks"]), 1)
        self.assertEqual(
            response.data["tasks"][0]["title"], "Task A"
        )

    def test_detail_as_member(self):
        """Member can access board detail."""
        token = Token.objects.create(user=self.member)
        self.client.credentials(
            HTTP_AUTHORIZATION="Token " + token.key
        )
        response = self.client.get(f"/api/boards/{self.board.id}/")
        self.assertEqual(response.status_code, 200)

    def test_detail_as_outsider(self):
        """Outsider gets 404."""
        token = Token.objects.create(user=self.outsider)
        self.client.credentials(
            HTTP_AUTHORIZATION="Token " + token.key
        )
        response = self.client.get(f"/api/boards/{self.board.id}/")
        self.assertEqual(response.status_code, 404)

    def test_detail_nonexistent_board(self):
        """Non-existent board returns 404."""
        response = self.client.get("/api/boards/9999/")
        self.assertEqual(response.status_code, 404)


class BoardUpdateTestCase(APITestCase):
    """Tests for PATCH /api/boards/{id}/"""

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
        self.board = Board.objects.create(
            title="Old Title", created_by=self.owner
        )
        self.board.members.add(self.member)
        self.token = Token.objects.create(user=self.owner)
        self.client.credentials(
            HTTP_AUTHORIZATION="Token " + self.token.key
        )

    def test_update_title(self):
        """Owner can update board title."""
        data = {"title": "New Title"}
        response = self.client.patch(
            f"/api/boards/{self.board.id}/", data, format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["title"], "New Title")

    def test_update_members(self):
        """Owner can update board members."""
        new_member = User.objects.create_user(
            username="new@test.com",
            email="new@test.com",
            password="testpass123",
            first_name="New",
        )
        data = {"members": [new_member.id]}
        response = self.client.patch(
            f"/api/boards/{self.board.id}/", data, format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["members_data"]), 1)

    def test_update_as_member(self):
        """Member can update board."""
        token = Token.objects.create(user=self.member)
        self.client.credentials(
            HTTP_AUTHORIZATION="Token " + token.key
        )
        data = {"title": "Member Update"}
        response = self.client.patch(
            f"/api/boards/{self.board.id}/", data, format="json"
        )
        self.assertEqual(response.status_code, 200)


class BoardDeleteTestCase(APITestCase):
    """Tests for DELETE /api/boards/{id}/"""

    def setUp(self):
        self.owner = User.objects.create_user(
            username="owner@test.com",
            email="owner@test.com",
            password="testpass123",
        )
        self.member = User.objects.create_user(
            username="member@test.com",
            email="member@test.com",
            password="testpass123",
        )
        self.board = Board.objects.create(
            title="Delete Me", created_by=self.owner
        )
        self.board.members.add(self.member)
        self.token = Token.objects.create(user=self.owner)
        self.client.credentials(
            HTTP_AUTHORIZATION="Token " + self.token.key
        )

    def test_delete_as_owner(self):
        """Owner can delete board."""
        response = self.client.delete(f"/api/boards/{self.board.id}/")
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Board.objects.filter(id=self.board.id).exists())

    def test_delete_as_member_forbidden(self):
        """Member cannot delete board."""
        token = Token.objects.create(user=self.member)
        self.client.credentials(
            HTTP_AUTHORIZATION="Token " + token.key
        )
        response = self.client.delete(f"/api/boards/{self.board.id}/")
        self.assertEqual(response.status_code, 403)

    def test_delete_unauthenticated(self):
        """Unauthenticated request returns 401."""
        self.client.credentials()
        response = self.client.delete(f"/api/boards/{self.board.id}/")
        self.assertEqual(response.status_code, 401)
