from django.urls import path
from rest_framework import routers
from kompello.core.views.auth_api_view import social_auth, password_auth, register
from kompello.core.views.tenant_api_view import TenantViewSet
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_simplejwt.views import TokenRefreshView
from kompello.core.views.user_api_view import UserViewSet

app_name = 'core'

router = routers.SimpleRouter()
router.register(r'users', UserViewSet, basename='users')
router.register(r'tenants', TenantViewSet, basename='tenants')

urlpatterns = [
    path('schema/', SpectacularAPIView.as_view(), name='schema.spec'),
    path('schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='core:schema.spec'), name='schema.swagger'),
    path('auth/social/', social_auth, name='auth.social'),
    path('auth/standard/', password_auth, name='auth.standard'),
    path('auth/register/', register, name='auth.register'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='auth.refresh'),
]

urlpatterns += router.urls