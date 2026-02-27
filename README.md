Endüstriyel Makine Tehlike Uyarı Sistemi 
Bu proje, endüstriyel üretim alanlarında makine kaynaklı iş kazalarını (özellikle el ve kol yaralanmalarını) önlemek amacıyla geliştirilmiş IoT tabanlı bir güvenlik prototipidir.

 Projenin Amacı
Sanal Güvenlik Bariyeri: Ultrasonik sensör ile görünmez bir bariyer oluşturarak tehlikeli bölgeye uzuv girişini algılamak. 
Çevresel İzleme: Ortam sıcaklığı, gürültü seviyesi ve hareketliliği takip ederek kestirimci bakım verisi sağlamak. 
Anlık Uyarı: Kritik durumlarda sesli (Buzzer) ve görsel (RGB LED) alarmlar üretmek. 
Web Dashboard: Tüm sensör verilerini Wi-Fi üzerinden bir web panelinde canlı olarak sunmak. 

 Donanım Bileşenleri & Bağlantılar
Sistem, ESP32 mikrodenetleyicisi üzerinde çalışmaktadır.
Donanım,ESP32 Pin,Görev
HC-SR04,GPIO 5 / 18,Sanal Bariyer (Mesafe)
PIR Sensör,GPIO 19,Hareket Algılama
DHT11,GPIO 4,Sıcaklık & Nem Takibi
Ses Sensörü,GPIO 34 (ADC),Gürültü Analizi
RGB LED,"GPIO 13, 12, 14","Görsel Uyarı (Kırmızı: Alarm, Yeşil: Güvenli)"
Buzzer,GPIO 25,Sesli Alarm


 Kurulum ve Çalıştırma
Bu depoyu klonlayın.
config_sample.py dosyasının adını config.py olarak değiştirin.
config.py içine kendi Wi-Fi adınızı ve şifrenizi girin.
Kodları Thonny IDE veya VS Code kullanarak ESP32 cihazınıza yükleyin. 


 Senaryolar ve Tepkiler
Kritik İhlal (<15cm): Kırmızı LED yanar, Buzzer öter, Web panelinde "KRİTİK MESAFE İHLALİ" görünür. 
Yüksek Ses (>2000 birim): Mor LED yanar, gürültü uyarısı verilir. 
Yüksek Sıcaklık (>25°C): Web panelinde tehlikeli sıcaklık uyarısı çıkar.