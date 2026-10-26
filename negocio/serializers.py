from rest_framework import serializers
from usuarios.serializers import UsuarioSerializer
from .models import (
    Cliente, Categoria, Marca, Producto, 
    Proveedor, Compra, DetalleCompra, Venta, DetalleVenta
)

# 1. MODELOS BASE
class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = '__all__'

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = '__all__'

class MarcaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marca
        fields = '__all__'

class ProveedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proveedor
        fields = '__all__'

# 2. PRODUCTOS
class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = '__all__'

class ProductoDetalleSerializer(serializers.ModelSerializer):
    categoria = CategoriaSerializer(read_only=True)
    marca = MarcaSerializer(read_only=True)
    class Meta:
        model = Producto
        fields = '__all__'

# 3. COMPRAS
class DetalleCompraSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetalleCompra
        fields = '__all__'

class CompraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Compra
        fields = '__all__'

class CompraDetalleSerializer(serializers.ModelSerializer):
    proveedor = ProveedorSerializer(read_only=True)
    detalles = DetalleCompraSerializer(many=True, read_only=True)
    class Meta:
        model = Compra
        fields = '__all__'

# 4. VENTAS
class DetalleVentaSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetalleVenta
        fields = '__all__'

class VentaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Venta
        fields = '__all__'

class VentaDetalleSerializer(serializers.ModelSerializer):
    cliente = ClienteSerializer(read_only=True)
    usuario_vendedor = UsuarioSerializer(read_only=True)
    detalles = DetalleVentaSerializer(many=True, read_only=True)
    class Meta:
        model = Venta
        fields = '__all__'