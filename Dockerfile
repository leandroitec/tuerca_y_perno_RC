FROM python:3.12-slim

# Evita que Python escriba archivos .pyc en disco y desactiva buffering de logs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_SYSTEM_PYTHON=1

WORKDIR /app

# Instalar dependencias del sistema mínimas
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Instalar uv desde imagen oficial o mediante pip
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copiar archivos de dependencias e instalarlas en el entorno de Python
COPY pyproject.toml README.md ./
RUN uv pip install --system -r <(uv pip compile pyproject.toml) || uv pip install --system -e .

# Copiar el resto del código
COPY . .

# Exponer puerto 8000
EXPOSE 8000

# Ejecutar migraciones e iniciar el servidor
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
