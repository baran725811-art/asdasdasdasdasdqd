# 🔐 HTTPS Development Server Setup

Bu kılavuz, Django development server'ınızı güvenilir SSL sertifikalarıyla HTTPS üzerinden çalıştırmanıza yardımcı olur.

## 🚀 Hızlı Başlangıç (Windows)

### Adım 1: mkcert Kurulumu

**Seçenek A - Chocolatey ile (Önerilen):**
```powershell
# PowerShell'i yönetici olarak açın
choco install mkcert -y
```

**Seçenek B - Manuel Kurulum:**
1. https://github.com/FiloSottile/mkcert/releases/latest adresinden `mkcert-v*-windows-amd64.exe` indirin
2. Dosyayı `mkcert.exe` olarak yeniden adlandırın
3. `C:\Windows\System32\` klasörüne taşıyın

### Adım 2: Otomatik Setup (Kolay Yol)

Proje klasöründe çift tıklayın:
```
setup_ssl.bat
```

Bu script otomatik olarak:
- ✅ Sertifika klasörü oluşturur
- ✅ Local CA kurar
- ✅ SSL sertifikaları üretir
- ✅ Dosyaları yeniden adlandırır

### Adım 3: HTTPS Server Başlatma

```bash
python manage.py runsslserver --certificate certs/cert.pem --key certs/key.pem
```

Veya kısa yol:
```bash
python manage.py runsslserver
```

Tarayıcıda açın: **https://127.0.0.1:8000/** 🎉

---

## 📋 Manuel Setup (İleri Kullanıcılar)

```bash
# Sertifika klasörü oluştur
mkdir certs
cd certs

# Local CA kur (ilk kez)
mkcert -install

# Sertifika oluştur
mkcert localhost 127.0.0.1 ::1

# Dosyaları yeniden adlandır
ren localhost+2.pem cert.pem
ren localhost+2-key.pem key.pem

cd ..
```

---

## 🐧 Linux/Mac Kullanıcıları

```bash
# mkcert kur
brew install mkcert  # Mac
# veya
sudo apt install libnss3-tools && brew install mkcert  # Linux

# Sertifika oluştur
mkdir -p certs && cd certs
mkcert -install
mkcert localhost 127.0.0.1 ::1
mv localhost+2.pem cert.pem
mv localhost+2-key.pem key.pem
cd ..
```

---

## ❓ Sık Sorulan Sorular

### Neden SSL sertifikası gerekiyor?
- Tarayıcı güvenlik uyarısı göstermez
- Modern web API'leri (PWA, Service Workers) HTTPS gerektirir
- Production ortamını simüle eder

### Sertifikalar güvenli mi?
- ✅ Evet, sadece **yerel development** için
- ✅ Sisteminize güvenilir CA olarak eklenir
- ⚠️ Production'da Let's Encrypt kullanın

### Sertifikalar nerede saklanıyor?
- `core/certs/` klasöründe
- `.gitignore` ile git'e eklenmez

### Nasıl kaldırırım?
```bash
mkcert -uninstall
```

---

## 🔧 Sorun Giderme

### "mkcert: command not found"
➡️ mkcert'i PATH'e ekleyin veya tam yolu kullanın

### "NET::ERR_CERT_AUTHORITY_INVALID" hatası
➡️ `mkcert -install` komutunu yönetici olarak çalıştırın

### Port zaten kullanımda
➡️ Farklı port kullanın: `python manage.py runsslserver 0.0.0.0:8443 --certificate ...`

---

## 📚 Kaynaklar

- [mkcert GitHub](https://github.com/FiloSottile/mkcert)
- [django-sslserver](https://github.com/teddziuba/django-sslserver)
- [Django HTTPS Deployment](https://docs.djangoproject.com/en/stable/topics/security/)
