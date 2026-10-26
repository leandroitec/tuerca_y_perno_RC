from rest_framework import serializers
from .models import UsuarioPersonalizado


class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsuarioPersonalizado
        fields = ['id', 'username', 'password', 'first_name', 'last_name', 'email', 'rol', 'telefono']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        usuario = super().create(validated_data)
        if password:
            usuario.set_password(password)
            usuario.save()
        return usuario
