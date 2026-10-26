from django.contrib.auth.models import AbstractUser
from django.db import models


class UsuarioPersonalizado(AbstractUser):
    ROLES = [
        ('ADMIN', 'Administrador'),
        ('VENDEDOR', 'Vendedor'),
        ('DEPOSITO', 'Operador de Depósito'),
    ]
    rol = models.CharField(max_length=20, choices=ROLES, default='VENDEDOR')
    telefono = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['id']

    def __str__(self):
        return f"{self.username} ({self.get_rol_display()})"
