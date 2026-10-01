# GUÍA DE DESPLIEGUE EN AWS EC2 — Chile Explorer

> **Estado:** Guía preparada para ejecución. El despliegue **no fue ejecutado**
> desde este entorno de desarrollo (no hay acceso a AWS). Sigue los pasos
> exactos en una instancia EC2 real.

---

## 1. Arquitectura del despliegue

```text
                    ┌─────────────────────────────────────┐
                    │         Amazon EC2 (Linux)          │
                    │                                     │
  Usuario ────────► │  Apache/Nginx ──► Gunicorn ──► Django│
  (navegador)       │                     │                │
                    │                     ▼                │
  phpMyAdmin ──────►│              MySQL/MariaDB           │
  (navegador)       │                     │                │
                    │                     ▼                │
                    │              chile_explorer BD       │
                    │              (tablas, registros)     │
                    └─────────────────────────────────────┘
```

## 2. Requisitos previos en AWS

1. Cuenta de AWS activa.
2. Instancia EC2 con:
   - SO: **Ubuntu 22.04/24.04** o **Amazon Linux 2023**.
   - Tipo: `t2.micro` o superior (suficiente para la demostración).
   - Grupo de seguridad con puertos abiertos:
     - **22** (SSH)
     - **80** (HTTP)
     - **8000** (Django runserver — solo para pruebas)
     - **8080** (phpMyAdmin — opcional, solo demostración)
3. Par de claves SSH (`.pem`) descargado localmente.
4. Repositorio en GitHub con el código del proyecto.

## 3. Conexión a la instancia EC2

```bash
# Desde tu máquina local
chmod 400 mi-clave.pem
ssh -i "mi-clave.pem" ubuntu@IP_PUBLICO_EC2
```

Reemplazar `mi-clave.pem` y `IP_PUBLICO_EC2` por los valores reales.

## 4. Actualizar el sistema e instalar dependencias

```bash
# Ubuntu
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-venv python3-pip git mysql-server nginx

# Amazon Linux 2023
# sudo dnf update -y
# sudo dnf install -y python3 python3-pip git mariadb-server nginx
```

## 5. Clonar el repositorio

```bash
cd /home/ubuntu
git clone https://github.com/USUARIO/chile_explorer.git
cd chile_explorer
```

## 6. Crear y activar el entorno virtual

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## 7. Configurar MySQL/MariaDB

### 7.1. Iniciar y asegurar MySQL

```bash
sudo systemctl start mysql
sudo systemctl enable mysql

# Ubuntu: asistente de instalación segura
sudo mysql_secure_installation
# - Cambiar contraseña de root: SÍ, definir contraseña segura
# - Eliminar usuarios anónimos: SÍ
# - Eliminar base de datos de prueba: SÍ
# - Acceso remoto a root: NO
```

### 7.2. Crear base de datos y usuario

```bash
sudo mysql -u root -p
```

```sql
-- Crear base de datos
CREATE DATABASE chile_explorer CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Crear usuario dedicado
CREATE USER 'chile_explorer_user'@'localhost' IDENTIFIED BY 'TU_PASSWORD_SEGURO';

-- Otorgar permisos
GRANT ALL PRIVILEGES ON chile_explorer.* TO 'chile_explorer_user'@'localhost';
FLUSH PRIVILEGES;

EXIT;
```

> **Importante:** Reemplazar `TU_PASSWORD_SEGURO` por una contraseña fuerte.
> Esta contraseña irá solo en `.env` (nunca en el repositorio).

## 8. Configurar phpMyAdmin (opcional pero recomendado para la demo)

```bash
sudo apt install -y phpmyadmin php-mysql

# Agregar phpMyAdmin a Apache/Nginx
sudo ln -s /etc/phpmyadmin/apache.conf /etc/nginx/sites-available/phpmyadmin
sudo ln -s /etc/nginx/sites-available/phpmyadmin /etc/nginx/sites-enabled/
sudo systemctl reload nginx
```

Acceso: `http://IP_EC2/phpmyadmin/` con el usuario `chile_explorer_user`.

## 9. Configurar variables de entorno

```bash
cd /home/ubuntu/chile_explorer
cp .env.example .env
nano .env
```

Contenido mínimo para EC2:

```env
SECRET_KEY=generar-con-python-c-o-secret-key
DEBUG=False
ALLOWED_HOSTS=IP_PUBLICO_EC2,localhost,127.0.0.1

DB_ENGINE=django.db.backends.mysql
DB_NAME=chile_explorer
DB_USER=chile_explorer_user
DB_PASSWORD=TU_PASSWORD_SEGURO
DB_HOST=127.0.0.1
DB_PORT=3306
```

Generar SECRET_KEY seguro:

```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Pegar el resultado en `.env` junto a `SECRET_KEY=`.

## 10. Aplicar migraciones y cargar datos

```bash
source venv/bin/activate
cd /home/ubuntu/chile_explorer

# Crear tablas
python manage.py migrate

# Cargar datos desde los JSON originales
python manage.py cargar_destinos
python manage.py cargar_gastronomia

# Crear superusuario de Django Admin
python manage.py createsuperuser

# Recopilar archivos estáticos
python manage.py collectstatic --noinput
```

## 11. Probar la aplicación

```bash
python manage.py runserver 0.0.0.0:8000
```

Verificar desde el navegador:

- `http://IP_EC2:8000/` → Inicio
- `http://IP_EC2:8000/destinos/` → Lista de destinos
- `http://IP_EC2:8000/gastronomia/` → Lista de gastronomía
- `http://IP_EC2:8000/admin/` → Django Admin

**Para la demostración**, `runserver` es suficiente. Para producción se recomienda
Gunicorn + Nginx (paso 12).

## 12. (Producción) Gunicorn + Nginx

```bash
pip install gunicorn

# Crear servicio Gunicorn
sudo tee /etc/systemd/system/chile_explorer.service <<EOF
[Unit]
Description=Chile Explorer Django
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/chile_explorer
ExecStart=/home/ubuntu/chile_explorer/venv/bin/gunicorn chile_explorer.wsgi:application
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl start chile_explorer
sudo systemctl enable chile_explorer
```

Configurar Nginx:

```bash
sudo tee /etc/nginx/sites-available/chile_explorer <<EOF
server {
    listen 80;
    server_name IP_PUBLICO_EC2;

    client_max_body_size 20M;

    location /static/ {
        alias /home/ubuntu/chile_explorer/static/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }
}
EOF

sudo ln -s /etc/nginx/sites-available/chile_explorer /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx
```

## 13. Verificar phpMyAdmin

1. Abrir `http://IP_EC2/phpmyadmin/`
2. Login con `chile_explorer_user` / `TU_PASSWORD_SEGURO`
3. Seleccionar base de datos `chile_explorer`
4. Verificar tablas:
   - `destinos_categoria`, `destinos_region`, `destinos_destino`, `destinos_actividad`
   - `gastronomia_tipoplato`, `gastronomia_plato`, `gastronomia_ingrediente`
5. Abrir `destinos_destino` → verificar 9 registros con sus relaciones FK
6. Abrir `gastronomia_plato` → verificar 9 registros

## 14. Checklist de verificación en EC2

- [ ] SSH funciona a la instancia
- [ ] `python3 --version` muestra 3.10+
- [ ] Entorno virtual creado y activado
- [ ] `pip install -r requirements.txt` sin errores
- [ ] MySQL corriendo (`sudo systemctl status mysql`)
- [ ] Base de datos `chile_explorer` creada
- [ ] Usuario MySQL creado con permisos
- [ ] `.env` configurado con MySQL
- [ ] `python manage.py migrate` sin errores
- [ ] `python manage.py cargar_destinos` → 9 destinos
- [ ] `python manage.py cargar_gastronomia` → 9 platos
- [ ] Superusuario creado
- [ ] `http://IP_EC2:8000/` muestra el sitio
- [ ] `http://IP_EC2:8000/destinos/` muestra destinos desde BD
- [ ] `http://IP_EC2:8000/gastronomia/` muestra platos desde BD
- [ ] `http://IP_EC2:8000/admin/` accesible con superusuario
- [ ] Admin muestra las 7 entidades
- [ ] phpMyAdmin muestra las 7 tablas con registros
- [ ] Botones CRUD visibles en el frontend
- [ ] `.env` NO está en el repositorio Git

## 15. Solución de problemas comunes

| Problema | Causa probable | Solución |
| -------- | -------------- | -------- |
| `Access denied for user` | Credenciales MySQL incorrectas | Revisar `.env` y usuarios MySQL |
| `Unknown database` | BD no creada | Ejecutar `CREATE DATABASE` en MySQL |
| `Port already in use` | Puerto 8000 ocupado | Cambiar puerto o terminar proceso |
| `TemplateDoesNotExist` | Static no recopilado | `python manage.py collectstatic --noinput` |
| `DisallowedHost` | ALLOWED_HOSTS incompleto | Agregar IP pública al `.env` |
| phpMyAdmin 403 | Permisos de Nginx | Revisar configuración de phpMyAdmin |

---

**Importante:** Esta guía describe los pasos exactos a ejecutar. El despliegue
debe ser verificado presencialmente durante la demostración de la evaluación.
