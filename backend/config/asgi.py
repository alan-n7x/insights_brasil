"""Configuração ASGI para o projeto Insight Brasil.

Expõe o callable ASGI como uma variável de módulo chamada ``application``.

Para mais informações, consulte:
https://docs.djangoproject.com/en/6.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_asgi_application()
