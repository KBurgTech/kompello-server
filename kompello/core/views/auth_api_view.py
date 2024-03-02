from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from kompello.core.auth import get_user_social_auth, parse_id_token
from rest_framework import exceptions
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

from kompello.core.models.auth_models import KompelloUser

class SocialAuthLoginSerializer(serializers.Serializer):
    provider = serializers.CharField()
    access_token = serializers.CharField()
    id_token = serializers.CharField()

class RefreshTokenRequestSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()

class UserPasswordLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

class RegisterSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField()
    password_repeated = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()

class UserInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = KompelloUser
        fields = ["uuid", "email", "first_name", "last_name"]

class LoginResponseSerializer(serializers.Serializer):
    access_token = serializers.CharField()
    refresh_token = serializers.CharField()
    exprires_at = serializers.IntegerField()
    user = UserInformationSerializer()

@extend_schema(
    request=SocialAuthLoginSerializer,
    responses={200: LoginResponseSerializer},
    description="Log a user in and create a session",
    operation_id="social_auth"
)
@api_view(['post'])
def social_auth(request: Request):
    serializer = SocialAuthLoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    try:
        id_token = parse_id_token(serializer.validated_data)
        user = get_user_social_auth(serializer.validated_data['provider'], id_token['sub'])
        if user is None:
            raise exceptions.NotAuthenticated("User not found") 

        return Response(RefreshToken.for_user(user))         
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(
    request=UserPasswordLoginSerializer,
    responses={200: LoginResponseSerializer},
    description="Log a user in and create a session",
    operation_id="password_auth"
)
@api_view(['post'])
def password_auth(request: Request):
    serializer = UserPasswordLoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = authenticate(request, username=serializer.validated_data["username"], password=serializer.validated_data["password"])
    if user is None:
        raise exceptions.NotAuthenticated("User not found")
    
    token = RefreshToken.for_user(user)

    return Response(LoginResponseSerializer({"access_token": str(token.access_token), "refresh_token": str(token), "user": user, "exprires_at": token.access_token.payload["exp"]}).data)

@extend_schema(
    request=RegisterSerializer,
    responses={200: LoginResponseSerializer},
    description="Register a new user and create a session",
    operation_id="register"
)
@api_view(['post'])
def register(request: Request):
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    if serializer.validated_data["password"] != serializer.validated_data["password_repeated"]:
        raise exceptions.ValidationError("Passwords do not match")
    
    if KompelloUser.objects.filter(email=serializer.validated_data["email"]).exists():
        raise exceptions.ValidationError("User with this email already exists")
    
    user = KompelloUser.objects.create_user(
        email=serializer.validated_data["email"],
        password=serializer.validated_data["password"],
        first_name=serializer.validated_data["first_name"],
        last_name=serializer.validated_data["last_name"]
    )
    
    return Response(RefreshToken.for_user(user))
