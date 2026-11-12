from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import random

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
    help = "Puebla la base de datos con un conjunto amplio y realista de datos para Tuerca y Perno RC"

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Iniciando carga masiva de datos iniciales..."))

        # =========================================================================
        # 1. USUARIOS Y ROLES
        # =========================================================================
        usuarios_data = [
            {
                "username": "admin",
                "email": "admin@tuercayperno.com",
                "password": "admin12345",
                "first_name": "Administrador",
                "last_name": "General",
                "rol": "ADMIN",
                "is_staff": True,
                "is_superuser": True,
                "telefono": "1140001001",
            },
            {
                "username": "vendedor",
                "email": "vendedor@tuercayperno.com",
                "password": "vendedor123",
                "first_name": "Lucas",
                "last_name": "Fernandez",
                "rol": "VENDEDOR",
                "is_staff": True,
                "is_superuser": False,
                "telefono": "1140001002",
            },
            {
                "username": "vendedora_sofia",
                "email": "sofia.lopez@tuercayperno.com",
                "password": "sofia123",
                "first_name": "Sofia",
                "last_name": "Lopez",
                "rol": "VENDEDOR",
                "is_staff": False,
                "is_superuser": False,
                "telefono": "1140001003",
            },
            {
                "username": "cajero_martin",
                "email": "martin.castro@tuercayperno.com",
                "password": "cajero123",
                "first_name": "Martin",
                "last_name": "Castro",
                "rol": "VENDEDOR",
                "is_staff": False,
                "is_superuser": False,
                "telefono": "1140001004",
            },
            {
                "username": "deposito_marcos",
                "email": "marcos.deposito@tuercayperno.com",
                "password": "deposito123",
                "first_name": "Marcos",
                "last_name": "Suarez",
                "rol": "DEPOSITO",
                "is_staff": False,
                "is_superuser": False,
                "telefono": "1140001005",
            },
            {
                "username": "deposito_raul",
                "email": "raul.alvarez@tuercayperno.com",
                "password": "raul123",
                "first_name": "Raul",
                "last_name": "Alvarez",
                "rol": "DEPOSITO",
                "is_staff": False,
                "is_superuser": False,
                "telefono": "1140001006",
            },
        ]

        usuarios_creados = {}
        for u in usuarios_data:
            user, _ = Usuario.objects.get_or_create(
                username=u["username"],
                defaults={
                    "email": u["email"],
                    "first_name": u["first_name"],
                    "last_name": u["last_name"],
                    "rol": u["rol"],
                    "is_staff": u["is_staff"],
                    "is_superuser": u["is_superuser"],
                    "telefono": u["telefono"],
                }
            )
            user.set_password(u["password"])
            user.rol = u["rol"]
            user.is_staff = u["is_staff"]
            user.is_superuser = u["is_superuser"]
            user.save()
            usuarios_creados[u["username"]] = user

        # =========================================================================
        # 2. CATEGORÍAS
        # =========================================================================
        categorias_data = [
            ("Tornillería y Fijaciones", "Bulones, pernos, arandelas, tirafondos, tuercas y tacos."),
            ("Herramientas y Maquinarias", "Amoladoras, taladros, llaves, pinzas, discos y rotomartillos."),
            ("Materiales de Corralón", "Cemento, cal, arena, hierro, viguetas, bloques y ladrillos."),
            ("Pinturería e Impermeabilizantes", "Látex, esmaltes sintéticos, membranas, brochas y rodillos."),
            ("Sanitarios y Grifería", "Caños termofusión, accesorios de PVC, griferías, válvulas y selladores."),
            ("Electricidad e Iluminación", "Cables normalizados, llaves térmicas, tomacorrientes y reflectores LED."),
            ("Seguridad Industrial y Protección", "Cascos de obra, guantes de descarne, antiparras y arneses."),
        ]

        categorias_dict = {}
        for nombre, desc in categorias_data:
            cat, _ = Categoria.objects.get_or_create(nombre=nombre, defaults={"descripcion": desc})
            categorias_dict[nombre] = cat

        # =========================================================================
        # 3. MARCAS
        # =========================================================================
        marcas_nombres = [
            "Stanley",
            "Bosch",
            "DeWalt",
            "Bahco",
            "Loma Negra",
            "Acindar",
            "Sinteplast",
            "Tigre",
            "FV",
            "Schneider Electric",
            "3M",
            "Sika",
        ]
        marcas_dict = {}
        for m in marcas_nombres:
            marca_obj, _ = Marca.objects.get_or_create(nombre=m)
            marcas_dict[m] = marca_obj

        # =========================================================================
        # 4. PRODUCTOS (CATÁLOGO EXTENSO)
        # =========================================================================
        productos_lista = [
            # Tornillería
            ("Perno Hexagonal Grado 5 1/2 x 3", "Perno de acero templado para estructuras pesadas", Decimal("450.00"), 350, "Tornillería y Fijaciones", "Stanley"),
            ("Tuerca Autofrenante 1/2", "Tuerca cincada con anillo de nylon anti-vibración", Decimal("180.00"), 600, "Tornillería y Fijaciones", "Stanley"),
            ("Tornillo Autoperforante T1 8x1/2 (Caja x 100)", "Punta mecha para perfilería de yeso y durlock", Decimal("2850.00"), 95, "Tornillería y Fijaciones", "Stanley"),
            ("Tirafondo Hexagonal 3/8 x 3 con Tarugo", "Fijación reforzada para maderas y paredes", Decimal("390.00"), 240, "Tornillería y Fijaciones", "Bahco"),
            ("Arandela Plana Cincada 1/2", "Distribución de carga para bulonería estructural", Decimal("75.00"), 1200, "Tornillería y Fijaciones", "Stanley"),

            # Corralón
            ("Bolsa de Cemento Portland 50kg", "Cemento tradicional de alta resistencia para hormigón", Decimal("9800.00"), 180, "Materiales de Corralón", "Loma Negra"),
            ("Cal Hidráulica Hidratada 25kg", "Cal para mezcla de revoques y mampostería", Decimal("4200.00"), 140, "Materiales de Corralón", "Loma Negra"),
            ("Barra de Hierro del 10 (12m)", "Acero torsionado ADN 420 para columnas y losas", Decimal("14200.00"), 110, "Materiales de Corralón", "Acindar"),
            ("Barra de Hierro del 8 (12m)", "Acero de construcción para estribos y encadenados", Decimal("9300.00"), 160, "Materiales de Corralón", "Acindar"),
            ("Malla Electrosoldada 15x15 (4.2mm) 2x3m", "Malla metálica para contrapisos y losas", Decimal("22500.00"), 45, "Materiales de Corralón", "Acindar"),
            ("Aditivo Acelerador de Fraguado Sika 1 (5L)", "Impermeabilizante inorgánico para morteros", Decimal("13400.00"), 40, "Materiales de Corralón", "Sika"),

            # Herramientas
            ("Amoladora Angular 4 1/2 850W", "Herramienta eléctrica de corte y desbaste profesional", Decimal("68900.00"), 28, "Herramientas y Maquinarias", "Bosch"),
            ("Taladro Percutor 13mm 650W", "Taladro con selector percutor y velocidad variable", Decimal("59800.00"), 32, "Herramientas y Maquinarias", "DeWalt"),
            ("Rotomartillo SDS Plus 800W", "Herramienta demoledora con 3 funciones y maletín", Decimal("145000.00"), 14, "Herramientas y Maquinarias", "Bosch"),
            ("Juego de Llaves Combinadas 6 a 24mm (12pz)", "Acero cromo vanadio de máxima durabilidad", Decimal("38900.00"), 22, "Herramientas y Maquinarias", "Bahco"),
            ("Pinza Universal 8 Pulgadas Ergonómica", "Aislamiento hasta 1000V y corte templado", Decimal("16500.00"), 50, "Herramientas y Maquinarias", "Bahco"),
            ("Disco de Corte para Metal 115x1.0mm", "Disco extra fino para corte veloz sin rebaba", Decimal("1250.00"), 250, "Herramientas y Maquinarias", "Stanley"),

            # Pinturería
            ("Látex Exterior Frentes 20L", "Pintura al agua antihongos y resistente al intemperie", Decimal("54000.00"), 42, "Pinturería e Impermeabilizantes", "Sinteplast"),
            ("Esmalte Sintético Brillante Blanco 4L", "Protección anticorrosiva para maderas y metales", Decimal("23500.00"), 36, "Pinturería e Impermeabilizantes", "Sinteplast"),
            ("Membrana Líquida Poliuretánica Techos 20kg", "Impermeabilizante transitable elástico blanco", Decimal("68500.00"), 25, "Pinturería e Impermeabilizantes", "Sika"),
            ("Rodillo Lana Sintética 22cm Pelo Corto", "Ideal para paredes lisas y cielorrasos", Decimal("4800.00"), 65, "Pinturería e Impermeabilizantes", "Sinteplast"),

            # Sanitarios
            ("Tubo Termofusión Agua 20mm x 4m", "Caño tricapa para agua fría y caliente", Decimal("7200.00"), 90, "Sanitarios y Grifería", "Tigre"),
            ("Grifería Monocomando Cocina Pico Móvil", "Cierre cerámico con acabado cromo brillante", Decimal("46000.00"), 18, "Sanitarios y Grifería", "FV"),
            ("Caño Cloacal PVC 110mm x 4m", "Desagüe reforzado para cloacas y pluviales", Decimal("15800.00"), 55, "Sanitarios y Grifería", "Tigre"),

            # Electricidad
            ("Rollo Cable Unipolar 2.5mm Normalizado (100m)", "Cobre electrolítico ignífugo antillama", Decimal("48900.00"), 30, "Electricidad e Iluminación", "Schneider Electric"),
            ("Interruptor Termomagnético Bipolar 2x20A", "Llave térmica de protección sobrecargas curva C", Decimal("12800.00"), 60, "Electricidad e Iluminación", "Schneider Electric"),
            ("Reflector LED Exterior 50W IP65 Luz Fría", "Luminaria estanca para patios y frentes", Decimal("18700.00"), 45, "Electricidad e Iluminación", "Schneider Electric"),

            # Seguridad Industrial
            ("Casco de Seguridad de Obra Amarillo", "Arnés a cremallera con protección UV certificada", Decimal("8900.00"), 75, "Seguridad Industrial y Protección", "3M"),
            ("Guantes de Descarne Amarillos Reforzados", "Protección para soldadura y manipulación pesada", Decimal("5200.00"), 120, "Seguridad Industrial y Protección", "3M"),
            ("Antiparras de Seguridad Antiempaño", "Lente de policarbonato con protección lateral", Decimal("4500.00"), 110, "Seguridad Industrial y Protección", "3M"),
        ]

        productos_dict = {}
        for nombre, desc, precio, stock, cat_nom, marca_nom in productos_lista:
            prod, _ = Producto.objects.get_or_create(
                nombre=nombre,
                defaults={
                    "descripcion": desc,
                    "precio": precio,
                    "stock": stock,
                    "categoria": categorias_dict[cat_nom],
                    "marca": marcas_dict[marca_nom],
                }
            )
            productos_dict[nombre] = prod

        # =========================================================================
        # 5. PROVEEDORES
        # =========================================================================
        proveedores_data = [
            ("Distribuidora Metalúrgica Central S.A.", "30-55667788-9", "1143218765", "ventas@metalurgicacentral.com.ar", "Av. Belgrano 1850, Avellaneda"),
            ("Cales y Cementos del Sur S.R.L.", "30-66778899-1", "1149887766", "pedidos@cementosdelsur.com.ar", "Ruta 2 Km 48, Berazategui"),
            ("Herramientas Industriales Bosch Argentina", "30-70809010-3", "1155443322", "contacto@bosch-herramientas.com.ar", "Panamericana Km 28, Don Torcuato"),
            ("Sinteplast Pinturas Mayoristas", "30-51223344-8", "1147778899", "mayorista@sinteplast.com", "Parque Industrial Ezeiza, Lote 45"),
            ("Bulonera y Fijaciones del Litoral", "30-64556677-2", "1148881122", "ventas@buloneralitoral.com", "Calle 14 Nº 890, San Martín"),
            ("Plásticos y Tubos Tigre Argentina", "30-69887711-5", "1142223344", "atencion@tubostigre.com.ar", "Ruta 8 Km 60, Pilar"),
            ("Distribuidora Eléctrica Schneider", "30-71002233-6", "1143339900", "ventas@distribuidoraschneider.com.ar", "Av. Mitre 3200, Munro"),
        ]

        proveedores_dict = {}
        for nombre, cuit, tel, email, direccion in proveedores_data:
            prov, _ = Proveedor.objects.get_or_create(
                cuit=cuit,
                defaults={
                    "nombre": nombre,
                    "telefono": tel,
                    "email": email,
                    "direccion": direccion,
                }
            )
            proveedores_dict[nombre] = prov

        # =========================================================================
        # 6. CLIENTES
        # =========================================================================
        clientes_data = [
            ("Construcciones Rodriguez S.R.L.", "20-33445566-8", "1155667788", "obras@rodriguezconstrucciones.com", "Ruta 8 Km 54, Pilar"),
            ("Arquitectura y Reformas Gomez", "27-28394857-4", "1198765432", "mariana.gomez@gmail.com", "Calle Mitre 450, Quilmes"),
            ("Obras Civiles del Norte S.A.", "30-74889900-2", "1147654321", "compras@obrasdelnorte.com.ar", "Av. Maipú 2100, Olivos"),
            ("Taller Metalúrgico Los Hermanos", "20-25667788-3", "1165432198", "loshermanostaller@yahoo.com.ar", "Av. Hipólito Yrigoyen 8400, Lomas de Zamora"),
            ("Juan Ignacio Morales (Contratista)", "20-35889922-1", "1133221100", "juan.morales.obras@outlook.com", "Calle Belgrano 340, Morón"),
            ("Estudio de Interiores Belgrano", "27-31224455-6", "1155449988", "contacto@interioresbelgrano.com", "Cabildo 1820, CABA"),
            ("Roberto Carlos Gutierrez (Particular)", "20-21334455-9", "1144009988", "robertocarlos.gutierrez@gmail.com", "Alvear 560, San Isidro"),
            ("Desarrollos Inmobiliarios del Plata", "30-76112233-4", "1148887744", "administracion@delplatadesarrollos.com", "Av. Libertador 4500, Vicente López"),
        ]

        clientes_dict = {}
        for nombre, cuit, tel, email, direccion in clientes_data:
            cli, _ = Cliente.objects.get_or_create(
                cuit=cuit,
                defaults={
                    "nombre": nombre,
                    "telefono": tel,
                    "email": email,
                    "direccion": direccion,
                }
            )
            clientes_dict[nombre] = cli

        # =========================================================================
        # 7. COMPRAS A PROVEEDORES (REABASTECIMIENTO CON DETALLES)
        # =========================================================================
        compras_data = [
            {
                "proveedor": "Distribuidora Metalúrgica Central S.A.",
                "observaciones": "Reabastecimiento mensual de hierro y perfiles de obra",
                "detalles": [
                    ("Barra de Hierro del 10 (12m)", 50, Decimal("11500.00")),
                    ("Barra de Hierro del 8 (12m)", 60, Decimal("7600.00")),
                    ("Malla Electrosoldada 15x15 (4.2mm) 2x3m", 20, Decimal("18000.00")),
                ]
            },
            {
                "proveedor": "Cales y Cementos del Sur S.R.L.",
                "observaciones": "Carga completa camión de cemento y cal hidratada",
                "detalles": [
                    ("Bolsa de Cemento Portland 50kg", 100, Decimal("8100.00")),
                    ("Cal Hidráulica Hidratada 25kg", 80, Decimal("3300.00")),
                ]
            },
            {
                "proveedor": "Herramientas Industriales Bosch Argentina",
                "observaciones": "Reposición de amoladoras, taladros y rotomartillos profesionales",
                "detalles": [
                    ("Amoladora Angular 4 1/2 850W", 15, Decimal("54000.00")),
                    ("Rotomartillo SDS Plus 800W", 8, Decimal("115000.00")),
                ]
            },
            {
                "proveedor": "Bulonera y Fijaciones del Litoral",
                "observaciones": "Pedido por mayor de bulonería, tuercas y tornillería T1",
                "detalles": [
                    ("Perno Hexagonal Grado 5 1/2 x 3", 200, Decimal("320.00")),
                    ("Tuerca Autofrenante 1/2", 300, Decimal("120.00")),
                    ("Tornillo Autoperforante T1 8x1/2 (Caja x 100)", 50, Decimal("2100.00")),
                ]
            },
            {
                "proveedor": "Sinteplast Pinturas Mayoristas",
                "observaciones": "Línea de látex y esmaltes para temporada de primavera",
                "detalles": [
                    ("Látex Exterior Frentes 20L", 25, Decimal("42000.00")),
                    ("Esmalte Sintético Brillante Blanco 4L", 30, Decimal("18000.00")),
                    ("Rodillo Lana Sintética 22cm Pelo Corto", 40, Decimal("3600.00")),
                ]
            },
        ]

        for c_data in compras_data:
            prov = proveedores_dict[c_data["proveedor"]]
            compra, created = Compra.objects.get_or_create(
                proveedor=prov,
                observaciones=c_data["observaciones"],
                defaults={"total": Decimal("0.00")}
            )
            if created:
                total_compra = Decimal("0.00")
                for prod_nom, cant, precio_u in c_data["detalles"]:
                    prod = productos_dict[prod_nom]
                    subtotal = Decimal(str(cant)) * precio_u
                    total_compra += subtotal
                    DetalleCompra.objects.create(
                        compra=compra,
                        producto=prod,
                        cantidad=cant,
                        precio_unitario=precio_u,
                        subtotal=subtotal
                    )
                compra.total = total_compra
                compra.save()

        # =========================================================================
        # 8. VENTAS Y DETALLES DE VENTA
        # =========================================================================
        ventas_data = [
            {
                "cliente": "Construcciones Rodriguez S.R.L.",
                "vendedor": "vendedor",
                "estado": "COMPLETADA",
                "dias_atras": 0,
                "detalles": [
                    ("Bolsa de Cemento Portland 50kg", 20),
                    ("Barra de Hierro del 10 (12m)", 15),
                    ("Malla Electrosoldada 15x15 (4.2mm) 2x3m", 5),
                ]
            },
            {
                "cliente": "Arquitectura y Reformas Gomez",
                "vendedor": "vendedora_sofia",
                "estado": "COMPLETADA",
                "dias_atras": 0,
                "detalles": [
                    ("Látex Exterior Frentes 20L", 3),
                    ("Esmalte Sintético Brillante Blanco 4L", 4),
                    ("Rodillo Lana Sintética 22cm Pelo Corto", 2),
                ]
            },
            {
                "cliente": "Obras Civiles del Norte S.A.",
                "vendedor": "cajero_martin",
                "estado": "COMPLETADA",
                "dias_atras": 1,
                "detalles": [
                    ("Bolsa de Cemento Portland 50kg", 40),
                    ("Cal Hidráulica Hidratada 25kg", 25),
                    ("Aditivo Acelerador de Fraguado Sika 1 (5L)", 4),
                ]
            },
            {
                "cliente": "Taller Metalúrgico Los Hermanos",
                "vendedor": "vendedor",
                "estado": "COMPLETADA",
                "dias_atras": 2,
                "detalles": [
                    ("Amoladora Angular 4 1/2 850W", 1),
                    ("Disco de Corte para Metal 115x1.0mm", 20),
                    ("Perno Hexagonal Grado 5 1/2 x 3", 50),
                    ("Tuerca Autofrenante 1/2", 50),
                ]
            },
            {
                "cliente": "Juan Ignacio Morales (Contratista)",
                "vendedor": "vendedora_sofia",
                "estado": "COMPLETADA",
                "dias_atras": 3,
                "detalles": [
                    ("Taladro Percutor 13mm 650W", 1),
                    ("Tirafondo Hexagonal 3/8 x 3 con Tarugo", 40),
                    ("Juego de Llaves Combinadas 6 a 24mm (12pz)", 1),
                ]
            },
            {
                "cliente": "Roberto Carlos Gutierrez (Particular)",
                "vendedor": "cajero_martin",
                "estado": "COMPLETADA",
                "dias_atras": 4,
                "detalles": [
                    ("Grifería Monocomando Cocina Pico Móvil", 1),
                    ("Tubo Termofusión Agua 20mm x 4m", 3),
                    ("Pinza Universal 8 Pulgadas Ergonómica", 1),
                ]
            },
            {
                "cliente": "Desarrollos Inmobiliarios del Plata",
                "vendedor": "vendedor",
                "estado": "PENDIENTE",
                "dias_atras": 0,
                "detalles": [
                    ("Barra de Hierro del 10 (12m)", 30),
                    ("Barra de Hierro del 8 (12m)", 40),
                    ("Casco de Seguridad de Obra Amarillo", 10),
                    ("Guantes de Descarne Amarillos Reforzados", 15),
                ]
            },
            {
                "cliente": "Estudio de Interiores Belgrano",
                "vendedor": "vendedora_sofia",
                "estado": "PENDIENTE",
                "dias_atras": 0,
                "detalles": [
                    ("Reflector LED Exterior 50W IP65 Luz Fría", 4),
                    ("Rollo Cable Unipolar 2.5mm Normalizado (100m)", 1),
                    ("Interruptor Termomagnético Bipolar 2x20A", 2),
                ]
            },
        ]

        ahora = timezone.now()
        for v_data in ventas_data:
            cli = clientes_dict[v_data["cliente"]]
            vend = usuarios_creados[v_data["vendedor"]]
            
            # Buscar si ya existe una venta similar
            venta_existente = Venta.objects.filter(
                cliente=cli,
                usuario_vendedor=vend,
                estado=v_data["estado"]
            ).first()

            if not venta_existente:
                fecha_venta = ahora - timedelta(days=v_data["dias_atras"])
                venta = Venta.objects.create(
                    cliente=cli,
                    usuario_vendedor=vend,
                    estado=v_data["estado"],
                    total=Decimal("0.00")
                )
                
                # Modificar manualmente fecha si es de días anteriores
                if v_data["dias_atras"] > 0:
                    Venta.objects.filter(id=venta.id).update(fecha=fecha_venta)

                total_venta = Decimal("0.00")
                for prod_nom, cant in v_data["detalles"]:
                    prod = productos_dict[prod_nom]
                    precio_u = prod.precio
                    subtotal = Decimal(str(cant)) * precio_u
                    total_venta += subtotal
                    DetalleVenta.objects.create(
                        venta=venta,
                        producto=prod,
                        cantidad=cant,
                        precio_unitario=precio_u,
                        subtotal=subtotal
                    )
                venta.total = total_venta
                venta.save()

        # =========================================================================
        # REPORTE EN CONSOLA
        # =========================================================================
        self.stdout.write(self.style.SUCCESS("=================================================="))
        self.stdout.write(self.style.SUCCESS("✓ BASE DE DATOS POBLADA EXITOSAMENTE"))
        self.stdout.write(self.style.SUCCESS("=================================================="))
        self.stdout.write(f"- Usuarios registrados: {Usuario.objects.count()}")
        self.stdout.write(f"- Categorías: {Categoria.objects.count()}")
        self.stdout.write(f"- Marcas: {Marca.objects.count()}")
        self.stdout.write(f"- Productos en catálogo: {Producto.objects.count()}")
        self.stdout.write(f"- Proveedores de corralón/ferretería: {Proveedor.objects.count()}")
        self.stdout.write(f"- Clientes registrados: {Cliente.objects.count()}")
        self.stdout.write(f"- Compras de abastecimiento: {Compra.objects.count()}")
        self.stdout.write(f"- Ventas emitidas: {Venta.objects.count()}")
        self.stdout.write(self.style.SUCCESS("=================================================="))
