from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from negocio.models import (
    Categoria,
    Marca,
    Producto,
    Cliente,
    Proveedor,
    Compra,
    DetalleCompra,
    Venta,
    DetalleVenta,
)

Usuario = get_user_model()


class Command(BaseCommand):
    help = "Puebla la base de datos con datos de prueba para Tuerca y Perno RC"

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Iniciando carga de datos iniciales..."))

        # 1. Crear Superusuario / Vendedores
        admin_user, _ = Usuario.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@tuercayperno.com",
                "first_name": "Administrador",
                "last_name": "General",
                "rol": "ADMIN",
                "is_staff": True,
                "is_superuser": True,
            }
        )
        admin_user.set_password("admin123")
        admin_user.save()

        vendedor, _ = Usuario.objects.get_or_create(
            username="vendedor",
            defaults={
                "email": "vendedor@tuercayperno.com",
                "first_name": "Lucas",
                "last_name": "Fernandez",
                "rol": "VENDEDOR",
                "telefono": "1140001122",
            }
        )
        vendedor.set_password("vendedor123")
        vendedor.save()

        # 2. Categorías
        cat_tornilleria, _ = Categoria.objects.get_or_create(
            nombre="Tornillería y Fijaciones",
            defaults={"descripcion": "Bulones, pernos, arandelas, tirafondos y tuercas."}
        )
        cat_herramientas, _ = Categoria.objects.get_or_create(
            nombre="Herramientas y Maquinarias",
            defaults={"descripcion": "Amoladoras, taladros, llaves y pinzas."}
        )
        cat_corralon, _ = Categoria.objects.get_or_create(
            nombre="Materiales de Corralón",
            defaults={"descripcion": "Cemento, cal, arena, hierro y ladrillos."}
        )
        cat_pinturas, _ = Categoria.objects.get_or_create(
            nombre="Pinturería e Impermeabilizantes",
            defaults={"descripcion": "Látex, esmaltes sintéticos y pinceles."}
        )

        # 3. Marcas
        marca_stanley, _ = Marca.objects.get_or_create(nombre="Stanley")
        marca_bosch, _ = Marca.objects.get_or_create(nombre="Bosch")
        marca_loma_negra, _ = Marca.objects.get_or_create(nombre="Loma Negra")
        marca_acindar, _ = Marca.objects.get_or_create(nombre="Acindar")
        marca_sinteplast, _ = Marca.objects.get_or_create(nombre="Sinteplast")

        # 4. Productos
        productos_data = [
            ("Perno Hexagonal Grado 5 1/2 x 3", "Perno de acero templado para estructuras", Decimal("450.00"), 300, cat_tornilleria, marca_stanley),
            ("Tuerca Autofrenante 1/2", "Tuerca con inserto de nylon anti-vibración", Decimal("180.00"), 500, cat_tornilleria, marca_stanley),
            ("Bolsa de Cemento Portland 50kg", "Cemento tradicional para albañilería y hormigón", Decimal("9800.00"), 120, cat_corralon, marca_loma_negra),
            ("Barra de Hierro del 10 (12m)", "Hierro torsionado para encadenados y losas", Decimal("14200.00"), 80, cat_corralon, marca_acindar),
            ("Amoladora Angular 4 1/2 850W", "Herramienta de corte y desbaste para metal y mampostería", Decimal("68900.00"), 25, cat_herramientas, marca_bosch),
            ("Látex Exterior Frentes 20L", "Pintura al agua de máxima durabilidad antihongos", Decimal("54000.00"), 35, cat_pinturas, marca_sinteplast),
        ]

        for nombre, desc, precio, stock, cat, marca in productos_data:
            Producto.objects.get_or_create(
                nombre=nombre,
                defaults={
                    "descripcion": desc,
                    "precio": precio,
                    "stock": stock,
                    "categoria": cat,
                    "marca": marca,
                }
            )

        # 5. Clientes
        cliente_rodriguez, _ = Cliente.objects.get_or_create(
            cuit="20-33445566-8",
            defaults={
                "nombre": "Construcciones Rodriguez S.R.L.",
                "telefono": "1155667788",
                "email": "obras@rodriguezconstrucciones.com",
                "direccion": "Ruta 8 Km 54, Pilar",
            }
        )
        cliente_gomez, _ = Cliente.objects.get_or_create(
            cuit="27-28394857-4",
            defaults={
                "nombre": "Mariana Gomez",
                "telefono": "1198765432",
                "email": "mariana.gomez@gmail.com",
                "direccion": "Calle Mitre 450, Quilmes",
            }
        )

        # 6. Proveedores
        prov_metal, _ = Proveedor.objects.get_or_create(
            cuit="30-55667788-9",
            defaults={
                "nombre": "Distribuidora Metalúrgica Central",
                "telefono": "1143218765",
                "email": "ventas@metalurgicacentral.com.ar",
                "direccion": "Av. Belgrano 1850, Avellaneda",
            }
        )

        self.stdout.write(self.style.SUCCESS("✓ Base de datos poblada exitosamente."))
        self.stdout.write(self.style.SUCCESS("  - Superusuario: admin / admin123"))
        self.stdout.write(self.style.SUCCESS("  - Vendedor: vendedor / vendedor123"))
