from rest_framework import viewsets, permissions
from .models import UsuarioPersonalizado
from .serializers import UsuarioSerializer


class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = UsuarioPersonalizado.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [permissions.IsAuthenticated]
