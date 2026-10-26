from django.contrib import admin

from .models import (
    Cliente,
    Categoria,
    Marca,
    Producto,
    Proveedor,
    Compra,
    DetalleCompra,
    Venta,
    DetalleVenta,
)


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    """
    1. Registro de Clientes.
    """
    list_display = ('id', 'nombre', 'cuit', 'telefono', 'email', 'fecha_creacion')
    search_fields = ('nombre', 'cuit', 'telefono', 'email')
    list_filter = ('fecha_creacion',)


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    """
    2. Registro de Categorías.
    """
    list_display = ('id', 'nombre', 'descripcion')
    search_fields = ('nombre',)


@admin.register(Marca)
class MarcaAdmin(admin.ModelAdmin):
    """
    3. Registro de Marcas.
    """
    list_display = ('id', 'nombre')
    search_fields = ('nombre',)


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    """
    4. Registro de Productos con filtros y búsqueda avanzada.
    """
    list_display = ('id', 'nombre', 'precio', 'stock', 'categoria', 'marca', 'fecha_modificacion')
    list_filter = ('categoria', 'marca', 'fecha_creacion')
    search_fields = ('nombre', 'descripcion')
    list_editable = ('precio', 'stock')
    ordering = ('nombre',)


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    """
    5. Registro de Proveedores.
    """
    list_display = ('id', 'nombre', 'cuit', 'telefono', 'email', 'fecha_creacion')
    search_fields = ('nombre', 'cuit', 'email')
    list_filter = ('fecha_creacion',)


class DetalleCompraInline(admin.TabularInline):
    model = DetalleCompra
    extra = 1
    autocomplete_fields = ['producto']


@admin.register(Compra)
class CompraAdmin(admin.ModelAdmin):
    """
    6. Registro de Compras con detalle en línea.
    """
    list_display = ('id', 'proveedor', 'fecha', 'total', 'observaciones')
    list_filter = ('proveedor', 'fecha')
    search_fields = ('proveedor__nombre', 'observaciones')
    inlines = [DetalleCompraInline]
    readonly_fields = ('fecha',)


@admin.register(DetalleCompra)
class DetalleCompraAdmin(admin.ModelAdmin):
    """
    7. Registro de Detalles de Compra.
    """
    list_display = ('id', 'compra', 'producto', 'cantidad', 'precio_unitario', 'subtotal')
    list_filter = ('compra__fecha',)
    search_fields = ('producto__nombre', 'compra__id')


class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 1
    autocomplete_fields = ['producto']


@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    """
    8. Registro de Ventas con detalle en línea y filtros por estado y vendedor.
    """
    list_display = ('id', 'cliente', 'usuario_vendedor', 'fecha', 'total', 'estado')
    list_filter = ('estado', 'fecha', 'usuario_vendedor')
    search_fields = ('cliente__nombre', 'cliente__cuit', 'usuario_vendedor__username')
    inlines = [DetalleVentaInline]
    readonly_fields = ('fecha',)


@admin.register(DetalleVenta)
class DetalleVentaAdmin(admin.ModelAdmin):
    """
    9. Registro de Detalles de Venta.
    """
    list_display = ('id', 'venta', 'producto', 'cantidad', 'precio_unitario', 'subtotal')
    list_filter = ('venta__fecha',)
    search_fields = ('producto__nombre', 'venta__id')
