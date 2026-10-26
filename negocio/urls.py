from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    ClienteViewSet,
    CategoriaViewSet,
    MarcaViewSet,
    ProductoViewSet,
    ProveedorViewSet,
    CompraViewSet,
    VentaViewSet,
    DetalleCompraViewSet,
    DetalleVentaViewSet,
)

router = DefaultRouter()
router.register(r'clientes', ClienteViewSet, basename='cliente')
router.register(r'categorias', CategoriaViewSet, basename='categoria')
router.register(r'marcas', MarcaViewSet, basename='marca')
router.register(r'productos', ProductoViewSet, basename='producto')
router.register(r'proveedores', ProveedorViewSet, basename='proveedor')
router.register(r'compras', CompraViewSet, basename='compra')
router.register(r'ventas', VentaViewSet, basename='venta')
router.register(r'detalles-compra', DetalleCompraViewSet, basename='detalle-compra')
router.register(r'detalles-venta', DetalleVentaViewSet, basename='detalle-venta')

urlpatterns = [
    path('', include(router.urls)),
]
