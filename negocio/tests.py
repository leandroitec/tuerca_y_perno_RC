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
    # PRUEBAS DE PRODUCTO: LECTURA ANIDADA, ESCRITURA POR PK, FILTROS
    # -------------------------------------------------------------
    def test_producto_get_nested_representation(self):
        """GET a /api/productos/{id}/ debe retornar categoria y marca anidadas con nombre y detalles"""
        url = reverse('producto-detail', kwargs={'pk': self.producto_llave.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Validar estructura anidada
        self.assertIsInstance(response.data['categoria'], dict)
        self.assertEqual(response.data['categoria']['id'], self.categoria_herramientas.id)
        self.assertEqual(response.data['categoria']['nombre'], "Herramientas Manuales")

        self.assertIsInstance(response.data['marca'], dict)
        self.assertEqual(response.data['marca']['id'], self.marca_stanley.id)
        self.assertEqual(response.data['marca']['nombre'], "Stanley")

    def test_producto_post_with_pks(self):
        """POST a /api/productos/ debe aceptar PrimaryKeys para categoria y marca"""
        url = reverse('producto-list')
        payload = {
            "nombre": "Tornillo Hexagonal 3/8 x 2",
            "descripcion": "Acero zincado para fijaciones pesadas",
            "precio": "250.00",
            "stock": 500,
            "categoria": self.categoria_tornilleria.id,
            "marca": self.marca_stanley.id,
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # La respuesta to_representation retorna la información anidada
        self.assertEqual(response.data['nombre'], "Tornillo Hexagonal 3/8 x 2")
        self.assertEqual(response.data['categoria']['nombre'], "Tornillería y Bulonería")

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

        # 1. Sumar 20 unidades
        response_sumar = self.client.post(url, {'cantidad': 20, 'operacion': 'sumar', 'motivo': 'Ingreso express'})
        self.assertEqual(response_sumar.status_code, status.HTTP_200_OK)
        self.producto_llave.refresh_from_db()
        self.assertEqual(self.producto_llave.stock, 70)
        self.assertEqual(response_sumar.data['stock_actual'], 70)

        # 2. Restar 15 unidades
        response_restar = self.client.post(url, {'cantidad': 15, 'operacion': 'restar', 'motivo': 'Ajuste rotura'})
        self.assertEqual(response_restar.status_code, status.HTTP_200_OK)
        self.producto_llave.refresh_from_db()
        self.assertEqual(self.producto_llave.stock, 55)

        # 3. Intentar restar más del stock existente (debe dar 400 Bad Request)
        response_error = self.client.post(url, {'cantidad': 200, 'operacion': 'restar'})
        self.assertEqual(response_error.status_code, status.HTTP_400_BAD_REQUEST)
        self.producto_llave.refresh_from_db()
        self.assertEqual(self.producto_llave.stock, 55)

    # -------------------------------------------------------------
    # PRUEBAS DE VENTA: CREACIÓN CON DESCUENTO DE STOCK Y GET ANIDADO
    # -------------------------------------------------------------
    def test_venta_create_and_nested_get(self):
        """
        POST a /api/ventas/ acepta IDs y descuenta stock automáticamente.
        GET a /api/ventas/{id}/ muestra cliente, vendedor y productos anidados.
        """
        stock_inicial = self.producto_llave.stock
        cantidad_vendida = 5

        url_list = reverse('venta-list')
        payload = {
            "cliente": self.cliente.id,
            "detalles": [
                {
                    "producto": self.producto_llave.id,
                    "cantidad": cantidad_vendida,
                    "precio_unitario": "15000.00"
                }
            ]
        }

        # 1. Crear venta
        response_post = self.client.post(url_list, payload, format='json')
        self.assertEqual(response_post.status_code, status.HTTP_201_CREATED)
        venta_id = response_post.data['id']

        # Verificar descuento de inventario
        self.producto_llave.refresh_from_db()
        self.assertEqual(self.producto_llave.stock, stock_inicial - cantidad_vendida)

        # Verificar total calculado (5 * 15000 = 75000)
        self.assertEqual(Decimal(str(response_post.data['total'])), Decimal("75000.00"))

        # 2. Realizar GET y validar representación anidada
        url_detail = reverse('venta-detail', kwargs={'pk': venta_id})
        response_get = self.client.get(url_detail)
        self.assertEqual(response_get.status_code, status.HTTP_200_OK)

        data = response_get.data
        self.assertEqual(data['cliente']['nombre'], self.cliente.nombre)
        self.assertEqual(data['usuario_vendedor']['username'], self.user.username)
        self.assertEqual(len(data['detalles']), 1)
        self.assertEqual(data['detalles'][0]['producto']['nombre'], self.producto_llave.nombre)

    def test_venta_stock_insuficiente(self):
        """Intentar vender más stock del disponible debe rechazar la transacción"""
        url_list = reverse('venta-list')
        payload = {
            "cliente": self.cliente.id,
            "detalles": [
                {
                    "producto": self.producto_llave.id,
                    "cantidad": 9999,  # Más del stock actual
                }
            ]
        }
        response = self.client.post(url_list, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # -------------------------------------------------------------
    # PRUEBA DE ACCIÓN PERSONALIZADA: VENTAS DEL DÍA
    # -------------------------------------------------------------
    def test_ventas_del_dia_action(self):
        """GET a /api/ventas/ventas-del-dia/ calcula métricas de hoy"""
        # Crear una venta hoy
        Venta.objects.create(
            cliente=self.cliente,
            usuario_vendedor=self.user,
            total=Decimal("25000.00"),
            estado="COMPLETADA"
        )

        url = reverse('venta-ventas-del-dia')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Validar métricas del día
        self.assertIn('metricas_dia', response.data)
        self.assertGreaterEqual(response.data['metricas_dia']['cantidad_operaciones'], 1)
        self.assertGreaterEqual(Decimal(str(response.data['metricas_dia']['total_recaudado'])), Decimal("25000.00"))

    # -------------------------------------------------------------
    # PRUEBA DE SEGURIDAD: ACCESO ANÓNIMO DENEGADO
    # -------------------------------------------------------------
    def test_unauthenticated_request_rejected(self):
        """Peticiones sin token a endpoints protegidos deben recibir 401 Unauthorized"""
        unauthenticated_client = APIClient()
        url = reverse('producto-list')
        response = unauthenticated_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
