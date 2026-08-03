import requests
import json
import os
from pathlib import Path

KULLANICI_ID     = 1623981172
KULLANICI_ADI    = "BabiOyundaya"
TELEGRAM_TOKEN   = os.environ.get("TELEGRAM_TOKEN", "8930204525:AAFgt3Yp9DGp0CyiodnCWc2d8cxVEMksf3c")
TELEGRAM_CHATLER = ["6074216089", "8796557376"]  # Sen + arkadaşın
DURUM_DOSYASI    = Path("durum.json")


def telegram_gonder(mesaj):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    for chat_id in TELEGRAM_CHATLER:
        try:
            requests.post(url, json={"chat_id": chat_id, "text": mesaj}, timeout=8)
        except Exception as e:
            print(f"  [!] Telegram hatasi ({chat_id}): {e}")


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
    except Exception as e:
        print(f"[!] API hatasi: {e}")
    return None


def onceki_durumu_oku():
    if DURUM_DOSYASI.exists():
        try:
            return json.loads(DURUM_DOSYASI.read_text()).get("durum")
        except Exception:
            return None
    return None


def durumu_kaydet(durum):
    DURUM_DOSYASI.write_text(json.dumps({"durum": durum}))


def main():
    yeni_durum = kullanici_durumu_al()
    if yeni_durum is None:
        print("Durum alinamadi, bu calismada bildirim gonderilmeyecek.")
        return

    onceki_durum = onceki_durumu_oku()
    print(f"Onceki: {onceki_durum} -> Yeni: {yeni_durum}")

    if onceki_durum is None:
        # Sistem ilk kez calisiyor
        if yeni_durum == "oyunda":
            telegram_gonder(f"🎮 {KULLANICI_ADI} su an OYUNDA!")
        elif yeni_durum == "online":
            telegram_gonder(f"🟡 {KULLANICI_ADI} su an AKTIF (oyunda degil).")
        else:
            telegram_gonder(f"🔴 {KULLANICI_ADI} su an CEVRIMDISI.")

    elif yeni_durum != onceki_durum:
        if yeni_durum == "oyunda" and onceki_durum == "offline":
            telegram_gonder(f"🎮 {KULLANICI_ADI} ROBLOX'A GİRDİ ve OYUNA BASLADI!")
        elif yeni_durum == "oyunda" and onceki_durum == "online":
            telegram_gonder(f"🎮 {KULLANICI_ADI} OYUNA GIRDI!")
        elif yeni_durum == "online" and onceki_durum == "offline":
            telegram_gonder(f"🟡 {KULLANICI_ADI} ROBLOX'A GİRDİ! (Henuz oyun secmedi)")
        elif yeni_durum == "online" and onceki_durum == "oyunda":
            telegram_gonder(f"🟡 {KULLANICI_ADI} OYUNDAN CIKTI ama hala Roblox'ta aktif.")
        elif yeni_durum == "offline" and onceki_durum != "offline":
            telegram_gonder(f"🔴 {KULLANICI_ADI} CEVRIMDISI OLDU.")
    else:
        print("Durum degismedi, bildirim yok.")

    durumu_kaydet(yeni_durum)


if __name__ == "__main__":
    main()
