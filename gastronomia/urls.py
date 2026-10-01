"""
Rutas de la aplicación "gastronomia".

Rutas disponibles:
- "gastronomia/"               -> lista de platos típicos
- "gastronomia/agregar/"       -> placeholder CRUD (evaluación siguiente)
- "gastronomia/modificar/"     -> placeholder CRUD (evaluación siguiente)
- "gastronomia/eliminar/"      -> placeholder CRUD (evaluación siguiente)
- "gastronomia/<slug:slug>/"   -> detalle de un plato

IMPORTANTE: las rutas estáticas (agregar/modificar/eliminar) se declaran
ANTES de la ruta con <slug:slug> para que no sean interpretadas como slugs.
"""

from django.urls import path

from . import views

app_name = 'gastronomia'

urlpatterns = [
    path('', views.lista_platos, name='lista'),
    # Placeholders CRUD — la funcionalidad real se implementa en la siguiente evaluación.
    # Deben ir antes de <slug:slug>/ para evitar conflictos de coincidencia.
    path('agregar/', views.placeholder_agregar, name='agregar'),
    path('modificar/', views.placeholder_modificar, name='modificar'),
    path('eliminar/', views.placeholder_eliminar, name='eliminar'),
    path('<slug:slug>/', views.detalle_plato, name='detalle'),
]
