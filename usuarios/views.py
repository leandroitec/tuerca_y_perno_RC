from rest_framework import viewsets, permissions
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.exceptions import AuthenticationFailed

from .models import UsuarioPersonalizado
from .serializers import UsuarioSerializer

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        try:
            # Intentamos validar el login normal de JWT
            data = super().validate(attrs)
            
        except AuthenticationFailed as e:
            # SI FALLA EL LOGIN: 
            # Buscamos al usuario por su username para aumentarle el contador si el campo existe
            username = attrs.get(self.username_field)
            try:
                user_fallido = UsuarioPersonalizado.objects.get(username=username)
                if hasattr(user_fallido, 'intentos_fallidos'):
                    user_fallido.intentos_fallidos += 1 
                    user_fallido.save()
            except UsuarioPersonalizado.DoesNotExist:
                pass
            
            # Volvemos a lanzar el error 401 hacia el frontend
            raise e

        # SI EL LOGIN ES EXITOSO:
        # 1. Reseteamos el contador de intentos fallidos si el campo existe
        if hasattr(self.user, 'intentos_fallidos'):
            self.user.intentos_fallidos = 0
            self.user.save()
        
        # 2. Inyectamos los datos de UsuarioPersonalizado para el frontend
        data['usuario'] = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            'rol': getattr(self.user, 'rol', 'VENDEDOR') 
        }
        return data

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = UsuarioPersonalizado.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [permissions.IsAuthenticated]