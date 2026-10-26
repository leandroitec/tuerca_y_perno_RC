from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UsuarioPersonalizado


@admin.register(UsuarioPersonalizado)
class UsuarioPersonalizadoAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Información de Negocio', {'fields': ('rol', 'telefono')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información de Negocio', {'fields': ('rol', 'telefono')}),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'rol', 'telefono', 'is_staff')
    list_filter = ('rol', 'is_staff', 'is_active')
    search_fields = ('username', 'first_name', 'last_name', 'email')
