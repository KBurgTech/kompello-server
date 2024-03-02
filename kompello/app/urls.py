from django.urls import include, path

urlpatterns = [
    path('api/', include("kompello.core.urls", namespace="core")),
]
