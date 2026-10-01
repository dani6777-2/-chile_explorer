#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════
#  Chile Explorer — Despliegue automático en AWS EC2
#  Uso: ./desplegar_ec2.sh ruta/al/archivo.pem usuario@dns-o-ip
#  Ejemplo: ./desplegar_ec2.sh eva_2.pem ec2-user@ec2-xx-xx-xx-xx.compute-1.amazonaws.com
# ═══════════════════════════════════════════════════════════════════
set -euo pipefail

# ── Colores ─────────────────────────────────────────────────────────
ROJO='\033[0;31m'; VERDE='\033[0;32m'; AMARILLO='\033[1;33m'; AZUL='\033[0;34m'; NC='\033[0m'
log()    { echo -e "${AZUL}[INFO]${NC} $1"; }
ok()     { echo -e "${VERDE}[OK]${NC} $1"; }
warn()   { echo -e "${AMARILLO}[AVISO]${NC} $1"; }
error()  { echo -e "${ROJO}[ERROR]${NC} $1"; exit 1; }

# ── Parámetros ──────────────────────────────────────────────────────
PEM="${1:-}"
DESTINO="${2:-}"
if [[ -z "$PEM" || -z "$DESTINO" ]]; then
  echo "Uso: $0 <ruta-pem> <usuario@dns-o-ip>"
  echo "Ej:  $0 eva_2.pem ec2-user@ec2-54-166-237-129.compute-1.amazonaws.com"
  exit 1
fi
[[ -f "$PEM" ]] || error "No existe el archivo PEM: $PEM"
chmod 400 "$PEM"

REPO="https://github.com/dani6777-2/-chile_explorer.git"
DIR_APP="chile_explorer"
PASS_MYSQL="ChileExplorerDemo2026!"
PASS_ADMIN="ChileExplorer2026!"
USUARIO_APP="chile_explorer_user"
BD="chile_explorer"
SSH_OPTS="-i $PEM -o StrictHostKeyChecking=accept-new -o ConnectTimeout=15"

# Función remota: ejecuta comando en la EC2
run() { ssh $SSH_OPTS "$DESTINO" "$@"; }

# Función remota: ejecuta como root
run_sudo() { ssh $SSH_OPTS "$DESTINO" "sudo bash -s" <<< "$1"; }

echo "════════════════════════════════════════════════════════════"
echo "  CHILE EXPLORER — DESPLIEGUE AUTOMÁTICO EN AWS EC2"
echo "  Destino: $DESTINO"
echo "  PEM:     $PEM"
echo "════════════════════════════════════════════════════════════"
echo ""

# ── 1. Verificar conexión ──────────────────────────────────────────
log "Verificando conexión SSH..."
run "echo CONEXION_OK && uname -m && cat /etc/os-release | grep '^VERSION=' | head -1" \
  || error "No se pudo conectar a $DESTINO. Verifica el PEM y el DNS."
ok "Conexión establecida"
echo ""

# ── 2. Instalar dependencias del sistema ───────────────────────────
log "Instalando dependencias del sistema (git, Python 3.12, MariaDB 10.11, PHP, nginx)..."
run_sudo '
set -e
dnf install -y git python3.12 python3.12-pip python3.12-devel \
  php8.1 php8.1-fpm php8.1-mysqlnd php8.1-mbstring php8.1-gd php8.1-xml \
  nginx curl tar gzip >/dev/null 2>&1
echo "  Paquetes base: OK"
' || error "Fallo al instalar paquetes base"

# MariaDB 10.11 desde repo oficial
run_sudo '
set -e
tee /etc/yum.repos.d/mariadb.repo > /dev/null << REPO
[mariadb]
name = MariaDB Server
baseurl = https://dlm.mariadb.com/repo/mariadb-server/10.11/yum/rhel/9/x86_64/
module_hotfixes = 1
gpgcheck = 0
REPO
dnf makecache -y >/dev/null 2>&1
if ! mariadb --version 2>/dev/null | grep -q "10.11"; then
  dnf install -y --nogpgcheck MariaDB-server MariaDB-client >/dev/null 2>&1
fi
echo "  MariaDB: $(mariadb --version 2>/dev/null | head -1)"
' || error "Fallo al instalar MariaDB 10.11"

python3.12 --version
ok "Dependencias del sistema instaladas"
echo ""

# ── 3. Clonar repositorio ──────────────────────────────────────────
log "Clonando repositorio..."
run "
if [ -d /home/ec2-user/$DIR_APP ]; then
  cd /home/ec2-user/$DIR_APP && git pull origin main >/dev/null 2>&1
  echo '  Repo actualizado'
else
  cd /home/ec2-user
  git clone $REPO 2>/dev/null
  # El repo puede clonarse con nombre con guion inicial
  if [ -d '-$DIR_APP' ]; then mv -- '-$DIR_APP' $DIR_APP; fi
  if [ -d '$DIR_APP' ]; then echo '  Repo clonado'; fi
fi
ls /home/ec2-user/$DIR_APP/manage.py >/dev/null 2>&1 || echo 'ERROR: no se encontro manage.py'
" || error "Fallo al clonar el repositorio"
ok "Repositorio listo en /home/ec2-user/$DIR_APP"
echo ""

# ── 4. Entorno virtual + dependencias Python ───────────────────────
log "Creando entorno virtual e instalando dependencias..."
run "
cd /home/ec2-user/$DIR_APP
if [ ! -d venv ]; then
  python3.12 -m venv venv
fi
source venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q
python --version
pip show Django | grep Version
" || error "Fallo al crear venv o instalar requirements"
ok "Entorno virtual listo"
echo ""

# ── 5. Configurar MariaDB ──────────────────────────────────────────
log "Configurando MariaDB (BD + usuario)..."
run_sudo "
systemctl enable mariadb >/dev/null 2>&1
systemctl start mariadb
sleep 3
mariadb << SQL
CREATE DATABASE IF NOT EXISTS $BD CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS '$USUARIO_APP'@'localhost' IDENTIFIED BY '$PASS_MYSQL';
GRANT ALL PRIVILEGES ON $BD.* TO '$USUARIO_APP'@'localhost';
FLUSH PRIVILEGES;
SQL
echo '  BD y usuario MySQL: OK'
mariadb -e \"SELECT VERSION();\" 2>/dev/null | head -2
" || error "Fallo al configurar MariaDB"
ok "MariaDB configurado"
echo ""

# ── 6. Configurar .env ─────────────────────────────────────────────
log "Creando archivo .env..."
run "
cd /home/ec2-user/$DIR_APP
SECRET_KEY=\$(python3.12 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
cat > .env << EOF
SECRET_KEY=\${SECRET_KEY}
DEBUG=False
ALLOWED_HOSTS=_,localhost,127.0.0.1,\$(hostname -f 2>/dev/null || true),\$(curl -s http://169.254.169.254/latest/meta-data/public-hostname 2>/dev/null || true),\$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || true)

DB_ENGINE=django.db.backends.mysql
DB_NAME=$BD
DB_USER=$USUARIO_APP
DB_PASSWORD=$PASS_MYSQL
DB_HOST=127.0.0.1
DB_PORT=3306
EOF
chmod 600 .env
echo '  .env creado (SECRET_KEY generada automáticamente)'
" || error "Fallo al crear .env"
ok ".env configurado"
echo ""

# ── 7. Migraciones + carga de datos + superusuario ─────────────────
log "Ejecutando migraciones y cargando datos en MySQL..."
run "
cd /home/ec2-user/$DIR_APP
source venv/bin/activate
python manage.py migrate 2>&1 | tail -3
python manage.py cargar_destinos 2>&1 | tail -1
python manage.py cargar_gastronomia 2>&1 | tail -1
DJANGO_SUPERUSER_USERNAME=admin \
DJANGO_SUPERUSER_EMAIL=admin@chile-explorer.cl \
DJANGO_SUPERUSER_PASSWORD=$PASS_ADMIN \
python manage.py createsuperuser --noinput 2>&1 || echo '  Superusuario ya existia'
python manage.py check 2>&1
" || error "Fallo en migrate o carga de datos"
ok "Datos migrados a MySQL"
echo ""

# ── 8. phpMyAdmin ──────────────────────────────────────────────────
log "Instalando phpMyAdmin..."
run_sudo "
if [ ! -d /usr/share/phpmyadmin ]; then
  cd /tmp
  curl -sL https://files.phpmyadmin.net/phpMyAdmin/5.2.2/phpMyAdmin-5.2.2-all-languages.tar.gz -o pma.tar.gz
  tar xzf pma.tar.gz
  mv phpMyAdmin-5.2.2-all-languages /usr/share/phpmyadmin
  rm -f pma.tar.gz
fi
cat > /usr/share/phpmyadmin/config.inc.php << PMACONF
<?php
declare(strict_types=1);
\$cfg['blowfish_secret'] = 'ChileExplorerDemo2026SecretKeyXX';
\$i = 1;
\$cfg['Servers'][\$i]['host'] = 'localhost';
\$cfg['Servers'][\$i]['port'] = '3306';
\$cfg['Servers'][\$i]['socket'] = '/var/lib/mysql/mysql.sock';
\$cfg['Servers'][\$i]['user'] = 'root';
\$cfg['Servers'][\$i]['password'] = '';
\$cfg['Servers'][\$i]['auth_type'] = 'cookie';
\$cfg['Servers'][\$i]['AllowNoPassword'] = true;
\$cfg['Servers'][\$i]['compress'] = false;
\$cfg['Servers'][\$i]['AllowRoot'] = true;
\$cfg['UploadDir'] = '';
\$cfg['SaveDir'] = '';
\$cfg['DefaultLang'] = 'es';
\$cfg['CheckConfigurationPassword'] = false;
PMACONF
chown nginx:nginx /usr/share/phpmyadmin/config.inc.php
chmod 644 /usr/share/phpmyadmin/config.inc.php
echo '  phpMyAdmin instalado'
" || error "Fallo al instalar phpMyAdmin"
ok "phpMyAdmin listo"
echo ""

# ── 9. php-fpm + nginx ─────────────────────────────────────────────
log "Configurando PHP-FPM y Nginx..."
PUBLIC_HOST=$(curl -s http://169.254.169.254/latest/meta-data/public-hostname 2>/dev/null || echo "_")
PUBLIC_IP=$(curl -s http://169.254.169.237-129.compute-1.amazonaws.com 2>/dev/null || curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo "_")

run_sudo "
# php-fpm pool
cat > /etc/php-fpm.d/www.conf << FPMCONF
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
FPMCONF
systemctl enable php-fpm >/dev/null 2>&1
systemctl restart php-fpm

# nginx: Django + phpMyAdmin + estáticos
cat > /etc/nginx/conf.d/chile_explorer.conf << NGINXCONF
server {
    listen 80;
    server_name $PUBLIC_HOST $PUBLIC_IP _;

    client_max_body_size 20M;

    location /static/ {
        alias /home/ec2-user/$DIR_APP/static/;
        expires 7d;
        add_header Cache-Control public;
    }

    location /phpmyadmin/ {
        alias /usr/share/phpmyadmin/;
        index index.php;

        location ~ ^/phpmyadmin/(.+\\.php)\\\$ {
            alias /usr/share/phpmyadmin/\\\$1;
            fastcgi_pass unix:/run/php-fpm/www.sock;
            fastcgi_index index.php;
            fastcgi_param SCRIPT_FILENAME /usr/share/phpmyadmin/\\\$1;
            include fastcgi_params;
        }

        location ~* ^/phpmyadmin/(.+\\.(jpg|jpeg|gif|css|png|js|ico|svg|woff|woff2|map))\\\$ {
            alias /usr/share/phpmyadmin/\\\$1;
            expires 30d;
            add_header Cache-Control public;
        }
    }

    location = /phpmyadmin {
        return 301 /phpmyadmin/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \\\$host;
        proxy_set_header X-Real-IP \\\$remote_addr;
        proxy_set_header X-Forwarded-For \\\$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \\\$scheme;
        proxy_read_timeout 60;
    }
}
NGINXCONF

# Permisos para nginx
chmod o+x /home/ec2-user
chmod -R o+rX /home/ec2-user/$DIR_APP/static
cp -r /home/ec2-user/$DIR_APP/destinos/static/destinos /home/ec2-user/$DIR_APP/static/ 2>/dev/null || true
cp -r /home/ec2-user/$DIR_APP/gastronomia/static/gastronomia /home/ec2-user/$DIR_APP/static/ 2>/dev/null || true
chmod -R o+rX /home/ec2-user/$DIR_APP/static

nginx -t 2>&1
systemctl enable nginx >/dev/null 2>&1
systemctl reload nginx
echo '  Nginx configurado'
" || error "Fallo al configurar php-fpm o nginx"
ok "php-fpm + Nginx configurados"
echo ""

# ── 10. Servicio systemd para Django ───────────────────────────────
log "Configurando servicio systemd para Django..."
run_sudo "
cat > /etc/systemd/system/chile_explorer.service << SVCCONF
[Unit]
Description=Chile Explorer Django
After=network.target mariadb.service

[Service]
User=ec2-user
Group=ec2-user
WorkingDirectory=/home/ec2-user/$DIR_APP
ExecStart=/home/ec2-user/$DIR_APP/venv/bin/python manage.py runserver 127.0.0.1:8000
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
SVCCONF
systemctl daemon-reload
systemctl enable chile_explorer >/dev/null 2>&1
systemctl restart chile_explorer
sleep 3
systemctl is-active chile_explorer
" || error "Fallo al configurar servicio systemd"
ok "Servicio Django activo"
echo ""

# ── 11. Verificación final ─────────────────────────────────────────
log "Verificando despliegue..."
sleep 2

# IP pública y DNS
EC2_IP=$(run "curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null" || echo "desconocida")
EC2_DNS=$(run "curl -s http://169.254.169.254/latest/meta-data/public-hostname 2>/dev/null" || echo "desconocida")
URL_BASE="http://${EC2_IP}"

echo ""
echo "════════════════════════════════════════════════════════════"
echo "  VERIFICACIÓN DE RUTAS"
echo "════════════════════════════════════════════════════════════"
for ruta in "/" "/destinos/" "/gastronomia/" "/admin/" "/phpmyadmin/"; do
  code=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 10 "${URL_BASE}${ruta}" 2>/dev/null || echo "000")
  if [[ "$code" == "200" || "$code" == "302" ]]; then
    ok "  $code  ${URL_BASE}${ruta}"
  else
    warn "  $code  ${URL_BASE}${ruta} (revisar Security Group puerto 80)"
  fi
done

echo ""
echo "════════════════════════════════════════════════════════════"
echo "  RESUMEN DEL DESPLIEGUE"
echo "════════════════════════════════════════════════════════════"
echo "  IP pública:    ${EC2_IP}"
echo "  DNS público:   ${EC2_DNS}"
echo "  Sitio:         ${URL_BASE}/"
echo "  Destinos:      ${URL_BASE}/destinos/"
echo "  Gastronomía:   ${URL_BASE}/gastronomia/"
echo "  Django Admin:  ${URL_BASE}/admin/"
echo "  phpMyAdmin:    ${URL_BASE}/phpmyadmin/"
echo ""
echo "  CREDENCIALES:"
echo "    Admin Django:  admin / $PASS_ADMIN"
echo "    phpMyAdmin:    $USUARIO_APP / $PASS_MYSQL"
echo "    MySQL:         $USUARIO_APP / $PASS_MYSQL (BD: $BD)"
echo ""
echo "  SERVICIOS:"
echo "    Django (systemd)  → chile_explorer"
echo "    Nginx (puerto 80) → nginx"
echo "    MariaDB 10.11     → mariadb"
echo "    PHP-FPM           → php-fpm"
echo "════════════════════════════════════════════════════════════"
echo ""
warn "Si las rutas externas dan timeout/000, abre el puerto 80 en el"
warn "Security Group de la instancia EC2 (AWS Console → EC2 → SG)."
echo ""
ok "Despliegue completado."
