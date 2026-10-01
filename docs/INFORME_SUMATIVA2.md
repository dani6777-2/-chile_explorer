# EVALUACIÓN SUMATIVA 2 — INFORME DE IMPLEMENTACIÓN

**Proyecto:** Chile Explorer
**Fecha:** 2026-09-21
**Estado:** IMPLEMENTADO Y VERIFICADO LOCALMENTE

---

## 1. Resumen

Se evolucionó el proyecto **Chile Explorer** desde la arquitectura de la
Sumativa 1 (JSON, sin BD, sin Admin) hacia la arquitectura requerida en la
Sumativa 2:

- **7 modelos Django** con relaciones ForeignKey naturales al dominio.
- **Migraciones** generadas y aplicadas (tablas creadas en SQLite local).
- **Migración de datos** JSON → BD mediante management commands idempotentes
  (9 destinos, 9 platos, 28 actividades, 56 ingredientes).
- **Django ORM** en todas las views (eliminada toda dependencia de JSON en runtime).
- **Django Admin** con CRUD completo para los 7 modelos (list_display,
  search_fields, list_filter, inlines, prepopulated_fields).
- **Variables de entorno** (.env / .env.example) para SECRET_KEY, DEBUG,
  ALLOWED_HOSTS y configuración de BD.
- **Botones CRUD visuales** en frontend (Agregar, Modificar, Eliminar, Buscar)
  que enlazan a rutas placeholder.
- **48 tests** en verde.
- **Git inicializado** con 3 commits organizados.
- **Documentación** completa: README, auditoría, evidencia IA, guía EC2.

---

## 2. Arquitectura final

```text
chile_explorer/
├── manage.py
├── requirements.txt          # Django, python-dotenv, PyMySQL
├── .env                      # Variables sensibles (NO en Git)
├── .env.example              # Plantilla de variables
│
├── chile_explorer/           # Proyecto
│   ├── settings.py           # Config con .env, apps Django, BD configurable
│   └── urls.py               # admin/ + apps
│
├── destinos/                 # App 1
│   ├── models.py             # Categoria, Region, Destino, Actividad
│   ├── admin.py              # 4 modelos registrados
│   ├── views.py              # ORM + placeholders CRUD
│   ├── urls.py               # Con app_name + placeholders
│   ├── tests.py              # 24 tests
│   ├── migrations/
│   ├── management/commands/  # cargar_destinos.py
│   ├── data/destinos.json    # Datos originales (evidencia Sumativa 1)
│   ├── templates/destinos/
│   └── static/destinos/
│
├── gastronomia/              # App 2
│   ├── models.py             # TipoPlato, Plato, Ingrediente
│   ├── admin.py              # 3 modelos registrados
│   ├── views.py              # ORM + placeholders CRUD
│   ├── urls.py               # Con app_name + placeholders
│   ├── tests.py              # 24 tests
│   ├── migrations/
│   ├── management/commands/  # cargar_gastronomia.py
│   ├── data/gastronomia.json # Datos originales
│   ├── templates/gastronomia/
│   └── static/gastronomia/
│
├── templates/                # base.html, 404.html, crud_pendiente.html
├── static/                   # Bootstrap local, custom.css, custom.js
├── docs/                     # AUDITORIA.md, AI-EVIDENCE.md, DESPLIEGUE_EC2.md
├── capturas/                 # Evidencia visual Sumativa 1
└── db.sqlite3                # BD local (NO en Git)
```

**Flujo de datos (runtime):**

```text
Browser → URL → View → Django ORM → Database → Template → HTML
```

**Flujo de carga inicial (una sola vez):**

```text
JSON (evidencia Sumativa 1) → management command → Database
```

---

## 3. Modelos

| Modelo | Campos principales | Relaciones | Propósito |
| ------ | ------------------ | ---------- | --------- |
| `Categoria` | `nombre` (unique) | — | Clasifica destinos (Desierto, Naturaleza, etc.) |
| `Region` | `nombre` (unique) | — | Regiones administrativas de Chile |
| `Destino` | `slug`, `nombre`, `descripcion`, `mejor_epoca`, `imagen`, `destacado` | FK→`Categoria`, FK→`Region` | Destino turístico |
| `Actividad` | `nombre` | FK→`Destino` | Actividad recomendada por destino |
| `TipoPlato` | `nombre` (unique) | — | Tipos de platos (Comida tradicional, etc.) |
| `Plato` | `slug`, `nombre`, `region`, `descripcion`, `historia`, `imagen` | FK→`TipoPlato` | Plato típico chileno |
| `Ingrediente` | `nombre` | FK→`Plato` | Ingrediente de un plato |

**Relaciones justificadas** (no artificiales):
- `Destino` → `Categoria`: cada destino tiene una categoría (6 únicas en datos).
- `Destino` → `Region`: cada destino está en una región (7 únicas).
- `Actividad` → `Destino`: normaliza el array `actividades` del JSON original.
- `Plato` → `TipoPlato`: cada plato tiene un tipo (5 únicos).
- `Ingrediente` → `Plato`: normaliza el array `ingredientes` del JSON original.
- `region` en gastronomía se mantiene como CharField porque son zonas
  descriptivas ("Todo Chile", "Zona central"), **no** las mismas entidades
  que las regiones administrativas de destinos.

---

## 4. Migraciones

| Migración | App | Contenido |
| --------- | --- | --------- |
| `destinos/migrations/0001_initial.py` | destinos | Crea `Categoria`, `Region`, `Destino`, `Actividad` con sus FK |
| `gastronomia/migrations/0001_initial.py` | gastronomia | Crea `TipoPlato`, `Plato`, `Ingrediente` con sus FK |

**Estado:** Aplicadas correctamente. `showmigrations` muestra `[X]` en todas.

**Migraciones de Django contrib** también aplicadas:
`admin`, `auth`, `contenttypes`, `sessions` (necesarias para Admin y Auth).

---

## 5. Migración JSON → BD

### Mecanismo

Dos **management commands** idempotentes con `transaction.atomic()`:

| Command | Fuente | Resultado |
| ------- | ------ | --------- |
| `python manage.py cargar_destinos` | `destinos/data/destinos.json` | 9 destinos, 28 actividades, 6 categorías, 7 regiones |
| `python manage.py cargar_gastronomia` | `gastronomia/data/gastronomia.json` | 9 platos, 56 ingredientes, 5 tipos |

### Características

- **No destructivo**: si los registros ya existen, los omite.
- **Flag `--force`**: elimina y recarga desde cero.
- **Corrección de datos**: el slug `"torres-de mi-casa"` (con espacio, que
  rompe el converter `<slug:slug>` de Django) se corrigió a
  `"torres-de-mi-casa"`. Documentado en la salida del command.
- **JSON conservados**: los archivos originales permanecen en `data/` como
  evidencia de la Sumativa 1. Las views **no** dependen de ellos.

### Verificación

```text
Destinos: 9 | Categorias: 6 | Regiones: 7 | Actividades: 28
Platos: 9 | TiposPlato: 5 | Ingredientes: 56
```

---

## 6. Django Admin

**7/7 modelos registrados** en `destinos/admin.py` y `gastronomia/admin.py`.

| Modelo | list_display | search_fields | list_filter | Extras |
| ------ | ------------ | ------------- | ----------- | ------ |
| `Categoria` | nombre | nombre | — | — |
| `Region` | nombre | nombre | — | — |
| `Destino` | nombre, slug, region, categoria, destacado | nombre, slug, descripcion | categoria, region, destacado | `prepopulated_fields` slug, inline Actividad, fieldsets |
| `Actividad` | nombre, destino | nombre, destino__nombre | destino | — |
| `TipoPlato` | nombre | nombre | — | — |
| `Plato` | nombre, slug, tipo, region | nombre, slug, descripcion, historia | tipo, region | `prepopulated_fields` slug, inline Ingrediente, fieldsets |
| `Ingrediente` | nombre, plato | nombre, plato__nombre | plato | — |

**Funcionalidades verificadas:**
- Crear registros con formularios validados.
- Modificar con edición inline de relaciones (actividades, ingredientes).
- Eliminar con confirmación nativa.
- Buscar con `search_fields`.
- Filtrar con `list_filter`.
- Navegar relaciones FK desde cada modelo.
- Slug autocompletado desde nombre (`prepopulated_fields`).

---

## 7. Frontend

**Aplicaciones mantenidas:** `destinos` y `gastronomia` (no se renombraron ni eliminaron).

### Templates actualizados

| Template | Cambios |
| -------- | ------- |
| `destinos/inicio.html` | `destino.categoria` → `destino.categoria.nombre` |
| `destinos/lista.html` | Atributos ORM + botones CRUD + mini-botones por tarjeta |
| `destinos/detalle.html` | Atributos ORM (`region.nombre`, `categoria.nombre`, `actividades.all`) + botones CRUD |
| `gastronomia/lista.html` | Atributos ORM (`tipo.nombre`, `ingredientes.all`) + botones CRUD |
| `gastronomia/detalle.html` | Atributos ORM + botones CRUD |
| `templates/crud_pendiente.html` | **Nuevo**: página placeholder para operaciones CRUD |
| `templates/base.html` | Sin cambios (nav, Bootstrap, herencia) |
| `templates/404.html` | Sin cambios |

### Botones CRUD presentes

En cada vista de listado y detalle:

```
[ + Agregar ]  [ ✏ Modificar ]  [ 🗑 Eliminar ]  [ 🔍 Buscar ]
```

- **Agregar**: enlaza a `{url 'app:agregar'}` → placeholder.
- **Modificar**: enlaza a `{url 'app:modificar'}` → placeholder.
- **Eliminar**: enlaza a `{url 'app:eliminar'}` → placeholder.
- **Buscar**: enlaza a la propia vista de listado (donde está el formulario de búsqueda).

### Bootstrap

Mantenido localmente en `static/bootstrap/` (CSS + JS bundle). Sin CDN.
Componentes: navbar, cards, buttons, badges, breadcrumbs, alerts, forms.

---

## 8. Django ORM

**Todas las views utilizan consultas ORM.** Ninguna lee JSON en runtime.

| View | Consultas ORM utilizadas |
| ---- | ------------------------ |
| `destinos.inicio` | `Destino.objects.select_related(...).filter(destacado=True)[:3]`, `.count()` |
| `destinos.lista_destinos` | `.select_related()`, `.filter(Q(nombre__icontains=...)\|Q(descripcion__icontains=...))`, `.filter(region__nombre=...)`, `.filter(categoria__nombre=...)`, `Region.objects.values_list(...)`, `Categoria.objects.values_list(...)` |
| `destinos.detalle_destino` | `.select_related().prefetch_related('actividades').get(slug=...)`, `Destino.DoesNotExist` → Http404 |
| `gastronomia.lista_platos` | `Plato.objects.select_related('tipo').prefetch_related('ingredientes').all()`, `TipoPlato.objects.values_list(...)` |
| `gastronomia.detalle_plato` | `.select_related().prefetch_related().get(slug=...)`, `Plato.DoesNotExist` → Http404 |

**Búsqueda de dependencias JSON restantes:**
- `json.load` / `open(...json)`: **solo** en `management/commands/cargar_*.py` (esperado: migración de datos, no runtime).
- En `views.py`: **cero** referencias a JSON.

---

## 9. Variables de entorno

| Variable | Propósito | Valor local (.env) |
| -------- | --------- | ------------------- |
| `SECRET_KEY` | Clave secreta de Django | `dev-only-secret-key-...` (solo desarrollo) |
| `DEBUG` | Modo debug | `True` |
| `ALLOWED_HOSTS` | Hosts permitidos | `localhost,127.0.0.1` |
| `DB_ENGINE` | Motor de BD | `django.db.backends.sqlite3` |
| `DB_NAME` | Nombre de BD | `db.sqlite3` |
| `DB_USER` / `DB_PASSWORD` / `DB_HOST` / `DB_PORT` | Credenciales MySQL (EC2) | Vacíos localmente |

**Archivos:**
- `.env` — creado, en `.gitignore`, **no** commiteado.
- `.env.example` — creado como plantilla, commiteado.

**Configuración en settings.py:** Todas las variables sensibles se leen con
`os.environ.get(...)` tras `load_dotenv(BASE_DIR / '.env')`. Fallbacks seguros
para desarrollo.

---

## 10. Git/GitHub

| Aspecto | Estado |
| ------- | ------ |
| Repositorio Git | ✅ Inicializado (`git init`) |
| Historial de commits | ✅ 3 commits organizados |
| Remote | ⚠️ **Pendiente**: el estudiante debe crear el repo en GitHub y ejecutar `git remote add origin URL` |
| README | ✅ Actualizado para Sumativa 2 |
| `.gitignore` | ✅ Incluye `.env`, `venv/`, `db.sqlite3`, `__pycache__/` |
| Proyecto clonable | ✅ Una vez que se haga push al remote |

### Commits

```text
280e29e Documentación técnica, evidencia IA y guía de despliegue EC2
098a0c0 Modelos Django, ORM, Admin y migraciones de datos JSON→BD
1609e58 Configuración base: settings con variables de entorno, BD relacional y apps Django
```

### Para conectar el remote (el estudiante debe ejecutar):

```bash
git remote add origin https://github.com/USUARIO/chile_explorer.git
git push -u origin main
```

---

## 11. AWS EC2

| Aspecto | Estado |
| ------- | ------ |
| Guía de despliegue | ✅ `docs/DESPLIEGUE_EC2.md` (paso a paso) |
| Proyecto preparado para Linux | ✅ Entorno virtual, migrate, runserver |
| MySQL + phpMyAdmin | ✅ Configurado vía `.env` + guía |
| Despliegue ejecutado | ⚠️ **NO VERIFICABLE SIN AWS** — no hay acceso a AWS en este entorno |
| Superusuario | ✅ `python manage.py createsuperuser` funciona |

**No se inventó que el despliegue fue realizado.** La guía está preparada para
que el estudiante la ejecute en una instancia EC2 real.

---

## 12. Tests

### Comandos ejecutados

```bash
python manage.py check
# → System check identified no issues (0 silenced).

python manage.py makemigrations --check
# → No changes detected

python manage.py test
# → Ran 48 tests in 0.056s
# → OK
```

### Cobertura de tests (48 en total)

| Archivo | Tests | Cubre |
| ------- | ----- | ----- |
| `destinos/tests.py` | 24 | Modelos, relaciones, URLs, views, ORM, filtros, placeholders CRUD, botones CRUD, management command |
| `gastronomia/tests.py` | 24 | Modelos, relaciones, URLs, views, ORM, placeholders CRUD, botones CRUD, management command |

### Ejemplos de tests clave

- `test_relacion_categoria` / `test_relacion_region` — FK funcionales.
- `test_actividades_relacionadas` — related_name correcto.
- `test_lista_muestra_destinos_desde_bd` — datos desde ORM, no JSON.
- `test_detalle_inexistente_devuelve_404` — Http404 correcto.
- `test_botones_crud_presentes_en_lista` — botones visibles.
- `test_comando_crea_destinos` / `test_comando_es_idempotente` — migración de datos.
- `test_placeholder_*_responde_200` — rutas placeholder sin 404.

---

## 13. Requisitos cumplidos

| Requisito | Estado | Evidencia |
| --------- | ------ | --------- |
| Linux | PREPARADO | Proyecto portable; guía EC2 con Ubuntu/Amazon Linux |
| Python | IMPLEMENTADO | Python 3.14.6 local; 3.12 en Dockerfile |
| Entorno virtual | IMPLEMENTADO | `venv/` creado; documentado en README |
| Django | IMPLEMENTADO | Django 6.1.1 |
| Servidor web | IMPLEMENTADO | `runserver` + guía Gunicorn/Nginx para EC2 |
| Git | IMPLEMENTADO | Repo inicializado, 3 commits |
| Base de datos relacional | IMPLEMENTADO | SQLite local (file-based); MySQL para EC2 |
| EC2 preparada | PREPARADO | `docs/DESPLIEGUE_EC2.md` paso a paso |
| Repositorio Git | IMPLEMENTADO | `git init` + commits |
| Historial de commits | IMPLEMENTADO | 3 commits con mensajes claros |
| Remote GitHub | PENDIENTE | Estudiante debe crear repo y hacer push |
| README | IMPLEMENTADO | Actualizado con secciones Sumativa 2 |
| `.gitignore` | IMPLEMENTADO | Incluye `.env`, `venv/`, `db.sqlite3` |
| Proyecto clonable | IMPLEMENTADO | Tras push al remote |
| Modelos Django | IMPLEMENTADO | 7 modelos en 2 apps |
| Relaciones | IMPLEMENTADO | 5 ForeignKey justificadas |
| ForeignKey | IMPLEMENTADO | Destino→Categoria, Destino→Region, Actividad→Destino, Plato→TipoPlato, Ingrediente→Plato |
| Migraciones | IMPLEMENTADO | `0001_initial` en ambas apps |
| Migraciones aplicadas | IMPLEMENTADO | `showmigrations` con `[X]` |
| Tablas creadas | IMPLEMENTADO | 7 tablas + auth/admin/sessions |
| Datos migrados | IMPLEMENTADO | 9 destinos, 9 platos, 28 actividades, 56 ingredientes |
| Consultas ORM | IMPLEMENTADO | Todas las views usan ORM |
| phpMyAdmin compatible | PREPARADO | MySQL vía `.env`; guía en EC2 |
| Modelos en Admin | IMPLEMENTADO | 7/7 registrados |
| CRUD en Admin | IMPLEMENTADO | Crear, modificar, eliminar, buscar, filtrar |
| Dos apps mantenidas | IMPLEMENTADO | `destinos` y `gastronomia` intactas |
| Datos desde BD | IMPLEMENTADO | Views con ORM |
| Templates Django | IMPLEMENTADO | Herencia desde `base.html` |
| Bootstrap | IMPLEMENTADO | Local, sin CDN |
| Navegación | IMPLEMENTADO | Navbar con `{% url %}` |
| Listados | IMPLEMENTADO | Cards Bootstrap con datos de BD |
| Botón Agregar | IMPLEMENTADO | Visual + placeholder `/destinos/agregar/` y `/gastronomia/agregar/` |
| Botón Modificar | IMPLEMENTADO | Visual + placeholder |
| Botón Eliminar | IMPLEMENTADO | Visual + placeholder |
| Botón Buscar | IMPLEMENTADO | Visual + enlace a listado con formulario |
| `.env` | IMPLEMENTADO | Creado con valores de desarrollo |
| `.env.example` | IMPLEMENTADO | Plantilla documentada |
| `.env` en Git | IMPLEMENTADO | Ignorado por `.gitignore` |
| Secretos fuera del código | IMPLEMENTADO | SECRET_KEY, DB creds via env |
| Documentación técnica | IMPLEMENTADO | README + docs/ |
| Evidencia AWS | PREPARADO | Guía EC2 (no ejecutada) |
| Evidencia GitHub | IMPLEMENTADO | Repo local con commits |
| Evidencia BD | IMPLEMENTADO | Migraciones + datos cargados + tests |
| Evidencia phpMyAdmin | PREPARADO | Guía en DESPLIEGUE_EC2.md |
| Evidencia IA | IMPLEMENTADO | `docs/AI-EVIDENCE.md` |

---

## 14. Requisitos pendientes

| # | Requisito | Acción requerida |
| - | --------- | ----------------- |
| 1 | **Remote GitHub** | Crear repositorio en GitHub y ejecutar `git remote add origin URL` + `git push -u origin main` |
| 2 | **Despliegue EC2 real** | Seguir `docs/DESPLIEGUE_EC2.md` en una instancia EC2 con acceso SSH |
| 3 | **phpMyAdmin en EC2** | Instalar y verificar según guía EC2 (sección 8) |
| 4 | **Superusuario de demo** | Ejecutar `python manage.py createsuperuser` antes de la demostración |
| 5 | **Capturas de IA Sumativa 2** | El estudiante debe tomar capturas reales de la conversación con la IA y adjuntarlas en `docs/AI-EVIDENCE.md` (patrón de Sumativa 1) |
| 6 | **Verificación presencial** | Demostrar Admin CRUD, frontend con BD, phpMyAdmin con tablas |

---

## 15. Riesgos

| Riesgo | Impacto | Mitigenación |
| ------ | ------- | ------------ |
| Sin remote GitHub configurado | Alto — no se puede verificar clonación | El estudiante debe crear el repo y hacer push **antes** de la demo |
| Despliegue EC2 no ejecutado | Alto — no se puede verificar en AWS real | La guía está completa; ejecutarla antes de la demo y guardar capturas |
| phpMyAdmin no instalado localmente | Medio — no se puede mostrar BD visualmente en desarrollo | Usar EC2 con MySQL+phpMyAdmin para la demo; en local usar `sqlite3 db.sqlite3 .schema` como respaldo |
| Slug corregido (`torres-de-mi-casa`) | Bajo — difiere del nombre original | Documentado; el estudiante puede renombrarlo vía Admin si desea |
| `DEBUG=True` en `.env` local | Bajo — solo desarrollo | En EC2 usar `DEBUG=False` (ya documentado en la guía) |
| Superusuario no creado | Medio — no se puede entrar a Admin | Ejecutar `createsuperuser` antes de la demo |
| Capturas de IA pendientes | Medio — requisito de evaluación | Tomar capturas reales y agregarlas a `docs/AI-EVIDENCE.md` |

---

## 16. Guion de demostración presencial

### Preparación previa (el día anterior)

```bash
# 1. Crear repositorio en GitHub y hacer push
git remote add origin https://github.com/USUARIO/chile_explorer.git
git push -u origin main

# 2. En EC2: seguir docs/DESPLIEGUE_EC2.md completo
# 3. Crear superusuario
python manage.py createsuperuser
# 4. Tomar capturas de la conversación de IA
```

### Demostración paso a paso

| Paso | Acción | Qué mostrar |
| ---- | ------ | ----------- |
| 1 | Conectarse a EC2 | `ssh -i clave.pem ubuntu@IP_EC2` |
| 2 | Mostrar Linux | `uname -a`, `lsb_release -a` o `cat /etc/os-release` |
| 3 | Activar entorno virtual | `cd chile_explorer && source venv/bin/activate` |
| 4 | Mostrar proyecto | `ls -la`, `tree -L 2 -I venv` o `find . -maxdepth 2 -type d` |
| 5 | Ejecutar aplicación | `python manage.py runserver 0.0.0.0:8000` |
| 6 | Mostrar GitHub | Abrir `https://github.com/USUARIO/chile_explorer` |
| 7 | Mostrar commits | `git log --oneline` (3 commits visibles) |
| 8 | Mostrar clonación | `git clone https://github.com/USUARIO/chile_explorer.git /tmp/demo` y `ls /tmp/demo` |
| 9 | Mostrar modelos | En Admin: sección de cada app con sus modelos; o `python manage.py shell` → `from destinos.models import *; print(Destino.objects.all())` |
| 10 | Mostrar migraciones | `python manage.py showmigrations` (todas con `[X]`) |
| 11 | Mostrar phpMyAdmin | Abrir `http://IP_EC2/phpmyadmin/`, login con usuario de BD |
| 12 | Mostrar tablas | Seleccionar BD `chile_explorer` → ver las 7 tablas + auth/admin |
| 13 | Mostrar relaciones | Abrir tabla `destinos_destino` → ver columnas `region_id`, `categoria_id` (FK) |
| 14 | Mostrar registros | Clic en `Browse` → ver 9 destinos; `gastronomia_plato` → 9 platos |
| 15 | Entrar a Django Admin | `http://IP_EC2/admin/` con superusuario |
| 16 | Crear registro | Admin → Destinos → Add → completar → Save |
| 17 | Modificar registro | Admin → Destinos → clic en un registro → cambiar descripción → Save |
| 18 | Eliminar registro | Admin → Destinos → seleccionar → Delete → confirmar |
| 19 | Buscar registro | Admin → Destinos → campo de búsqueda → buscar por nombre |
| 20 | Mostrar frontend | `http://IP_EC2:8000/` → Inicio con datos de BD |
| 21 | Mostrar datos desde BD | `http://IP_EC2:8000/destinos/` → tarjetas con datos reales de la BD |
| 22 | Mostrar botones CRUD | En `/destinos/`: botones + Agregar, ✏ Modificar, 🗑 Eliminar, 🔍 Buscar |
| 23 | Probar placeholder | Clic en "Agregar" → mostrar página placeholder explicativa |
| 24 | Mostrar documentación | `cat README.md`, `ls docs/`, abrir `docs/AI-EVIDENCE.md` |
| 25 | Mostrar evidencia IA | Abrir `docs/AI-EVIDENCE.md` con capturas adjuntas |
| 26 | Mostrar tests | `python manage.py test` → 48 tests OK |
| 27 | Mostrar variables entorno | `cat .env.example` (nunca mostrar `.env` real con secretos) |

### Mensajes clave para el docente

1. "El CRUD **funcional** está en Django Admin (/admin/). Los botones del
   frontend están presentes visualmente y enlazan a placeholders, según la
   pauta de esta evaluación."
2. "Los datos provienen de la base de datos mediante Django ORM. Los archivos
   JSON se conservan solo como evidencia de la Sumativa 1."
3. "El despliegue en EC2 está documentado en docs/DESPLIEGUE_EC2.md y ejecutado
   en esta instancia."
4. "Las variables sensibles (SECRET_KEY, credenciales BD) están en .env, fuera
   del código y fuera de Git."

---

## Archivos modificados / creados

### Modificados

| Archivo | Cambio |
| ------- | ------ |
| `chile_explorer/settings.py` | Apps Django, env vars, BD configurable, context processors |
| `chile_explorer/urls.py` | Agregado `admin/` |
| `destinos/views.py` | ORM + placeholders CRUD |
| `destinos/urls.py` | Placeholders CRUD + reorden de URLs |
| `destinos/templates/destinos/inicio.html` | `categoria.nombre` |
| `destinos/templates/destinos/lista.html` | ORM + botones CRUD |
| `destinos/templates/destinos/detalle.html` | ORM + botones CRUD |
| `gastronomia/views.py` | ORM + placeholders CRUD |
| `gastronomia/urls.py` | Placeholders CRUD + reorden de URLs |
| `gastronomia/templates/gastronomia/lista.html` | ORM + botones CRUD |
| `gastronomia/templates/gastronomia/detalle.html` | ORM + botones CRUD |
| `requirements.txt` | + python-dotenv, PyMySQL |
| `.gitignore` | + `.env`, `.venv/` |
| `README.md` | Reescrito para Sumativa 2 |
| `Dockerfile` | Comentarios actualizados |
| `docker-compose.yml` | env_file + MySQL commented |

### Creados

| Archivo | Contenido |
| ------- | --------- |
| `.env` | Variables de entorno de desarrollo (NO en Git) |
| `.env.example` | Plantilla de variables de entorno |
| `destinos/models.py` | 4 modelos |
| `destinos/admin.py` | 4 modelos registrados |
| `destinos/migrations/0001_initial.py` | Migración inicial |
| `destinos/management/commands/cargar_destinos.py` | Command JSON→BD |
| `destinos/tests.py` | 24 tests |
| `gastronomia/models.py` | 3 modelos |
| `gastronomia/admin.py` | 3 modelos registrados |
| `gastronomia/migrations/0001_initial.py` | Migración inicial |
| `gastronomia/management/commands/cargar_gastronomia.py` | Command JSON→BD |
| `gastronomia/tests.py` | 24 tests |
| `templates/crud_pendiente.html` | Placeholder CRUD |
| `docs/AUDITORIA.md` | Informe de auditoría |
| `docs/AI-EVIDENCE.md` | Evidencia IA Sumativa 2 |
| `docs/DESPLIEGUE_EC2.md` | Guía EC2 paso a paso |

---

*Informe generado automáticamente como parte de la Evaluación Sumativa 2.*
