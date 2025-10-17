import os
import requests
from pathlib import Path

def download_file(url, path):
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'wb') as f:
            f.write(response.content)
        print(f"✅ {path} indirildi")
        return True
    except Exception as e:
        print(f"❌ {path} indirilemedi: {e}")
        return False

# Klasörleri oluştur
vendor_dirs = [
    "static/vendor/bootstrap/css",
    "static/vendor/bootstrap/js", 
    "static/vendor/fontawesome/css",
    "static/vendor/fontawesome/webfonts",
    "static/vendor/jquery"
]

for dir_path in vendor_dirs:
    Path(dir_path).mkdir(parents=True, exist_ok=True)

print("📁 Vendor klasörleri oluşturuldu...")

# İndirilecek dosyalar
downloads = [
    # Bootstrap
    {
        "url": "https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css",
        "path": "static/vendor/bootstrap/css/bootstrap.min.css"
    },
    {
        "url": "https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js", 
        "path": "static/vendor/bootstrap/js/bootstrap.bundle.min.js"
    },
    
    # jQuery
    {
        "url": "https://code.jquery.com/jquery-3.6.0.min.js",
        "path": "static/vendor/jquery/jquery.min.js"
    },
    
    # Font Awesome CSS
    {
        "url": "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css",
        "path": "static/vendor/fontawesome/css/all.min.css"
    },
    
    # Font Awesome Fonts
    {
        "url": "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/webfonts/fa-solid-900.woff2",
        "path": "static/vendor/fontawesome/webfonts/fa-solid-900.woff2"
    },
    {
        "url": "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/webfonts/fa-regular-400.woff2",
        "path": "static/vendor/fontawesome/webfonts/fa-regular-400.woff2"
    },
    {
        "url": "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/webfonts/fa-brands-400.woff2",
        "path": "static/vendor/fontawesome/webfonts/fa-brands-400.woff2"
    }
]

print("📥 Dosyalar indiriliyor...")
success_count = 0

for item in downloads:
    if download_file(item["url"], item["path"]):
        success_count += 1

print(f"\n🎉 {success_count}/{len(downloads)} dosya başarıyla indirildi!")
print("📝 Şimdi template dosyalarını güncelleyebilirsiniz.")