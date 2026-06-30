import requests
import time
from datetime import datetime

KULLANICI_ID    = 1623981172
KULLANICI_ADI   = "BabiOyundaya"
KONTROL_ARALIGI = 60
TELEGRAM_TOKEN  = "8930204525:AAFgt3Yp9DGp0CyiodnCWc2d8cxVEMksf3c"
TELEGRAM_CHAT   = "6074216089"

def telegram_gonder(mesaj):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": TELEGRAM_CHAT, "text": mesaj}, timeout=8)
    except Exception as e:
        print(f"  [!] Telegram hatasi: {e}")

def kullanici_durumu_al():
    url = "https://presence.roblox.com/v1/presence/users"
    try:
        r = requests.post(url, json={"userIds": [KULLANICI_ID]}, timeout=8)
        r.raise_for_status()
        data = r.json()
        if data.get("userPresences"):
            tip = data["userPresences"][0].get("userPresenceType", 0)
            if tip == 2:
                return "oyunda"
            elif tip in (1, 3):
                return "online"
            else:
                return "offline"
    except requests.exceptions.HTTPError as e:
        print(f"[{zaman()}] [!] HTTP hatasi: {e}")
    except requests.exceptions.RequestException as e:
        print(f"[{zaman()}] [!] Baglanti hatasi: {e}")
    return None

def zaman():
    return datetime.now().strftime("%H:%M:%S")

def main():
    print("=" * 50)
    print(f"   Roblox Notifier - {KULLANICI_ADI} takip ediliyor")
    print("=" * 50)
    print(f"   Kullanici ID   : {KULLANICI_ID}")
    print(f"   Kontrol suresi : her {KONTROL_ARALIGI} saniye")
    print("=" * 50)

    telegram_gonder(
        f"✅ Roblox Notifier baslatildi!\n"
        f"👤 Takip edilen: {KULLANICI_ADI}\n"
        f"🔄 Her {KONTROL_ARALIGI} saniyede bir kontrol edilecek."
    )

    onceki_durum = None
    hata_sayisi = 0

    while True:
        durum = kullanici_durumu_al()

        if durum is None:
            hata_sayisi += 1
            bekleme = 120 if hata_sayisi >= 5 else KONTROL_ARALIGI
            print(f"[{zaman()}] Hata ({hata_sayisi}), {bekleme}sn bekleniyor...")
            time.sleep(bekleme)
            continue

        hata_sayisi = 0

        if onceki_durum is None:
            # İlk kontrol
            if durum == "oyunda":
                mesaj = f"🎮 {KULLANICI_ADI} su an OYUNDA!"
            elif durum == "online":
                mesaj = f"🟡 {KULLANICI_ADI} su an AKTIF (oyunda degil)."
            else:
                mesaj = f"🔴 {KULLANICI_ADI} su an CEVRIMDISI."
            print(f"[{zaman()}] Baslangic: {durum}")
            telegram_gonder(mesaj)

        elif durum == "oyunda" and onceki_durum == "offline":
            # Çevrimdışı → Oyunda (direkt oyuna girdi)
            print(f"[{zaman()}] Cevrimdisi -> Oyunda!")
            telegram_gonder(
                f"🎮 {KULLANICI_ADI} ROBLOX'A GİRDİ ve OYUNA BASLADI!\n"
                f"⏰ Saat: {zaman()}"
            )

        elif durum == "oyunda" and onceki_durum == "online":
            # Aktif → Oyunda
            print(f"[{zaman()}] Aktif -> Oyunda!")
            telegram_gonder(
                f"🎮 {KULLANICI_ADI} OYUNA GIRDI!\n"
                f"⏰ Saat: {zaman()}"
            )

        elif durum == "online" and onceki_durum == "offline":
            # Çevrimdışı → Aktif (Roblox'a girdi ama oyun seçmedi)
            print(f"[{zaman()}] Cevrimdisi -> Aktif!")
            telegram_gonder(
                f"🟡 {KULLANICI_ADI} ROBLOX'A GİRDİ! (Henuz oyun secmedi)\n"
                f"⏰ Saat: {zaman()}"
            )

        elif durum == "online" and onceki_durum == "oyunda":
            # Oyunda → Aktif (oyundan çıktı ama Roblox'ta)
            print(f"[{zaman()}] Oyundan cikti, hala aktif.")
            telegram_gonder(
                f"🟡 {KULLANICI_ADI} OYUNDAN CIKTI ama hala Roblox'ta aktif.\n"
                f"⏰ Saat: {zaman()}"
            )

        elif durum == "offline" and onceki_durum != "offline":
            # Her türlü → Çevrimdışı
            print(f"[{zaman()}] Cevrimdisi oldu.")
            telegram_gonder(
                f"🔴 {KULLANICI_ADI} CEVRIMDISI OLDU.\n"
                f"⏰ Saat: {zaman()}"
            )

        onceki_durum = durum
        time.sleep(KONTROL_ARALIGI)

if __name__ == "__main__":
    main()