# 🤖 SmartLead AI

SmartLead AI, potansiyel müşteriler (lead) ile etkileşime geçen, sorularını yapay zekâ (Groq API / Qwen) desteğiyle yanıtlayan ve müşteri adayı bilgilerini SQLite veritabanında saklayan Flask tabanlı bir web servis uygulamasıdır.

---

## 🚀 Özellikler

- **AI Sohbet Servisi (`/api/sohbet`):** Groq API (Qwen 3.6 27B) entegrasyonu ile özelleştirilebilir müşteri destek asistanı.
- **Lead Yönetimi (`/api/leads`):** Müşteri adayı bilgilerini (isim, telefon, mesaj) veritabanına kaydetme ve listeleme.
- **Web Arayüzleri:** Karşılama sayfası (`/`) ve yönetim paneli (`/dashboard`).
- **Canlılık Kontrolü (`/health`):** Sunucu durum kontrolü (Health check).
- **Esnek Yapılandırma:** `.env` dosyası üzerinden API anahtarları ve sistem talimatı (*Business Context*) yönetimi.

---

## 🛠️ Kurulum

### 1. Sanal Ortam Oluşturun ve Aktifleştirin
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 2. Bağımlılıkları Yükleyin
```bash
pip install -r requirements.txt
```

### 3. Ortam Değişkenlerini Yapılandırın (`.env`)
Proje kök dizininde bir `.env` dosyası oluşturun veya mevcut dosyayı düzenleyin:

```env
FLASK_ENV=development
SECRET_KEY=super-gizli-anahtar
GROQ_API_KEY=gsk_... # Groq API Anahtarınız
BUSINESS_CONTEXT="Sen SmartLead AI müşteri destek asistanısın. Müşterilere nazik ve çözüm odaklı yardımcı olursun."
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```
*(Not: `GROQ_API_KEY` girilmediğinde sistem otomatik olarak **Demo Modu**nda yanıt verir.)*

---

## 🏃‍♂️ Uygulamayı Çalıştırma

```bash
python run.py
```
Sunucu başlatıldığında **`http://127.0.0.1:5000`** adresinden erişilebilir hale gelecektir.

---

## 📌 API Uç Noktaları (Endpoints)

| Yöntem | Uç Nokta | Açıklama | Body Örneği / Not |
| :--- | :--- | :--- | :--- |
| `GET` | `/health` | Sunucu sağlık durumu | - |
| `POST` | `/api/sohbet` | AI sohbet yanıtı alır | `{"mesaj": "Merhaba", "gecmis": []}` |
| `POST` | `/api/leads` | Müşteri adayı kaydeder | `{"isim": "Ahmet", "telefon": "0555...", "mesaj": "..."}` |
| `GET` | `/api/leads` | Tüm leadleri listeler | - |

---

## 📂 Proje Yapısı

```
smartlead_ai/
├── app/
│   ├── services/
│   │   └── ai_service.py   # Groq AI entegrasyonu ve istem mantığı
│   ├── templates/          # HTML şablonları
│   ├── database.py         # SQLite veritabanı yönetimi
│   ├── routes.py           # API ve Sayfa rotaları (Blueprints)
│   └── __init__.py         # App factory ve CORS ayarları
├── config.py               # Yapılandırma sınıfları
├── run.py                  # Sunucu başlatıcı
├── requirements.txt        # Python paket bağımlılıkları
└── .env                    # Ortam değişkenleri
```
