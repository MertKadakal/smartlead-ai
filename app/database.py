import sqlite3
from flask import g

DB_NAME = "app.db"


def get_db():
    """Veritabanına bağlanır ve sütun isimleriyle erişim (sqlite3.Row) sağlar."""
    if "db" not in g:
        g.db = sqlite3.connect(DB_NAME)
        # Satırlara sütun adıyla (dict gibi) erişebilmek için:
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(e=None):
    """İstek bittiğinde veritabanı bağlantısını güvenle kapatır."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db(app=None):
    """'leads' tablosunu oluşturur (yoksa) ve app teardown kaydını yapar."""
    if app:
        app.teardown_appcontext(close_db)
        with app.app_context():
            _create_tables()
    else:
        _create_tables()


def _create_tables():
    """Tablo oluşturma SQL sorgusunu çalıştırır."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            isim TEXT NOT NULL,
            telefon TEXT NOT NULL,
            mesaj TEXT,
            tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )
    conn.commit()
    conn.close()


def lead_ekle(isim, telefon, mesaj=None):
    """Yeni bir müşteri adayı (lead) ekler.

    SQL Injection koruması için '?' yer tutucuları kullanılmıştır.
    """
    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        """
        INSERT INTO leads (isim, telefon, mesaj)
        VALUES (?, ?, ?)
    """,
        (isim, telefon, mesaj),
    )

    db.commit()
    return cursor.lastrowid


def tum_leadler():
    """Tüm kayıtları en yeniden en eskiye doğru sıralı olarak getirir."""
    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        """
        SELECT id, isim, telefon, mesaj, tarih
        FROM leads
        ORDER BY tarih DESC, id DESC
    """
    )

    # Sözlük listesi olarak döndürmek isterseniz: [dict(row) for row in cursor.fetchall()]
    return cursor.fetchall()