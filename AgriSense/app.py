import pyodbc
import random
from flask import Flask, render_template
from apscheduler.schedulers.background import BackgroundScheduler
import atexit # Uygulama kapanırken scheduler'ı durdurmak için

# --- Konfigürasyon ---
app = Flask(__name__)
# Tarlalarınız
PARCELS = ["Tarla A (Buğday)", "Tarla B (Mısır)"]

# SQL SERVER CONNECTION STRING (localhost\SQLEXPRESS örneğinizle uyumlu)
# ODBC Driver 17'nin kurulu olduğundan emin olun.
CONNECTION_STRING = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost\\SQLEXPRESS;"
    "DATABASE=AgriSenseDB;"
    "Trusted_Connection=yes;"
)

# --- Veritabanı Fonksiyonları ---

def get_db_connection():
    """pyodbc ile SQL Server bağlantısını döndürür."""
    try:
        conn = pyodbc.connect(CONNECTION_STRING)
        return conn
    except pyodbc.Error as ex:
        sqlstate = ex.args[0]
        print(f"Veritabanı bağlantı hatası: {sqlstate}. Lütfen SQL Server ve AgriSenseDB'nin çalıştığından emin olun.")
        # Bağlantı hatasında None döndür
        return None

def simulate_and_insert_data():
    """Her parsel için rastgele veriyi SQL Server'a kaydeder (Scheduler tarafından düzenli çalıştırılır)."""
    conn = get_db_connection()
    if conn is None:
        return # Bağlantı yoksa devam etme

    cursor = conn.cursor()
    
    for parcel_id in PARCELS:
        # Rastgele ancak anlamlı veri üretimi
        moisture = round(random.uniform(15.0, 50.0), 2)
        temp = round(random.uniform(18.0, 35.0), 2)
        
        # ✅ DÜZELTİLMİŞ SQL INSERT SORGUSU: 3 Sütun ve 3 Parametre Eşleşmesi
        # timestamp sütunu, tabloda DEFAULT GETDATE() olduğu için sorgu listesine dahil edilmez.
        cursor.execute("""
            INSERT INTO sensor_data (parcel_id, soil_moisture, air_temp) 
            VALUES (?, ?, ?);
        """, (parcel_id, moisture, temp))
        
    conn.commit()
    conn.close()
    print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Yeni simülasyon verileri başarıyla eklendi.")


def get_latest_data(parcel_id):
    """Belirtilen parselin son sensör verisini çeker (SQL Server için TOP 1)."""
    conn = get_db_connection()
    if conn is None: return None
    
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT TOP 1 * FROM sensor_data 
        WHERE parcel_id = ? 
        ORDER BY [timestamp] DESC
    """, (parcel_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        # Sütun isimlerini kullanarak dict formatına dönüştürelim
        columns = [column[0] for column in cursor.description]
        return dict(zip(columns, row))
    return None


def get_time_series_data(parcel_id, hours=12):
    """Dashboard için son X saatlik veriyi çeker (SQL Server T-SQL kullanımı)."""
    conn = get_db_connection()
    if conn is None: return []

    cursor = conn.cursor()
    
    # SQL Server için tarih/saat sorgusu (DATEADD)
    query = """
    SELECT 
        -- Saat ve dakikayı formatlayıp gruplayarak saatlik ortalama alır
        CAST(FORMAT([timestamp], 'HH:00') AS NVARCHAR(5)) as hour, 
        AVG(soil_moisture) as avg_moisture
    FROM sensor_data 
    WHERE parcel_id = ? AND [timestamp] >= DATEADD(hour, ?, GETDATE())
    GROUP BY FORMAT([timestamp], 'HH:00')
    ORDER BY hour;
    """
    
    time_limit = -hours 
    
    cursor.execute(query, (parcel_id, time_limit))
    data = cursor.fetchall()
    conn.close()
    
    # (hour, avg_moisture) tuple'larını dict listesine dönüştürelim
    columns = ['hour', 'avg_moisture']
    return [dict(zip(columns, row)) for row in data]


# --- Analiz ve Kural Tabanlı Fonksiyonlar ---

def check_for_alerts(moisture):
    """Neme göre sulama uyarısı kontrolü yapar."""
    if moisture < 20.0:
        return {"status": "ACİL SULAMA GEREKLİ", "color": "red"}
    elif moisture < 30.0:
        return {"status": "Sulama Yapılması Önerilir", "color": "orange"}
    else:
        return {"status": "Normal Seviyede", "color": "green"}

# --- Flask Rotaları ---

@app.route('/')
def dashboard():
    latest_data = {}
    labels = []
    moisture_values = []
    
    for parcel_id in PARCELS:
        data = get_latest_data(parcel_id)
        if data:
            alert = check_for_alerts(data['soil_moisture'])
            
            # Sadece ilk parselin (Tarla A) verilerini grafiğe gönder
            if parcel_id == PARCELS[0]:
                chart_data_raw = get_time_series_data(parcel_id, hours=12)
                labels = [row['hour'] for row in chart_data_raw]
                moisture_values = [row['avg_moisture'] for row in chart_data_raw]
            
            latest_data[parcel_id] = {
                "moisture": data['soil_moisture'],
                "temp": data['air_temp'],
                "alert": alert
            }
        
    # NOT: simulate_and_insert_data artık scheduler tarafından çalıştırıldığı için 
    # bu fonksiyondan kaldırıldı.
    
    return render_template('index.html', 
                           parcels=latest_data,
                           parcel_ids=PARCELS,
                           chart_labels=labels,
                           chart_values=moisture_values)

if __name__ == '__main__':
    # --- APScheduler Kurulumu ---
    scheduler = BackgroundScheduler()
    # Veri ekleme fonksiyonunu her 1 dakikada bir çalışacak şekilde ayarla
    scheduler.add_job(func=simulate_and_insert_data, trigger="interval", minutes=1)
    scheduler.start()
    
    # Uygulama kapandığında scheduler'ın durdurulmasını sağla (zorunlu)
    atexit.register(lambda: scheduler.shutdown())
    
    print("--- AgriSense SQL Server Versiyonu Başlatılıyor ---")
    # use_reloader=False ayarı, scheduler'ın iki kez başlamasını engeller.
    app.run(debug=True, use_reloader=False)