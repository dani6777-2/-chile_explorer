"""Tests de la aplicación gastronomia."""

from django.test import TestCase
from django.urls import reverse

from .models import Ingrediente, Plato, TipoPlato


class PlatoModelTests(TestCase):
    """Pruebas de los modelos de gastronomía."""

    @classmethod
    def setUpTestData(cls):
        cls.tipo = TipoPlato.objects.create(nombre='Comida tradicional')
        cls.plato = Plato.objects.create(
            slug='empanada-de-pino',
            nombre='Empanada de Pino',
            region='Todo Chile',
            tipo=cls.tipo,
            descripcion='Masa horneada rellena de carne de vacuno picada.',
            historia='De origen español, se adaptó en Chile.',
            imagen='gastronomia/images/empanada-de-pino.jpg',
        )
        Ingrediente.objects.create(plato=cls.plato, nombre='Carne molida')
        Ingrediente.objects.create(plato=cls.plato, nombre='Cebolla')
        Ingrediente.objects.create(plato=cls.plato, nombre='Huevo')

    def test_creacion_plato(self):
        self.assertEqual(self.plato.nombre, 'Empanada de Pino')
        self.assertEqual(self.plato.slug, 'empanada-de-pino')
        self.assertEqual(self.plato.region, 'Todo Chile')

    def test_str_plato(self):
        self.assertEqual(str(self.plato), 'Empanada de Pino')

    def test_relacion_tipo(self):
        self.assertEqual(self.plato.tipo.nombre, 'Comida tradicional')
        self.assertEqual(self.tipo.platos.count(), 1)

    def test_ingredientes_relacionados(self):
        self.assertEqual(self.plato.ingredientes.count(), 3)
        nombres = [i.nombre for i in self.plato.ingredientes.all()]
        self.assertIn('Carne molida', nombres)
        self.assertIn('Cebolla', nombres)
        self.assertIn('Huevo', nombres)

    def test_get_absolute_url(self):
        url = self.plato.get_absolute_url()
        self.assertEqual(url, '/gastronomia/empanada-de-pino/')


class PlatoUrlTests(TestCase):
    """Pruebas de las URLs principales de gastronomía."""

    def test_url_lista(self):
        self.assertEqual(reverse('gastronomia:lista'), '/gastronomia/')

    def test_url_detalle(self):
        url = reverse('gastronomia:detalle', kwargs={'slug': 'cazuela'})
        self.assertEqual(url, '/gastronomia/cazuela/')

    def test_url_agregar_placeholder(self):
        self.assertEqual(reverse('gastronomia:agregar'), '/gastronomia/agregar/')

    def test_url_modificar_placeholder(self):
        self.assertEqual(reverse('gastronomia:modificar'), '/gastronomia/modificar/')

    def test_url_eliminar_placeholder(self):
        self.assertEqual(reverse('gastronomia:eliminar'), '/gastronomia/eliminar/')


class PlatoViewTests(TestCase):
    """Pruebas de las views de gastronomía."""

    @classmethod
    def setUpTestData(cls):
        cls.tipo = TipoPlato.objects.create(nombre='Plato de fondo')
        cls.plato = Plato.objects.create(
            slug='cazuela',
            nombre='Cazuela',
            region='Todo Chile',
            tipo=cls.tipo,
            descripcion='Caldo caliente con presa de ave o carne.',
            historia='De raíz mapuche-huinca.',
            imagen='gastronomia/images/cazuela.jpg',
        )
        Ingrediente.objects.create(plato=cls.plato, nombre='Pollo o vacuno')
        Ingrediente.objects.create(plato=cls.plato, nombre='Papa')

    def test_lista_responde_200(self):
        respuesta = self.client.get(reverse('gastronomia:lista'))
        self.assertEqual(respuesta.status_code, 200)

    def test_lista_muestra_platos_desde_bd(self):
        respuesta = self.client.get(reverse('gastronomia:lista'))
        self.assertContains(respuesta, 'Cazuela')

    def test_detalle_responde_200(self):
        respuesta = self.client.get(reverse('gastronomia:detalle', kwargs={'slug': 'cazuela'}))
        self.assertEqual(respuesta.status_code, 200)

    def test_detalle_muestra_datos(self):
        respuesta = self.client.get(reverse('gastronomia:detalle', kwargs={'slug': 'cazuela'}))
        self.assertContains(respuesta, 'Cazuela')
        self.assertContains(respuesta, 'Plato de fondo')
        self.assertContains(respuesta, 'Pollo o vacuno')

    def test_detalle_inexistente_devuelve_404(self):
        respuesta = self.client.get(reverse('gastronomia:detalle', kwargs={'slug': 'no-existe'}))
        self.assertEqual(respuesta.status_code, 404)

    def test_placeholder_agregar_responde_200(self):
        respuesta = self.client.get(reverse('gastronomia:agregar'))
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, 'Agregar plato')

    def test_placeholder_modificar_responde_200(self):
        respuesta = self.client.get(reverse('gastronomia:modificar'))
        self.assertEqual(respuesta.status_code, 200)

    def test_placeholder_eliminar_responde_200(self):
        respuesta = self.client.get(reverse('gastronomia:eliminar'))
        self.assertEqual(respuesta.status_code, 200)

    def test_botones_crud_presentes_en_lista(self):
        respuesta = self.client.get(reverse('gastronomia:lista'))
        self.assertContains(respuesta, 'Agregar')
        self.assertContains(respuesta, 'Modificar')
        self.assertContains(respuesta, 'Eliminar')
        self.assertContains(respuesta, 'Buscar')


class CargarGastronomiaCommandTests(TestCase):
    """Prueba del management command de carga de datos de gastronomía."""

    def test_comando_crea_platos(self):
        from django.core.management import call_command

        call_command('cargar_gastronomia')
        # El JSON original tiene 9 platos.
        self.assertEqual(Plato.objects.count(), 9)
        self.assertGreaterEqual(TipoPlato.objects.count(), 1)
        self.assertGreater(Ingrediente.objects.count(), 0)

    def test_comando_es_idempotente(self):
        from django.core.management import call_command

        call_command('cargar_gastronomia')
        call_command('cargar_gastronomia')
        self.assertEqual(Plato.objects.count(), 9)
