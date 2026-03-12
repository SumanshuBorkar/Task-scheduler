"""
Authentication API views.
"""
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from .serializers import RegisterSerializer, UserSerializer, LoginSerializer

User = get_user_model()


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """POST /api/auth/register/"""
    serializer = RegisterSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            {"success": False, "message": "Registration failed.", "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )
    user = serializer.save()
    refresh = RefreshToken.for_user(user)
    return Response(
        {
            "success": True,
            "message": "Account created successfully.",
            "user": UserSerializer(user).data,
            "tokens": {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            }
        },
        status=status.HTTP_201_CREATED
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """
    POST /api/auth/login/
    Custom login view — validates email+password directly,
    then generates JWT tokens manually.
    This bypasses SimpleJWT's TokenObtainPairView entirely,
    avoiding all username/email field naming issues.
    """
    serializer = LoginSerializer(
        data=request.data,
        context={'request': request}
    )
    if not serializer.is_valid():
        return Response(
            {
                "success": False,
                "message": "Login failed.",
                "errors": serializer.errors,
            },
            status=status.HTTP_401_UNAUTHORIZED
        )

    user = serializer.validated_data['user']
    refresh = RefreshToken.for_user(user)

    return Response(
        {
            "success": True,
            "message": "Login successful.",
            "user": UserSerializer(user).data,
            "tokens": {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def logout(request):
    """POST /api/auth/logout/"""
    refresh_token = request.data.get('refresh')
    if not refresh_token:
        return Response(
            {"success": False, "message": "Refresh token is required."},
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        token = RefreshToken(refresh_token)
        token.blacklist()
    except TokenError:
        return Response(
            {"success": False, "message": "Token is invalid or already expired."},
            status=status.HTTP_400_BAD_REQUEST
        )
    return Response(
        {"success": True, "message": "Logged out successfully."},
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me(request):
    """GET /api/auth/me/"""
    return Response(
        {"success": True, "user": UserSerializer(request.user).data},
        status=status.HTTP_200_OK
    )