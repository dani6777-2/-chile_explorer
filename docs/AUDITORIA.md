# AUDITORÍA — EVALUACIÓN SUMATIVA 2

**Proyecto:** Chile Explorer (`/Users/dani/Documents/chile_explorer`)
**Fecha de auditoría:** 2026-09-21
**Estado previo:** Evaluación Sumativa 1 (arquitectura JSON, sin BD)

---

## 1. Arquitectura actual

Proyecto Django 6.1.1 con dos aplicaciones independientes (`destinos`, `gastronomia`).
Toda la información se lee desde archivos JSON. `DATABASES` usa SQLite `:memory:`
(sin persistencia). No existen modelos, migraciones ni Django Admin.

Flujo de datos actual:

```text
Browser → URL → View → json.load() → Template → HTML
```

Flujo requerido (Sumativa 2):

```text
Browser → URL → View → Django ORM → Database → Template → HTML
```

## 2. Apps existentes

| App           | Vistas                     | Templates                        | Static              | Data JSON                     |
| ------------- | -------------------------- | -------------------------------- | ------------------- | ----------------------------- |
| `destinos`    | inicio, lista, detalle     | inicio.html, lista.html, detalle.html | images de destinos | `data/destinos.json`          |
| `gastronomia` | lista_platos, detalle_plato | lista.html, detalle.html         | images de platos    | `data/gastronomia.json`       |

## 3. Modelos existentes

**[FALTA]** No existe `models.py` en ninguna de las dos aplicaciones.
No hay entidades ni relaciones definidas en Django.

## 4. Datos JSON encontrados

### `destinos/data/destinos.json` — 9 destinos

| Campo         | Tipo en JSON              | Observación                              |
| ------------- | ------------------------- | ---------------------------------------- |
| id            | number                    | id incremental                           |
| slug          | string                    | `"torres-de mi-casa"` tiene un espacio (error de datos) |
| nombre        | string                    | nombre del destino                       |
| region        | string                    | región administrativa de Chile           |
| categoria     | string                    | Desierto, Naturaleza, Ciudad, etc.       |
| descripcion   | string                    | texto largo                              |
| mejor_epoca   | string                    | época recomendada                        |
| actividades   | array de strings          | lista de actividades por destino         |
| imagen        | string                    | ruta relativa a `static/`                |
| destacado     | boolean                   | para sección destacados                  |

Valores únicos de `categoria`: Desierto, Naturaleza, Ciudad, Isla, Aventura, Cultura.
Valores únicos de `region`: Antofagasta, Magallanes, Valparaíso, Araucanía, Los Lagos, Coquimbo, Metropolitana.

### `gastronomia/data/gastronomia.json` — 9 platos

| Campo        | Tipo en JSON         | Observación                            |
| ------------ | -------------------- | -------------------------------------- |
| id           | number               | id incremental                         |
| slug         | string               | slug válido                            |
| nombre       | string               | nombre del plato                       |
| region       | string               | zona geográfica (no es la misma entidad que regiones de destinos) |
| tipo         | string               | Comida tradicional, Plato de fondo, etc. |
| descripcion  | string               | texto largo                            |
| historia     | string               | origen y evolución del plato            |
| ingredientes | array de strings     | lista de ingredientes                   |
| imagen       | string               | ruta relativa a `static/`              |

Valores únicos de `tipo`: Comida tradicional, Plato de fondo, Comida rápida, Entrada / aperitivo, Bebida / postre.
Regiones gastronómicas: Todo Chile, Zona central, Zona central y sur, Chiloé (zonas descriptivas, distintas de las regiones administrativas de destinos).

## 5. Relaciones necesarias

Las relaciones son **naturales** al dominio, no artificiales:

### App `destinos`

| Modelo          | Relación        | Justificación                                            |
| --------------- | --------------- | -------------------------------------------------------- |
| `Categoria`     | entidad propia  | 6 categorías únicas que clasifican destinos              |
| `Region`        | entidad propia  | 7 regiones administrativas únicas                        |
| `Destino`       | FK → `Categoria` | cada destino pertenece a una categoría                  |
| `Destino`       | FK → `Region`   | cada destino está en una región                           |
| `Actividad`     | FK → `Destino`  | normaliza el array `actividades` del JSON                |

### App `gastronomia`

| Modelo        | Relación        | Justificación                                           |
| ------------- | --------------- | ------------------------------------------------------- |
| `TipoPlato`   | entidad propia  | 5 tipos únicos de platos                                |
| `Plato`       | FK → `TipoPlato` | cada plato tiene un tipo                               |
| `Ingrediente` | FK → `Plato`    | normaliza el array `ingredientes` del JSON              |

> **Nota:** `region` en gastronomia se mantiene como `CharField` porque los
> valores ("Todo Chile", "Zona central", etc.) son zonas descriptivas y **no**
> corresponden a las mismas entidades que las regiones administrativas de
> `destinos`. Unificarlos sería artificial.

## 6. Estado de migraciones

**[FALTA]** No existen directorios `migrations/` ni migraciones en ninguna app.
No hay tablas creadas.

## 7. Estado Django Admin

**[FALTA]**
- No existe `admin.py` en ninguna app.
- `django.contrib.admin` **no está** en `INSTALLED_APPS`.
- No hay rutas `/admin/`.
- No hay superusuario posible (faltan `auth`, `sessions`, `contenttypes`).

## 8. Estado frontend

**[PARCIAL]**
- Templates Django con herencia desde `base.html`: **OK**
- Navegación global con `{% url %}`: **OK**
- Breadcrumb en listados y detalles: **OK**
- Estados vacíos y 404 amigable: **OK**
- Búsqueda/filtros GET en destinos: **OK**
- Botones CRUD (Agregar, Modificar, Eliminar, Buscar): **[FALTA]**
- Datos desde BD (ORM): **[FALTA]** (actualmente desde JSON)

## 9. Estado Bootstrap

**[OK]**
- Bootstrap 5.3 local en `static/bootstrap/` (CSS + JS bundle).
- Sin CDN.
- Componentes usados: navbar, container, row/col, cards, buttons, badges,
  alerts, breadcrumbs, form controls.
- `custom.css` complementa con colores de la bandera chilena.

## 10. Estado variables de entorno

**[ERROR]**
- `SECRET_KEY` hardcodeado en `settings.py`.
- `DEBUG = True` hardcodeado.
- `ALLOWED_HOSTS = []` hardcodeado.
- No existe `.env` ni `.env.example`.
- No hay librería de entorno (`python-dotenv` u otra).
- `.gitignore` **no** incluye `.env`.

## 11. Estado Git

**[ERROR]**
- **No existe repositorio Git** (no hay carpeta `.git`).
- No hay historial de commits.
- No hay remote configurado.
- `.gitignore` existe y es básico (venv, __pycache__, sqlite3, DS_Store, IDE).
- `.pre-commit-config.yaml` existe pero no puede activarse sin repo Git.

## 12. Estado README

**[PARCIAL]**
- `README.md` completo y detallado (309 líneas), pero describe la arquitectura
  de la **Sumativa 1** (JSON, sin BD, sin admin, sin modelos).
- Falta documentar: modelos, migraciones, BD, Admin, variables de entorno,
  despliegue EC2, estructura con models/admin/migrations.
- `DOCUMENTACION_IA.md` existe (evidencia Sumativa 1).

## 13. Problemas detectados

| # | Problema | Severidad | Archivo |
|---|----------|-----------|---------|
| 1 | No hay repositorio Git | Alta | raíz del proyecto |
| 2 | `SECRET_KEY` hardcodeado | Alta | `chile_explorer/settings.py` |
| 3 | `DEBUG = True` hardcodeado | Alta | `chile_explorer/settings.py` |
| 4 | `DATABASES = :memory:` (sin persistencia) | Alta | `chile_explorer/settings.py` |
| 5 | Sin modelos Django | Alta | `destinos/`, `gastronomia/` |
| 6 | Sin migraciones | Alta | ambas apps |
| 7 | Sin Django Admin | Alta | proyecto completo |
| 8 | `INSTALLED_APPS` sin admin/auth/sessions/contenttypes | Alta | `settings.py` |
| 9 | Sin context processors de auth/messages | Media | `settings.py` |
| 10 | `MIDDLEWARE` sin sessions/csrf/auth/messages | Media | `settings.py` |
| 11 | Views dependen de `json.load` | Alta | `views.py` de ambas apps |
| 12 | Sin `.env` / `.env.example` | Alta | raíz |
| 13 | `.gitignore` sin `.env` | Media | `.gitignore` |
| 14 | Slug `"torres-de mi-casa"` con espacio (rompe `<slug:slug>`) | Media | `destinos.json` |
| 15 | `requirements.txt` solo tiene Django | Media | `requirements.txt` |
| 16 | Sin tests | Media | proyecto completo |
| 17 | README basado en arquitectura Sumativa 1 | Media | `README.md` |
| 18 | Sin botones CRUD en frontend | Media | templates de listado |
| 19 | `DEFAULT_AUTO_FIELD` no definido | Baja | `settings.py` |
| 20 | Dockerfile/docker-compose sin BD ni migrate | Baja | `Dockerfile`, `docker-compose.yml` |

## 14. Requerimientos ya cumplidos

```text
[OK]   Proyecto Django existente
[OK]   Dos aplicaciones (destinos, gastronomia)
[OK]   URLs propias por app con app_name
[OK]   Templates Django con herencia (base.html)
[OK]   Bootstrap local (sin CDN)
[OK]   Navegación global con {% url %}
[OK]   Imágenes locales
[OK]   CSS/JS local
[OK]   Manejo de errores 404
[OK]   Diseño responsive
[OK]   Búsqueda/filtros en destinos (parámetros GET)
[OK]   Documentación de IA (Sumativa 1)
[OK]   Estructura de carpetas organizada
[OK]   Virtualenv creado (venv/)
[OK]   Python 3.14.6 + Django 6.1.1 instalados
```

## 15. Requerimientos pendientes

```text
[FALTA] Modelos Django con relaciones
[FALTA] Migraciones (makemigrations + migrate)
[FALTA] Migración de datos JSON → base de datos
[FALTA] Django ORM en todas las views
[FALTA] Django Admin con CRUD completo
[FALTA] Superusuario
[FALTA] Variables de entorno (.env, .env.example)
[FALTA] SECRET_KEY / DEBUG / ALLOWED_HOSTS externos
[FALTA] Base de datos relacional persistente
[FALTA] Botones CRUD visuales en frontend
[FALTA] Repositorio Git + commits + remote
[FALTA] README actualizado para Sumativa 2
[FALTA] Documentación técnica (modelos, BD, admin, EC2)
[FALTA] docs/AI-EVIDENCE.md (evidencia IA Sumativa 2)
[FALTA] Tests básicos
[FALTA] Guía de despliegue EC2
[FALTA] phpMyAdmin (requiere MySQL en EC2)
```

## 16. Plan de implementación

| Fase | Acción | Archivos |
|------|--------|----------|
| 1 | Crear `.env` y `.env.example` | raíz |
| 2 | Actualizar `settings.py` (apps Django, env vars, BD) | `chile_explorer/settings.py` |
| 3 | Crear modelos en ambas apps | `destinos/models.py`, `gastronomia/models.py` |
| 4 | Crear `admin.py` en ambas apps | `destinos/admin.py`, `gastronomia/admin.py` |
| 5 | Crear management commands de carga de datos | `*/management/commands/cargar_*.py` |
| 6 | Generar y aplicar migraciones | `*/migrations/` |
| 7 | Ejecutar migración de datos JSON → BD | management commands |
| 8 | Actualizar views con ORM | `*/views.py` |
| 9 | Actualizar URLs (admin + placeholders CRUD) | `chile_explorer/urls.py`, `*/urls.py` |
| 10 | Actualizar templates (atributos ORM + botones CRUD) | `*/templates/`, `templates/` |
| 11 | Crear tests | `*/tests.py` |
| 12 | Actualizar `requirements.txt` | raíz |
| 13 | Actualizar `.gitignore` | raíz |
| 14 | Actualizar README + documentación | `README.md`, `docs/` |
| 15 | Crear `docs/AI-EVIDENCE.md` | `docs/` |
| 16 | Crear guía EC2 | `docs/DESPLIEGUE_EC2.md` |
| 17 | Ejecutar validaciones (check, migrate, test) | terminal |
| 18 | Inicializar Git y hacer commits | raíz |

---

*Informe generado antes de iniciar la implementación de la Sumativa 2.*
