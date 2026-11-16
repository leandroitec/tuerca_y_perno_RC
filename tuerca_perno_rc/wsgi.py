"""
WSGI config for tuerca_perno_rc project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tuerca_perno_rc.settings')

application = get_wsgi_application()
