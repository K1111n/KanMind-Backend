from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase


class RegistrationTestCase(APITestCase):
    """Tests for POST /api/registration/"""

    def test_registration_success(self):
        """Successful registration returns 201 with token."""
        data = {
            "fullname": "Max Mustermann",
            "email": "max@example.com",
            "password": "securepass123",
            "repeated_password": "securepass123",
        }
        response = self.client.post("/api/registration/", data)
        self.assertEqual(response.status_code, 201)
        self.assertIn("token", response.data)
        self.assertEqual(response.data["email"], "max@example.com")
        self.assertEqual(response.data["fullname"], "Max Mustermann")
        self.assertIn("user_id", response.data)

    def test_registration_duplicate_email(self):
        """Registration with existing email returns 400."""
        User.objects.create_user(
            username="max@example.com",
            email="max@example.com",
            password="securepass123",
        )
        data = {
            "fullname": "Max Mustermann",
            "email": "max@example.com",
            "password": "securepass123",
            "repeated_password": "securepass123",
        }
        response = self.client.post("/api/registration/", data)
        self.assertEqual(response.status_code, 400)

    def test_registration_password_mismatch(self):
        """Mismatched passwords return 400."""
        data = {
            "fullname": "Max Mustermann",
            "email": "max@example.com",
            "password": "securepass123",
            "repeated_password": "wrongpass456",
        }
        response = self.client.post("/api/registration/", data)
        self.assertEqual(response.status_code, 400)

    def test_registration_short_password(self):
        """Password shorter than 8 characters returns 400."""
        data = {
            "fullname": "Max Mustermann",
            "email": "max@example.com",
            "password": "short",
            "repeated_password": "short",
        }
        response = self.client.post("/api/registration/", data)
        self.assertEqual(response.status_code, 400)

    def test_registration_missing_fields(self):
        """Missing required fields return 400."""
        response = self.client.post("/api/registration/", {})
        self.assertEqual(response.status_code, 400)


class LoginTestCase(APITestCase):
    """Tests for POST /api/login/"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="max@example.com",
            email="max@example.com",
            password="securepass123",
            first_name="Max Mustermann",
        )

    def test_login_success(self):
        """Successful login returns 200 with token."""
        data = {"email": "max@example.com", "password": "securepass123"}
        response = self.client.post("/api/login/", data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("token", response.data)
        self.assertEqual(response.data["email"], "max@example.com")
        self.assertEqual(response.data["fullname"], "Max Mustermann")

    def test_login_wrong_password(self):
        """Wrong password returns 400."""
        data = {"email": "max@example.com", "password": "wrongpass"}
        response = self.client.post("/api/login/", data)
        self.assertEqual(response.status_code, 400)

    def test_login_nonexistent_user(self):
        """Non-existent email returns 400."""
        data = {"email": "nobody@example.com", "password": "securepass123"}
        response = self.client.post("/api/login/", data)
        self.assertEqual(response.status_code, 400)

    def test_login_missing_fields(self):
        """Missing fields return 400."""
        response = self.client.post("/api/login/", {})
        self.assertEqual(response.status_code, 400)


class EmailCheckTestCase(APITestCase):
    """Tests for GET /api/email-check/"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="max@example.com",
            email="max@example.com",
            password="securepass123",
            first_name="Max Mustermann",
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION="Token " + self.token.key
        )

    def test_email_check_found(self):
        """Existing email returns 200 with user data."""
        response = self.client.get(
            "/api/email-check/", {"email": "max@example.com"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["email"], "max@example.com")
        self.assertEqual(response.data["fullname"], "Max Mustermann")
        self.assertIn("id", response.data)

    def test_email_check_not_found(self):
        """Non-existent email returns 404."""
        response = self.client.get(
            "/api/email-check/", {"email": "nobody@example.com"}
        )
        self.assertEqual(response.status_code, 404)

    def test_email_check_missing_param(self):
        """Missing email parameter returns 400."""
        response = self.client.get("/api/email-check/")
        self.assertEqual(response.status_code, 400)

    def test_email_check_unauthenticated(self):
        """Unauthenticated request returns 401."""
        self.client.credentials()
        response = self.client.get(
            "/api/email-check/", {"email": "max@example.com"}
        )
        self.assertEqual(response.status_code, 401)
