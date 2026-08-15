# -*- coding: utf-8 -*-
"""Premium haftalık rapor üretici.

Kullanım:  python3 premium_rapor.py "PLAN 1.xlsx" [cikti.html]
"""
from __future__ import annotations

import html
import sys
from datetime import date

from haftalik_rapor import haftalik_veri, anlatim, durum_sinifi, kisa, ilk_ad
from premium_sablon import TEMPLATE

import base64
import os

_BURASI = os.path.dirname(os.path.abspath(__file__))
_FRAUNCES = os.path.join(_BURASI, "f_fontsource-variable-fraunces-5.3.0/package/files")
_INTER = os.path.join(_BURASI, "f_fontsource-variable-inter-5.3.0/package/files")
_LATIN = "U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+2000-206F, U+2074, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD"
_LATIN_EXT = "U+0100-02AF, U+0300-0301, U+0303-0304, U+0308-0309, U+0323, U+0329, U+1E00-1EFF, U+2020, U+20A0-20AB, U+20AD-20C0, U+2113, U+2C60-2C7F, U+A720-A7FF"


def _f64(yol: str) -> str:
    with open(yol, "rb") as f:
        return base64.b64encode(f.read()).decode()


WEB_FONT_IMPORT = ("@import url('https://fonts.googleapis.com/css2?"
                   "family=Fraunces:ital,opsz,wght@0,9..144,300..700;1,9..144,300..700&"
                   "family=Inter:wght@100..900&display=swap');")
WEB_GSAP_TAGS = ('<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>\n'
                 '<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/ScrollTrigger.min.js"></script>')


def web_modu() -> bool:
    return os.environ.get("WEB_CDN") == "1"


def font_css() -> str:
    if web_modu():
        return WEB_FONT_IMPORT
    parcalar = []
    tanimlar = [
        ("Fraunces", "normal", f"{_FRAUNCES}/fraunces-latin-wght-normal.woff2", _LATIN),
        ("Fraunces", "normal", f"{_FRAUNCES}/fraunces-latin-ext-wght-normal.woff2", _LATIN_EXT),
        ("Fraunces", "italic", f"{_FRAUNCES}/fraunces-latin-wght-italic.woff2", _LATIN),
        ("Fraunces", "italic", f"{_FRAUNCES}/fraunces-latin-ext-wght-italic.woff2", _LATIN_EXT),
        ("Inter", "normal", f"{_INTER}/inter-latin-wght-normal.woff2", _LATIN),
        ("Inter", "normal", f"{_INTER}/inter-latin-ext-wght-normal.woff2", _LATIN_EXT),
    ]
    for aile, stil, yol, aralik in tanimlar:
        parcalar.append(
            f"@font-face {{ font-family:'{aile}'; font-style:{stil}; font-weight:100 900;"
            f" font-display:swap; src:url(data:font/woff2;base64,{_f64(yol)}) format('woff2-variations');"
            f" unicode-range:{aralik}; }}")
    return "\n".join(parcalar)


def gsap_js() -> str:
    if web_modu():
        return "/*CDN*/"
    with open(os.path.join(_BURASI, "package/dist/gsap.min.js"), encoding="utf-8") as f:
        g = f.read()
    with open(os.path.join(_BURASI, "package/dist/ScrollTrigger.min.js"), encoding="utf-8") as f:
        s = f.read()
    return g + "\n" + s

AY_AD = ["", "Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz",
         "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]

AVATAR_RENK = ["#3987e5", "#d95926", "#199e70", "#c98500", "#d55181",
               "#008300", "#9085e9", "#e66767", "#2a78d6", "#1baf7a", "#eb6834"]


def madalya_svg(renk: str, no: int) -> str:
    return (f'<svg width="26" height="26" viewBox="0 0 26 26" aria-label="{no}. sıra">'
            f'<path d="M9 1h3l2 6-4 1z" fill="{renk}" opacity=".55"/>'
            f'<path d="M17 1h-3l-2 6 4 1z" fill="{renk}" opacity=".8"/>'
            f'<circle cx="13" cy="15" r="8.5" fill="{renk}"/>'
            f'<circle cx="13" cy="15" r="6.2" fill="none" stroke="rgba(0,0,0,.25)" stroke-width="1"/>'
            f'<text x="13" y="18.6" text-anchor="middle" font-family="Inter,system-ui,sans-serif" '
            f'font-size="9.5" font-weight="800" fill="rgba(0,0,0,.62)">{no}</text></svg>')


def bas_harfler(isim: str) -> str:
    p = isim.split()
    return (p[0][0] + (p[-1][0] if len(p) > 1 else "")).upper()


def unvanlar(siralama: list[tuple[str, int, int, int]]) -> dict[str, str]:
    """[(isim, buhafta, toplam, acik)] → {isim: eğlenceli unvan}. Kişi başı bir unvan."""
    u: dict[str, str] = {}
    if not siralama:
        return u
    isimler = [s[0] for s in siralama]
    u[isimler[0]] = "Haftanın Şampiyonu"
    if len(siralama) > 1 and siralama[1][1] > 0:
        u[isimler[1]] = "Fotofinişte İkinci"
    if len(siralama) > 2 and siralama[2][1] > 0:
        u[isimler[2]] = "Kürsünün Üçüncüsü"
    def ata(isim, unvan):
        if isim not in u:
            u[isim] = unvan
    # sezon lideri: tüm zamanların en çok kapatanı
    sezon = max(siralama, key=lambda s: s[2])
    ata(sezon[0], "Sezonun Lideri")
    # en dolu ajanda: en çok açık iş
    dolu = max(siralama, key=lambda s: s[3])
    ata(dolu[0], "En Dolu Ajanda")
    # temiz masa: iş bitirmiş + en az açık iş
    bitirenler = [s for s in siralama if s[1] > 0]
    if bitirenler:
        temiz = min(bitirenler, key=lambda s: s[3])
        ata(temiz[0], "Temiz Masa")
    for isim, buhafta, _, acik in siralama:
        if isim not in u:
            u[isim] = "Bu Hafta Şarj Oldu" if buhafta == 0 else "İstikrarlı Oyuncu"
    return u


IKON = {
    "alert": '<svg viewBox="0 0 16 16" width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M8 2 14.5 13.5H1.5Z"/><path d="M8 6.5v3.2"/><circle cx="8" cy="11.9" r="0.4" fill="currentColor"/></svg>',
    "clock": '<svg viewBox="0 0 16 16" width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><circle cx="8" cy="8" r="6.2"/><path d="M8 4.8V8l2.4 1.6"/></svg>',
    "cal": '<svg viewBox="0 0 16 16" width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><rect x="2" y="3" width="12" height="11" rx="2"/><path d="M2 6.5h12M5.5 1.5v3M10.5 1.5v3"/></svg>',
    "check": '<svg viewBox="0 0 16 16" width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M2.5 8.5l3.5 3.5 7-8"/></svg>',
}


def esc(s) -> str:
    return html.escape(str(s if s is not None else ""))


def vurgulu_baslik(baslik: str) -> str:
    """Başlıktaki sayı öbeğini italik-mavi vurguya alır."""
    import re
    m = re.search(r"(\d+ iş bitti)", baslik)
    if m:
        return esc(baslik).replace(esc(m.group(1)), f'<span class="vurgu">{esc(m.group(1))}</span>')
    return esc(baslik)


def uret(v: dict) -> str:
    h, k = v["hafta"], v["kpi"]
    baslik, para = anlatim(v)
    d = date.fromisoformat(v["tarih"])
    aralik = f"{kisa(h['baslangic'])} – {kisa(h['bitis'])} {d.year}"

    # --- hero sayıları
    fark = h["tamamlanan"] - h["onceki_tamamlanan"]
    if h["onceki_tamamlanan"]:
        yon, cls = ("↑", "k-iyi") if fark > 0 else (("↓", "k-kotu") if fark < 0 else ("→", "k-notr"))
        kiyas = f'<div class="sayi-kiyas {cls}">{yon} geçen hafta {h["onceki_tamamlanan"]}</div>'
    else:
        kiyas = ""
    sayilar = f"""
      <div class="sayi"><div class="sayi-deger" data-count="{h['tamamlanan']}">{h['tamamlanan']}</div>
        <div class="sayi-ad">iş bitti</div>{kiyas}</div>
      <div class="sayi"><div class="sayi-deger" data-count="{h['eklenen']}">{h['eklenen']}</div>
        <div class="sayi-ad">yeni iş eklendi</div></div>
      <div class="sayi"><div class="sayi-deger" data-count="{k['acik']}">{k['acik']}</div>
        <div class="sayi-ad">açık iş</div></div>
      <div class="sayi"><div class="sayi-deger{' kirmizi' if k['geciken'] else ''}" data-count="{k['geciken']}">{k['geciken']}</div>
        <div class="sayi-ad">geciken</div></div>"""

    # --- organizasyonlar (+ tıkla-aç Claude yorumu)
    import json as _json
    yorum_yolu = os.path.join(_BURASI, "yorumlar.json")
    yorumlar: dict = {}
    if os.path.exists(yorum_yolu):
        with open(yorum_yolu, encoding="utf-8") as f:
            yorumlar = {k2: v2 for k2, v2 in _json.load(f).items() if not k2.startswith("_")}

    gelecek = [o for o in v["orglar"] if o["kalan_gun"] >= -3]
    ilk, kalanlar = gelecek[:10], gelecek[10:]

    def org_satir(o):
        cls, etiket = durum_sinifi(o)
        gun = o["kalan_gun"]
        if gun < 0:
            zaman = "şu an devam ediyor"
        elif gun == 0:
            zaman = "bugün başlıyor!"
        elif gun <= 14:
            zaman = f"{gun} gün kaldı"
        else:
            zaman = kisa(o["baslangic"])
        oran = round(100 * o["tamam"] / o["toplam"]) if o["toplam"] else 100
        yorum = yorumlar.get(o["ad"], "Bu hafta için bu organizasyona özel bir not yazmadım — "
                                       "sayılar yeterince konuşuyor: "
                                       f"{o['tamam']}/{o['toplam']} iş tamam, {o['acik']} iş açık.")
        aciklar = "".join(
            f'<li{" class=gec" if a["geciken"] else ""}>{esc(a["baslik"][:90])}'
            f' <span class="kim">— {esc(", ".join(ilk_ad(x) for x in a["kisiler"]))}</span>'
            + (f' <span class="tarih-gec">({kisa(a["son"])}{", gecikti!" if a["geciken"] else ""})</span>' if a["son"] else "")
            + '</li>'
            for a in o.get("acik_isler", [])[:6])
        bitenler = "".join(f'<li>{esc(b[:90])}</li>' for b in o.get("bitenler_hafta", [])[:5])
        listeler = ""
        if aciklar or bitenler:
            listeler = f"""<div class="od-listeler">
              {f'<div class="od-liste aciklar"><h4>Açık işler</h4><ul>{aciklar}</ul></div>' if aciklar else ''}
              {f'<div class="od-liste bitenler"><h4>Bu hafta bitenler</h4><ul>{bitenler}</ul></div>' if bitenler else ''}
            </div>"""
        return f"""
        <div class="org-blok {cls}">
          <button class="org-satir" aria-expanded="false">
            <div class="o-ust"><span class="dot"></span><span class="o-ad">{esc(o['ad'])}</span>
              <span class="o-zaman">{zaman}</span></div>
            <div class="o-alt"><span class="o-durum">{etiket}</span></div>
            <div class="o-sag">
              <span class="mtrack"><span class="mfill" style="--w:{oran}%"></span></span>
              <span class="mtxt">{o['acik']} açık · %{oran} hazır</span>
            </div>
            <span class="cev"><svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6l5 5 5-5"/></svg></span>
          </button>
          <div class="org-detay"><div class="od-ic"><div class="od-kutu">
            <p class="od-yorum">{esc(yorum)}</p>
            {listeler}
          </div></div></div>
        </div>"""

    orglar = "".join(org_satir(o) for o in ilk)
    org_devam = ""
    if kalanlar:
        org_devam = (f'<details class="devam"><summary>İleri tarihli {len(kalanlar)} organizasyon daha</summary>'
                     f'<div class="org-liste">{"".join(org_satir(o) for o in kalanlar)}</div></details>')

    # --- kişiler
    yuk = {x["isim"]: x["acik"] for x in v["kisi_yuku"]}
    isimler = list(dict.fromkeys([i for i, _ in h["kisi"]] + list(yuk.keys())))
    maxb = max([a for _, a in h["kisi"]], default=1) or 1
    kisiler = ""
    for isim in isimler:
        biten = dict(h["kisi"]).get(isim, 0)
        acik = yuk.get(isim, 0)
        w = round(100 * biten / maxb)
        sifir = " sifir" if biten == 0 else ""
        kisiler += f"""
        <div class="k-satir" data-tip="{esc(isim)}: bu hafta {biten} iş bitirdi, üzerinde {acik} açık iş var">
          <span class="k-ad">{esc(isim)}</span>
          <span class="k-bar"><span class="k-fill{sifir}" style="--w:{w}%"></span></span>
          <span class="k-say">{biten if biten else '–'}</span>
          <span class="k-acik">{acik} açık</span>
        </div>"""
    sahipsiz = ""
    if k["atanmamis"]:
        sahipsiz = (f'<p class="not-satir">{IKON["alert"]}<span>Ayrıca <b>{k["atanmamis"]} açık işin</b> '
                    f'üzerinde kimse yok — pazartesi dağıtmakta fayda var.</span></p>')

    # --- gecikenler
    if v["gecikenler"]:
        g_baslik = "Takılan işler"
        g_alt = "Bunlar son tarihini geçmiş — çoğu küçük bir dokunuşla kapanır."
        rows = "".join(f"""
        <div class="gec-satir">
          <div class="g-baslik">{esc(g['baslik'])}</div>
          <div class="g-meta">{esc(g['kutu'])}</div>
          <div class="g-sure"><div class="g-gun">{g['gun']} gün</div>
            <div class="g-kisi">{esc(', '.join(ilk_ad(x) for x in g['kisiler']))}</div></div>
        </div>""" for g in v["gecikenler"])
        gecikenler = f'<div class="gec-liste">{rows}</div>'
    else:
        g_baslik = "Takılan iş yok"
        g_alt = "Hiçbir görev son tarihini geçmemiş."
        gecikenler = f'<p class="temiz">{IKON["check"]}<span>Tertemiz bir hafta — böyle devam.</span></p>'

    # --- radar
    radar = []
    for o in v["orglar"]:
        if 0 <= o["kalan_gun"] <= 21:
            radar.append(f'<li>{IKON["cal"]}<span class="r-txt"><b>{esc(o["ad"])}</b> — '
                         f'{o["kalan_gun"]} gün kaldı, {o["acik"]} iş açık</span></li>')
    for y in v["yaklasan"]:
        radar.append(f'<li>{IKON["clock"]}<span class="r-txt"><b>{kisa(y["son"])}:</b> {esc(y["baslik"])} '
                     f'<span class="soluk">({esc(", ".join(ilk_ad(x) for x in y["kisiler"]))})</span></span></li>')
    if not radar:
        radar.append('<li><span class="r-txt">Yakın vadede kritik tarih görünmüyor.</span></li>')

    # --- kişi kişi bu hafta (nötr pano: açtığı + tamamladığı)
    hafta_map = dict(h["kisi"])
    toplam_map = h.get("kisi_toplam", {})
    acan_h = h.get("kisi_acan_hafta", {})
    acan_t = h.get("kisi_acan_toplam", {})
    tum = list(dict.fromkeys(list(hafta_map.keys()) + list(yuk.keys())
                             + list(toplam_map.keys()) + list(acan_t.keys())))
    siralama = sorted(
        [(i, hafta_map.get(i, 0), toplam_map.get(i, 0), yuk.get(i, 0)) for i in tum],
        key=lambda s: (-s[1], -acan_h.get(s[0], 0), -s[2]))
    kisi_yorum_yolu = os.path.join(_BURASI, "kisi_yorumlar.json")
    kisi_yorumlar: dict = {}
    if os.path.exists(kisi_yorum_yolu):
        with open(kisi_yorum_yolu, encoding="utf-8") as f:
            kisi_yorumlar = {k2: v2 for k2, v2 in _json.load(f).items() if not k2.startswith("_")}
    kisi_detay = h.get("kisi_detay", {})
    lig_rows = ""
    for idx, (isim, buhafta, toplam, acik) in enumerate(siralama):
        no = idx + 1
        rutbe = f'<span class="rütbe">{no}</span>'
        renk = AVATAR_RENK[idx % len(AVATAR_RENK)]
        acti_h, acti_t = acan_h.get(isim, 0), acan_t.get(isim, 0)
        yorum = kisi_yorumlar.get(isim, f"{ilk_ad(isim)} için bu hafta ayrıca not yazmadım — "
                                        f"bu hafta {acti_h} görev açtı, {buhafta} iş bitirdi, "
                                        f"üzerinde {acik} açık iş var.")
        det = kisi_detay.get(isim, {"bitenler": [], "aciklar": []})
        bitenler = "".join(
            f'<li>{esc(b["baslik"][:80])} <span class="kim">— {esc(b["kutu"] or "")}</span></li>'
            for b in det["bitenler"][:5])
        if len(det["bitenler"]) > 5:
            bitenler += f'<li><span class="kim">… ve {len(det["bitenler"]) - 5} iş daha</span></li>'
        aciklar = "".join(
            f'<li{" class=gec" if a["geciken"] else ""}>{esc(a["baslik"][:80])}'
            f' <span class="kim">— {esc(a["kutu"] or "")}{", GECİKMİŞ" if a["geciken"] else ""}</span></li>'
            for a in det["aciklar"][:5])
        if len(det["aciklar"]) > 5:
            aciklar += f'<li><span class="kim">… ve {len(det["aciklar"]) - 5} iş daha</span></li>'
        listeler = ""
        if bitenler or aciklar:
            listeler = f"""<div class="od-listeler">
              {f'<div class="od-liste bitenler"><h4>Bu hafta bitirdikleri</h4><ul>{bitenler}</ul></div>' if bitenler else ''}
              {f'<div class="od-liste aciklar"><h4>Üzerindeki işlerden öne çıkanlar</h4><ul>{aciklar}</ul></div>' if aciklar else ''}
            </div>"""
        lig_rows += f"""
        <tr class="lig-satir" tabindex="0" aria-expanded="false"
            data-tip="{esc(isim)}: bu hafta {acti_h} görev açtı, {buhafta} iş tamamladı (toplam: {acti_t} açtı, {toplam} tamamladı); üzerinde {acik} açık iş var — yorum için tıklayın">
          <td class="siralama">{rutbe}</td>
          <td><div class="oyuncu"><span class="avatar" style="--av:{renk}">{esc(bas_harfler(isim))}</span>
            <span><span class="o-isim">{esc(isim)}</span></span></div></td>
          <td class="sag"><span class="cift"><span class="lig-buhafta" data-count-scroll="{acti_h}">{acti_h}</span>
            <span class="toplami">toplam {acti_t}</span></span></td>
          <td class="sag"><span class="cift yesil"><span class="lig-buhafta" data-count-scroll="{buhafta}">{buhafta}</span>
            <span class="toplami">toplam {toplam}</span></span></td>
          <td class="sag gizle"><span class="lig-kucuk">{acik}</span></td>
          <td class="lig-cev"><svg width="15" height="15" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6l5 5 5-5"/></svg></td>
        </tr>
        <tr class="lig-detay-tr kapali"><td colspan="6">
          <div class="lig-detay"><div class="od-ic"><div class="od-kutu">
            <p class="od-yorum">{esc(yorum)}</p>
            {listeler}
          </div></div></div>
        </td></tr>"""

    out = TEMPLATE
    out = out.replace("__FONT_CSS__", font_css())
    out = out.replace("__GSAP_JS__", gsap_js())
    if web_modu():
        out = out.replace("<script>\n/*CDN*/\n</script>", WEB_GSAP_TAGS)
    out = out.replace("__LIG__", lig_rows)
    for anahtar, deger in {
        "__TITLE__": f"{esc(v['plan_adi'])} · Haftalık Rapor · {aralik}",
        "__PLAN_ADI__": esc(v["plan_adi"]),
        "__ARALIK__": aralik,
        "__BASLIK__": vurgulu_baslik(baslik),
        "__ANLATI__": esc(para),
        "__SAYILAR__": sayilar,
        "__ORGLAR__": orglar,
        "__ORG_DEVAM__": org_devam,
        "__KISILER__": kisiler,
        "__SAHIPSIZ__": sahipsiz,
        "__GECIKEN_BASLIK__": g_baslik,
        "__GECIKEN_ALT__": g_alt,
        "__GECIKENLER__": gecikenler,
        "__RADAR__": "".join(radar),
    }.items():
        out = out.replace(anahtar, deger)
    return out


if __name__ == "__main__":
    xlsx = sys.argv[1]
    cikti = sys.argv[2] if len(sys.argv) > 2 else "haftalik_rapor_premium.html"
    v = haftalik_veri(xlsx)
    with open(cikti, "w", encoding="utf-8") as f:
        f.write(uret(v))
    print(f"✓ {cikti} üretildi")
