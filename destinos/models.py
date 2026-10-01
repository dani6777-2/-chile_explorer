"""
Modelos de la aplicación "destinos".

Representa los destinos turísticos de Chile con sus categorías,
regiones administrativas y actividades recomendadas.
"""

from django.db import models
from django.urls import reverse


class Categoria(models.Model):
    """Categoría de destino (Desierto, Naturaleza, Ciudad, etc.)."""

    nombre = models.CharField(
        'nombre',
        max_length=100,
        unique=True,
        help_text='Nombre de la categoría (ej: Desierto, Naturaleza).',
    )

    class Meta:
        verbose_name = 'categoría'
        verbose_name_plural = 'categorías'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Region(models.Model):
    """Región administrativa de Chile."""

    nombre = models.CharField(
        'nombre',
        max_length=100,
        unique=True,
        help_text='Nombre de la región (ej: Valparaíso, Los Lagos).',
    )

    class Meta:
        verbose_name = 'región'
        verbose_name_plural = 'regiones'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Destino(models.Model):
    """Destino turístico de Chile."""

    slug = models.SlugField(
        'slug',
        max_length=100,
        unique=True,
        help_text='Identificador único usado en la URL.',
    )
    nombre = models.CharField('nombre', max_length=200)
    region = models.ForeignKey(
        Region,
        on_delete=models.CASCADE,
        related_name='destinos',
        verbose_name='región',
    )
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.CASCADE,
        related_name='destinos',
        verbose_name='categoría',
    )
    descripcion = models.TextField('descripción')
    mejor_epoca = models.CharField(
        'mejor época',
        max_length=200,
        blank=True,
        help_text='Época recomendada para visitar.',
    )
    imagen = models.CharField(
        'imagen',
        max_length=300,
        blank=True,
        help_text='Ruta relativa a static/ (ej: destinos/images/foto.jpg).',
    )
    destacado = models.BooleanField(
        'destacado',
        default=False,
        help_text='¿Aparece en la sección destacados del inicio?',
    )

    class Meta:
        verbose_name = 'destino'
        verbose_name_plural = 'destinos'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

    def get_absolute_url(self):
        return reverse('destinos:detalle', kwargs={'slug': self.slug})


class Actividad(models.Model):
    """Actividad recomendada asociada a un destino."""

    destino = models.ForeignKey(
        Destino,
        on_delete=models.CASCADE,
        related_name='actividades',
        verbose_name='destino',
    )
    nombre = models.CharField('nombre', max_length=200)

    class Meta:
        verbose_name = 'actividad'
        verbose_name_plural = 'actividades'
        ordering = ['nombre']

    def __str__(self):
        return f'{self.nombre} ({self.destino.nombre})'
