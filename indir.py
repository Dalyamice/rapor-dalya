# -*- coding: utf-8 -*-
"""OneDrive paylaşım linklerinden dosya indirir (v3).
Yöntem 1: SharePoint download.aspx kapısı (share token ile)
Yöntem 2: klasik ?download=1
İkisi de çerez takibi yapar; başarısızsa yanıtın ilk satırını loglar."""
import json
import sys
import urllib.request
import urllib.parse
from http.cookiejar import CookieJar

UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124 Safari/537.36",
      "Accept": "*/*"}


def ac(url: str) -> bytes:
    cj = CookieJar()
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    istek = urllib.request.Request(url, headers=UA)
    with op.open(istek, timeout=60) as y:
        return y.read()


def adaylar(link: str):
    # https://TENANT/:u:/g/personal/KULLANICI/TOKEN?e=xx  →  download.aspx?share=TOKEN
    p = urllib.parse.urlparse(link)
    parcalar = [x for x in p.path.split("/") if x]
    try:
        i = parcalar.index("personal")
        kullanici = parcalar[i + 1]
        token = parcalar[i + 2]
        yield (f"{p.scheme}://{p.netloc}/personal/{kullanici}"
               f"/_layouts/15/download.aspx?share={token}")
    except (ValueError, IndexError):
        pass
    ayrac = "&" if "?" in link else "?"
    yield link + ayrac + "download=1"


def indir(link: str, hedef: str) -> None:
    son_hata = None
    for url in adaylar(link):
        try:
            veri = ac(url)
            metin = veri.decode("utf-8-sig")
            json.loads(metin)
            with open(hedef, "w", encoding="utf-8") as f:
                f.write(metin)
            print(f"  ✓ {hedef}: {len(veri)//1024} KB")
            return
        except Exception as e:  # noqa: BLE001
            ozet = ""
            try:
                ozet = " | yanıt başı: " + veri[:80].decode("utf-8", "ignore").replace("\n", " ")
            except Exception:  # noqa: BLE001
                pass
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
            indir(link, dosya)
        except Exception as e:  # noqa: BLE001
            print(f"  ✗ {anahtar} indirilemedi: {e}"); hata = True
    sys.exit(1 if hata else 0)
