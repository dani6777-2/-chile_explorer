"""
Vistas de la aplicación "destinos".

La información se obtiene desde la base de datos mediante Django ORM.
Los datos originales se cargaron desde JSON mediante el management
command `cargar_destinos`.
"""

import logging

from django.db.models import Q
from django.http import Http404
from django.shortcuts import render

from .models import Categoria, Destino, Region

logger = logging.getLogger(__name__)


def inicio(request):
    """Vista 1: página de presentación del sitio."""
    destinos = Destino.objects.select_related('region', 'categoria').all()
    # Destinos destacados para la sección principal (máximo 3).
    destacados = destinos.filter(destacado=True)[:3]
    contexto = {
        'nombre_sitio': 'Chile Explorer',
        'total_destinos': destinos.count(),
        'destacados': destacados,
    }
    return render(request, 'destinos/inicio.html', contexto)


def lista_destinos(request):
    """Vista 2: lista de todos los destinos turísticos.

    Acepta filtros vía parámetros GET (?q=, ?region=, ?categoria=)
    para la barra de búsqueda. El filtrado se realiza con consultas ORM.
    """
    destinos = Destino.objects.select_related('region', 'categoria').all()

    # Los filtros se recogen de la URL.
    texto = request.GET.get('q', '').strip()
    region = request.GET.get('region', '').strip()
    categoria = request.GET.get('categoria', '').strip()

    # Aplica cada filtro activo con consultas ORM.
    if texto:
        destinos = destinos.filter(
            Q(nombre__icontains=texto) | Q(descripcion__icontains=texto)
        )
    if region:
        destinos = destinos.filter(region__nombre=region)
    if categoria:
        destinos = destinos.filter(categoria__nombre=categoria)

    # Regiones y categorías únicas (para los selectores del filtro).
    regiones = Region.objects.values_list('nombre', flat=True).order_by('nombre')
    categorias = Categoria.objects.values_list('nombre', flat=True).order_by('nombre')

    contexto = {
        'destinos': destinos,
        'total_destinos': destinos.count(),
        'regiones': regiones,
        'categorias': categorias,
        'texto_busqueda': texto,
        'region_seleccionada': region,
        'categoria_seleccionada': categoria,
    }
    return render(request, 'destinos/lista.html', contexto)


def detalle_destino(request, slug):
    """Vista 3: detalle de un destino según su slug."""
    try:
        destino = Destino.objects.select_related(
            'region', 'categoria'
        ).prefetch_related('actividades').get(slug=slug)
    except Destino.DoesNotExist:
        raise Http404('El destino solicitado no existe.') from None

    contexto = {
        'destino': destino,
        'total_destinos': Destino.objects.count(),
    }
    return render(request, 'destinos/detalle.html', contexto)


def placeholder_agregar(request):
    """Placeholder: operación Agregar (CRUD funcional en la siguiente evaluación)."""
    return render(request, 'crud_pendiente.html', {
        'modulo': 'Destinos',
        'operacion': 'Agregar destino',
        'mensaje': (
            'El formulario de creación de destinos se implementará funcionalmente '
            'en la Evaluación Sumativa 3. En esta etapa, el botón Agregar está '
            'presente visualmente y enlaza a esta ruta.'
        ),
        'volver_url': 'destinos:lista',
        'volver_texto': 'Volver a la lista de destinos',
    })


def placeholder_modificar(request):
    """Placeholder: operación Modificar (CRUD funcional en la siguiente evaluación)."""
    return render(request, 'crud_pendiente.html', {
        'modulo': 'Destinos',
        'operacion': 'Modificar destino',
        'mensaje': (
            'El formulario de modificación de destinos se implementará funcionalmente '
            'en la Evaluación Sumativa 3. En esta etapa, el botón Modificar está '
            'presente visualmente y enlaza a esta ruta.'
        ),
        'volver_url': 'destinos:lista',
        'volver_texto': 'Volver a la lista de destinos',
    })


def placeholder_eliminar(request):
    """Placeholder: operación Eliminar (CRUD funcional en la siguiente evaluación)."""
    return render(request, 'crud_pendiente.html', {
        'modulo': 'Destinos',
        'operacion': 'Eliminar destino',
        'mensaje': (
            'La confirmación de eliminación de destinos se implementará funcionalmente '
            'en la Evaluación Sumativa 3. En esta etapa, el botón Eliminar está '
            'presente visualmente y enlaza a esta ruta.'
        ),
        'volver_url': 'destinos:lista',
        'volver_texto': 'Volver a la lista de destinos',
    })
