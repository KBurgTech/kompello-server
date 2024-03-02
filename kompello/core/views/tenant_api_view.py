from drf_spectacular.utils import extend_schema
from rest_framework import serializers, viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from kompello.core.helper.serializers import SimpleResponseSerializer
from kompello.core.models.auth_models import KompelloUser, Tenant
from kompello.core.views.user_api_view import UserSerializer


class TenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = ['uuid', 'slug', 'name']
        extra_kwargs = {'uuid': {'read_only': True}}

    def create(self, validated_data):
        tenant = Tenant(
            slug=validated_data['slug'],
            name=validated_data['name']
        )
        tenant.save()
        return tenant


class TenantPermissions(permissions.BasePermission):
    """
    Allows a user to only access their own user object
    """

    def has_object_permission(self, request, view, obj):
        return request.user in obj.users.all()


class UserUuidListSerializer(serializers.Serializer):
    uuids = serializers.ListField(child=serializers.UUIDField())


class TenantViewSet(viewsets.ModelViewSet):
    """
    A viewset that serializes Users
    """
    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer
    lookup_field = 'uuid'

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ('list', 'create'):
            permission_classes = [IsAuthenticated]
        elif self.action in ('update', 'partial_update', 'destroy', 'users', 'retrieve', 'add_users', 'remove_users'):
            permission_classes = [TenantPermissions | IsAdminUser]
        else:
            return False

        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        serializer.instance.users.add(request.user)
        serializer.instance.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def list(self, request, *args, **kwargs):
        queryset = Tenant.objects.all()
        if not bool(request.user and request.user.is_staff):
            queryset = queryset.filter(users__in=[request.user])

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(
        responses={200: UserSerializer(many=True)},
        description="Get all users in the tenant",
        operation_id="tenant_users"
    )
    @action(detail=True, methods=['get'])
    def users(self, request: Request, uuid=None):
        tenant = self.get_object()
        serializer = UserSerializer(tenant.users.all(), many=True)
        return Response(serializer.data)

    @extend_schema(
        request=UserUuidListSerializer,
        responses={200: SimpleResponseSerializer},
        description="Add users to a tenant",
        operation_id="tenant_add_users"
    )
    @action(detail=True, methods=['post'])
    def add_users(self, request: Request, uuid=None):
        tenant = self.get_object()
        serializer = UserUuidListSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tenant.users.add(*KompelloUser.objects.filter(uuid__in=serializer.validated_data['uuids']))
        tenant.save()
        return Response(SimpleResponseSerializer({"message": "Success"}).data)

    @extend_schema(
        request=UserUuidListSerializer,
        responses={200: SimpleResponseSerializer},
        description="Remove users from a tenant",
        operation_id="tenant_remove_users"
    )
    @action(detail=True, methods=['post'])
    def remove_users(self, request: Request, uuid=None):
        tenant = self.get_object()
        serializer = UserUuidListSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tenant.users.remove(*KompelloUser.objects.filter(uuid__in=serializer.validated_data['uuids']))
        tenant.save()
        return Response(SimpleResponseSerializer({"message": "Success"}).data)
