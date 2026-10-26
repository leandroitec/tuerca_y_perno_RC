from django.conf import settings
from django.db import models


class Cliente(models.Model):
    """
    1. Modelo para registro de clientes del corralón y ferretería.
    """
    nombre = models.CharField(max_length=150)
    cuit = models.CharField(max_length=20, unique=True)
    telefono = models.CharField(max_length=30, blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} (CUIT: {self.cuit})"


class Categoria(models.Model):
    """
    2. Categorías de productos (ej: Tornillería, Pinturería, Corralón, Sanitarios, Herramientas).
    """
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Marca(models.Model):
    """
    3. Marcas de los productos comercializados.
    """
    nombre = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = 'Marca'
        verbose_name_plural = 'Marcas'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    """
    4. Catálogo de productos y control de existencias en depósito/mostrador.
    """
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(max_digits=12, decimal_places=2)
    stock = models.IntegerField(default=0)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name='productos')
    marca = models.ForeignKey(Marca, on_delete=models.PROTECT, related_name='productos')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} - ${self.precio} (Stock: {self.stock})"


class Proveedor(models.Model):
    """
    5. Proveedores mayoristas y de corralón (cemento, áridos, hierros, tornillos).
    """
    nombre = models.CharField(max_length=150)
    cuit = models.CharField(max_length=20, unique=True)
    telefono = models.CharField(max_length=30, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} (CUIT: {self.cuit})"


class Compra(models.Model):
    """
    6. Registro de compras a proveedores para reabastecimiento.
    """
    proveedor = models.ForeignKey(Proveedor, on_delete=models.PROTECT, related_name='compras')
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    observaciones = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Compra'
        verbose_name_plural = 'Compras'
        ordering = ['-fecha']

    def __str__(self):
        return f"Compra #{self.id} - {self.proveedor.nombre} - ${self.total}"


class DetalleCompra(models.Model):
    """
    7. Detalle línea a línea de los productos adquiridos en una compra.
    """
    compra = models.ForeignKey(Compra, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, related_name='detalles_compra')
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        verbose_name = 'Detalle de Compra'
        verbose_name_plural = 'Detalles de Compra'
        ordering = ['id']

    def save(self, *args, **kwargs):
        if not self.subtotal:
            self.subtotal = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.cantidad}x {self.producto.nombre} en Compra #{self.compra_id}"


class Venta(models.Model):
    """
    8. Registro de ventas a clientes emitidas por vendedores.
    """
    ESTADOS = [
        ('PENDIENTE', 'Pendiente'),
        ('COMPLETADA', 'Completada'),
        ('CANCELADA', 'Cancelada'),
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='ventas')
    usuario_vendedor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='ventas')
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='COMPLETADA')

    class Meta:
        verbose_name = 'Venta'
        verbose_name_plural = 'Ventas'
        ordering = ['-fecha']

    def __str__(self):
        return f"Venta #{self.id} - {self.cliente.nombre} (${self.total})"


class DetalleVenta(models.Model):
    """
    9. Ítems vendidos en cada transacción.
    """
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, related_name='detalles_venta')
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        verbose_name = 'Detalle de Venta'
        verbose_name_plural = 'Detalles de Venta'
        ordering = ['id']

    def save(self, *args, **kwargs):
        if not self.subtotal:
            self.subtotal = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.cantidad}x {self.producto.nombre} en Venta #{self.venta_id}"
