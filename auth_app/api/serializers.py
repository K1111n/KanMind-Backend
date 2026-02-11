from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import serializers


class UserDetailsSerializer(serializers.ModelSerializer):
    """Read-only serializer for user info in nested responses."""

    fullname = serializers.CharField(source="first_name", read_only=True)

    class Meta:
        model = User
        fields = ["id", "email", "fullname"]
        read_only_fields = ["id", "email", "fullname"]


class RegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration (create)."""

    fullname = serializers.CharField(
        max_length=150, source="first_name"
    )
    repeated_password = serializers.CharField(
        write_only=True, min_length=8
    )

    class Meta:
        model = User
        fields = ["fullname", "email", "password", "repeated_password"]
        extra_kwargs = {
            "password": {"write_only": True, "min_length": 8},
        }

    def validate_email(self, value):
        """Ensure email is unique."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists.")
        return value

    def validate(self, attrs):
        """Ensure both passwords match."""
        if attrs["password"] != attrs["repeated_password"]:
            raise serializers.ValidationError(
                {"repeated_password": "Passwords do not match."}
            )
        return attrs

    def create(self, validated_data):
        """Create user with email as username."""
        validated_data.pop("repeated_password")
        return User.objects.create_user(
            username=validated_data["email"],
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data["first_name"],
        )


class LoginSerializer(serializers.Serializer):
    """Serializer for user login (authentication)."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        """Authenticate user with email and password."""
        user = authenticate(
            username=attrs["email"], password=attrs["password"]
        )
        if not user:
            raise serializers.ValidationError(
                "Invalid email or password."
            )
        attrs["user"] = user
        return attrs
