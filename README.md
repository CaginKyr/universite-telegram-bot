# 🎓 Üniversite Telegram Bot

Üniversite öğrencileri için geliştirilmiş, kapsamlı bir topluluk yönetim botu. Duyuru paylaşımı, kaynak paylaşımı, soru-cevap sistemi, etkinlik yönetimi ve daha fazlası!

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Telegram](https://img.shields.io/badge/Telegram-Bot-blue.svg)](https://telegram.org/)

## 📋 İçindekiler

- [Özellikler](#-özellikler)
- [Kurulum](#-kurulum)
- [Kullanım](#-kullanım)
- [Yapılandırma](#-yapılandırma)
- [Komutlar](#-komutlar)
- [Veritabanı Yapısı](#-veritabanı-yapısı)
- [Ekran Görüntüleri](#-ekran-görüntüleri)
- [Katkıda Bulunma](#-katkıda-bulunma)
- [Lisans](#-lisans)


## ✨ Özellikler

### 👥 Kullanıcı Yönetimi
- ✅ Güvenli kayıt sistemi (öğrenci numarası, e-posta doğrulama)
- 🎓 Fakülte ve bölüm bazlı kayıt
- 🔐 Kanal/grup üyeliği kontrolü
- 👑 Rol bazlı yetkilendirme (Öğrenci, Moderatör, Admin)

### 📢 İletişim
- 📣 Kategorize duyuru sistemi (Akademik, Sosyal, İdari, Acil)
- 📊 Anket oluşturma ve yönetimi
- ❓ Soru-cevap sistemi
- 💬 Gerçek zamanlı bildirimler

### 📚 İçerik Yönetimi
- 📤 Kaynak paylaşımı (PDF, Word, PowerPoint, vb.)
- 🔍 Bölüm bazlı kaynak filtreleme
- 📥 İndirme sayaç sistemi
- 🎉 Etkinlik oluşturma ve katılım takibi

### 🛡️ Güvenlik
- 🚫 Spam koruması (1 dakikada 5+ mesaj)
- 🤬 Küfür filtresi
- ⚠️ Uyarı sistemi (3 uyarı = ban)
- 🔒 Doğrulanmamış kullanıcı kontrolü

### 📊 İstatistikler
- 👥 Kullanıcı istatistikleri
- 📈 İçerik analizi
- 📋 Detaylı raporlama

## 🚀 Kurulum

### Gereksinimler

- Python 3.8 veya üzeri
- pip (Python paket yöneticisi)
- Telegram Bot Token ([BotFather](https://t.me/BotFather)'dan alınabilir)

### Adım 1: Depoyu Klonlayın

```bash
git clone https://github.com/caginkyr/universite-telegram-bot.git
cd universite-telegram-bot
```

### Adım 2: Sanal Ortam Oluşturun (Önerilen)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### Adım 3: Gerekli Paketleri Yükleyin

```bash
pip install -r requirements.txt
```

### Adım 4: Yapılandırma

`config.py` dosyasını oluşturun veya `main.py` içindeki değişkenleri düzenleyin:

```python
BOT_TOKEN = 'YOUR_BOT_TOKEN_HERE'
CHANNEL_ID = '@your_channel'
GROUP_ID = '@your_group'
```

### Adım 5: Botu Başlatın

```bash
python main.py
```

## 📝 Kullanım

### İlk Kurulum

1. **Bot Oluşturma**: [BotFather](https://t.me/BotFather) ile yeni bir bot oluşturun
2. **Kanal/Grup Oluşturma**: Duyuru kanalı ve sohbet grubu oluşturun
3. **Bot İzinleri**: Botu kanal ve gruba admin olarak ekleyin
4. **Yapılandırma**: Token ve ID'leri kodunuza ekleyin

### Kullanıcı Akışı

1. Kullanıcı `/start` komutu ile başlar
2. Kayıt olma butonuna tıklar
3. Kanal ve gruba katılır
4. Bilgilerini girer (ad, öğrenci no, bölüm, e-posta)
5. Doğrulama kodunu girer
6. Sisteme giriş yapar ve özellikleri kullanır

## ⚙️ Yapılandırma

### Fakülte ve Bölüm Ekleme

`UNIVERSITY_DEPARTMENTS` dictionary'sini düzenleyerek kendi üniversitenizin yapısını ekleyebilirsiniz:

```python
UNIVERSITY_DEPARTMENTS = {
    'muhendislik': {
        'name': '🏗️ Mühendislik Fakültesi',
        'departments': [
            'Bilgisayar Mühendisliği',
            'Elektrik-Elektronik Mühendisliği',
            # Diğer bölümler...
        ]
    },
    # Diğer fakülteler...
}
```

### Küfür Filtresi

`bad_words` listesine istediğiniz kelimeleri ekleyebilirsiniz:

```python
self.bad_words = ['kelime1', 'kelime2']
```

## 📜 Komutlar

### Genel Komutlar

| Komut | Açıklama |
|-------|----------|
| `/start` | Botu başlatır ve ana menüyü gösterir |
| `/profil` | Kullanıcı profilini görüntüler |
| `/kaynaklar` | Paylaşılan kaynakları listeler |
| `/kaynak_paylas` | Yeni kaynak paylaşır |
| `/sorular` | Soruları listeler |
| `/soru_sor` | Yeni soru sorar |
| `/etkinlikler` | Etkinlikleri listeler |
| `/yardim` | Yardım menüsünü gösterir |

### Admin Komutları

| Komut | Açıklama |
|-------|----------|
| `/duyuru` | Yeni duyuru yayınlar |
| `/anket` | Yeni anket oluşturur |
| `/etkinlik` | Yeni etkinlik oluşturur |
| `/istatistik` | Bot istatistiklerini gösterir |
| `/onay_bekleyenler` | Bekleyen kayıtları listeler |

## 🗄️ Veritabanı Yapısı

Bot SQLite veritabanı kullanır. Ana tablolar:

- **users**: Kullanıcı bilgileri
- **announcements**: Duyurular
- **polls**: Anketler
- **resources**: Kaynaklar
- **questions**: Sorular
- **events**: Etkinlikler
- **event_participants**: Etkinlik katılımcıları
- **spam_tracker**: Spam takibi
- **user_roles**: Kullanıcı rolleri

## 📸 Ekran Görüntüleri

> 📝 **Not**: Ekran görüntülerini `screenshots` klasörüne ekleyin ve buraya linkleyin

```markdown
### Ana Menü
![Ana Menü](screenshots/main_menu.png)

### Kayıt Ekranı
![Kayıt](screenshots/registration.png)

### Kaynak Paylaşımı
![Kaynaklar](screenshots/resources.png)

### Admin Paneli
![Admin Panel](screenshots/admin_panel.png)
```

## 🔧 Geliştirme

### requirements.txt

```
python-telegram-bot==20.7
```

### Proje Yapısı

```
universite-telegram-bot/
│
├── main.py                 # Ana bot kodu
├── config.py              # Yapılandırma dosyası (oluşturulacak)
├── requirements.txt       # Python bağımlılıkları
├── README.md             # Bu dosya
├── LICENSE               # Lisans dosyası
├── .gitignore           # Git ignore dosyası
│
├── screenshots/         # Ekran görüntüleri
│   ├── main_menu.png
│   ├── registration.png
│   └── ...
│
└── university_bot.db    # SQLite veritabanı (otomatik oluşturulur)
```

### .gitignore

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/

# Veritabanı
*.db
*.sqlite

# Yapılandırma
config.py

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
```

## 🤝 Katkıda Bulunma

Katkılarınızı bekliyoruz! Lütfen şu adımları izleyin:

1. Bu depoyu fork edin
2. Yeni bir branch oluşturun (`git checkout -b feature/yeniOzellik`)
3. Değişikliklerinizi commit edin (`git commit -m 'Yeni özellik eklendi'`)
4. Branch'inizi push edin (`git push origin feature/yeniOzellik`)
5. Pull Request oluşturun

### Katkı Rehberi

- Kod standartlarına uyun
- Yeni özellikler için testler ekleyin
- README'yi güncel tutun
- Commit mesajlarını açıklayıcı yazın

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın.

## 👨‍💻 Geliştirici

**Adınız Soyadınız**

- GitHub: [@CaginKyr](https://github.com/CaginKyr)
- Linkedin: [Tıkla](https://www.linkedin.com/in/%C3%A7a%C4%9F%C4%B1n-kayra-y%C4%B1ld%C4%B1r%C4%B1m-760806385/)

## 🙏 Teşekkürler

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) - Harika Telegram bot kütüphanesi için
- Tüm katkıda bulunanlara

## ⚠️ Sorumluluk Reddi

Bu bot eğitim amaçlıdır. Gerçek üretim ortamında kullanmadan önce güvenlik önlemlerini ve veri koruma yasalarını gözden geçirin.

## 📞 Destek

Sorularınız veya sorunlarınız için:

1. [Issues](https://github.com/caginkyr/universite-telegram-bot/issues) bölümünde yeni bir konu açın
2. [Discussions](https://github.com/caginkyr/universite-telegram-bot/discussions) bölümünde tartışmaya katılın

---

⭐ Bu projeyi beğendiyseniz yıldız vermeyi unutmayın!

**Son Güncelleme**: 2025 Kasım
