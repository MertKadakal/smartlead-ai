import os
from flask import Flask, jsonify, make_response
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

    # 2. Global CORS Başlatma (flask-cors tüm başlıkları ve preflight'ı yönetir)
    CORS(
        app,
        resources={r"/*": {"origins": "*"}},
        allow_headers=["Content-Type", "Authorization", "X-Requested-With", "x-api-key"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    )

    # 3. Her ihtimale karşı manuel fallback kancası (düz string formatında)
    @app.after_request
    def add_cors_headers(response):
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        # Tek bir düz string olmalıdır (aradaki tuple oluşturan virgül kaldırıldı):
        response.headers["Access-Control-Allow-Headers"] = (
            "Content-Type, Authorization, X-Requested-With, x-api-key"
        )
        return response

    # 4. OPTIONS (Preflight) isteklerinin hatasız dönmesini garantiye al
    @app.before_request
    def handle_preflight():
        from flask import request
        if request.method == "OPTIONS":
            response = make_response()
            response.status_code = 204
            return response

    # 5. Veritabanını Başlat
    with app.app_context():
        init_db(app)

    # 6. Blueprint'leri Kaydet
    from app.routes import api_bp, views_bp

    app.register_blueprint(views_bp)
    app.register_blueprint(api_bp, url_prefix="/api")

    # 7. /health Uç Noktası
    @app.route("/health", methods=["GET"])
    def health_check():
        return jsonify(
            {"durum": "aktif", "mesaj": "Sunucu sorunsuz calisiyor."}
        ), 200

    return app