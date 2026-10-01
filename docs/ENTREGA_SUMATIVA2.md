# EVALUACIÓN SUMATIVA 2 — DOCUMENTO DE ENTREGA

## Chile Explorer — Django + ORM + Base de datos + Django Admin + AWS EC2

---

**Proyecto:** Chile Explorer
**Asignatura:** Evaluación Sumativa N.º 2
**Tecnologías:** Python · Django 6.1 · MariaDB/MySQL · Django ORM · Django Admin · Bootstrap · AWS EC2 · Git/GitHub
**Repositorio:** https://github.com/dani6777-2/-chile_explorer
**Demostración en vivo:** Sí (presencial)
**Fecha de entrega:** 2026-10-01

---

## 1. Descripción del proyecto

**Chile Explorer** es un sitio web informativo sobre destinos turísticos y gastronomía típica de Chile. La aplicación consta de dos módulos independientes:

- **Destinos:** guía de 9 destinos turísticos emblemáticos (San Pedro de Atacama, Torres del Paine, Valparaíso, Isla de Pascua, Pucón, Chiloé, Valle del Elqui, Puerto Varas, Santiago).
- **Gastronomía:** guía de 9 platos típicos (Empanada de Pino, Pastel de Choclo, Cazuela, Completo, Curanto, Sopaipillas, Humitas, Charquicán, Mote con Huesillos).

### Evolución desde la Sumativa 1

| Aspecto | Sumativa 1 | Sumativa 2 |
| ------- | ---------- | ---------- |
| Almacenamiento | Archivos JSON | Base de datos relacional (MariaDB 10.11) |
| Modelos Django | No existían | 7 modelos con relaciones ForeignKey |
| Migraciones | No existían | Aplicadas y verificadas |
| Acceso a datos | `json.load()` en views | Django ORM (`objects.all()`, `filter()`, `select_related()`) |
| Administración | No existía | Django Admin con CRUD completo |
| Variables de entorno | SECRET_KEY hardcodeado | `.env` con python-dotenv |
| Botones CRUD | No existían | Visuales + rutas placeholder |
| Tests | No existían | 48 tests automatizados |
| Git | No existía | Repositorio con historial |
| Despliegue | Solo local | AWS EC2 + Nginx + MariaDB + phpMyAdmin |

---

## 2. Arquitectura del sistema

### Flujo de datos

```
Navegador
   ↓ puerto 80
Nginx (proxy inverso + archivos estáticos)
   ├── /static/        → archivos locales (Bootstrap, CSS, imágenes)
   ├── /phpmyadmin/    → PHP-FPM → phpMyAdmin → MariaDB
   └── /               → Django (127.0.0.1:8000)
                              ↓ Django ORM
                         MariaDB 10.11 (base de datos chile_explorer)
                              ↓
                         Templates Django → HTML
```

### Estructura del proyecto

```
chile_explorer/
├── manage.py
├── requirements.txt              # Django 6.1.1, python-dotenv, PyMySQL
├── .env                          # Variables sensibles (NO en Git)
├── .env.example                  # Plantilla de configuración
├── .gitignore                    # Incluye .env, venv/, db.sqlite3
├── desplegar_ec2.sh              # Script automático de despliegue EC2
│
├── chile_explorer/               # Proyecto principal
│   ├── settings.py               # Config con .env, apps Django, BD configurable
│   └── urls.py                   # Rutas raíz (admin + apps)
│
├── destinos/                     # Aplicación 1
│   ├── models.py                 # Categoria, Region, Destino, Actividad
│   ├── admin.py                  # 4 modelos registrados en Django Admin
│   ├── views.py                  # Views con Django ORM
│   ├── urls.py                   # URLs con app_name + placeholders CRUD
│   ├── tests.py                  # 24 tests automatizados
│   ├── migrations/               # Migraciones Django
│   ├── management/commands/      # cargar_destinos.py (JSON → BD)
│   ├── data/destinos.json        # Datos originales (evidencia Sumativa 1)
│   ├── templates/destinos/       # inicio.html, lista.html, detalle.html
│   └── static/destinos/          # Imágenes de destinos
│
├── gastronomia/                  # Aplicación 2
│   ├── models.py                 # TipoPlato, Plato, Ingrediente
│   ├── admin.py                  # 3 modelos registrados en Django Admin
│   ├── views.py                  # Views con Django ORM
│   ├── urls.py                   # URLs con app_name + placeholders CRUD
│   ├── tests.py                  # 24 tests automatizados
│   ├── migrations/               # Migraciones Django
│   ├── management/commands/      # cargar_gastronomia.py (JSON → BD)
│   ├── data/gastronomia.json     # Datos originales (evidencia Sumativa 1)
│   ├── templates/gastronomia/    # lista.html, detalle.html
│   └── static/gastronomia/       # Imágenes de platos
│
├── templates/                    # Templates compartidos
│   ├── base.html                 # Plantilla base con herencia
│   ├── 404.html                  # Error 404 amigable
│   └── crud_pendiente.html       # Placeholder para operaciones CRUD
│
├── static/                       # Estáticos globales
│   ├── bootstrap/                # Bootstrap 5.3 local (sin CDN)
│   ├── css/custom.css            # Estilos personalizados
│   └── js/custom.js              # Interacciones menores
│
├── docs/                         # Documentación
│   ├── AUDITORIA.md              # Auditoría técnica previa
│   ├── AI-EVIDENCE.md            # Evidencia del uso de IA
│   ├── DESPLIEGUE_EC2.md         # Guía de despliegue AWS
│   ├── REDESPLIEGO_EC2.md        # Guía para redespliegue
│   └── INFORME_SUMATIVA2.md      # Informe de implementación
│
├── DOCUMENTACION_IA.md           # Evidencia IA de la Sumativa 1
└── capturas/                     # Capturas de pantalla
```

---

## 3. Modelos y relaciones

Se definieron **7 modelos Django** con relaciones ForeignKey naturales al dominio del proyecto (no artificiales).

### Tabla de modelos

| Modelo | App | Campos principales | Relaciones | Propósito |
| ------ | --- | ------------------ | ---------- | --------- |
| `Categoria` | destinos | `nombre` (unique) | — | Clasifica destinos (Desierto, Naturaleza, Ciudad, Isla, Aventura, Cultura) |
| `Region` | destinos | `nombre` (unique) | — | Regiones administrativas de Chile |
| `Destino` | destinos | `slug`, `nombre`, `descripcion`, `mejor_epoca`, `imagen`, `destacado` | FK→`Categoria`, FK→`Region` | Destino turístico |
| `Actividad` | destinos | `nombre` | FK→`Destino` | Actividad recomendada por destino |
| `TipoPlato` | gastronomia | `nombre` (unique) | — | Tipos de platos (Comida tradicional, Plato de fondo, etc.) |
| `Plato` | gastronomia | `slug`, `nombre`, `region`, `descripcion`, `historia`, `imagen` | FK→`TipoPlato` | Plato típico chileno |
| `Ingrediente` | gastronomia | `nombre` | FK→`Plato` | Ingrediente de un plato |

### Relaciones implementadas

```
destinos_categoria ←──┐
                      ├── FK ── destinos_destino ── FK ──→ destinos_actividad
destinos_region ──────┘

gastronomia_tipoplato ── FK ──→ gastronomia_plato ── FK ──→ gastronomia_ingrediente
```

**Justificación de las relaciones:**
- `Destino → Categoria`: cada destino pertenece a una categoría (6 únicas en los datos).
- `Destino → Region`: cada destino está en una región administrativa (7 únicas).
- `Actividad → Destino`: normaliza el array `actividades` del JSON original (28 registros).
- `Plato → TipoPlato`: cada plato tiene un tipo (5 únicos).
- `Ingrediente → Plato`: normaliza el array `ingredientes` del JSON original (56 registros).
- `region` en gastronomía se mantiene como `CharField` porque los valores ("Todo Chile", "Zona central") son zonas descriptivas, **no** las mismas entidades que las regiones administrativas de destinos.

---

## 4. Migraciones

### Migraciones creadas

| Archivo | App | Contenido |
| ------- | --- | --------- |
| `destinos/migrations/0001_initial.py` | destinos | Crea `Categoria`, `Region`, `Destino`, `Actividad` con sus campos y relaciones FK |
| `gastronomia/migrations/0001_initial.py` | gastronomia | Crea `TipoPlato`, `Plato`, `Ingrediente` con sus campos y relaciones FK |

### Migraciones de Django contrib aplicadas

- `contenttypes` (2 migraciones)
- `auth` (13 migraciones)
- `admin` (3 migraciones)
- `sessions` (1 migración)

### Verificación

```bash
$ python manage.py showmigrations
admin        [X] 0001_initial ... [X] 0003_logentry_add_action_flag_choices
auth         [X] 0001_initial ... [X] 0012_alter_user_first_name_max_length
contenttypes [X] 0001_initial, [X] 0002_remove_content_type_name
destinos     [X] 0001_initial
gastronomia  [X] 0001_initial
sessions     [X] 0001_initial
```

Todas las migraciones están aplicadas. No hay migraciones pendientes.

---

## 5. Migración de datos JSON → Base de datos

### Mecanismo

Se crearon dos **management commands** idempotentes que migran los archivos JSON originales (evidencia de la Sumativa 1) hacia la base de datos relacional:

| Command | Fuente | Comando |
| ------- | ------ |--------- |
| `cargar_destinos` | `destinos/data/destinos.json` | `python manage.py cargar_destinos` |
| `cargar_gastronomia` | `gastronomia/data/gastronomia.json` | `python manage.py cargar_gastronomia` |

### Características del mecanismo

- **No destructivo:** si los registros ya existen, los omite.
- **Flag `--force`:** permite recrear los datos desde cero.
- **Transaccional:** usa `transaction.atomic()` para integridad.
- **Corrección de datos:** el slug `"torres-de mi-casa"` (con espacio, incompatible con el converter `<slug:slug>` de Django) se corrigió automáticamente a `"torres-de-mi-casa"`.

### Datos migrados

| Entidad | Registros creados |
| ------- | ----------------- |
| Destinos | 9 |
| Categorías | 6 |
| Regiones | 7 |
| Actividades | 28 |
| Platos | 9 |
| Tipos de plato | 5 |
| Ingredientes | 56 |

### Verificación post-migración

```bash
$ python manage.py shell
>>> from destinos.models import Destino, Actividad
>>> from gastronomia.models import Plato, Ingrediente
>>> Destino.objects.count()
9
>>> Actividad.objects.count()
28
>>> Plato.objects.count()
9
>>> Ingrediente.objects.count()
56
```

Los archivos JSON se conservan en `data/` como evidencia histórica. Las views **no** dependen de ellos en tiempo de ejecución.

---

## 6. Django Admin

### Modelos registrados (7/7)

| Modelo | list_display | search_fields | list_filter | Extras |
| ------ | ------------ | ------------- | ----------- | ------ |
| `Categoria` | nombre | nombre | — | — |
| `Region` | nombre | nombre | — | — |
| `Destino` | nombre, slug, region, categoria, destacado | nombre, slug, descripcion | categoria, region, destacado | `prepopulated_fields` (slug←nombre), inline de Actividades, fieldsets |
| `Actividad` | nombre, destino | nombre, destino__nombre | destino | — |
| `TipoPlato` | nombre | nombre | — | — |
| `Plato` | nombre, slug, tipo, region | nombre, slug, descripcion, historia | tipo, region | `prepopulated_fields` (slug←nombre), inline de Ingredientes, fieldsets |
| `Ingrediente` | nombre, plato | nombre, plato__nombre | plato | — |

### Funcionalidades del Admin

- **Crear:** formularios con validación y autocompletado de slug.
- **Visualizar:** listas con columnas configuradas y filtros laterales.
- **Modificar:** edición inline de actividades (en Destino) e ingredientes (en Plato).
- **Eliminar:** confirmación nativa de Django.
- **Buscar:** campo de búsqueda en todos los modelos.
- **Filtrar:** filtros por categoría, región, tipo, destacado.
- **Navegar relaciones:** desde cada modelo se puede acceder a los registros relacionados.

### URL de acceso

```
http://IP_EC2/admin/
```

---

## 7. Frontend

### Aplicaciones mantenidas

Las dos aplicaciones originales se mantuvieron intactas: `destinos` y `gastronomia`. No se renombraron, eliminaron ni fusionaron.

### Templates actualizados para ORM

| Template | Cambios realizados |
| -------- | ------------------ |
| `destinos/inicio.html` | `destino.categoria` → `destino.categoria.nombre` |
| `destinos/lista.html` | Atributos ORM + botones CRUD + mini-botones por tarjeta |
| `destinos/detalle.html` | Atributos ORM (`region.nombre`, `categoria.nombre`, `actividades.all`) + botones CRUD |
| `gastronomia/lista.html` | Atributos ORM (`tipo.nombre`, `ingredientes.all`) + botones CRUD |
| `gastronomia/detalle.html` | Atributos ORM + botones CRUD |
| `templates/crud_pendiente.html` | **Nuevo:** página placeholder para operaciones CRUD |

### Botones CRUD del frontend

Cada vista de listado y detalle muestra visualmente:

```
[ + Agregar ]   [ ✏ Modificar ]   [ 🗑 Eliminar ]   [ 🔍 Buscar ]
```

- **Agregar:** enlaza a `{url 'app:agregar'}` → vista placeholder.
- **Modificar:** enlaza a `{url 'app:modificar'}` → vista placeholder.
- **Eliminar:** enlaza a `{url 'app:eliminar'}` → vista placeholder.
- **Buscar:** enlaza a la vista de listado (donde está el formulario de búsqueda).

Según la pauta, estos botones **solo necesitan estar visualmente presentes y enlazar a una ruta o placeholder**. El CRUD funcional se realiza mediante Django Admin. La funcionalidad CRUD frontend se implementará en la evaluación siguiente.

### Bootstrap

Bootstrap 5.3 está descargado localmente en `static/bootstrap/` (CSS + JS bundle). **No se usa ningún CDN.** Componentes utilizados: navbar, container, row/col, cards, buttons, badges, breadcrumbs, alerts, form controls.

---

## 8. Django ORM en las views

**Todas las views utilizan consultas ORM de Django.** Ninguna lee archivos JSON en tiempo de ejecución.

### Consultas por vista

| View | Consultas ORM |
| ---- | ------------- |
| `destinos.inicio` | `Destino.objects.select_related('region', 'categoria').filter(destacado=True)[:3]` |
| `destinos.lista_destinos` | `.select_related()`, `.filter(Q(nombre__icontains=...) \| Q(descripcion__icontains=...))`, `.filter(region__nombre=...)`, `.filter(categoria__nombre=...)`, `Region.objects.values_list('nombre', flat=True)` |
| `destinos.detalle_destino` | `.select_related().prefetch_related('actividades').get(slug=...)` |
| `gastronomia.lista_platos` | `Plato.objects.select_related('tipo').prefetch_related('ingredientes').all()` |
| `gastronomia.detalle_plato` | `.select_related().prefetch_related().get(slug=...)` |

### Ejemplo de código (lista_destinos)

```python
def lista_destinos(request):
    destinos = Destino.objects.select_related('region', 'categoria').all()

    texto = request.GET.get('q', '').strip()
    region = request.GET.get('region', '').strip()
    categoria = request.GET.get('categoria', '').strip()

    if texto:
        destinos = destinos.filter(
            Q(nombre__icontains=texto) | Q(descripcion__icontains=texto)
        )
    if region:
        destinos = destinos.filter(region__nombre=region)
    if categoria:
        destinos = destinos.filter(categoria__nombre=categoria)

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
```

### Búsqueda de dependencias JSON restantes

Se realizó una búsqueda exhaustiva de `json.load`, `open(*.json)` y referencias a JSON:

- **En views.py:** cero dependencias. ✅
- **En management commands:** las referencias son esperadas (son los commands que migran los datos inicialmente).

---

## 9. Variables de entorno

### Archivos creados

| Archivo | Propósito | En Git |
| ------- | --------- | ------ |
| `.env` | Variables sensibles reales | **NO** (ignorado por `.gitignore`) |
| `.env.example` | Plantilla de configuración | Sí |

### Variables configuradas

| Variable | Propósito | Valor en EC2 |
| -------- | --------- | ------------ |
| `SECRET_KEY` | Clave secreta de Django | Generada automáticamente por script |
| `DEBUG` | Modo debug | `False` (producción) |
| `ALLOWED_HOSTS` | Hosts permitidos | IP y DNS públicos de la instancia |
| `DB_ENGINE` | Motor de BD | `django.db.backends.mysql` |
| `DB_NAME` | Nombre de BD | `chile_explorer` |
| `DB_USER` | Usuario MySQL | `chile_explorer_user` |
| `DB_PASSWORD` | Contraseña MySQL | Configurada en `.env` |
| `DB_HOST` | Host de BD | `127.0.0.1` |
| `DB_PORT` | Puerto de BD | `3306` |

### Configuración en settings.py

```python
from dotenv import load_dotenv
load_dotenv(BASE_DIR / '.env')

SECRET_KEY = os.environ.get('SECRET_KEY', 'fallback-inseguro-solo-dev')
DEBUG = _env_bool('DEBUG', default=True)
ALLOWED_HOSTS = _env_list('ALLOWED_HOSTS', default='localhost,127.0.0.1')

DATABASES = {
    'default': {
        'ENGINE': os.environ.get('DB_ENGINE', 'django.db.backends.sqlite3'),
        'NAME': os.environ.get('DB_NAME', str(BASE_DIR / 'db.sqlite3')),
        'USER': os.environ.get('DB_USER', ''),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', ''),
        'PORT': os.environ.get('DB_PORT', ''),
    }
}
```

---

## 10. Git / GitHub

### Estado del repositorio

| Aspecto | Estado |
| ------- | ------ |
| Repositorio Git | ✅ Inicializado |
| Historial de commits | ✅ 5 commits organizados |
| Remote configurado | ✅ `origin` → `https://github.com/dani6777-2/-chile_explorer.git` |
| Código completo | ✅ Subido a GitHub |
| README | ✅ Actualizado para Sumativa 2 |
| `.gitignore` | ✅ Incluye `.env`, `venv/`, `db.sqlite3` |
| Proyecto clonable | ✅ `git clone https://github.com/dani6777-2/-chile_explorer.git` |

### Historial de commits

```
45df423 Script automático de despliegue EC2 + guía de redespliegue
7e4a27b Informe final de implementación — Evaluación Sumativa 2
280e29e Documentación técnica, evidencia IA y guía de despliegue EC2
098a0c0 Modelos Django, ORM, Admin y migraciones de datos JSON→BD
1609e58 Configuración base: settings con variables de entorno, BD relacional y apps Django
```

### Archivos NO versionados (correctamente excluidos)

- `.env` (credenciales)
- `db.sqlite3` (base de datos local)
- `venv/` (entorno virtual)
- `__pycache__/` (archivos Python)
- `eva_2.pem` (clave SSH)

---

## 11. Despliegue en AWS EC2

### Arquitectura desplegada

| Componente | Tecnología | Estado |
| ---------- | ---------- | ------ |
| Instancia | Amazon Linux 2023 (t2.micro+) | ✅ Activa |
| Python | 3.12.14 | ✅ Instalado |
| Servidor web | Nginx (puerto 80) | ✅ Activo |
| Framework | Django 6.1.1 (systemd) | ✅ Activo |
| Base de datos | MariaDB 10.11.19 | ✅ Activa |
| phpMyAdmin | 5.2.2 + PHP-FPM 8.1 | ✅ Activo |
| Git | Clonado desde GitHub | ✅ Listo |

### Servicios configurados en EC2

| Servicio | systemd | Descripción |
| -------- | ------- | ----------- |
| `chile_explorer` | ✅ enabled | Django runserver (127.0.0.1:8000) |
| `nginx` | ✅ enabled | Proxy inverso + estáticos (puerto 80) |
| `mariadb` | ✅ enabled | Servidor de base de datos (puerto 3306) |
| `php-fpm` | ✅ enabled | Procesamiento PHP para phpMyAdmin |

### Script de despliegue automático

Se creó `desplegar_ec2.sh` que ejecuta todo el proceso automáticamente:

```bash
./desplegar_ec2.sh NUEVA_CLAVE.pem ec2-user@IP_O_DNS
```

El script instala dependencias, clona el repo, configura MariaDB, phpMyAdmin, nginx, Django, carga datos y verifica el despliegue.

### URLs de acceso en EC2

```
Sitio:        http://IP_PUBLICA/
Destinos:     http://IP_PUBLICA/destinos/
Gastronomía:  http://IP_PUBLICA/gastronomia/
Admin:        http://IP_PUBLICA/admin/
phpMyAdmin:   http://IP_PUBLICA/phpmyadmin/
```

### Nota sobre acceso

El despliegue fue ejecutado y verificado en la instancia EC2 proporcionada. El script de redespliegue (`desplegar_ec2.sh`) permite reconstruir el entorno completo en una instancia nueva en aproximadamente 5-8 minutos.

---

## 12. Base de datos — Evidencia

### Tablas creadas en MySQL (17 tablas)

**Tablas de la aplicación:**

| Tabla | Registros | Descripción |
| ----- | --------- | ----------- |
| `destinos_categoria` | 6 | Categorías de destinos |
| `destinos_region` | 7 | Regiones administrativas |
| `destinos_destino` | 9 | Destinos turísticos |
| `destinos_actividad` | 28 | Actividades por destino |
| `gastronomia_tipoplato` | 5 | Tipos de plato |
| `gastronomia_plato` | 9 | Platos típicos |
| `gastronomia_ingrediente` | 56 | Ingredientes por plato |

**Tablas de Django (auth/admin/sessions):**

| Tabla | Descripción |
| ----- | ----------- |
| `auth_user` | Usuarios (incluye superusuario) |
| `auth_group` | Grupos |
| `auth_permission` | Permisos |
| `django_admin_log` | Registro de acciones en Admin |
| `django_session` | Sesiones |
| `django_content_type` | Tipos de contenido |
| `django_migrations` | Historial de migraciones |

### Relaciones verificables en phpMyAdmin

Al abrir la tabla `destinos_destino` en phpMyAdmin se observan las columnas de clave foránea:
- `categoria_id` → referencia a `destinos_categoria`
- `region_id` → referencia a `destinos_region`

Al abrir `gastronomia_plato`:
- `tipo_id` → referencia a `gastronomia_tipoplato`

Al abrir `destinos_actividad`:
- `destino_id` → referencia a `destinos_destino`

---

## 13. Tests automatizados

### Comandos ejecutados

```bash
$ python manage.py check
System check identified no issues (0 silenced).

$ python manage.py makemigrations --check
No changes detected

$ python manage.py test
Found 48 test(s).
Ran 48 tests in 0.055s
OK
```

### Cobertura de tests

| Archivo | Tests | Áreas cubiertas |
| ------- | ----- | --------------- |
| `destinos/tests.py` | 24 | Modelos, relaciones FK, URLs, views, ORM, filtros de búsqueda, placeholders CRUD, botones CRUD, management command |
| `gastronomia/tests.py` | 24 | Modelos, relaciones FK, URLs, views, ORM, placeholders CRUD, botones CRUD, management command |

### Ejemplos de tests clave

```python
# Relaciones FK
def test_relacion_categoria(self):
    self.assertEqual(self.destino.categoria.nombre, 'Naturaleza')
    self.assertEqual(self.categoria.destinos.count(), 1)

# Datos desde BD (no JSON)
def test_lista_muestra_destinos_desde_bd(self):
    respuesta = self.client.get(reverse('destinos:lista'))
    self.assertContains(respuesta, 'Santiago de Chile')

# Botones CRUD visibles
def test_botones_crud_presentes_en_lista(self):
    respuesta = self.client.get(reverse('destinos:lista'))
    self.assertContains(respuesta, 'Agregar')
    self.assertContains(respuesta, 'Modificar')
    self.assertContains(respuesta, 'Eliminar')
    self.assertContains(respuesta, 'Buscar')

# Management command idempotente
def test_comando_es_idempotente(self):
    call_command('cargar_destinos')
    call_command('cargar_destinos')
    self.assertEqual(Destino.objects.count(), 9)
```

---

## 14. Evidencia de inteligencia artificial

Se utilizó **opencode** (agente de programación con IA, modelo `mimo-v2.5-free`) como herramienta de apoyo durante el desarrollo de la Sumativa 2.

### Prompts principales utilizados

1. **Auditoría inicial:** "Realiza una auditoría completa del repositorio y genera un informe clasificando cada requisito como [OK], [PARCIAL], [FALTA] o [ERROR]."
2. **Diseño de modelos:** "Diseña los modelos Django con relaciones ForeignKey naturales al dominio. No agregues relaciones artificiales."
3. **Migración de datos:** "Crea management commands para migrar los JSON a la BD de forma no destructiva."
4. **Django Admin:** "Registra TODOS los modelos en Admin con list_display, search_fields, list_filter e inlines."
5. **Variables de entorno:** "Externaliza SECRET_KEY, DEBUG y configuración de BD en .env."
6. **Frontend ORM:** "Actualiza views y templates para usar ORM. Agrega botones CRUD visuales que enlacen a placeholders."
7. **Tests:** "Crea tests para modelos, relaciones, URLs, views y management commands."
8. **Despliegue EC2:** "Genera script automático y guía para desplegar en AWS EC2 con MySQL y phpMyAdmin."

### Aplicación de las respuestas

Cada respuesta de la IA fue revisada, adaptada y validada antes de incorporarse al proyecto. El documento completo con el detalle de prompts, respuestas, cambios aplicados y validaciones se encuentra en:

**`docs/AI-EVIDENCE.md`**

### Evidencia de la Sumativa 1

La documentación del uso de IA en la evaluación anterior se conserva en:

**`DOCUMENTACION_IA.md`** (con capturas en `capturas/`)

---

## 15. Matriz de cumplimiento de la pauta

### Infraestructura

| Requisito | Estado | Evidencia |
| --------- | ------ | --------- |
| Linux | ✅ | Amazon Linux 2023 en EC2 |
| Python | ✅ | Python 3.12.14 |
| Entorno virtual | ✅ | `venv/` creado en EC2 y local |
| Django | ✅ | Django 6.1.1 |
| Servidor web | ✅ | Nginx (proxy inverso) + Gunicorn documentado |
| Git | ✅ | Repositorio con 5 commits |
| Base de datos | ✅ | MariaDB 10.11.19 (MySQL-compatible) |
| EC2 preparada | ✅ | Desplegada y verificada + script de redespliegue |

### GitHub

| Requisito | Estado | Evidencia |
| --------- | ------ | --------- |
| Repositorio | ✅ | github.com/dani6777-2/-chile_explorer |
| Historial de commits | ✅ | 5 commits con mensajes descriptivos |
| Remote | ✅ | `origin` configurado y push realizado |
| README | ✅ | Actualizado con secciones Sumativa 2 |
| `.gitignore` | ✅ | Excluye .env, venv/, db.sqlite3 |
| Proyecto clonable | ✅ | `git clone` funciona correctamente |

### Base de datos

| Requisito | Estado | Evidencia |
| --------- | ------ | --------- |
| Modelos Django | ✅ | 7 modelos en 2 apps |
| Relaciones | ✅ | 5 ForeignKey naturales |
| ForeignKey | ✅ | Destino→Categoria, Destino→Region, Actividad→Destino, Plato→TipoPlato, Ingrediente→Plato |
| Migraciones | ✅ | 0001_initial en ambas apps |
| Migraciones aplicadas | ✅ | showmigrations con [X] en todas |
| Tablas creadas | ✅ | 17 tablas en MySQL |
| Datos migrados | ✅ | 9 destinos, 9 platos, 28 actividades, 56 ingredientes |
| Consultas ORM | ✅ | Todas las views usan ORM |
| phpMyAdmin | ✅ | Instalado y accesible en EC2 |

### Django Admin

| Requisito | Estado | Evidencia |
| --------- | ------ | --------- |
| Todos los modelos registrados | ✅ | 7/7 modelos |
| Crear | ✅ | Formularios con validación |
| Modificar | ✅ | Edición inline de relaciones |
| Eliminar | ✅ | Confirmación nativa |
| Visualizar | ✅ | list_display configurado |
| Buscar | ✅ | search_fields en todos |
| Relaciones navegables | ✅ | inlines + FK navegables |

### Frontend

| Requisito | Estado | Evidencia |
| --------- | ------ | --------- |
| Dos aplicaciones mantenidas | ✅ | destinos y gastronomia intactas |
| Datos provenientes de BD | ✅ | ORM en todas las views |
| Django ORM | ✅ | select_related, prefetch_related, filter |
| Templates Django | ✅ | Herencia desde base.html |
| Bootstrap | ✅ | Local, sin CDN |
| Navegación | ✅ | Navbar con {% url %} |
| Listados | ✅ | Cards con datos de BD |
| Botón Agregar | ✅ | Visual + placeholder |
| Botón Modificar | ✅ | Visual + placeholder |
| Botón Eliminar | ✅ | Visual + placeholder |
| Botón Buscar | ✅ | Visual + formulario GET |

### Variables de entorno

| Requisito | Estado | Evidencia |
| --------- | ------ | --------- |
| `.env` | ✅ | Creado con valores de producción |
| `.env.example` | ✅ | Plantilla documentada |
| `.env` en Git | ✅ | Ignorado por .gitignore |
| Secretos fuera del código | ✅ | SECRET_KEY y BD vía variables |

### Documentación

| Requisito | Estado | Evidencia |
| --------- | ------ | --------- |
| Documento técnico | ✅ | README + docs/INFORME_SUMATIVA2.md |
| Evidencia AWS | ✅ | EC2 desplegada + docs/DESPLIEGUE_EC2.md |
| Evidencia GitHub | ✅ | Repo con historial de commits |
| Evidencia BD | ✅ | Migraciones + datos + phpMyAdmin |
| Evidencia phpMyAdmin | ✅ | Instalado y accesible en EC2 |
| Evidencia IA | ✅ | docs/AI-EVIDENCE.md |

---

## 16. Resumen de archivos entregados

### Archivos modificados

| Archivo | Cambio principal |
| ------- | ---------------- |
| `chile_explorer/settings.py` | Apps Django, env vars, BD configurable |
| `chile_explorer/urls.py` | Ruta admin/ |
| `destinos/views.py` | ORM + placeholders CRUD |
| `destinos/urls.py` | Placeholders CRUD |
| `destinos/templates/*` | Atributos ORM + botones CRUD |
| `gastronomia/views.py` | ORM + placeholders CRUD |
| `gastronomia/urls.py` | Placeholders CRUD |
| `gastronomia/templates/*` | Atributos ORM + botones CRUD |
| `requirements.txt` | + python-dotenv, PyMySQL |
| `.gitignore` | + .env, .venv/ |
| `README.md` | Reescrito para Sumativa 2 |

### Archivos nuevos

| Archivo | Contenido |
| ------- | --------- |
| `.env` / `.env.example` | Variables de entorno |
| `destinos/models.py` | 4 modelos |
| `destinos/admin.py` | 4 modelos registrados |
| `destinos/migrations/0001_initial.py` | Migración |
| `destinos/management/commands/cargar_destinos.py` | Command JSON→BD |
| `destinos/tests.py` | 24 tests |
| `gastronomia/models.py` | 3 modelos |
| `gastronomia/admin.py` | 3 modelos registrados |
| `gastronomia/migrations/0001_initial.py` | Migración |
| `gastronomia/management/commands/cargar_gastronomia.py` | Command JSON→BD |
| `gastronomia/tests.py` | 24 tests |
| `templates/crud_pendiente.html` | Placeholder CRUD |
| `desplegar_ec2.sh` | Script de despliegue automático |
| `docs/AUDITORIA.md` | Auditoría técnica |
| `docs/AI-EVIDENCE.md` | Evidencia IA |
| `docs/DESPLIEGUE_EC2.md` | Guía de despliegue |
| `docs/REDESPLIEGO_EC2.md` | Guía de redespliegue |
| `docs/INFORME_SUMATIVA2.md` | Informe de implementación |

---

## 17. Guion para la demostración en vivo

### Preparación previa

1. La EC2 está desplegada con el script `desplegar_ec2.sh`.
2. Superusuario creado: `admin` / `ChileExplorer2026!`
3. phpMyAdmin accesible con `chile_explorer_user` / `ChileExplorerDemo2026!`
4. Todos los servicios activos (Django, Nginx, MariaDB, PHP-FPM).

### Demostración paso a paso

| Paso | Acción | Qué mostrar al docente |
| ---- | ------ | ---------------------- |
| 1 | Conectarse a EC2 | `ssh -i clave.pem ec2-user@IP` |
| 2 | Mostrar Linux | `uname -a` → Amazon Linux 2023 |
| 3 | Activar venv | `source venv/bin/activate` |
| 4 | Mostrar proyecto | `ls -la` → estructura completa |
| 5 | Estado servicios | `systemctl is-active mariadb nginx chile_explorer` → todos activos |
| 6 | Abrir el sitio | Navegador → `http://IP/` |
| 7 | Mostrar inicio | Destinos destacados con imágenes y datos de BD |
| 8 | Navegar a destinos | `http://IP/destinos/` → 9 tarjetas + botones CRUD |
| 9 | Ver detalle | Clic en un destino → región, categoría, actividades desde BD |
| 10 | Navegar a gastronomía | `http://IP/gastronomia/` → 9 platos + botones CRUD |
| 11 | Ver receta | Clic en un plato → tipo, ingredientes, historia |
| 12 | Probar botones CRUD | Clic en "Agregar" → placeholder explicativo |
| 13 | Entrar al Admin | `http://IP/admin/` → login admin / ChileExplorer2026! |
| 14 | Mostrar entidades | Admin → Destinos, Categorías, Regiones, Actividades, Platos, Tipos, Ingredientes |
| 15 | CRUD en Admin | Crear registro → Modificar → Eliminar → Buscar |
| 16 | Mostrar relaciones | Abrir Destino → ver FK a Categoría y Región |
| 17 | Abrir phpMyAdmin | `http://IP/phpmyadmin/` → login chile_explorer_user |
| 18 | Mostrar BD | Seleccionar `chile_explorer` → 17 tablas |
| 19 | Ver tablas | Abrir `destinos_destino` → columnas con FK |
| 20 | Ver registros | Browse → 9 destinos con datos reales |
| 21 | Verificar coherencia | Comparar registros phpMyAdmin con frontend |
| 22 | Mostrar Git | `git log --oneline` → 5 commits |
| 23 | Mostrar GitHub | Navegador → repositorio completo |
| 24 | Ejecutar tests | `python manage.py test` → 48 tests OK |
| 25 | Mostrar documentación | `docs/` → auditoría, IA, despliegue |
| 26 | Mostrar script EC2 | `desplegar_ec2.sh` → redespliegue automático |

### Mensajes clave para el docente

1. **"El CRUD funcional está en Django Admin."** Los botones del frontend están presentes visualmente y enlazan a placeholders, según la pauta de esta evaluación.
2. **"Los datos provienen de MySQL mediante Django ORM."** Los archivos JSON se conservan solo como evidencia de la Sumativa 1.
3. **"La BD tiene 17 tablas con relaciones ForeignKey verificables en phpMyAdmin."**
4. **"Las variables sensibles están en .env, fuera del código y fuera de Git."**
5. **"El proyecto es redesplegable en una EC2 nueva con un solo script."**

---

## 18. Credenciales de acceso (para la demostración)

| Servicio | URL | Usuario | Contraseña |
| -------- | --- | ------- | ---------- |
| Sitio web | `http://IP_PUBLICA/` | — | — |
| Django Admin | `http://IP_PUBLICA/admin/` | `admin` | `ChileExplorer2026!` |
| phpMyAdmin | `http://IP_PUBLICA/phpmyadmin/` | `chile_explorer_user` | `ChileExplorerDemo2026!` |
| MySQL | `127.0.0.1:3306` | `chile_explorer_user` | `ChileExplorerDemo2026!` |

Base de datos: `chile_explorer`

---

*Documento preparado para la entrega en plataforma de la Evaluación Sumativa 2.*
*La demostración funcional se realizará en vivo.*
