# Tuerca y Perno RC - Backend

Sistema de gestión comercial y de inventario para Ferretería y Corralón **"Tuerca y Perno RC"**.

## Stack Tecnológico
- Python 3.12+ gestionado con `uv`.
- Django 5.x y Django REST Framework.
- Autenticación: SimpleJWT y SessionAuthentication.
- Documentación OpenAPI 3.0: `drf-spectacular` (Swagger UI y ReDoc).
- Filtros: `django-filter` y búsqueda con `SearchFilter`.
- CORS: `django-cors-headers`.
- Base de datos: SQLite (desarrollo).
- Docker y Docker Compose.

## Puesta en marcha rápida con `uv`
```bash
# Crear entorno virtual e instalar dependencias
uv venv
source .venv/bin/activate
uv pip install -e .

# Ejecutar migraciones
python manage.py makemigrations negocio
python manage.py migrate

# Crear superusuario para el panel de administración
python manage.py createsuperuser

# Iniciar servidor
python manage.py runserver
```

## Puesta en marcha con Docker
```bash
docker compose up --build
```

## Endpoints Principales
- **Página de Bienvenida:** `http://127.0.0.1:8000/`
- **Swagger UI:** `http://127.0.0.1:8000/api/docs/`
- **ReDoc:** `http://127.0.0.1:8000/api/redoc/`
- **Esquema OpenAPI:** `http://127.0.0.1:8000/api/schema/`
- **Panel de Administración:** `http://127.0.0.1:8000/admin/`
- **Autenticación JWT:**
  - Obtener Token: `POST /api/auth/token/`
  - Refrescar Token: `POST /api/auth/token/refresh/`
- **API Resources:** `http://127.0.0.1:8000/api/`
