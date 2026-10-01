"""Configuración de Django Admin para la aplicación "gastronomia"."""

from django.contrib import admin

from .models import Ingrediente, Plato, TipoPlato


@admin.register(TipoPlato)
class TipoPlatoAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)
    ordering = ('nombre',)


class IngredienteInline(admin.TabularInline):
    model = Ingrediente
    extra = 1
    fields = ('nombre',)
    verbose_name = 'ingrediente'
    verbose_name_plural = 'ingredientes'


@admin.register(Plato)
class PlatoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'slug', 'tipo', 'region')
    list_filter = ('tipo', 'region')
    search_fields = ('nombre', 'slug', 'descripcion', 'historia')
    prepopulated_fields = {'slug': ('nombre',)}
    inlines = (IngredienteInline,)
    fieldsets = (
        (None, {'fields': ('slug', 'nombre')}),
        ('Clasificación', {'fields': ('tipo', 'region')}),
        ('Contenido', {'fields': ('descripcion', 'historia', 'imagen')}),
    )


@admin.register(Ingrediente)
class IngredienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'plato')
    list_filter = ('plato',)
    search_fields = ('nombre', 'plato__nombre')
