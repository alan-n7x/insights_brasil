"""Configuração WSGI para o projeto Insight Brasil.

Expõe o callable WSGI como uma variável de módulo chamada ``application``.

Para mais informações, consulte:
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_wsgi_application()
