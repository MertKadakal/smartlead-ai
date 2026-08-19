import os
from dotenv import load_dotenv

# .env dosyasındaki ortam değişkenlerini yükle
load_dotenv()


class Config:
    """Temel yapılandırma sınıfı (Tüm ortamlarda ortak olan ayarlar)"""
    JSON_AS_ASCII = False

    SECRET_KEY = os.environ.get("SECRET_KEY", "varsayilan-guvensiz-anahtar-degistirin")
    DATABASE_URL = os.environ.get(
        "DATABASE_URL", "sqlite:///app.db"
    )
    GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
    AI_PROVIDER = os.environ.get("AI_PROVIDER", "groq")

    # Yapay zekanın sistem istemi / kişiliği
    BUSINESS_CONTEXT = os.environ.get(
        "BUSINESS_CONTEXT",
        "Sen [İşletmenizin Adı] müşteri destek asistanısın. Müşterilere nazik, çözüm odaklı ve profesyonel bir dille yardımcı olursun.",
    )

    # CORS ayarları (virgülle ayrılmış string'i listeye çevirir)
    CORS_ORIGINS = os.environ.get(
        "CORS_ORIGINS", "http://localhost:3000,http://localhost:5173"
    ).split(",")


class DevelopmentConfig(Config):
    """Geliştirme ortamı yapılandırması"""

    DEBUG = True


class ProductionConfig(Config):
    """Üretim ortamı yapılandırması"""

    DEBUG = False
    # Üretimde SECRET_KEY'in mutlaka .env içinde tanımlanmış olması önerilir


# Ortam seçimi için sözlük yapısı
config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}