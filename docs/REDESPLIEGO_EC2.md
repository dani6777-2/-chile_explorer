# PROMPT PARA REDESPLEGAR CHILE EXPLORER EN UNA EC2 NUEVA

> Copia y pega este prompt en una sesión de IA (opencode / ChatGPT / etc.)
> con los datos de tu nueva instancia EC2, o ejecuta el script automático.

---

## OPCIÓN A — Script automático (recomendada)

Desde tu máquina local, con la nueva `.pem` descargada:

```bash
cd /Users/dani/Documents/chile_explorer
chmod +x desplegar_ec2.sh
./desplegar_ec2.sh NUEVA_CLAVE.pem ec2-user@NUEVO_DNS.compute-1.amazonaws.com
```

El script hace **todo** automáticamente:
1. Conexión SSH
2. Instala git, Python 3.12, MariaDB 10.11, PHP 8.1, nginx, phpMyAdmin
3. Clona el repo desde GitHub
4. Crea venv + instala requirements
5. Configura BD MySQL + usuario
6. Crea `.env` con SECRET_KEY automática
7. Ejecuta migrate + carga datos JSON + crea superusuario
8. Configura nginx (Django + phpMyAdmin + estáticos)
9. Crea servicio systemd para Django
10. Verifica todas las rutas

**Tiempo estimado: 5-8 minutos.**

---

## OPCIÓN B — Prompt para IA

Copia esto en tu asistente de IA:

```
Actúa como ingeniero DevOps especializado en AWS EC2 y Django.
Necesito redesplegar el proyecto "Chile Explorer" en una instancia EC2 nueva.

DATOS DE LA NUEVA INSTANCIA:
- PEM: [nombre-del-archivo].pem  (ya está en mi directorio de trabajo)
- Usuario: ec2-user
- DNS/IP: [IP_O_DNS_DE_LA_INSTANCIA]
- SO: Amazon Linux 2023

REPOSITORIO:
- https://github.com/dani6777-2/-chile_explorer.git

CONTRASEÑAS A USAR:
- MySQL user: chile_explorer_user
- MySQL pass: ChileExplorerDemo2026!
- BD: chile_explorer
- Admin Django: admin / ChileExplorer2026!

DESPLEGAR ESTA ARQUITECTURA:
1. Instalar: git, python3.12, python3.12-venv, MariaDB 10.11 (repo oficial),
   PHP 8.1 + php-fpm + php-mysqlnd, nginx, phpMyAdmin 5.2.2
2. Clonar el repo en /home/ec2-user/chile_explorer
3. Crear venv con python3.12 e instalar requirements.txt
4. Crear BD chile_explorer + usuario chile_explorer_user en MariaDB
5. Crear .env con DB_ENGINE=mysql, las credenciales MySQL, DEBUG=False,
   ALLOWED_HOSTS con la IP y DNS públicos de la instancia
6. python manage.py migrate
7. python manage.py cargar_destinos && python manage.py cargar_gastronomia
8. Crear superusuario admin con password ChileExplorer2026!
9. Configurar nginx como proxy inverso:
   - /static/ → archivos locales del proyecto
   - /phpmyadmin/ → PHP-FPM → /usr/share/phpmyadmin
   - / → proxy_pass http://127.0.0.1:8000 (Django)
10. Crear servicio systemd chile_explorer para Django (puerto 8000)
11. Activar y verificar: mariadb, php-fpm, nginx, chile_explorer
12. Probar HTTP en puerto 80: /, /destinos/, /gastronomia/, /admin/, /phpmyadmin/

Al finalizar, muestra:
- IP y DNS de la instancia
- URLs de acceso
- Credenciales
- Estado de cada servicio
- Resultado de cada ruta HTTP probada
```

---

## OPCIÓN C — Checklist manual paso a paso

Si prefieres hacerlo tú mismo, sigue esta secuencia exacta por SSH:

### Paso 1 — Conectar

```bash
chmod 400 NUEVA_CLAVE.pem
ssh -i NUEVA_CLAVE.pem ec2-user@IP_O_DNS
```

### Paso 2 — Instalar dependencias

```bash
sudo dnf install -y git python3.12 python3.12-pip python3.12-devel \
  php8.1 php8.1-fpm php8.1-mysqlnd php8.1-mbstring php8.1-gd php8.1-xml \
  nginx curl tar gzip

# MariaDB 10.11 (repo oficial)
sudo tee /etc/yum.repos.d/mariadb.repo > /dev/null << 'EOF'
[mariadb]
name = MariaDB Server
baseurl = https://dlm.mariadb.com/repo/mariadb-server/10.11/yum/rhel/9/x86_64/
module_hotfixes = 1
gpgcheck = 0
EOF
sudo dnf install -y --nogpgcheck MariaDB-server MariaDB-client
```

### Paso 3 — Clonar proyecto

```bash
cd /home/ec2-user
git clone https://github.com/dani6777-2/-chile_explorer.git
cd chile_explorer
# Si se clonó con nombre "-chile_explorer":
# mv -- '-chile_explorer' chile_explorer
```

### Paso 4 — Entorno virtual

```bash
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Paso 5 — MariaDB

```bash
sudo systemctl enable mariadb && sudo systemctl start mariadb
sudo mariadb << 'SQL'
CREATE DATABASE chile_explorer CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'chile_explorer_user'@'localhost' IDENTIFIED BY 'ChileExplorerDemo2026!';
GRANT ALL PRIVILEGES ON chile_explorer.* TO 'chile_explorer_user'@'localhost';
FLUSH PRIVILEGES;
SQL
```

### Paso 6 — .env

```bash
cd /home/ec2-user/chile_explorer
SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
cat > .env << EOF
SECRET_KEY=${SECRET_KEY}
DEBUG=False
ALLOWED_HOSTS=_,localhost,127.0.0.1,TU_IP_PUBLICA

DB_ENGINE=django.db.backends.mysql
DB_NAME=chile_explorer
DB_USER=chile_explorer_user
DB_PASSWORD=ChileExplorerDemo2026!
DB_HOST=127.0.0.1
DB_PORT=3306
EOF
chmod 600 .env
```

### Paso 7 — Migrar y cargar datos

```bash
source venv/bin/activate
python manage.py migrate
python manage.py cargar_destinos
python manage.py cargar_gastronomia
DJANGO_SUPERUSER_USERNAME=admin \
DJANGO_SUPERUSER_EMAIL=admin@chile-explorer.cl \
DJANGO_SUPERUSER_PASSWORD=ChileExplorer2026! \
python manage.py createsuperuser --noinput
```

### Paso 8 — phpMyAdmin

```bash
cd /tmp
curl -sL https://files.phpmyadmin.net/phpMyAdmin/5.2.2/phpMyAdmin-5.2.2-all-languages.tar.gz -o pma.tar.gz
tar xzf pma.tar.gz
sudo mv phpMyAdmin-5.2.2-all-languages /usr/share/phpmyadmin

sudo tee /usr/share/phpmyadmin/config.inc.php > /dev/null << 'EOF'
<?php
declare(strict_types=1);
$cfg['blowfish_secret'] = 'ChileExplorerDemo2026SecretKeyXX';
$i = 1;
$cfg['Servers'][$i]['host'] = 'localhost';
$cfg['Servers'][$i]['port'] = '3306';
$cfg['Servers'][$i]['socket'] = '/var/lib/mysql/mysql.sock';
$cfg['Servers'][$i]['auth_type'] = 'cookie';
$cfg['Servers'][$i]['AllowNoPassword'] = true;
$cfg['Servers'][$i]['AllowRoot'] = true;
$cfg['DefaultLang'] = 'es';
$cfg['CheckConfigurationPassword'] = false;
EOF
sudo chown nginx:nginx /usr/share/phpmyadmin/config.inc.php
```

### Paso 9 — PHP-FPM + Nginx

```bash
# php-fpm
sudo tee /etc/php-fpm.d/www.conf > /dev/null << 'EOF'
[www]
user = nginx
group = nginx
listen = /run/php-fpm/www.sock
listen.owner = nginx
listen.group = nginx
listen.mode = 0660
pm = dynamic
pm.max_children = 5
pm.start_servers = 2
pm.min_spare_servers = 1
pm.max_spare_servers = 3
pm.max_requests = 500
catch_workers_output = yes
EOF
sudo systemctl enable php-fpm && sudo systemctl restart php-fpm

# nginx (reemplaza TU_IP con la IP pública real)
sudo tee /etc/nginx/conf.d/chile_explorer.conf > /dev/null << 'EOF'
server {
    listen 80;
    server_name _;
    client_max_body_size 20M;

    location /static/ {
        alias /home/ec2-user/chile_explorer/static/;
        expires 7d;
        add_header Cache-Control public;
    }

    location /phpmyadmin/ {
        alias /usr/share/phpmyadmin/;
        index index.php;
        location ~ ^/phpmyadmin/(.+\.php)$ {
            alias /usr/share/phpmyadmin/$1;
            fastcgi_pass unix:/run/php-fpm/www.sock;
            fastcgi_index index.php;
            fastcgi_param SCRIPT_FILENAME /usr/share/phpmyadmin/$1;
            include fastcgi_params;
        }
        location ~* ^/phpmyadmin/(.+\.(jpg|jpeg|gif|css|png|js|ico|svg|woff|woff2))$ {
            alias /usr/share/phpmyadmin/$1;
            expires 30d;
        }
    }
    location = /phpmyadmin { return 301 /phpmyadmin/; }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# Permisos estáticos
chmod o+x /home/ec2-user
chmod -R o+rX /home/ec2-user/chile_explorer/static
cp -r /home/ec2-user/chile_explorer/destinos/static/destinos /home/ec2-user/chile_explorer/static/ 2>/dev/null || true
cp -r /home/ec2-user/chile_explorer/gastronomia/static/gastronomia /home/ec2-user/chile_explorer/static/ 2>/dev/null || true
chmod -R o+rX /home/ec2-user/chile_explorer/static

sudo nginx -t && sudo systemctl enable nginx && sudo systemctl reload nginx
```

### Paso 10 — Servicio systemd Django

```bash
sudo tee /etc/systemd/system/chile_explorer.service > /dev/null << 'EOF'
[Unit]
Description=Chile Explorer Django
After=network.target mariadb.service

[Service]
User=ec2-user
Group=ec2-user
WorkingDirectory=/home/ec2-user/chile_explorer
ExecStart=/home/ec2-user/chile_explorer/venv/bin/python manage.py runserver 127.0.0.1:8000
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
sudo systemctl daemon-reload
sudo systemctl enable chile_explorer
sudo systemctl restart chile_explorer
```

### Paso 11 — Verificar

```bash
# Servicios
sudo systemctl is-active mariadb php-fpm nginx chile_explorer

# Rutas internas
curl -s -o /dev/null -w "%{http_code} /\n" http://127.0.0.1/
curl -s -o /dev/null -w "%{http_code} /destinos/\n" http://127.0.0.1/destinos/
curl -s -o /dev/null -w "%{http_code} /gastronomia/\n" http://127.0.0.1/gastronomia/
curl -s -o /dev/null -w "%{http_code} /admin/\n" http://127.0.0.1/admin/
curl -s -o /dev/null -w "%{http_code} /phpmyadmin/\n" http://127.0.0.1/phpmyadmin/
```

---

## Datos para la demo (siempre los mismos)

| Elemento | Valor |
| -------- | ----- |
| Sitio | `http://IP_PUBLICA/` |
| Django Admin | `http://IP_PUBLICA/admin/` |
| Usuario admin | `admin` |
| Password admin | `ChileExplorer2026!` |
| phpMyAdmin | `http://IP_PUBLICA/phpmyadmin/` |
| Usuario MySQL | `chile_explorer_user` |
| Password MySQL | `ChileExplorerDemo2026!` |
| Base de datos | `chile_explorer` |

---

## Security Group (puertos que deben estar abiertos)

| Puerto | Protocolo | Origen | Motivo |
| ------ | --------- | ------ | ------ |
| 22 | TCP | Tu IP | SSH |
| 80 | TCP | 0.0.0.0/0 | HTTP (nginx → Django + phpMyAdmin) |

> El puerto 8000 **no** necesita estar abierto: nginx hace de proxy inverso.
