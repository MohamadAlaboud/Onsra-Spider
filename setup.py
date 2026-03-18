import sqlite3
from pathlib import Path

# Dosya yolunu otomatik belirler
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "onsra_records.db"

def init_db():
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    # Tabloyu oluştur
    cursor.execute("CREATE TABLE IF NOT EXISTS vehicle_data (id INTEGER PRIMARY KEY, plate_no TEXT, owner TEXT, price TEXT)")
    # Test verisini ekle (27 ME 7422)
    cursor.execute("INSERT OR IGNORE INTO vehicle_data (id, plate_no, owner, price) VALUES (1, '27ME7422', 'HKU Student Project', '850.000 TL')")
    conn.commit()
    conn.close()
    print(f"✅ Veritabanı başarıyla oluşturuldu: {DB_PATH.name}")

if __name__ == "__main__":
    init_db()