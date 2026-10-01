"""
Rutas principales de "Chile Explorer".

Incluye:
- Django Admin:        "/admin/"
- destinos:            "" y "destinos/..."
- gastronomia:         "gastronomia/..."
"""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('destinos.urls')),
    path('gastronomia/', include('gastronomia.urls')),
]
