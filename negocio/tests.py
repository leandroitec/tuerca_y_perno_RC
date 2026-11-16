from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

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

Usuario = get_user_model()


class TuercaYPernoRCAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

        # 1. Crear usuario vendedor para pruebas
        self.password = "password123"
        self.user = Usuario.objects.create_user(
            username="vendedor1",
            password=self.password,
            email="vendedor@tuercayperno.com",
            first_name="Carlos",
            last_name="Gomez",
            rol="VENDEDOR",
            telefono="1122334455"
        )

        # 2. Obtener Token JWT
        token_url = reverse('token_obtain_pair')
        response = self.client.post(token_url, {'username': self.user.username, 'password': self.password})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

        # Usuarios de los otros roles para probar los permisos
        self.user_deposito = Usuario.objects.create_user(
            username="deposito1", password=self.password, rol="DEPOSITO"
        )
        self.user_admin = Usuario.objects.create_user(
            username="admin1", password=self.password, rol="ADMIN"
        )

        # 3. Crear datos base (Categoría, Marca, Proveedor, Cliente)
        self.categoria_herramientas = Categoria.objects.create(
            nombre="Herramientas Manuales",
            descripcion="Llaves, destornilladores y martillos"
        )
        self.categoria_tornilleria = Categoria.objects.create(
            nombre="Tornillería y Bulonería",
            descripcion="Tornillos, tuercas, pernos y arandelas"
        )

        self.marca_stanley = Marca.objects.create(nombre="Stanley")
        self.marca_bosch = Marca.objects.create(nombre="Bosch")

        self.cliente = Cliente.objects.create(
            nombre="Juan Perez",
            cuit="20-30405060-7",
            telefono="1199887766",
            email="juan.perez@example.com",
            direccion="Av. San Martin 1234"
        )

        self.proveedor = Proveedor.objects.create(
            nombre="Distribuidora Mayorista Metalúrgica",
            cuit="30-71829304-9",
            telefono="1144556677",
            email="contacto@metalurgica.com"
        )

        # 4. Crear producto inicial
        self.producto_llave = Producto.objects.create(
            nombre="Llave Francesa 10 Pulgadas",
            descripcion="Llave ajustable cromada de alta resistencia",
            precio=Decimal("15000.00"),
            stock=50,
            categoria=self.categoria_herramientas,
            marca=self.marca_stanley
        )

    def cliente_con_rol(self, user):
        """Devuelve un APIClient autenticado con el token JWT del usuario dado."""
        client = APIClient()
        res = client.post(
            reverse('token_obtain_pair'),
            {'username': user.username, 'password': self.password},
        )
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")
        return client

    # -------------------------------------------------------------
    # PRUEBA DE LANDING PAGE TRADICIONAL
    # -------------------------------------------------------------
    def test_landing_page_view(self):
        """Verifica que la ruta raíz '/' renderice correctamente con código 200"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "Tuerca y Perno")
        self.assertContains(response, "Swagger UI")

    # -------------------------------------------------------------
    # PRUEBAS DE PRODUCTO: ANIDADO EXCLUSIVO EN LIST, PLANO EN RETRIEVE/POST
    # -------------------------------------------------------------
    def test_producto_get_nested_representation_only_on_list(self):
        """GET a /api/productos/ (list) debe retornar categoria y marca anidadas con NestedSerializers"""
        url = reverse('producto-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Validar estructura anidada en el listado general
        producto_item = response.data['results'][0]
        self.assertIsInstance(producto_item['categoria'], dict)
        self.assertEqual(producto_item['categoria']['id'], self.categoria_herramientas.id)
        self.assertEqual(producto_item['categoria']['nombre'], "Herramientas Manuales")

        self.assertIsInstance(producto_item['marca'], dict)
        self.assertEqual(producto_item['marca']['id'], self.marca_stanley.id)
        self.assertEqual(producto_item['marca']['nombre'], "Stanley")

    def test_producto_get_retrieve_flat(self):
        """GET a /api/productos/{id}/ (retrieve) debe retornar IDs primarios (no anidados)"""
        url = reverse('producto-detail', kwargs={'pk': self.producto_llave.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # En retrieve no es anidado, devuelve la FK directa
        self.assertEqual(response.data['categoria'], self.categoria_herramientas.id)
        self.assertEqual(response.data['marca'], self.marca_stanley.id)

    def test_producto_post_with_pks(self):
        """POST a /api/productos/ acepta PrimaryKeys para categoria y marca"""
        url = reverse('producto-list')
        payload = {
            "nombre": "Tornillo Hexagonal 3/8 x 2",
            "descripcion": "Acero zincado para fijaciones pesadas",
            "precio": "250.00",
            "stock": 500,
            "categoria": self.categoria_tornilleria.id,
            "marca": self.marca_stanley.id,
        }
        # Crear productos es tarea de DEPOSITO (o ADMIN)
        response = self.cliente_con_rol(self.user_deposito).post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['nombre'], "Tornillo Hexagonal 3/8 x 2")
        self.assertEqual(response.data['categoria'], self.categoria_tornilleria.id)

    def test_producto_filter_and_search(self):
        """Prueba de filtrado por categoría y búsqueda por nombre"""
        Producto.objects.create(
            nombre="Taladro Percutor 750W",
            descripcion="Taladro eléctrico profesional",
            precio=Decimal("85000.00"),
            stock=15,
            categoria=self.categoria_herramientas,
            marca=self.marca_bosch
        )

        url = reverse('producto-list')

        # Búsqueda por texto "Taladro"
        response_search = self.client.get(url, {'search': 'Taladro'})
        self.assertEqual(response_search.status_code, status.HTTP_200_OK)
        results = response_search.data['results']
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['nombre'], "Taladro Percutor 750W")

        # Filtrado por categoría de Tornillería (actualmente vacía antes del post)
        response_filter = self.client.get(url, {'categoria': self.categoria_tornilleria.id})
        self.assertEqual(response_filter.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_filter.data['results']), 0)

    # -------------------------------------------------------------
    # PRUEBA DE ACCIÓN PERSONALIZADA: ACTUALIZAR STOCK
    # -------------------------------------------------------------
    def test_actualizar_stock_action(self):
        """POST a /api/productos/{id}/actualizar-stock/ para sumar o restar existencias"""
        url = reverse('producto-actualizar-stock', kwargs={'pk': self.producto_llave.id})
        # Manejar stock es tarea de DEPOSITO (o ADMIN)
        deposito = self.cliente_con_rol(self.user_deposito)

        # 1. Sumar 20 unidades
        response_sumar = deposito.post(url, {'cantidad': 20, 'operacion': 'sumar'})
        self.assertEqual(response_sumar.status_code, status.HTTP_200_OK)
        self.producto_llave.refresh_from_db()
        self.assertEqual(self.producto_llave.stock, 70)
        self.assertIn("70", response_sumar.data['mensaje'])

        # 2. Restar 15 unidades
        response_restar = deposito.post(url, {'cantidad': 15, 'operacion': 'restar'})
        self.assertEqual(response_restar.status_code, status.HTTP_200_OK)
        self.producto_llave.refresh_from_db()
        self.assertEqual(self.producto_llave.stock, 55)

    # -------------------------------------------------------------
    # PRUEBAS DE VENTA: CREACIÓN, DETALLE Y GET ANIDADO EN LIST
    # -------------------------------------------------------------
    def test_venta_create_detalle_and_nested_list(self):
        """
        Crear Venta, asociar DetalleVenta (descuenta stock automáticamente)
        y validar representación anidada en GET list.
        """
        stock_inicial = self.producto_llave.stock
        cantidad_vendida = 5

        # 1. Crear cabecera de venta
        url_venta = reverse('venta-list')
        res_venta = self.client.post(url_venta, {
            "cliente": self.cliente.id,
            "estado": "COMPLETADA",
            "total": "0.00"
        }, format='json')
        self.assertEqual(res_venta.status_code, status.HTTP_201_CREATED)
        venta_id = res_venta.data['id']

        # 2. Crear detalle de venta (activa perform_create que descuenta stock)
        url_detalle = reverse('detalle-venta-list')
        subtotal_esperado = Decimal("15000.00") * cantidad_vendida
        res_det = self.client.post(url_detalle, {
            "venta": venta_id,
            "producto": self.producto_llave.id,
            "cantidad": cantidad_vendida,
            "precio_unitario": "15000.00",
            "subtotal": str(subtotal_esperado)
        }, format='json')
        self.assertEqual(res_det.status_code, status.HTTP_201_CREATED)

        # Verificar descuento de inventario
        self.producto_llave.refresh_from_db()
        self.assertEqual(self.producto_llave.stock, stock_inicial - cantidad_vendida)

        # 3. GET list de ventas debe retornar representación anidada
        response_list = self.client.get(url_venta)
        self.assertEqual(response_list.status_code, status.HTTP_200_OK)

        data = response_list.data['results'][0]
        self.assertEqual(data['cliente']['nombre'], self.cliente.nombre)
        self.assertEqual(data['usuario_vendedor']['username'], self.user.username)
        self.assertEqual(data['detalles'][0]['producto'], self.producto_llave.id)

    # -------------------------------------------------------------
    # PRUEBA DE ACCIÓN PERSONALIZADA: VENTAS DEL DÍA
    # -------------------------------------------------------------
    def test_ventas_del_dia_action(self):
        """GET a /api/ventas/ventas-del-dia/ retorna ventas del día con datos anidados"""
        Venta.objects.create(
            cliente=self.cliente,
            usuario_vendedor=self.user,
            total=Decimal("25000.00"),
            estado="COMPLETADA"
        )

        url = reverse('venta-ventas-del-dia')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['cliente']['nombre'], self.cliente.nombre)

    # -------------------------------------------------------------
    # PRUEBA DE SEGURIDAD: ACCESO ANÓNIMO DENEGADO
    # -------------------------------------------------------------
    def test_unauthenticated_request_rejected(self):
        """Peticiones sin token a endpoints protegidos deben recibir 401 Unauthorized"""
        unauthenticated_client = APIClient()
        url = reverse('venta-list')
        response = unauthenticated_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    # -------------------------------------------------------------
    # PRUEBAS DE PERMISOS POR ROL
    # -------------------------------------------------------------
    def test_vendedor_no_puede_modificar_productos(self):
        """VENDEDOR puede ver productos pero no crearlos, editarlos ni borrarlos"""
        url_lista = reverse('producto-list')
        url_detalle = reverse('producto-detail', kwargs={'pk': self.producto_llave.id})

        self.assertEqual(self.client.get(url_lista).status_code, status.HTTP_200_OK)
        res = self.client.post(url_lista, {
            "nombre": "No permitido", "precio": "1.00", "stock": 1,
            "categoria": self.categoria_herramientas.id, "marca": self.marca_bosch.id,
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.client.delete(url_detalle).status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Producto.objects.filter(id=self.producto_llave.id).exists())

    def test_deposito_no_puede_ver_ventas_ni_clientes(self):
        """DEPOSITO no accede a ventas ni a clientes"""
        deposito = self.cliente_con_rol(self.user_deposito)
        self.assertEqual(deposito.get(reverse('venta-list')).status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(deposito.get(reverse('cliente-list')).status_code, status.HTTP_403_FORBIDDEN)

    def test_vendedor_no_puede_ver_compras_ni_proveedores(self):
        """VENDEDOR no accede a compras ni a proveedores"""
        self.assertEqual(self.client.get(reverse('compra-list')).status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.client.get(reverse('proveedor-list')).status_code, status.HTTP_403_FORBIDDEN)

    def test_gestion_de_usuarios_solo_admin(self):
        """Solo ADMIN puede listar usuarios en /api/gestion/"""
        url = '/api/gestion/'
        self.assertEqual(self.client.get(url).status_code, status.HTTP_403_FORBIDDEN)
        deposito = self.cliente_con_rol(self.user_deposito)
        self.assertEqual(deposito.get(url).status_code, status.HTTP_403_FORBIDDEN)
        admin = self.cliente_con_rol(self.user_admin)
        self.assertEqual(admin.get(url).status_code, status.HTTP_200_OK)

    def test_catalogo_publico_sin_token(self):
        """Productos, categorías y marcas se leen sin token, pero no se escriben"""
        anonimo = APIClient()
        for nombre in ('producto-list', 'categoria-list', 'marca-list'):
            self.assertEqual(anonimo.get(reverse(nombre)).status_code, status.HTTP_200_OK)
        res = anonimo.post(reverse('marca-list'), {"nombre": "X"}, format='json')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
