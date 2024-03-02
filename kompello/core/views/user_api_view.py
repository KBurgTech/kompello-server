from auditlog.models import Q
from django.contrib.auth.models import Permission
from rest_framework_simplejwt.tokens import RefreshToken
from kompello.core.helper.serializers import SimpleResponseSerializer
from kompello.core.models.auth_models import KompelloUser
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, serializers, status, permissions
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = KompelloUser
        fields = ['uuid', 'first_name', 'last_name', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}, 'uuid': {'read_only': True}}

    def create(self, validated_data):
        user = KompelloUser(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    def update(self, instance, validated_data):
        user = super().update(instance, validated_data)
        try:
            user.set_password(validated_data['password'])
            user.save()
        except KeyError:
            pass
        return user


class PasswordSerializer(serializers.Serializer):
    password = serializers.CharField()

class PermissionListSerializer(serializers.Serializer):
    permissions = serializers.ListField(child=serializers.CharField())

class KompelloUserPermissions(permissions.BasePermission):
    """
    Allows a user to only access their own user object
    """

    def has_object_permission(self, request, view, obj):
        return request.user == obj


class UserViewSet(viewsets.ModelViewSet):
    """
    A viewset that serializes Users
    """
    queryset = KompelloUser.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'uuid'

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'list':
            permission_classes = [IsAdminUser]
        elif self.action in ('retrieve', 'update', 'partial_update', 'destroy', 'set_password', 'permissions'):
            permission_classes = [KompelloUserPermissions | IsAdminUser]
        else:
            permission_classes = [permissions.AllowAny]

        return [permission() for permission in permission_classes]

    @extend_schema(
        request=PasswordSerializer,
        responses={200: SimpleResponseSerializer},
        description="Change a users password",
        operation_id="users_set_password"
    )
    @action(detail=True, methods=['post'])
    def set_password(self, request: Request, uuid=None):
        user = self.get_object()
        if user != request.user:
            return Response({'message': 'You can only change your own password!'}, status=status.HTTP_403_FORBIDDEN)
        serializer = PasswordSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user.set_password(serializer.validated_data['password'])
            user.save()
            return Response({'message': 'Password set'})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        responses={200: UserSerializer},
        description="Get currently logged in user",
        operation_id="users_me"
    )
    @action(detail=False, methods=['get'])
    def me(self, request: Request):
        user = request.user
        return Response(UserSerializer(user).data)
    
    @extend_schema(
        responses={200: PermissionListSerializer},
        description="Get all permissions for the user",
        operation_id="permissions"
    )
    @action(detail=True, methods=['get'])
    def permissions(self, request: Request, uuid=None):
        user = self.get_object()
        if user.is_staff:
            permissions = Permission.objects.all().values_list('codename', flat=True)
        else:
            permissions = Permission.objects.filter(Q(user=user) | Q(group__user=user)).values_list('codename', flat=True).all()
        return Response(PermissionListSerializer({"permissions": permissions}).data)
