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

    # 2. Global CORS Başlatma
    CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

    # 3. Tüm yanıtlara (404/500/OPTIONS dahil) CORS başlığı ekleyen kanca
    @app.after_request
    def add_cors_headers(response):
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = (
            "GET, POST, PUT, DELETE, OPTIONS"
        )
        response.headers["Access-Control-Allow-Headers"] = (
            "Content-Type, Authorization, X-Requested-With"
        )
        return response

    # 4. Veritabanını Başlat
    with app.app_context():
        init_db(app)

    # 5. Blueprint'leri Kaydet
    from app.routes import api_bp, views_bp

    app.register_blueprint(views_bp)
    app.register_blueprint(api_bp, url_prefix="/api")

    # 6. /health Uç Noktası
    @app.route("/health", methods=["GET"])
    def health_check():
        return jsonify(
            {"durum": "aktif", "mesaj": "Sunucu sorunsuz calisiyor."}
        ), 200

    return app