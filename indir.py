# -*- coding: utf-8 -*-
"""OneDrive paylaşım linklerinden dosya indirir (v4).
- download.aspx kapısı + ?download=1 yedeği, çerez takibi
- gorevler dosyasının gerçek Son Değiştirilme zamanını veri_zamani.txt'ye yazar"""
import json
import sys
import urllib.request
import urllib.parse
from email.utils import parsedate_to_datetime
from datetime import timedelta, timezone
from http.cookiejar import CookieJar

UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124 Safari/537.36",
      "Accept": "*/*"}
TRT = timezone(timedelta(hours=3))


def ac(url: str):
    cj = CookieJar()
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    istek = urllib.request.Request(url, headers=UA)
    with op.open(istek, timeout=60) as y:
        return y.read(), dict(y.headers)


def adaylar(link: str):
    p = urllib.parse.urlparse(link)
    parcalar = [x for x in p.path.split("/") if x]
    try:
        i = parcalar.index("personal")
        yield (f"{p.scheme}://{p.netloc}/personal/{parcalar[i+1]}"
               f"/_layouts/15/download.aspx?share={parcalar[i+2]}")
    except (ValueError, IndexError):
        pass
    yield link + ("&" if "?" in link else "?") + "download=1"


def indir(link: str, hedef: str, zaman_yaz: bool = False) -> None:
    son_hata = None
    for url in adaylar(link):
        veri = b""
        try:
            veri, basliklar = ac(url)
            metin = veri.decode("utf-8-sig")
            json.loads(metin)
            with open(hedef, "w", encoding="utf-8") as f:
                f.write(metin)
            print(f"  ✓ {hedef}: {len(veri)//1024} KB")
            if zaman_yaz:
                lm = basliklar.get("Last-Modified")
                if lm:
                    t = parsedate_to_datetime(lm).astimezone(TRT)
                    with open("veri_zamani.txt", "w") as f:
                        f.write(t.isoformat())
                    print(f"  ✓ veri zamanı: {t.isoformat()}")
            return
        except Exception as e:  # noqa: BLE001
            ozet = ""
            if veri:
                ozet = " | yanıt başı: " + veri[:80].decode("utf-8", "ignore").replace("\n", " ")
            son_hata = f"{e}{ozet}"
    raise RuntimeError(son_hata or "indirilemedi")


if __name__ == "__main__":
    with open("kaynaklar.json", encoding="utf-8") as f:
        k = json.load(f)
    hedefler = {"gorevler": "gorevler.json", "kutular": "kutular.json",
                "yorumlar": "yorumlar.json", "kisi_yorumlar": "kisi_yorumlar.json"}
    hata = False
    for anahtar, dosya in hedefler.items():
        link = k.get(anahtar, "")
        if not link.startswith("http"):
            print(f"  ✗ {anahtar}: kaynaklar.json içinde link yok!"); hata = True; continue
        try:
            indir(link, dosya, zaman_yaz=(anahtar == "gorevler"))
        except Exception as e:  # noqa: BLE001
            print(f"  ✗ {anahtar} indirilemedi: {e}"); hata = True
    sys.exit(1 if hata else 0)
