"""
Management command: cargar_gastronomia

Migra los datos del archivo JSON original (gastronomia/data/gastronomia.json)
hacia la base de datos relacional, creando las entidades y relaciones
definidas en los modelos de la aplicación gastronomia.

Uso:
    python manage.py cargar_gastronomia
    python manage.py cargar_gastronomia --force   # recrea desde cero

No es destructivo por defecto: si ya existen registros, los omite.
Con --force elimina todos los platos (y sus ingredientes) antes de cargar.
"""

import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from gastronomia.models import Ingrediente, Plato, TipoPlato

DATA_FILE = Path(__file__).resolve().parents[2] / 'data' / 'gastronomia.json'


class Command(BaseCommand):
    help = 'Carga los platos de gastronomía desde el archivo JSON a la base de datos.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Elimina todos los platos existentes antes de cargar los datos del JSON.',
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
            raise CommandError('El archivo JSON debe contener una lista de platos.')

        if options['force']:
            eliminados = Plato.objects.count()
            Plato.objects.all().delete()
            self.stdout.write(
                self.style.WARNING(f'Se eliminaron {eliminados} plato(s) existentes (--force).')
            )

        creados = 0
        omitidos = 0
        ingredientes_creados = 0

        with transaction.atomic():
            for item in datos:
                slug = (item.get('slug') or '').strip()
                if not slug:
                    self.stderr.write(self.style.WARNING(f'Se omitió un registro sin slug: {item.get("nombre", "?")}'))
                    omitidos += 1
                    continue

                if Plato.objects.filter(slug=slug).exists():
                    omitidos += 1
                    continue

                tipo_nombre = (item.get('tipo') or '').strip()
                tipo, _ = TipoPlato.objects.get_or_create(
                    nombre=tipo_nombre or 'Sin tipo'
                )

                plato = Plato.objects.create(
                    slug=slug,
                    nombre=item.get('nombre', ''),
                    region=item.get('region', ''),
                    tipo=tipo,
                    descripcion=item.get('descripcion', ''),
                    historia=item.get('historia', ''),
                    imagen=item.get('imagen', ''),
                )
                creados += 1

                for ingrediente_nombre in item.get('ingredientes', []):
                    nombre_limpio = (ingrediente_nombre or '').strip()
                    if not nombre_limpio:
                        continue
                    Ingrediente.objects.create(plato=plato, nombre=nombre_limpio)
                    ingredientes_creados += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Listo. Platos creados: {creados} | '
                f'Omitidos: {omitidos} | '
                f'Ingredientes creados: {ingredientes_creados}'
            )
        )
        self.stdout.write(
            f'Totales en BD: Plato={Plato.objects.count()}, '
            f'TipoPlato={TipoPlato.objects.count()}, '
            f'Ingrediente={Ingrediente.objects.count()}'
        )
