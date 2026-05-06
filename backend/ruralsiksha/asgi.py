"""
ASGI config for ruralsiksha project.
Plain Django ASGI - no channels (for local dev simplicity).
"""

import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ruralsiksha.settings')

application = get_asgi_application()
