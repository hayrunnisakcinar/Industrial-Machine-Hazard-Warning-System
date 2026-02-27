import network
import socket
import time
from machine import Pin, ADC, time_pulse_us
import dht
from config import SSID, PASSWORD

# ===================== LIMITLER =====================
SICAKLIK_LIMIT_TEHLIKE = 40.0
MESAFE_LIMIT_TEHLIKE = 15
SES_LIMIT_TEHLIKE = 2000

# ===================== PIN TANIMLARI =====================
trig = Pin(4, Pin.OUT)
echo = Pin(18, Pin.IN)
pir = Pin(27, Pin.IN)

dht_sensoru = dht.DHT11(Pin(32))
ses_pin = ADC(Pin(34))
ses_pin.atten(ADC.ATTN_11DB)

buzzer = Pin(33, Pin.OUT)
led_r = Pin(25, Pin.OUT)
led_g = Pin(26, Pin.OUT)
led_b = Pin(14, Pin.OUT)

# ===================== HAFIZA =====================
hafiza_min_mesafe = 250
hafiza_max_ses = 0
son_hareket_zamani = 0
son_risk_kaydi = "Sistem temiz. Henüz risk algılanmadı."

# ===================== YARDIMCI FONKSİYONLAR =====================
def rgb_yak(r, g, b):
    led_r.value(r)
    led_g.value(g)
    led_b.value(b)

def mesafe_oku():
    trig.value(0)
    time.sleep_us(5)
    trig.value(1)
    time.sleep_us(10)
    trig.value(0)

    try:
        sure = time_pulse_us(echo, 1, 30000)
        dist = (sure * 0.0343) / 2
        if dist < 2 or dist > 250:
            return 250
        return round(dist, 1)
    except:
        return 250

def dht_oku():
    try:
        dht_sensoru.measure()
        return dht_sensoru.temperature(), dht_sensoru.humidity()
    except:
        return None, None

def ses_anlik_oku():
    return ses_pin.read()

# ===================== WIFI =====================
def wifi_baglan():
    rgb_yak(1, 1, 0)
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if not wlan.isconnected():
        print(f"{SSID} ağına bağlanılıyor...")
        wlan.connect(SSID, PASSWORD)

        sayac = 0
        while not wlan.isconnected() and sayac < 25:
            time.sleep(0.5)
            sayac += 1
            print(".", end="")

    if wlan.isconnected():
        ip = wlan.ifconfig()[0]
        print("\nBağlantı başarılı! IP:", ip)
        rgb_yak(0, 1, 0)
        buzzer.value(1)
        time.sleep(0.2)
        buzzer.value(0)
        return ip
    else:
        print("Bağlantı başarısız!")
        rgb_yak(1, 0, 0)
        return None

# ===================== WEB SAYFASI =====================
def web_sayfasi_olustur(sicaklik, nem, mesafe, hareket, ses, risk):

    sicaklik_str = sicaklik if sicaklik is not None else "--"
    nem_str = nem if nem is not None else "--"

    html = f"""
    <html>
    <head>
    <meta http-equiv="refresh" content="1">
    <title>Guvenlik Istasyonu</title>
    </head>
    <body style="background:#2c3e50;color:white;text-align:center;">
    <h1>ENDUSTRIYEL UYARI SISTEMI</h1>
    <h2>Son Risk: {risk}</h2>
    <p>Sicaklik: {sicaklik_str} °C</p>
    <p>Nem: {nem_str} %</p>
    <p>Mesafe: {mesafe} cm</p>
    <p>Ses: {ses}</p>
    <p>Hareket: {"VAR" if hareket else "YOK"}</p>
    </body>
    </html>
    """
    return html

# ===================== ANA PROGRAM =====================
ip_adresi = wifi_baglan()

if ip_adresi:
    soket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soket.bind(('', 80))
    soket.listen(5)
    soket.settimeout(0.1)

    print("Tarayıcıdan gir:", "http://" + ip_adresi)

    son_dht_okuma = 0
    sicaklik_w, nem_w = None, None

    while True:

        mes_anlik = mesafe_oku()
        har_anlik = pir.value()
        ses_anlik = ses_anlik_oku()

        # DHT 2 saniyede bir
        if time.time() - son_dht_okuma > 2:
            sicaklik_w, nem_w = dht_oku()
            son_dht_okuma = time.time()

        # Risk kontrol
        if mes_anlik < MESAFE_LIMIT_TEHLIKE:
            son_risk_kaydi = "KRITIK MESAFE IHLALI"
            rgb_yak(1, 0, 0)
            buzzer.value(1)

        elif ses_anlik > SES_LIMIT_TEHLIKE:
            son_risk_kaydi = "YUKSEK SES ALGILANDI"
            rgb_yak(1, 0, 1)
            buzzer.value(0)

        elif sicaklik_w and sicaklik_w > SICAKLIK_LIMIT_TEHLIKE:
            son_risk_kaydi = "TEHLIKELI SICAKLIK"
            rgb_yak(1, 1, 0)
            buzzer.value(0)

        elif har_anlik == 1:
            son_risk_kaydi = "HAREKET ALGILANDI"
            rgb_yak(0, 0, 1)
            buzzer.value(0)

        else:
            rgb_yak(0, 1, 0)
            buzzer.value(0)

        # Web server
        try:
            conn, addr = soket.accept()
            request = conn.recv(1024)

            response = web_sayfasi_olustur(
                sicaklik_w,
                nem_w,
                mes_anlik,
                har_anlik,
                ses_anlik,
                son_risk_kaydi
            )

            conn.send("HTTP/1.1 200 OK\n")
            conn.send("Content-Type: text/html\n\n")
            conn.sendall(response)
            conn.close()

        except OSError:
            pass