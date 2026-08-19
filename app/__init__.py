import os
from flask import Flask, jsonify
from flask_cors import CORS
from config import config
from app.database import init_db


def create_app(config_name=None):
    """Flask uygulama fabrikası fonksiyonu."""
    app = Flask(__name__)

    app.config["JSON_AS_ASCII"] = False

    # 1. Ayarları Yükle
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "development")
    app.config.from_object(config.get(config_name, config["default"]))

    # 2. CORS Yapılandırması
    CORS(app, resources={r"/*": {"origins": app.config.get("CORS_ORIGINS", "*")}})

    # 3. Veritabanını Başlat (App Context İçinde)
    with app.app_context():
        init_db(app)

    # 4. Blueprint'leri Kaydet
    from routes import api_bp, views_bp

    app.register_blueprint(views_bp)
    app.register_blueprint(api_bp, url_prefix="/api")

    # 5. /health Uç Noktası (Sunucu canlılık kontrolü)
    @app.route("/health", methods=["GET"])
    def health_check():
        return jsonify({"durum": "aktif", "mesaj": "Sunucu sorunsuz calisiyor."}), 200

    # 6. Uygulamayı Döndür
    return app