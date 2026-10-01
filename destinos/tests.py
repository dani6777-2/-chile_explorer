"""Tests de la aplicación destinos."""

from django.test import TestCase
from django.urls import reverse

from .models import Actividad, Categoria, Destino, Region


class DestinoModelTests(TestCase):
    """Pruebas de los modelos de destinos."""

    @classmethod
    def setUpTestData(cls):
        cls.categoria = Categoria.objects.create(nombre='Naturaleza')
        cls.region = Region.objects.create(nombre='Los Lagos')
        cls.destino = Destino.objects.create(
            slug='puerto-varas',
            nombre='Puerto Varas',
            region=cls.region,
            categoria=cls.categoria,
            descripcion='Ciudad de influencia alemana frente al lago Llanquihue.',
            mejor_epoca='Diciembre a febrero',
            imagen='destinos/images/puerto-varas.jpg',
            destacado=True,
        )
        Actividad.objects.create(destino=cls.destino, nombre='Lago Llanquihue')
        Actividad.objects.create(destino=cls.destino, nombre='Saltos de Petrohué')

    def test_creacion_destino(self):
        self.assertEqual(self.destino.nombre, 'Puerto Varas')
        self.assertEqual(self.destino.slug, 'puerto-varas')
        self.assertTrue(self.destino.destacado)

    def test_str_destino(self):
        self.assertEqual(str(self.destino), 'Puerto Varas')

    def test_relacion_categoria(self):
        self.assertEqual(self.destino.categoria.nombre, 'Naturaleza')
        self.assertEqual(self.categoria.destinos.count(), 1)

    def test_relacion_region(self):
        self.assertEqual(self.destino.region.nombre, 'Los Lagos')
        self.assertEqual(self.region.destinos.count(), 1)

    def test_actividades_relacionadas(self):
        self.assertEqual(self.destino.actividades.count(), 2)
        self.assertIn('Lago Llanquihue', [a.nombre for a in self.destino.actividades.all()])

    def test_get_absolute_url(self):
        url = self.destino.get_absolute_url()
        self.assertEqual(url, '/destinos/puerto-varas/')


class DestinoUrlTests(TestCase):
    """Pruebas de las URLs principales de destinos."""

    def test_url_inicio(self):
        self.assertEqual(reverse('destinos:inicio'), '/')

    def test_url_lista(self):
        self.assertEqual(reverse('destinos:lista'), '/destinos/')

    def test_url_detalle(self):
        url = reverse('destinos:detalle', kwargs={'slug': 'san-pedro-de-atacama'})
        self.assertEqual(url, '/destinos/san-pedro-de-atacama/')

    def test_url_agregar_placeholder(self):
        self.assertEqual(reverse('destinos:agregar'), '/destinos/agregar/')

    def test_url_modificar_placeholder(self):
        self.assertEqual(reverse('destinos:modificar'), '/destinos/modificar/')

    def test_url_eliminar_placeholder(self):
        self.assertEqual(reverse('destinos:eliminar'), '/destinos/eliminar/')


class DestinoViewTests(TestCase):
    """Pruebas de las views de destinos."""

    @classmethod
    def setUpTestData(cls):
        cls.categoria = Categoria.objects.create(nombre='Ciudad')
        cls.region = Region.objects.create(nombre='Metropolitana')
        cls.destino = Destino.objects.create(
            slug='santiago',
            nombre='Santiago de Chile',
            region=cls.region,
            categoria=cls.categoria,
            descripcion='Capital del país, rodeada por la cordillera de los Andes.',
            mejor_epoca='Primavera y otoño',
            imagen='destinos/images/santiago.jpg',
            destacado=False,
        )

    def test_inicio_responde_200(self):
        respuesta = self.client.get(reverse('destinos:inicio'))
        self.assertEqual(respuesta.status_code, 200)

    def test_lista_responde_200(self):
        respuesta = self.client.get(reverse('destinos:lista'))
        self.assertEqual(respuesta.status_code, 200)

    def test_lista_muestra_destinos_desde_bd(self):
        respuesta = self.client.get(reverse('destinos:lista'))
        self.assertContains(respuesta, 'Santiago de Chile')

    def test_detalle_responde_200(self):
        respuesta = self.client.get(reverse('destinos:detalle', kwargs={'slug': 'santiago'}))
        self.assertEqual(respuesta.status_code, 200)

    def test_detalle_muestra_datos(self):
        respuesta = self.client.get(reverse('destinos:detalle', kwargs={'slug': 'santiago'}))
        self.assertContains(respuesta, 'Santiago de Chile')
        self.assertContains(respuesta, 'Ciudad')
        self.assertContains(respuesta, 'Metropolitana')

    def test_detalle_inexistente_devuelve_404(self):
        respuesta = self.client.get(reverse('destinos:detalle', kwargs={'slug': 'no-existe'}))
        self.assertEqual(respuesta.status_code, 404)

    def test_placeholder_agregar_responde_200(self):
        respuesta = self.client.get(reverse('destinos:agregar'))
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, 'Agregar destino')

    def test_placeholder_modificar_responde_200(self):
        respuesta = self.client.get(reverse('destinos:modificar'))
        self.assertEqual(respuesta.status_code, 200)

    def test_placeholder_eliminar_responde_200(self):
        respuesta = self.client.get(reverse('destinos:eliminar'))
        self.assertEqual(respuesta.status_code, 200)

    def test_busqueda_por_texto(self):
        respuesta = self.client.get(reverse('destinos:lista'), {'q': 'Santiago'})
        self.assertContains(respuesta, 'Santiago de Chile')

    def test_filtro_por_region(self):
        respuesta = self.client.get(reverse('destinos:lista'), {'region': 'Metropolitana'})
        self.assertContains(respuesta, 'Santiago de Chile')

    def test_filtro_por_categoria(self):
        respuesta = self.client.get(reverse('destinos:lista'), {'categoria': 'Ciudad'})
        self.assertContains(respuesta, 'Santiago de Chile')

    def test_botones_crud_presentes_en_lista(self):
        respuesta = self.client.get(reverse('destinos:lista'))
        self.assertContains(respuesta, 'Agregar')
        self.assertContains(respuesta, 'Modificar')
        self.assertContains(respuesta, 'Eliminar')
        self.assertContains(respuesta, 'Buscar')


class CargarDestinosCommandTests(TestCase):
    """Prueba del management command de carga de datos."""

    def test_comando_crea_destinos(self):
        from django.core.management import call_command

        call_command('cargar_destinos')
        # El JSON original tiene 9 destinos.
        self.assertEqual(Destino.objects.count(), 9)
        self.assertGreaterEqual(Categoria.objects.count(), 1)
        self.assertGreaterEqual(Region.objects.count(), 1)
        self.assertGreater(Actividad.objects.count(), 0)

    def test_comando_es_idempotente(self):
        from django.core.management import call_command

        call_command('cargar_destinos')
        call_command('cargar_destinos')
        # La segunda ejecución omite registros existentes.
        self.assertEqual(Destino.objects.count(), 9)
