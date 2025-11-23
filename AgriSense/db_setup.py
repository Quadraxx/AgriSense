import sqlite3
import os
from datetime import datetime

DATABASE = 'agrisense.db'

def create_database():
    """
    SQLite veritabanını oluşturur ve 'sensor_data' tablosunu kurar.
    Bu tablo, tarladan gelen simüle edilmiş sensör verilerini tutar.
    """
    try:
        # Veritabanı dosyasına bağlantı kurar. Dosya yoksa otomatik oluşturulur.
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        # sensor_data tablosu
        # parcel_id: Hangi tarlaya ait olduğunu belirler (Örn: "Tarla A")
        # timestamp: Verinin alındığı zamanı otomatik kaydeder (Veri analizi için kritik)
        # soil_moisture: Toprak Nemi (%)
        # air_temp: Hava Sıcaklığı (°C)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sensor_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                parcel_id TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                soil_moisture REAL,
                air_temp REAL
            );
        """)
        
        conn.commit()
        conn.close()
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ '{DATABASE}' veritabanı ve 'sensor_data' tablosu başarıyla kuruldu.")

    except sqlite3.Error as e:
        print(f"Bir veritabanı hatası oluştu: {e}")

if __name__ == '__main__':
    # Mevcut veritabanı dosyasını silerek temiz bir başlangıç yapabiliriz (Opsiyonel)
    if os.path.exists(DATABASE):
        # os.remove(DATABASE)
        # print(f"Mevcut '{DATABASE}' silindi.")
        pass # Mevcut olanı silme adımını şimdilik pas geçelim
        
    create_database()