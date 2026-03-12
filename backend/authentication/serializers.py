"""
Serializers for user registration and profile.
Serializers convert between Python objects and JSON,
and validate incoming request data.
"""
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate

# Always use get_user_model() instead of importing User directly.
# This respects the AUTH_USER_MODEL setting.
User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    """
    Validates and creates a new user account.
    Accepts: username, email, password, password_confirm
    """
    password = serializers.CharField(
        write_only=True,        # Never returned in responses
        min_length=8,
        style={'input_type': 'password'},
        help_text="Must be at least 8 characters."
    )
    password_confirm = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        help_text="Must match the password field."
    )

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'password_confirm']
        read_only_fields = ['id']

    def validate_email(self, value):
        """Ensure the email is not already registered."""
        if User.objects.filter(email=value.lower()).exists():
            raise serializers.ValidationError(
                "An account with this email already exists."
            )
        return value.lower()

    def validate(self, attrs):
        """Ensure both password fields match."""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError(
                {"password_confirm": "Passwords do not match."}
            )
        # Run Django's built-in password strength validators
        validate_password(attrs['password'])
        return attrs

    def create(self, validated_data):
        # Remove password_confirm — not a model field
        validated_data.pop('password_confirm')

        # create_user handles password hashing automatically
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    """
    Read-only serializer for returning user profile data.
    Used in /api/auth/me/ endpoint.
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'date_joined', 'last_login']
        read_only_fields = fields





class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Corrected serializer that accepts 'email' as the login field.
    
    How SimpleJWT works internally:
    - It reads self.username_field to know which field to authenticate with
    - It then calls AuthBackend.authenticate(request, **{username_field: value})
    - We must rename the field AND ensure username_field matches exactly
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # SimpleJWT adds a field named after the model's USERNAME_FIELD
        # Since our USERNAME_FIELD = 'email', the field should already
        # be named 'email' — but the parent may label it 'username'
        # This ensures the field is explicitly named 'email'
        if 'username' in self.fields:
            self.fields['email'] = self.fields.pop('username')


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )

    def validate(self, attrs):
        email = attrs.get('email', '').lower()
        password = attrs.get('password', '')

        # USERNAME_FIELD = 'email', so authenticate() expects 'email' kwarg
        user = authenticate(
            request=self.context.get('request'),
            email=email,
            password=password,
        )

        if not user:
            raise serializers.ValidationError(
                "No active account found with the given credentials."
            )
        if not user.is_active:
            raise serializers.ValidationError(
                "This account has been deactivated."
            )

        attrs['user'] = user
        return attrs