# 🌾 AgriSense: Akıllı Tarım İzleme Sistemi

![AgriSense Logo](https://i.imgur.com/kS9Qp2P.png) 
*(Bu bir yer tutucu resimdir, isterseniz projenize ait bir logo ekleyebilirsiniz.)*

AgriSense, IoT (Nesnelerin İnterneti) cihazlarından gelen sensör verilerini simüle eden, bu verileri **SQL Server** veritabanına kaydeden ve **Python Flask** tabanlı dinamik bir dashboard üzerinden görselleştiren akıllı bir tarım izleme sistemidir. Sistem, toprak nemi seviyelerine göre kural tabanlı anlık sulama uyarıları sunar.

## ✨ Temel Özellikler

* **SQL Server Entegrasyonu:** Tüm sensör verileri `pyodbc` kütüphanesi aracılığıyla MSSQL veritabanına güvenli bir şekilde kaydedilir ve çekilir.
* **Asenkron Veri Akışı:** `APScheduler` kullanılarak, web isteğinden bağımsız olarak arka planda düzenli aralıklarla (dakikalık) yeni simüle edilmiş veriler üretilir.
* **Dinamik Dashboard:** Flask ve Bootstrap 5 ile oluşturulmuş responsive arayüz.
* **Zaman Serisi Analizi:** `Chart.js` kütüphanesi ile geçmiş saatlik nem ortalamaları trend grafiği olarak görselleştirilir.
* **Kural Tabanlı Uyarılar:** Toprak nemi değerlerine göre (`< %30 Sulama Önerilir`, `< %20 Acil Sulama Gerekli`) otomatik renk kodlu uyarılar üretilir.

## 🛠️ Kullanılan Teknolojiler

* **Backend:** Python 3.x
* **Web Framework:** Flask
* **Veritabanı:** Microsoft SQL Server (MSSQL)
* **Veritabanı Bağlantısı:** pyodbc
* **Zamanlama:** APScheduler
* **Frontend:** HTML5, CSS3, Bootstrap 5
* **Görselleştirme:** Chart.js

## ⚙️ Kurulum Adımları

Projeyi yerel makinenizde çalıştırmak için aşağıdaki adımları sırasıyla takip edin.

### Adım 1: SQL Server Kurulumu

1.  **MSSQL ve ODBC Kurulumu:** Microsoft SQL Server ve sisteme uygun **ODBC Driver 17 for SQL Server** sürücüsünün kurulu olduğundan emin olun.
2.  **Veritabanını Oluşturma:** SQL Server Management Studio (SSMS) üzerinde bir `AgriSenseDB` adında veritabanı oluşturun ve aşağıdaki T-SQL komutlarını çalıştırarak `sensor_data` tablosunu kurun:
    ```sql
    -- AgriSenseDB veritabanı kurulduktan sonra bu komutları çalıştırın
    USE AgriSenseDB;
    GO

    CREATE TABLE sensor_data (
        id INT PRIMARY KEY IDENTITY(1,1),
        parcel_id NVARCHAR(100) NOT NULL,
        soil_moisture DECIMAL(5, 2) NOT NULL,
        air_temp DECIMAL(5, 2) NOT NULL,
        [timestamp] DATETIME DEFAULT GETDATE()
    );
    GO
    ```
3.  **Bağlantı Ayarı:** `app.py` dosyasındaki `CONNECTION_STRING` değişkeninin yerel SQL Server örneğinizle eşleştiğinden emin olun:
    ```python
    CONNECTION_STRING = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=localhost\\SQLEXPRESS;"  # Örnek sunucu adı
        "DATABASE=AgriSenseDB;"
        "Trusted_Connection=yes;"
    )
    ```

### Adım 2: Python Ortamını Hazırlama

1.  **Projeyi Klonlama:** GitHub üzerinden projeyi yerel makinenize indirin.
    ```bash
    git clone [REPO_ADRESİNİZ]
    cd AgriSense
    ```
2.  **Sanal Ortam Oluşturma (Önerilir):**
    ```bash
    python -m venv venv
    # Windows
    .\venv\Scripts\activate
    ```
3.  **Bağımlılıkları Kurma:** Projenin kullandığı tüm kütüphaneleri yükleyin.
    ```bash
    pip install -r requirements.txt
    ```

### Adım 3: Projeyi Çalıştırma

1.  **Uygulamayı Başlatın:**
    ```bash
    python app.py
    ```
    Uygulama, `APScheduler` sayesinde arka planda her dakika veritabanına yeni simülasyon verileri eklemeye başlayacaktır.

2.  **Dashboard'u Görüntüleme:**
    Tarayıcınızda aşağıdaki adrese gidin:
    ```
    [http://127.0.0.1:5000/](http://127.0.0.1:5000/)
    ```

### 💡 Not: Grafik Verilerinin Dolması

Uygulama yeni başlatıldığında, zaman serisi grafiği (son 12 saatlik nem eğilimi) tek bir veri noktası gösterebilir. Grafiğin tam olarak dolması ve saatlik ortalamaları gösterebilmesi için uygulamanın arka planda **birkaç saat** çalışması veya SSMS üzerinden geriye dönük sahte veriler eklenmesi gerekir.

## 🤝 Katkıda Bulunma

Projenin geliştirilmesine katkıda bulunmaktan çekinmeyin! Hata raporları veya öneriler için bir "Issue" açabilir veya doğrudan bir "Pull Request" gönderebilirsiniz.
