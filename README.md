# 🇨🇱 Chile Explorer

Sitio web informativo sobre los destinos turísticos y la gastronomía típica de Chile,
desarrollado con **Python + Django**, **base de datos relacional**, **Django ORM**,
**Django Admin** y **variables de entorno**, para la Evaluación Sumativa 2.

## 1. Descripción

**Chile Explorer** es una guía informativa que reúne destinos turísticos emblemáticos
de Chile y la gastronomía típica del país. El proyecto evoluciona desde una
arquitectura basada en archivos JSON (Sumativa 1) hacia una arquitectura con
**base de datos relacional**, **modelos Django**, **ORM**, **migraciones** y
**Django Admin** para la gestión completa de la información.

### Problemática

Las guías turísticas y gastronómicas dispersas en archivos planos dificultan:
- la gestión centralizada de la información;
- la búsqueda y filtrado eficiente;
- el mantenimiento y actualización de los datos;
- la escalabilidad a múltiples administradores.

### Solución

Sitio web con dos módulos independientes que muestran información proveniente de
una base de datos relacional, administrable mediante Django Admin, con frontend
que visualiza los datos a través de templates Django y Bootstrap.

## 2. Tecnologías

| Tecnología       | Uso                                              |
| ---------------- | ------------------------------------------------ |
| Python 3         | Lenguaje de programación                         |
| Django 6.1       | Framework web (proyecto + 2 aplicaciones)        |
| SQLite / MySQL   | Base de datos relacional (SQLite local, MySQL en EC2) |
| Django ORM       | Acceso a datos mediante modelos                  |
| Django Admin     | CRUD administrativo completo                     |
| python-dotenv    | Variables de entorno (.env)                      |
| PyMySQL          | Driver MySQL para EC2                            |
| HTML5 / CSS3     | Estructura y estilos                             |
| Bootstrap 5.3    | Framework CSS/JS local (sin CDN)                 |
| JavaScript       | Interacciones menores                            |
| Git / GitHub     | Control de versiones                             |

## 3. Requisitos

- Python 3.10 o superior
- pip
- Entorno virtual (recomendado)
- Git (opcional para clonar)
- MySQL/MariaDB + phpMyAdmin (solo para despliegue en EC2)

## 4. Instalación

```bash
# 1. Clonar el repositorio
git clone URL_DEL_REPOSITORIO
cd chile_explorer

# 2. Crear entorno virtual
python3 -m venv venv

# 3. Activar entorno virtual
source venv/bin/activate          # macOS / Linux
# venv\Scripts\activate           # Windows

# 4. Instalar dependencias
pip install -r requirements.txt
```

## 5. Variables de entorno

El proyecto usa `.env` para configuraciones sensibles. **Nunca** subas `.env` a Git.

```bash
# Copiar el archivo de ejemplo
cp .env.example .env
```

Editar `.env` con valores reales:

```env
SECRET_KEY=tu-clave-secreta-segura
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# SQLite (desarrollo local — por defecto)
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3

# MySQL (EC2 + phpMyAdmin) — descomentar y completar:
# DB_ENGINE=django.db.backends.mysql
# DB_NAME=chile_explorer
# DB_USER=chile_explorer_user
# DB_PASSWORD=tu_password_seguro
# DB_HOST=127.0.0.1
# DB_PORT=3306
```

## 6. Base de datos

### Desarrollo local (SQLite)

SQLite está configurado por defecto. No requiere servidor externo.

### EC2 con MySQL + phpMyAdmin

En el servidor EC2 se usa MySQL para poder visualizar tablas y relaciones con
phpMyAdmin. Ver la guía completa en [`docs/DESPLIEGUE_EC2.md`](docs/DESPLIEGUE_EC2.md).

### Modelos y relaciones

| App           | Modelo        | Relaciones                                    |
| ------------- | ------------- | --------------------------------------------- |
| `destinos`    | `Categoria`   | —                                             |
| `destinos`    | `Region`      | —                                             |
| `destinos`    | `Destino`     | FK → `Categoria`, FK → `Region`               |
| `destinos`    | `Actividad`   | FK → `Destino`                                |
| `gastronomia` | `TipoPlato`   | —                                             |
| `gastronomia` | `Plato`       | FK → `TipoPlato`                              |
| `gastronomia` | `Ingrediente` | FK → `Plato`                                  |

### Tablas creadas

| Tabla                    | Registros |
| ------------------------ | --------- |
| `destinos_categoria`     | 6         |
| `destinos_region`        | 7         |
| `destinos_destino`       | 9         |
| `destinos_actividad`     | 28        |
| `gastronomia_tipoplato`  | 5         |
| `gastronomia_plato`      | 9         |
| `gastronomia_ingrediente`| 56        |

## 7. Migraciones

```bash
# Generar migraciones (si se modifican los modelos)
python manage.py makemigrations

# Aplicar migraciones (crea las tablas en la BD)
python manage.py migrate

# Verificar estado de migraciones
python manage.py showmigrations
```

## 8. Cargar datos desde JSON (solo primera vez)

Los datos originales están en archivos JSON (evidencia de la Sumativa 1).
Para migrarlos a la base de datos:

```bash
python manage.py cargar_destinos
python manage.py cargar_gastronomia
```

> Estos comandos **no son destructivos**: si los registros ya existen, los omiten.
> Para recrear desde cero: `python manage.py cargar_destinos --force`

## 9. Crear superusuario

```bash
python manage.py createsuperuser
```

Seguir las instrucciones (nombre de usuario, email, contraseña).
Las credenciales **no** se almacenan en el repositorio.

## 10. Ejecutar el proyecto

```bash
python manage.py runserver
```

Abrir <http://127.0.0.1:8000/>

### Rutas principales

| Ruta                          | Descripción                    |
| ----------------------------- | ------------------------------ |
| `/`                           | Inicio                         |
| `/destinos/`                  | Lista de destinos              |
| `/destinos/<slug>/`           | Detalle de un destino          |
| `/gastronomia/`               | Lista de platos                |
| `/gastronomia/<slug>/`        | Detalle de un plato            |
| `/destinos/agregar/`          | Placeholder CRUD (agregar)     |
| `/destinos/modificar/`        | Placeholder CRUD (modificar)   |
| `/destinos/eliminar/`         | Placeholder CRUD (eliminar)    |
| `/gastronomia/agregar/`       | Placeholder CRUD (agregar)     |
| `/gastronomia/modificar/`     | Placeholder CRUD (modificar)   |
| `/gastronomia/eliminar/`      | Placeholder CRUD (eliminar)    |
| `/admin/`                     | Django Admin                   |
| `/destinos/inexistente/`      | Página 404 amigable            |

## 11. Django Admin

Acceder a <http://127.0.0.1:8000/admin/> con el superusuario creado.

### Entidades administrables

| App           | Modelo        | Funciones Admin                                        |
| ------------- | ------------- | ------------------------------------------------------ |
| `destinos`    | `Categoria`   | Crear, listar, buscar                                  |
| `destinos`    | `Region`      | Crear, listar, buscar                                  |
| `destinos`    | `Destino`     | CRUD completo, filtros, búsqueda, inline de actividades|
| `destinos`    | `Actividad`   | CRUD completo, filtros, búsqueda                       |
| `gastronomia` | `TipoPlato`   | Crear, listar, buscar                                  |
| `gastronomia` | `Plato`       | CRUD completo, filtros, búsqueda, inline de ingredientes|
| `gastronomia` | `Ingrediente` | CRUD completo, filtros, búsqueda                       |

### Funcionalidades del Admin

- **Crear**: formularios con validación y `prepopulated_fields` para slug.
- **Visualizar**: listas con `list_display` y `list_filter`.
- **Modificar**: edición inline de actividades/ingredientes.
- **Eliminar**: con confirmación nativa de Django.
- **Buscar**: `search_fields` en todos los modelos.
- **Navegar**: relaciones FK navegables desde cada modelo.

## 12. Estructura del proyecto

```text
chile_explorer/
│
├── manage.py
├── requirements.txt
├── .env                      # Variables de entorno (NO se versiona)
├── .env.example              # Plantilla de variables de entorno
├── .gitignore
├── README.md
│
├── chile_explorer/           # Proyecto principal
│   ├── settings.py           # Configuración con variables de entorno
│   ├── urls.py               # URLs raíz (admin + apps)
│   ├── asgi.py
│   └── wsgi.py
│
├── destinos/                 # Aplicación 1
│   ├── models.py             # Categoria, Region, Destino, Actividad
│   ├── admin.py              # Registro en Django Admin
│   ├── views.py              # Views con Django ORM
│   ├── urls.py               # URLs con app_name
│   ├── tests.py              # Tests
│   ├── migrations/           # Migraciones
│   ├── management/commands/  # cargar_destinos.py
│   ├── data/destinos.json    # Datos originales (Sumativa 1)
│   ├── templates/destinos/   # inicio, lista, detalle
│   └── static/destinos/      # Imágenes
│
├── gastronomia/              # Aplicación 2
│   ├── models.py             # TipoPlato, Plato, Ingrediente
│   ├── admin.py              # Registro en Django Admin
│   ├── views.py              # Views con Django ORM
│   ├── urls.py               # URLs con app_name
│   ├── tests.py              # Tests
│   ├── migrations/           # Migraciones
│   ├── management/commands/  # cargar_gastronomia.py
│   ├── data/gastronomia.json # Datos originales (Sumativa 1)
│   ├── templates/gastronomia/
│   └── static/gastronomia/   # Imágenes
│
├── templates/                # Templates compartidos
│   ├── base.html             # Plantilla base (herencia)
│   ├── 404.html              # Error 404 amigable
│   └── crud_pendiente.html   # Placeholder CRUD
│
├── static/                   # Estáticos globales
│   ├── bootstrap/            # Bootstrap 5.3 local
│   ├── css/custom.css
│   └── js/custom.js
│
├── docs/                     # Documentación
│   ├── AUDITORIA.md          # Auditoría previa
│   ├── AI-EVIDENCE.md        # Evidencia de IA
│   └── DESPLIEGUE_EC2.md     # Guía de despliegue AWS
│
├── Dockerfile                # Imagen Docker (opcional)
└── docker-compose.yml        # Orquestación local (opcional)
```

## 13. Despliegue en EC2

Guía completa en [`docs/DESPLIEGUE_EC2.md`](docs/DESPLIEGUE_EC2.md).

Resumen:

```bash
# En la instancia EC2 (Amazon Linux / Ubuntu)
sudo apt update && sudo apt install -y python3 python3-venv python3-pip git mysql-server

git clone URL_DEL_REPOSITORIO
cd chile_explorer
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configurar .env con MySQL
cp .env.example .env
# Editar .env con credenciales de MySQL

python manage.py migrate
python manage.py cargar_destinos
python manage.py cargar_gastronomia
python manage.py createsuperuser
python manage.py collectstatic --noinput
python manage.py runserver 0.0.0.0:8000
```

## 14. Validación del proyecto

```bash
# Verificar configuración
python manage.py check

# Verificar migraciones pendientes
python manage.py makemigrations --check

# Ejecutar tests
python manage.py test
```

Resultado esperado: `System check identified no issues (0 silenced).` y todos los tests en verde.

## 15. Botones CRUD del frontend

Cada vista de listado muestra visualmente:

```
[ + Agregar ]  [ ✏ Modificar ]  [ 🗑 Eliminar ]  [ 🔍 Buscar ]
```

- Están presentes y enlazan a rutas placeholder.
- El CRUD **funcional** se realiza mediante **Django Admin** (`/admin/`).
- El CRUD frontend funcional se implementará en la Evaluación Sumativa 3.

## 16. Créditos de imágenes

Las fotografías son de **Wikimedia Commons** (Creative Commons y dominio público),
almacenadas localmente. Créditos detallados en la versión original del README
(Sumativa 1) y en `capturas/`.

## 17. Documentación adicional

| Documento                   | Contenido                              |
| --------------------------- | -------------------------------------- |
| `docs/AUDITORIA.md`         | Auditoría técnica previa a la implementación |
| `docs/AI-EVIDENCE.md`       | Evidencia del uso de IA generativa     |
| `docs/DESPLIEGUE_EC2.md`    | Guía paso a paso para AWS EC2          |
| `DOCUMENTACION_IA.md`       | Evidencia IA de la Sumativa 1          |

---

**Chile Explorer** · Evaluación Sumativa 2 · Django + ORM + BD + Admin + AWS
