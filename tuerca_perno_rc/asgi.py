"""
ASGI config for tuerca_perno_rc project.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tuerca_perno_rc.settings')

application = get_asgi_application()
