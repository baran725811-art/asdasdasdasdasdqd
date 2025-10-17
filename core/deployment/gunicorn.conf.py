# deployment/gunicorn.conf.py
import multiprocessing

# Bağlantı ayarları
bind = "unix:/run/gunicorn.sock"  # Unix socket kullanıyoruz
backlog = 2048  # Bağlantı kuyruğu

# İşçi süreçleri
workers = multiprocessing.cpu_count() * 2 + 1  # CPU sayısına göre işçi sayısı
worker_class = 'sync'  # Senkron işçi tipi
worker_connections = 1000  # İşçi başına maksimum bağlantı
timeout = 30  # İstek zaman aşımı (saniye)
keepalive = 2  # Keep-alive bağlantı süresi

# Process naming
proc_name = 'baran_anahtarci'
pythonpath = '/var/www/baran_anahtarci'

# Logging
accesslog = '/var/log/gunicorn/access.log'
errorlog = '/var/log/gunicorn/error.log'
loglevel = 'info'

# SSL/TLS ayarları
keyfile = None
certfile = None

# Django'nun WSGI uygulamasını yükle
wsgi_app = 'core.wsgi:application'