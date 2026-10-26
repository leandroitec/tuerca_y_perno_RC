from django.shortcuts import render
from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import (
    Cliente, Categoria, Marca, Producto, 
    Proveedor, Compra, DetalleCompra, Venta, DetalleVenta
)
from .serializers import (
    ClienteSerializer, CategoriaSerializer, MarcaSerializer, 
    ProductoSerializer, ProductoDetalleSerializer, ProveedorSerializer, 
    CompraSerializer, CompraDetalleSerializer, DetalleCompraSerializer, 
    VentaSerializer, VentaDetalleSerializer, DetalleVentaSerializer
)

def home_view(request):
    return render(request, 'index.html', {})

class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    permission_classes = [permissions.IsAuthenticated]

class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [permissions.IsAuthenticated]

class MarcaViewSet(viewsets.ModelViewSet):
    queryset = Marca.objects.all()
    serializer_class = MarcaSerializer
    permission_classes = [permissions.IsAuthenticated]

class ProveedorViewSet(viewsets.ModelViewSet):
    queryset = Proveedor.objects.all()
    serializer_class = ProveedorSerializer
    permission_classes = [permissions.IsAuthenticated]

# ==========================================
# PRODUCTOS CON RUTINA DE STOCK
# ==========================================
class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['categoria', 'marca']
    search_fields = ['nombre', 'descripcion']
    ordering_fields = ['precio', 'stock', 'nombre']

    def get_serializer_class(self):
        # Muestra datos anidados exclusivamente al consultar list (get all)
        if self.action == 'list':
            return ProductoDetalleSerializer
        return ProductoSerializer

    @action(detail=True, methods=['post'], url_path='actualizar-stock')
    def actualizar_stock(self, request, pk=None):
        producto = self.get_object()
        cantidad = int(request.data.get('cantidad', 0))
        operacion = request.data.get('operacion', 'sumar')

        if operacion == 'sumar':
            producto.stock += cantidad
        elif operacion == 'restar':
            producto.stock -= cantidad
        elif operacion == 'fijar':
            producto.stock = cantidad

        producto.save()
        return Response({"mensaje": f"Stock actualizado a {producto.stock}"}, status=status.HTTP_200_OK)

# ==========================================
# VENTAS Y SUS DETALLES
# ==========================================
class VentaViewSet(viewsets.ModelViewSet):
    queryset = Venta.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['cliente', 'estado']
    ordering_fields = ['fecha', 'total']

    def get_serializer_class(self):
        # Muestra datos anidados exclusivamente al consultar list (get all)
        if self.action == 'list':
            return VentaDetalleSerializer
        return VentaSerializer

    def perform_create(self, serializer):
        serializer.save(usuario_vendedor=self.request.user)

    @action(detail=False, methods=['get'], url_path='ventas-del-dia')
    def ventas_del_dia(self, request):
        hoy = timezone.now().date()
        ventas = self.get_queryset().filter(fecha__date=hoy)
        serializer = VentaDetalleSerializer(ventas, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='finalizar-venta')
    def finalizar_venta(self, request, pk=None):
        venta = self.get_object()
        venta.estado = 'COMPLETADA'
        venta.save()
        return Response({"mensaje": "Venta completada exitosamente."}, status=status.HTTP_200_OK)

class DetalleVentaViewSet(viewsets.ModelViewSet):
    queryset = DetalleVenta.objects.all()
    serializer_class = DetalleVentaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        detalle = serializer.save()
        producto = detalle.producto
        producto.stock -= detalle.cantidad
        producto.save()

        venta = detalle.venta
        venta.total += detalle.subtotal
        venta.save()

# ==========================================
# COMPRAS (Misma lógica que Ventas)
# ==========================================
class CompraViewSet(viewsets.ModelViewSet):
    queryset = Compra.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        # Muestra datos anidados exclusivamente al consultar list (get all)
        if self.action == 'list':
            return CompraDetalleSerializer
        return CompraSerializer

class DetalleCompraViewSet(viewsets.ModelViewSet):
    queryset = DetalleCompra.objects.all()
    serializer_class = DetalleCompraSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        detalle = serializer.save()
        producto = detalle.producto
        producto.stock += detalle.cantidad
        producto.save()

        compra = detalle.compra
        compra.total += detalle.subtotal
        compra.save()