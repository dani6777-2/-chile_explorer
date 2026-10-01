"""
Rutas de la aplicación "destinos".

Rutas disponibles:
- ""                        -> página de inicio (presentación)
- "destinos/"               -> lista de destinos
- "destinos/agregar/"       -> placeholder CRUD (evaluación siguiente)
- "destinos/modificar/"     -> placeholder CRUD (evaluación siguiente)
- "destinos/eliminar/"      -> placeholder CRUD (evaluación siguiente)
- "destinos/<slug:slug>/"   -> detalle de un destino

IMPORTANTE: las rutas estáticas (agregar/modificar/eliminar) se declaran
ANTES de la ruta con <slug:slug> para que no sean interpretadas como slugs.
"""

from django.urls import path

from . import views

app_name = 'destinos'

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('destinos/', views.lista_destinos, name='lista'),
    # Placeholders CRUD — la funcionalidad real se implementa en la siguiente evaluación.
    # Deben ir antes de <slug:slug>/ para evitar conflictos de coincidencia.
    path('destinos/agregar/', views.placeholder_agregar, name='agregar'),
    path('destinos/modificar/', views.placeholder_modificar, name='modificar'),
    path('destinos/eliminar/', views.placeholder_eliminar, name='eliminar'),
    path('destinos/<slug:slug>/', views.detalle_destino, name='detalle'),
]
