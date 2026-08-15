# -*- coding: utf-8 -*-
"""OneDrive paylaşım linklerinden güncel veri ve yorum dosyalarını indirir.
(v2 — düz depo yapısı: tüm dosyalar ana dizinde)"""
import json
import sys
import urllib.request


def indir(link: str, hedef: str) -> None:
    ayrac = "&" if "?" in link else "?"
    url = link + ayrac + "download=1"
    istek = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"})
    with urllib.request.urlopen(istek, timeout=60) as y:
        veri = y.read()
    metin = veri.decode("utf-8-sig")
    json.loads(metin)  # HTML dönerse burada patlar
    with open(hedef, "w", encoding="utf-8") as f:
        f.write(metin)
    print(f"  ✓ {hedef}: {len(veri)//1024} KB")


if __name__ == "__main__":
    with open("kaynaklar.json", encoding="utf-8") as f:
        k = json.load(f)
    hedefler = {
        "gorevler": "gorevler.json",
        "kutular": "kutular.json",
        "yorumlar": "yorumlar.json",
        "kisi_yorumlar": "kisi_yorumlar.json",
    }
    hata = False
    for anahtar, dosya in hedefler.items():
        link = k.get(anahtar, "")
        if not link.startswith("http"):
            print(f"  ✗ {anahtar}: kaynaklar.json içinde link yok!"); hata = True; continue
        try:
            indir(link, dosya)
        except Exception as e:  # noqa: BLE001
            print(f"  ✗ {anahtar} indirilemedi: {e}"); hata = True
    sys.exit(1 if hata else 0)
