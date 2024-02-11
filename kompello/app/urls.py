from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('api/schema/', SpectacularAPIView.as_view(), name='schema.spec'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='core:schema.spec'), name='schema.swagger'),
    path('api/', include("kompello.core.urls", namespace="core")),
]
