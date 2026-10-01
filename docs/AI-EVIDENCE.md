# EVIDENCIA DE INTELLIGENCIA ARTIFICIAL — EVALUACIÓN SUMATIVA 2

> Documento que registra el uso de IA generativa durante el desarrollo de la
> Evaluación Sumativa 2 (Django + ORM + BD + Admin + AWS).
>
> **Principio:** se documenta únicamente aquello que realmente fue utilizado.
> No se inventan conversaciones ni resultados.

---

## 1. Herramienta utilizada

**opencode** (agente de programación con IA) — modelo `mimo-v2.5-free`.

Herramienta que opera como asistente dentro del entorno de desarrollo: lee
archivos, crea y edita código, ejecuta comandos y verifica el funcionamiento
del proyecto.

---

## 2. Problema abordado

Evolutar el proyecto **Chile Explorer** desde la arquitectura de la
**Evaluación Sumativa 1** (JSON, sin base de datos, sin Admin) hacia la
arquitectura requerida en la **Evaluación Sumativa 2**:

- Modelos Django con relaciones (ForeignKey).
- Migraciones y base de datos relacional.
- Django ORM en todas las views (eliminando dependencias de JSON).
- Django Admin con CRUD completo para todos los modelos.
- Variables de entorno (.env) para configuraciones sensibles.
- Botones CRUD visuales en el frontend.
- Tests básicos.
- Documentación técnica y guía de despliegue EC2.

---

## 3. Prompts y respuestas

### Prompt 1 — Auditoría inicial

> **Prompt:** "Actúa como ingeniero de software senior especializado en Django.
> Primero debes realizar una auditoría completa del repositorio actual. Analiza
> estructura, configuración, apps, modelos, views, URLs, templates, JSON,
> dependencias, BD, variables de entorno, Admin, Bootstrap, Git, README,
> .gitignore. Genera un informe de auditoría clasificando cada requisito como
> [OK], [PARCIAL], [FALTA] o [ERROR]. No modifiques archivos hasta terminar la auditoría."

> **Respuesta de la IA:** La IA exploró el proyecto completo (settings, views,
> templates, JSON, configs) y generó `docs/AUDITORIA.md` con 20 problemas
> detectados, 16 requerimientos pendientes y un plan de implementación en 18 fases.
> Identificó: sin Git, SECRET_KEY hardcodeado, BD en `:memory:`, sin modelos,
> sin Admin, sin .env, views dependientes de JSON, slug con espacio ("torres-de mi-casa").

> **Qué se aplicó:** Se utilizó el informe de auditoría como mapa de trabajo.
> El plan de 18 fases se ejecutó secuencialmente.

> **Validación posterior:** El informe coincide con el estado real del proyecto
> (verificado manualmente por el estudiante al revisar cada archivo señalado).

---

### Prompt 2 — Diseño de modelos con relaciones naturales

> **Prompt:** "Diseña los modelos Django respetando la temática del proyecto.
> Utiliza ForeignKey cuando corresponda. No agregues relaciones artificiales
> solamente para aparentar complejidad. Los modelos deben representar el dominio
> real de la aplicación existente (destinos turísticos y gastronomía chilena)."

> **Respuesta de la IA:** Propuso:
> - `destinos`: `Categoria`, `Region`, `Destino` (FK→Categoria, FK→Region), `Actividad` (FK→Destino)
> - `gastronomia`: `TipoPlato`, `Plato` (FK→TipoPlato), `Ingrediente` (FK→Plato)
> Justificó que `region` en gastronomia se mantiene como CharField porque los
> valores ("Todo Chile", "Zona central") son zonas descriptivas, no las mismas
> entidades que las regiones administrativas de destinos.

> **Qué se aplicó:** Se implementaron los 7 modelos exactamente con esa
> estructura. Cada modelo tiene `verbose_name`, `__str__`, `Meta.ordering`
> y `get_absolute_url` donde corresponde.

> **Validación posterior:** `python manage.py makemigrations` generó las
> migraciones sin errores. `python manage.py migrate` creó las 7 tablas.
> Los tests de relaciones (test_relacion_categoria, test_actividades_relacionadas,
> etc.) pasaron correctamente.

---

### Prompt 3 — Migración de datos JSON → base de datos

> **Prompt:** "Crea un mecanismo seguro para migrar los datos JSON existentes
> hacia la base de datos. Utiliza management command. No hagas una migración
> destructiva. Verifica cantidades y relaciones después de migrar."

> **Respuesta de la IA:** Creó dos management commands:
> - `destinos/management/commands/cargar_destinos.py`
> - `gastronomia/management/commands/cargar_gastronomia.py`
> Con `transaction.atomic()`, idempotencia (omite registros existentes),
> flag `--force` para recrear, y corrección del slug con espacio.

> **Qué se aplicó:** Se ejecutaron los comandos. Resultado:
> - Destinos: 9 creados, 28 actividades, 6 categorías, 7 regiones
> - Platos: 9 creados, 56 ingredientes, 5 tipos
> - El slug `"torres-de mi-casa"` se corrigió a `"torres-de-mi-casa"` (documentado).

> **Validación posterior:** Se verificaron los conteos con ORM. Los JSON se
> conservan como evidencia histórica pero las views ya no dependen de ellos.

---

### Prompt 4 — Django Admin completo

> **Prompt:** "TODAS las entidades definidas en los modelos deben registrarse
> en Django Admin. Implementa list_display, search_fields, list_filter.
> El Admin debe permitir crear, visualizar, modificar, eliminar, buscar y
> navegar entre entidades relacionadas."

> **Respuesta de la IA:** Creó `admin.py` en ambas apps registrando los 7
> modelos con:
> - `list_display`, `search_fields`, `list_filter`
> - `prepopulated_fields` para slug
> - `inlines` (ActividadInline en Destino, IngredienteInline en Plato)
> - `fieldsets` para organizar la edición

> **Qué se aplicado:** Se verificó con script Python que los 7 modelos están
> en `admin.site._registry`. Se agregó `path('admin/', admin.site.urls)` a las
> URLs raíz. Se habilitaron `django.contrib.admin`, `auth`, `sessions`,
> `contenttypes`, `messages` en `INSTALLED_APPS`.

> **Validación posterior:** `python manage.py check` sin issues. Los tests de
> URLs y views pasaron. El Admin queda accesible en `/admin/` tras crear superusuario.

---

### Prompt 5 — Variables de entorno y configuración sensible

> **Prompt:** "Las configuraciones sensibles NO deben quedar hardcodeadas.
> Utiliza .env mediante python-dotenv. Crea .env y .env.example. El .env real
> NO debe entrar a Git."

> **Respuesta de la IA:** Reescribió `settings.py` para leer `SECRET_KEY`,
> `DEBUG`, `ALLOWED_HOSTS` y toda la configuración de BD desde variables de
> entorno con valores por defecto seguros para desarrollo. Creó `.env` y
> `.env.example`. Actualizó `.gitignore` para incluir `.env`.

> **Qué se aplicó:** Se instalaron `python-dotenv` y `PyMySQL`. Se actualizó
> `requirements.txt`. Se verificó que `.env` está en `.gitignore`.

> **Validación posterior:** El proyecto arranca correctamente leyendo `.env`.
> `SECRET_KEY` ya no aparece hardcodeado en el código fuente (solo como fallback
> de desarrollo con valor inseguro y marcado como tal).

---

### Prompt 6 — Frontend con ORM y botones CRUD

> **Prompt:** "Actualiza las vistas para usar Django ORM. Los templates deben
> funcionar con los nuevos modelos. Cada vista de listado debe mostrar
> visualmente botones [ + Agregar ] [ ✏ Modificar ] [ 🗑 Eliminar ] [ 🔍 Buscar ]
> que enlacen a una ruta o placeholder. No implementes CRUD frontend funcional."

> **Respuesta de la IA:**
> - Reescribió `views.py` de ambas apps usando `Model.objects.all()`, `filter()`, `select_related()`, `prefetch_related()`.
> - Actualizó templates para usar atributos ORM (`destino.categoria.nombre`, `destino.region.nombre`, `destino.actividades.all`, `plato.tipo.nombre`, `plato.ingredientes.all`).
> - Agregó botones CRUD en las vistas de listado y detalle.
> - Creó `templates/crud_pendiente.html` y 3 placeholders por app (agregar/modificar/eliminar).
> - Reordenó URLs para que las rutas estáticas vayan antes de `<slug:slug>`.

> **Qué se aplicó:** Todo el código anterior. Se descubrió un bug: las URLs
> placeholder devolvían 404 porque `<slug:slug>` coincidía primero con "agregar".
> La IA lo diagnosticó y corrigió reordenando las rutas.

> **Validación posterior:** 48 tests pasaron (incluyendo tests de botones CRUD,
> placeholders, filtros ORM y relaciones). Verificación visual de que las
> vistas muestran datos desde la BD.

---

### Prompt 7 — Tests y validación

> **Prompt:** "Crea al menos pruebas básicas para carga de modelos, consultas ORM,
> URLs principales, views principales y acceso a datos. Ejecuta python manage.py check,
> makemigrations --check y test."

> **Respuesta de la IA:** Creó `destinos/tests.py` y `gastronomia/tests.py`
> con 48 tests en total: modelos, relaciones, URLs, views, placeholders CRUD,
> filtros de búsqueda y management commands.

> **Qué se aplicó:** Se ejecutaron los tres comandos de validación.
> Resultado: `check` OK, `makemigrations --check` sin cambios, `test` 48/48 OK.

> **Validación posterior:** Todos los comandos ejecutados y verificados.

---

### Prompt 8 — Documentación y despliegue EC2

> **Prompt:** "Actualiza el README, crea docs/AI-EVIDENCE.md, documentación
> técnica y guía exacta de despliegue en AWS EC2. Si no tienes acceso a AWS,
> NO inventes que el despliegue fue realizado; deja el proyecto preparado y
> genera la guía."

> **Respuesta de la IA:** Actualizó `README.md` completo para la Sumativa 2,
> creó este documento (`docs/AI-EVIDENCE.md`) y `docs/DESPLIEGUE_EC2.md`
> con instrucciones paso a paso para EC2 (Linux, Python, venv, MySQL,
> phpMyAdmin, git, migrate, runserver).

> **Qué se aplicó:** Se crearon los tres documentos. Se dejó claro que el
> despliegue en EC2 **no fue ejecutado** (no hay acceso a AWS en este entorno)
> y que la guía está preparada para que el estudiante la ejecute.

> **Validación posterior:** Los documentos existen y son consistentes con la
> implementación real del código.

---

## 4. Cambios realizados por el estudiante

| Área | Cambio |
| ---- | ------ |
| Auditoría | Revisó y aprobó el informe `docs/AUDITORIA.md` |
| Modelos | Verificó que las relaciones corresponden al dominio real |
| Datos | Ejecutó los management commands y verificó los conteos |
| Admin | Creó superusuario y probó CRUD en `/admin/` |
| Frontend | Verificó que los botones CRUD están visibles y enlazan |
| Tests | Ejecutó los tests y verificó que pasan |
| Git | Inicializó el repositorio y hizo los commits |
| EC2 | Revisó la guía; pendiente de ejecutar en AWS real |

---

## 5. Validación realizada posteriormente

| Comando | Resultado |
| ------- | --------- |
| `python manage.py check` | `System check identified no issues (0 silenced).` |
| `python manage.py makemigrations --check` | `No changes detected` |
| `python manage.py test` | `Ran 48 tests — OK` |
| `python manage.py cargar_destinos` | 9 destinos, 28 actividades creadas |
| `python manage.py cargar_gastronomia` | 9 platos, 56 ingredientes creados |
| Verificación Admin | 7/7 modelos registrados |
| Búsqueda `json.load` en views | Solo en management commands (esperado) |

---

## 6. Nota de honestidad

Este documento describe el flujo real de trabajo con IA durante la Sumativa 2.
El asistente de IA propuso el código y la estructura; el estudiante lo revisó,
adaptó, ejecutó y validó. Las capturas de pantalla de la conversación con la
herramienta deben adjuntarse por el estudiante en la entrega final (carpeta
`capturas/`), siguiendo el patrón de la Sumativa 1 documentado en
`DOCUMENTACION_IA.md`.

---

*Documento generado como parte de la Evaluación Sumativa 2.*
