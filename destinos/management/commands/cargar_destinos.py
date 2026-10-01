"""
Management command: cargar_destinos

Migra los datos del archivo JSON original (destinos/data/destinos.json)
hacia la base de datos relacional, creando las entidades y relaciones
definidas en los modelos de la aplicación destinos.

Uso:
    python manage.py cargar_destinos
    python manage.py cargar_destinos --force   # recrea desde cero

No es destructivo por defecto: si ya existen registros, los omite.
Con --force elimina todos los destinos (y sus actividades) antes de cargar.
"""

import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from destinos.models import Actividad, Categoria, Destino, Region

DATA_FILE = Path(__file__).resolve().parents[2] / 'data' / 'destinos.json'


class Command(BaseCommand):
    help = 'Carga los destinos turísticos desde el archivo JSON a la base de datos.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Elimina todos los destinos existentes antes de cargar los datos del JSON.',
        )

    def handle(self, *args, **options):
        if not DATA_FILE.exists():
            raise CommandError(f'No se encontró el archivo de datos: {DATA_FILE}')

        try:
            with open(DATA_FILE, encoding='utf-8') as archivo:
                datos = json.load(archivo)
        except json.JSONDecodeError as exc:
            raise CommandError(f'El archivo JSON no es válido: {exc}') from exc

        if not isinstance(datos, list):
            raise CommandError('El archivo JSON debe contener una lista de destinos.')

        if options['force']:
            eliminados = Destino.objects.count()
            Destino.objects.all().delete()
            self.stdout.write(
                self.style.WARNING(f'Se eliminaron {eliminados} destino(s) existentes (--force).')
            )

        creados = 0
        omitidos = 0
        actividades_creadas = 0

        with transaction.atomic():
            for item in datos:
                slug = item.get('slug', '').strip()
                if not slug:
                    self.stderr.write(self.style.WARNING(f'Se omitió un registro sin slug: {item.get("nombre", "?")}'))
                    omitidos += 1
                    continue

                if Destino.objects.filter(slug=slug).exists():
                    omitidos += 1
                    continue

                # Corrige el slug con espacio que no funciona en URLs Django.
                if ' ' in slug:
                    slug_corregido = slug.replace(' ', '-')
                    self.stdout.write(
                        self.style.WARNING(
                            f'Slug con espacio corregido: "{slug}" → "{slug_corregido}".'
                        )
                    )
                    slug = slug_corregido
                    if Destino.objects.filter(slug=slug).exists():
                        omitidos += 1
                        continue

                categoria_nombre = (item.get('categoria') or '').strip()
                categoria, _ = Categoria.objects.get_or_create(
                    nombre=categoria_nombre or 'Sin categoría'
                )

                region_nombre = (item.get('region') or '').strip()
                region, _ = Region.objects.get_or_create(
                    nombre=region_nombre or 'Sin región'
                )

                destino = Destino.objects.create(
                    slug=slug,
                    nombre=item.get('nombre', ''),
                    region=region,
                    categoria=categoria,
                    descripcion=item.get('descripcion', ''),
                    mejor_epoca=item.get('mejor_epoca', ''),
                    imagen=item.get('imagen', ''),
                    destacado=bool(item.get('destacado', False)),
                )
                creados += 1

                for actividad_nombre in item.get('actividades', []):
                    nombre_limpio = (actividad_nombre or '').strip()
                    if not nombre_limpio:
                        continue
                    Actividad.objects.create(destino=destino, nombre=nombre_limpio)
                    actividades_creadas += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Listo. Destinos creados: {creados} | '
                f'Omitidos: {omitidos} | '
                f'Actividades creadas: {actividades_creadas}'
            )
        )
        self.stdout.write(
            f'Totales en BD: Destino={Destino.objects.count()}, '
            f'Categoria={Categoria.objects.count()}, '
            f'Region={Region.objects.count()}, '
            f'Actividad={Actividad.objects.count()}'
        )
