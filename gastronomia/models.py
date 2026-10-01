"""
Modelos de la aplicación "gastronomia".

Representa los platos típicos de la gastronomía chilena con sus
tipos, ingredientes e historia.
"""

from django.db import models
from django.urls import reverse


class TipoPlato(models.Model):
    """Tipo de plato (Comida tradicional, Plato de fondo, etc.)."""

    nombre = models.CharField(
        'nombre',
        max_length=100,
        unique=True,
        help_text='Nombre del tipo (ej: Comida tradicional, Plato de fondo).',
    )

    class Meta:
        verbose_name = 'tipo de plato'
        verbose_name_plural = 'tipos de plato'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Plato(models.Model):
    """Plato típico de la gastronomía chilena."""

    slug = models.SlugField(
        'slug',
        max_length=100,
        unique=True,
        help_text='Identificador único usado en la URL.',
    )
    nombre = models.CharField('nombre', max_length=200)
    region = models.CharField(
        'región',
        max_length=100,
        blank=True,
        help_text='Zona geográfica (ej: Todo Chile, Chiloé, Zona central).',
    )
    tipo = models.ForeignKey(
        TipoPlato,
        on_delete=models.CASCADE,
        related_name='platos',
        verbose_name='tipo',
    )
    descripcion = models.TextField('descripción')
    historia = models.TextField('historia', blank=True)
    imagen = models.CharField(
        'imagen',
        max_length=300,
        blank=True,
        help_text='Ruta relativa a static/ (ej: gastronomia/images/foto.jpg).',
    )

    class Meta:
        verbose_name = 'plato'
        verbose_name_plural = 'platos'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

    def get_absolute_url(self):
        return reverse('gastronomia:detalle', kwargs={'slug': self.slug})


class Ingrediente(models.Model):
    """Ingrediente de un plato."""

    plato = models.ForeignKey(
        Plato,
        on_delete=models.CASCADE,
        related_name='ingredientes',
        verbose_name='plato',
    )
    nombre = models.CharField('nombre', max_length=200)

    class Meta:
        verbose_name = 'ingrediente'
        verbose_name_plural = 'ingredientes'
        ordering = ['nombre']

    def __str__(self):
        return f'{self.nombre} ({self.plato.nombre})'
