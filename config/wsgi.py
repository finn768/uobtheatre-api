"""
WSGI config for uobtheatre-api project.
It exposes the WSGI callable as a module-level variable named ``application``.
For more information on this file, see
https://docs.djangoproject.com/en/2.0/howto/deployment/wsgi/gunicorn/
"""
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "uobtheatre-api.config")


from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
