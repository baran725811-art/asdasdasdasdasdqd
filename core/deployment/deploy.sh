#!/bin/bash

# Renk kodları
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

echo -e "${GREEN}Baran Anahtarci deployment başlıyor...${NC}"

# Git değişikliklerini çek
echo "Git değişikliklerini çekiliyor..."
git pull origin main

# Virtual environment'ı aktive et
source venv/bin/activate

# Gereksinimleri yükle
echo "Gereksinimler yükleniyor..."
pip install -r requirements.txt

# Statik dosyaları topla
echo "Statik dosyalar toplanıyor..."
python manage.py collectstatic --noinput

# Veritabanı migrasyonlarını uygula
echo "Veritabanı migrasyonları uygulanıyor..."
python manage.py migrate

# Gunicorn'u yeniden başlat
echo "Gunicorn yeniden başlatılıyor..."
sudo systemctl restart gunicorn

# Nginx'i yeniden başlat
echo "Nginx yeniden başlatılıyor..."
sudo systemctl restart nginx

echo -e "${GREEN}Deployment tamamlandı!${NC}"