from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import CustomTokenObtainPairView, UsuarioViewSet

# Creamos el router para el CRUD de Usuarios
router = DefaultRouter()
router.register(r'', UsuarioViewSet, basename='usuarios')

urlpatterns = [
    # 1. Rutas de Autenticación JWT (Dejamos solo la que usa Next.js)
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # 2. Rutas del CRUD de UsuarioPersonalizado
    path('gestion/', include(router.urls)),
]