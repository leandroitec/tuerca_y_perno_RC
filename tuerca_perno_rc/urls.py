from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from negocio.views import home_view

urlpatterns = [
    # Vista raíz tradicional (Template HTML)
    path('', home_view, name='home'),

    # Panel de administración Django
    path('admin/', admin.site.urls),

    # Autenticación JWT
    path('api/auth/token/', TokenObtainPairView.as_view(permission_classes=[AllowAny]), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(permission_classes=[AllowAny]), name='token_refresh'),

    # Autenticación por Sesión para DRF Browsable API
    path('api-auth/', include('rest_framework.urls')),

    # Endpoints de la API REST (Apps Usuarios y Negocio)
    path('api/', include('usuarios.urls')),
    path('api/', include('negocio.urls')),

    # Documentación OpenAPI con drf-spectacular (Swagger UI y ReDoc)
    path(
        'api/schema/',
        SpectacularAPIView.as_view(permission_classes=[AllowAny]),
        name='schema'
    ),
    path(
        'api/docs/',
        SpectacularSwaggerView.as_view(url_name='schema', permission_classes=[AllowAny]),
        name='swagger-ui'
    ),
    path(
        'api/redoc/',
        SpectacularRedocView.as_view(url_name='schema', permission_classes=[AllowAny]),
        name='redoc'
    ),
]
