import os
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import g

DATABASE_URL = os.environ.get("DATABASE_URL")

# Render bazen URL'i 'postgres://' olarak verir; psycopg2 'postgresql://' bekler:
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)


def get_db():
    """Her istek döngüsünde PostgreSQL bağlantısı açar veya mevcut olanı döner."""
    if "db" not in g:
        g.db = psycopg2.connect(DATABASE_URL)
    return g.db


def close_db(e=None):
    """İstek tamamlandığında bağlantıyı güvenle kapatır."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db(app=None):
    """leads tablosunu oluşturur ve Flask teardown kaydını yapar."""
    if app:
        app.teardown_appcontext(close_db)
        with app.app_context():
            _create_tables()
    else:
        _create_tables()


def _create_tables():
    """Tablo yoksa otomatik oluşturur."""
    if not DATABASE_URL:
        print("UYARI: DATABASE_URL tanımlı değil, tablo oluşturulamadı.")
        return

    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS leads (
            id SERIAL PRIMARY KEY,
            isim VARCHAR(255) NOT NULL,
            telefon VARCHAR(50) NOT NULL,
            mesaj TEXT,
            tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    )
    conn.commit()
    cursor.close()
    conn.close()


def lead_ekle(isim, telefon, mesaj=None):
    """Yeni lead ekler ve oluşturulan ID değerini string olarak döner."""
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        """
        INSERT INTO leads (isim, telefon, mesaj)
        VALUES (%s, %s, %s)
        RETURNING id;
        """,
        (isim, telefon, mesaj),
    )
    yeni_id = cursor.fetchone()[0]
    db.commit()
    cursor.close()
    return str(yeni_id)


def tum_leadler():
    """Tüm kayıtları çeker, tarihleri metne çevirir ve Wix ile %100 uyumlu hale getirir."""
    db = get_db()
    cursor = db.cursor(cursor_factory=RealDictCursor)
    cursor.execute(
        """
        SELECT id, isim, telefon, mesaj, tarih
        FROM leads
        ORDER BY tarih DESC, id DESC;
        """
    )
    satirlar = cursor.fetchall()
    cursor.close()

    kayitlar = []
    for satir in satirlar:
        kayit = dict(satir)
        # Wix Repeater varsayılan olarak '_id' (string) alanı arar:
        kayit["_id"] = str(kayit["id"])
        # Wix Table için standart 'id' (string):
        kayit["id"] = str(kayit["id"])
        # Tarih alanını JSON'a uygun metin formatına çevir:
        if kayit.get("tarih"):
            kayit["tarih"] = kayit["tarih"].strftime("%d.%m.%Y %H:%M")
        kayitlar.append(kayit)

    return kayitlar

def lead_sil(lead_id):
    """Belirtilen ID'ye sahip lead kaydını siler.
    Kayıt silindiyse True, bulunamadıysa False döner."""
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        """
        DELETE FROM leads
        WHERE id = %s;
        """,
        (lead_id,),
    )
    etkilenen_satir = cursor.rowcount
    db.commit()
    cursor.close()
    return etkilenen_satir > 0