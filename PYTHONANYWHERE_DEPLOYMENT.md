# 🐍 PythonAnywhere'de Ücretsiz Django Deployment Rehberi

Bu rehber, Django projenizi PythonAnywhere'de ücretsiz bir şekilde nasıl yayınlayacağınızı adım adım anlatır.

## 📋 İçindekiler
1. [Ön Hazırlık](#ön-hazırlık)
2. [PythonAnywhere Hesabı Oluşturma](#pythonanywhere-hesabı-oluşturma)
3. [Projeyi Upload Etme](#projeyi-upload-etme)
4. [Sanal Ortam (Virtual Environment) Kurulumu](#sanal-ortam-kurulumu)
5. [Web Uygulaması Ayarları](#web-uygulaması-ayarları)
6. [Static Dosyaları Yapılandırma](#static-dosyaları-yapılandırma)
7. [Database Migrate İşlemleri](#database-migrate-i̇şlemleri)
8. [Superuser Oluşturma](#superuser-oluşturma)
9. [Son Kontroller ve Yayınlama](#son-kontroller-ve-yayınlama)
10. [Sorun Giderme](#sorun-giderme)

---

## 🚀 Ön Hazırlık

### Gerekli Değişiklikler (Zaten Yapıldı ✅)
- ✅ PythonAnywhere özel settings dosyası oluşturuldu
- ✅ PythonAnywhere WSGI configuration hazırlandı
- ✅ PythonAnywhere uyumlu requirements.txt hazırlandı

### Dosya Kontrolü
Projenizde şu dosyalar olmalı:
- `core/core/settings/pythonanywhere.py` - PythonAnywhere ayarları
- `core/pythonanywhere_wsgi.py` - WSGI configuration
- `core/requirements_pythonanywhere.txt` - Paket listesi

---

## 📝 1. PythonAnywhere Hesabı Oluşturma

1. **Hesap Oluşturun:**
   - https://www.pythonanywhere.com adresine gidin
   - "Start running Python online in less than a minute!" butonuna tıklayın
   - "Create a Beginner account" seçin (ÜCRETSİZ)
   - Kullanıcı adı, email ve şifre belirleyin
   - **ÖNEMLİ:** Kullanıcı adınızı not edin (örnek: kullaniciadi)

2. **Email Doğrulama:**
   - Email adresinize gelen doğrulama linkine tıklayın

3. **Dashboard'a Giriş:**
   - Giriş yaptıktan sonra Dashboard ekranını göreceksiniz

---

## 📂 2. Projeyi Upload Etme

### Yöntem 1: Git ile (ÖNERİLİR)

1. **Bash Console Açın:**
   - Dashboard'da "Consoles" sekmesine tıklayın
   - "Bash" console başlatın

2. **Projeyi GitHub'dan Klonlayın:**
   ```bash
   cd ~
   git clone https://github.com/baran725811-art/asdasdasdasdasdqd.git
   cd asdasdasdasdasdqd
   git checkout claude/deploy-pythonanywhere-Eq93Z
   ```

### Yöntem 2: Manuel Upload (Alternatif)

1. **Files Sekmesine Gidin**
2. **Upload a file** butonunu kullanarak projenizi zip olarak yükleyin
3. **Console'da unzip edin:**
   ```bash
   cd ~
   unzip asdasdasdasdasdqd.zip
   ```

---

## 🐍 3. Sanal Ortam (Virtual Environment) Kurulumu

1. **Bash Console'da Sanal Ortam Oluşturun:**
   ```bash
   cd ~
   mkvirtualenv myenv --python=python3.10
   ```

2. **Sanal Ortamı Aktifleştirin:**
   ```bash
   workon myenv
   ```

3. **Paketleri Yükleyin:**
   ```bash
   cd ~/asdasdasdasdasdqd/core
   pip install -r requirements_pythonanywhere.txt
   ```

   ⏱️ Bu işlem 5-10 dakika sürebilir. Bekleyin...

4. **Yüklemeyi Doğrulayın:**
   ```bash
   pip list
   ```

---

## 🌐 4. Web Uygulaması Ayarları

### A) Web App Oluşturma

1. **Dashboard'da "Web" Sekmesine Gidin**
2. **"Add a new web app" Butonuna Tıklayın**
3. **"Manual configuration" Seçin**
4. **Python 3.10 Seçin**
5. **"Next" Tıklayın**

### B) Web App Ayarlarını Yapın

#### Virtualenv Ayarı
1. Web tab'ında "Virtualenv" bölümünü bulun
2. "Enter path to a virtualenv" kutusuna yazın:
   ```
   /home/KULLANICI_ADINIZ/.virtualenvs/myenv
   ```
   **ÖNEMLİ:** `KULLANICI_ADINIZ` yerine kendi kullanıcı adınızı yazın!

#### Code Ayarı
1. "Code" bölümünde "Source code" kutusuna:
   ```
   /home/KULLANICI_ADINIZ/asdasdasdasdasdqd/core
   ```

2. "Working directory" kutusuna:
   ```
   /home/KULLANICI_ADINIZ/asdasdasdasdasdqd/core
   ```

### C) WSGI Configuration Dosyasını Düzenleyin

1. **Web tab'ında "WSGI configuration file" linkine tıklayın**

2. **Açılan dosyanın tüm içeriğini silin**

3. **`core/pythonanywhere_wsgi.py` dosyasının içeriğini kopyalayıp yapıştırın**

4. **USERNAME değişkenini düzenleyin:**
   ```python
   USERNAME = 'sizinkullaniciadi'  # <- Kendi kullanıcı adınızı yazın
   ```

5. **Dosyayı kaydedin (Ctrl+S veya Save butonu)**

---

## 📁 5. Static Dosyaları Yapılandırma

### A) Static Files Toplama

1. **Bash Console'da:**
   ```bash
   cd ~/asdasdasdasdasdqd/core
   workon myenv
   python manage.py collectstatic --noinput
   ```

### B) Web Tab'ında Static Files Ayarı

1. **Web tab'ında "Static files" bölümüne gidin**

2. **Şu mapping'leri ekleyin:**

   | URL          | Directory                                                    |
   |--------------|--------------------------------------------------------------|
   | /static/     | /home/KULLANICI_ADINIZ/asdasdasdasdasdqd/core/staticfiles   |
   | /media/      | /home/KULLANICI_ADINIZ/asdasdasdasdasdqd/core/media         |

   **ÖNEMLİ:** `KULLANICI_ADINIZ` yerine kendi kullanıcı adınızı yazın!

---

## 🗄️ 6. Database Migrate İşlemleri

1. **Bash Console'da Migration'ları Uygulayın:**
   ```bash
   cd ~/asdasdasdasdasdqd/core
   workon myenv
   python manage.py migrate
   ```

2. **Hataları Kontrol Edin:**
   - Eğer hata varsa, konsol çıktısını okuyun
   - Çoğu migration hatası eksik paketlerden kaynaklanır

---

## 👤 7. Superuser Oluşturma

1. **Admin Paneline Giriş İçin Superuser Oluşturun:**
   ```bash
   cd ~/asdasdasdasdasdqd/core
   workon myenv
   python manage.py createsuperuser
   ```

2. **Bilgileri Girin:**
   - Username: admin (veya istediğiniz)
   - Email: email@example.com
   - Password: güçlü bir şifre girin

---

## ✅ 8. Son Kontroller ve Yayınlama

### A) Environment Değişkenlerini Ayarlayın

1. **Bash Console'da .env dosyası oluşturun:**
   ```bash
   cd ~/asdasdasdasdasdqd/core
   nano .env
   ```

2. **Şu içeriği yapıştırın:**
   ```env
   DJANGO_ENV=pythonanywhere
   DEBUG=False
   SECRET_KEY=pythonanywhere-gizli-anahtar-buraya-rastgele-50-karakter-yazin
   ALLOWED_HOSTS=.pythonanywhere.com,kullaniciadi.pythonanywhere.com

   # Cloudinary (opsiyonel - medya dosyaları için)
   # CLOUDINARY_CLOUD_NAME=your_cloud_name
   # CLOUDINARY_API_KEY=your_api_key
   # CLOUDINARY_API_SECRET=your_api_secret
   ```

3. **Kaydedin ve Çıkın:**
   - `Ctrl+X` -> `Y` -> `Enter`

### B) Web Uygulamasını Reload Edin

1. **Web tab'ında yeşil "Reload kullaniciadi.pythonanywhere.com" butonuna basın**

2. **Birkaç saniye bekleyin...**

### C) Siteyi Test Edin

1. **Web tab'ındaki linke tıklayın:**
   ```
   https://kullaniciadi.pythonanywhere.com
   ```

2. **Siteniz açılmalı! 🎉**

3. **Admin paneline giriş yapın:**
   ```
   https://kullaniciadi.pythonanywhere.com/admin/
   ```

---

## 🔧 9. Sorun Giderme

### Hata: "ImportError: No module named..."

**Çözüm:**
```bash
cd ~/asdasdasdasdasdqd/core
workon myenv
pip install eksik-paket-adi
```
Web app'i reload edin.

### Hata: "DisallowedHost at /"

**Çözüm:**
1. `.env` dosyasında `ALLOWED_HOSTS` ayarını kontrol edin:
   ```env
   ALLOWED_HOSTS=.pythonanywhere.com,kullaniciadi.pythonanywhere.com
   ```
2. Web app'i reload edin.

### Static Dosyalar Yüklenmiyor

**Çözüm:**
1. Static files mapping'i kontrol edin (URL ve Directory)
2. `collectstatic` komutunu tekrar çalıştırın:
   ```bash
   cd ~/asdasdasdasdasdqd/core
   workon myenv
   python manage.py collectstatic --noinput
   ```
3. Web app'i reload edin.

### Error Log'larını Görme

1. **Web tab'ında "Log files" bölümüne gidin**
2. **"Error log" linkine tıklayın**
3. **Hata mesajlarını okuyun**

### Database Hatası

**Çözüm:**
```bash
cd ~/asdasdasdasdasdqd/core
workon myenv
python manage.py migrate --run-syncdb
```

---

## 🎯 Önemli Notlar

### ⚠️ Ücretsiz Hesap Kısıtlamaları:
- **CPU süresi:** Günde maksimum 100 saniye
- **Disk alanı:** 512 MB
- **Web app sayısı:** 1 adet
- **Otomatik reload:** 3 ay sonra manuel reload gerekir
- **HTTPS:** Otomatik sağlanır
- **Custom domain:** Ücretli hesaplarda

### 🔄 Proje Güncellemesi:
```bash
cd ~/asdasdasdasdasdqd
git pull origin claude/deploy-pythonanywhere-Eq93Z
cd core
workon myenv
pip install -r requirements_pythonanywhere.txt
python manage.py migrate
python manage.py collectstatic --noinput
```
Sonra Web tab'ında "Reload" butonuna basın.

### 📊 Performans İpuçları:
1. Cloudinary kullanarak medya dosyalarını dışarıda barındırın
2. Gereksiz middleware'leri kapatın
3. Template caching'i aktif tutun (zaten aktif)
4. Database sorgularını optimize edin

---

## 📞 Destek

### PythonAnywhere Yardım:
- Forum: https://www.pythonanywhere.com/forums/
- Help: Dashboard'da "Help" sekmesi

### Django Dokümantasyon:
- https://docs.djangoproject.com/

---

## 🎉 Tebrikler!

Projeniz artık canlı! Link'i paylaşabilirsiniz:

```
https://kullaniciadi.pythonanywhere.com
```

**İyi Çalışmalar! 🚀**
