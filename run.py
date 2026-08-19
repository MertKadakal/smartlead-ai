import os
import sys

# Proje kök dizinini ve alt modülleri Python yoluna (sys.path) ekle
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.join(BASE_DIR, "app")
SERVICES_DIR = os.path.join(APP_DIR, "services")

for path in [BASE_DIR, APP_DIR, SERVICES_DIR]:
    if path not in sys.path:
        sys.path.insert(0, path)

from app import create_app

# Ortam değişkenine göre Flask uygulamasını başlat ("development" veya "production")
env_mode = os.environ.get("FLASK_ENV", "development")
app = create_app(env_mode)

if __name__ == "__main__":
    # Sunucu çalışma parametreleri
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "True").lower() in ["true", "1", "t"]

    print("=== SmartLead AI Sunucusu Baslatiliyor ===")
    print(f"Calisma Ortami: {env_mode}")
    print(f"Baglanti Adresi: http://{host}:{port}")

    app.run(host=host, port=port, debug=debug)
