"""Configuración de Django Admin para la aplicación "destinos"."""

from django.contrib import admin

from .models import Actividad, Categoria, Destino, Region


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)
    ordering = ('nombre',)


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)
    ordering = ('nombre',)


class ActividadInline(admin.TabularInline):
    model = Actividad
    extra = 1
    fields = ('nombre',)
    verbose_name = 'actividad'
    verbose_name_plural = 'actividades'


@admin.register(Destino)
class DestinoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'slug', 'region', 'categoria', 'destacado')
    list_filter = ('categoria', 'region', 'destacado')
    search_fields = ('nombre', 'slug', 'descripcion')
    list_editable = ('destacado',)
    prepopulated_fields = {'slug': ('nombre',)}
    inlines = (ActividadInline,)
    fieldsets = (
        (None, {'fields': ('slug', 'nombre')}),
        ('Clasificación', {'fields': ('region', 'categoria', 'destacado')}),
        ('Contenido', {'fields': ('descripcion', 'mejor_epoca', 'imagen')}),
    )


@admin.register(Actividad)
class ActividadAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'destino')
    list_filter = ('destino',)
    search_fields = ('nombre', 'destino__nombre')
