"""
Vistas de la aplicación "gastronomia".

La información se obtiene desde la base de datos mediante Django ORM.
Los datos originales se cargaron desde JSON mediante el management
command `cargar_gastronomia`.
"""

import logging

from django.http import Http404
from django.shortcuts import render

from .models import Plato, TipoPlato

logger = logging.getLogger(__name__)


def lista_platos(request):
    """Vista 1: lista de platos típicos de la gastronomía chilena."""
    platos = Plato.objects.select_related('tipo').prefetch_related('ingredientes').all()
    # Tipos únicos ordenados, para los badges/filtros de la página.
    tipos = TipoPlato.objects.values_list('nombre', flat=True).order_by('nombre')
    contexto = {
        'platos': platos,
        'total_platos': platos.count(),
        'tipos': tipos,
    }
    return render(request, 'gastronomia/lista.html', contexto)


def detalle_plato(request, slug):
    """Vista 2: detalle de un plato según su slug."""
    try:
        plato = Plato.objects.select_related(
            'tipo'
        ).prefetch_related('ingredientes').get(slug=slug)
    except Plato.DoesNotExist:
        raise Http404('El plato solicitado no existe.') from None

    contexto = {
        'plato': plato,
        'total_platos': Plato.objects.count(),
    }
    return render(request, 'gastronomia/detalle.html', contexto)


def placeholder_agregar(request):
    """Placeholder: operación Agregar (CRUD funcional en la siguiente evaluación)."""
    return render(request, 'crud_pendiente.html', {
        'modulo': 'Gastronomía',
        'operacion': 'Agregar plato',
        'mensaje': (
            'El formulario de creación de platos se implementará funcionalmente '
            'en la Evaluación Sumativa 3. En esta etapa, el botón Agregar está '
            'presente visualmente y enlaza a esta ruta.'
        ),
        'volver_url': 'gastronomia:lista',
        'volver_texto': 'Volver a la lista de platos',
    })


def placeholder_modificar(request):
    """Placeholder: operación Modificar (CRUD funcional en la siguiente evaluación)."""
    return render(request, 'crud_pendiente.html', {
        'modulo': 'Gastronomía',
        'operacion': 'Modificar plato',
        'mensaje': (
            'El formulario de modificación de platos se implementará funcionalmente '
            'en la Evaluación Sumativa 3. En esta etapa, el botón Modificar está '
            'presente visualmente y enlaza a esta ruta.'
        ),
        'volver_url': 'gastronomia:lista',
        'volver_texto': 'Volver a la lista de platos',
    })


def placeholder_eliminar(request):
    """Placeholder: operación Eliminar (CRUD funcional en la siguiente evaluación)."""
    return render(request, 'crud_pendiente.html', {
        'modulo': 'Gastronomía',
        'operacion': 'Eliminar plato',
        'mensaje': (
            'La confirmación de eliminación de platos se implementará funcionalmente '
            'en la Evaluación Sumativa 3. En esta etapa, el botón Eliminar está '
            'presente visualmente y enlaza a esta ruta.'
        ),
        'volver_url': 'gastronomia:lista',
        'volver_texto': 'Volver a la lista de platos',
    })
