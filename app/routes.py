import os
from flask import Blueprint, jsonify, render_template, request
from app.services.ai_service import AIServiceError, ai_service
from app import database

views_bp = Blueprint("views", __name__)
api_bp = Blueprint("api", __name__)

# Render Environment kısmına ekleyeceğiniz gizli anahtar
API_SECRET_KEY = os.environ.get("SECRET_KEY", "super-gizli-anahtar-123")


# ==========================================
# SAYFA ROTALARI (views_bp)
# ==========================================


@views_bp.route("/", methods=["GET"])
def index():
    """Karşılama sayfasını gösterir."""
    return render_template("index.html")


@views_bp.route("/dashboard", methods=["GET"])
def dashboard():
    """Yönetim panelini gösterir."""
    return render_template("dashboard.html")


# ==========================================
# API UÇ NOKTALARI (api_bp)
# ==========================================


@api_bp.route("/sohbet", methods=["POST"])
def sohbet():
    """AI servisine mesaj iletir ve yanıtı döndürür."""
    data = request.get_json(silent=True) or {}
    mesaj = data.get("mesaj")
    gecmis = data.get("gecmis", [])

    if not mesaj or not str(mesaj).strip():
        return (
            jsonify(
                {"basari": False, "hata": "Lütfen bir mesaj metni girin."}
            ),
            400,
        )

    try:
        yanit = ai_service.yanit_uret(mesaj, gecmis)
        return jsonify({"basari": True, "yanit": yanit}), 200
    except AIServiceError as e:
        return (
            jsonify(
                {
                    "basari": False,
                    "hata": str(e),
                }
            ),
            503,
        )


@api_bp.route("/leads", methods=["POST"])
def lead_kaydet():
    """Yeni bir müşteri adayı (lead) kaydeder."""
    data = request.get_json(silent=True) or {}
    isim = data.get("isim")
    telefon = data.get("telefon")
    mesaj = data.get("mesaj")

    if not isim or not telefon:
        return (
            jsonify(
                {
                    "basari": False,
                    "hata": "'isim' ve 'telefon' alanları zorunludur.",
                }
            ),
            400,
        )

    try:
        lead_id = database.lead_ekle(isim=isim, telefon=telefon, mesaj=mesaj)
        return (
            jsonify(
                {
                    "basari": True,
                    "mesaj": "Müşteri adayı başarıyla kaydedildi.",
                    "lead_id": lead_id,
                }
            ),
            201,
        )
    except Exception as e:
        return (
            jsonify(
                {
                    "basari": False,
                    "hata": f"Kayıt eklenirken hata oluştu: {str(e)}",
                }
            ),
            500,
        )


@api_bp.route("/leads", methods=["GET"])
def lead_listele():
    """Tüm lead kayıtlarını listeler (Wix paneli ve /dashboard için)."""
    api_key = request.headers.get("x-api-key")
    istemci_kaynak = request.headers.get("Referer", "")

    # Kendi /dashboard sayfanız haricindeki isteklerde API Key kontrolü
    dashboard_istegi = "/dashboard" in istemci_kaynak
    if not dashboard_istegi and api_key != API_SECRET_KEY:
        return (
            jsonify({"basari": False, "hata": "Yetkisiz erişim: Geçersiz API anahtarı."}),
            401,
        )

    try:
        leadler = database.tum_leadler()
        return jsonify({"basari": True, "leadler": leadler, "data": leadler}), 200
    except Exception as e:
        return (
            jsonify(
                {
                    "basari": False,
                    "hata": f"Kayıtlar getirilirken hata oluştu: {str(e)}",
                }
            ),
            500,
        )