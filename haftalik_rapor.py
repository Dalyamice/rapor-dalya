# -*- coding: utf-8 -*-
"""Planner Excel dışa aktarımından samimi, okuması kolay HAFTALIK HTML rapor üretir.

Kullanım:  python3 haftalik_rapor.py "PLAN 1.xlsx" [cikti.html]
"""
from __future__ import annotations

import html
import re
import sys
from collections import Counter
from datetime import date, timedelta

import pandas as pd

from analiz import analiz_et, etkinlik_tarihi, OPERASYONEL

GUNLER = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
AY_AD = ["", "Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz",
         "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]


def kisa(iso: str) -> str:
    d = date.fromisoformat(iso)
    return f"{d.day} {AY_AD[d.month]}"


def esc(s) -> str:
    return html.escape(str(s if s is not None else ""))


def ilk_ad(tam: str) -> str:
    return tam.split()[0] if tam and tam != "Atanmamış" else tam


# --------------------------------------------------------------------------
def haftalik_veri(xlsx_yolu: str) -> dict:
    """Günlük analizin üstüne haftalık pencere hesapları ekler."""
    v = analiz_et(xlsx_yolu)
    bugun = date.fromisoformat(v["tarih"])
    h_bas = bugun - timedelta(days=6)          # bu hafta: son 7 gün
    o_bas, o_son = h_bas - timedelta(days=7), h_bas - timedelta(days=1)

    xl = pd.ExcelFile(xlsx_yolu)
    t = xl.parse("Görevler")
    u = xl.parse("Kullanıcılar")
    k = xl.parse("Kutular")
    for df in (t, u, k):
        df.columns = [c.strip() for c in df.columns]
    umap = {r["Kullanıcı Kimliği"]: re.sub(r"\s+", " ", str(r["Kullanıcı Adı"])).strip()
            for _, r in u.iterrows()}
    kmap = {r["Kutu Kimliği"]: str(r["Demet Adı"]).strip() for _, r in k.iterrows()}
    t["kutu"] = t["Kutu"].map(kmap)
    t["ct"] = pd.to_datetime(t["Tamamlanma Tarihi"], errors="coerce").dt.date
    t["cr"] = pd.to_datetime(t["Oluşturma Tarihi"], errors="coerce").dt.date

    bu = t[(t["ct"].notna()) & (t["ct"] >= h_bas) & (t["ct"] <= bugun)]
    onceki = t[(t["ct"].notna()) & (t["ct"] >= o_bas) & (t["ct"] <= o_son)]
    yeni = t[(t["cr"].notna()) & (t["cr"] >= h_bas) & (t["cr"] <= bugun)]

    kisi_hafta = Counter()
    for _, r in bu.iterrows():
        isim = umap.get(str(r["Tarafından tamamlanmıştır"]).strip())
        if isim:
            kisi_hafta[isim] += 1

    kisi_toplam = Counter()  # tüm zamanlar: kişinin kapattığı iş
    for _, r in t[t["ct"].notna()].iterrows():
        isim = umap.get(str(r["Tarafından tamamlanmıştır"]).strip())
        if isim:
            kisi_toplam[isim] += 1

    # kişinin AÇTIĞI (oluşturduğu) görevler — bu hafta ve toplam
    kisi_acan_hafta, kisi_acan_toplam = Counter(), Counter()
    for _, r in t.iterrows():
        isim = umap.get(str(r.get("Oluşturan", "")).strip())
        if isim:
            kisi_acan_toplam[isim] += 1
            if r["cr"] and r["cr"] >= h_bas:
                kisi_acan_hafta[isim] += 1

    org_hafta = Counter(bu["kutu"].dropna())

    # kişi başına detay: bu hafta bitirdikleri + açık işleri
    kisi_detay: dict = {}
    for _, r in bu.iterrows():
        isim = umap.get(str(r["Tarafından tamamlanmıştır"]).strip())
        if isim:
            kisi_detay.setdefault(isim, {"bitenler": [], "aciklar": []})
            kisi_detay[isim]["bitenler"].append(
                {"baslik": str(r["Görev Adı"]).strip(), "kutu": r["kutu"]})
    acik_t = t[t["Durum"] != "Tamamlandı"]
    for _, r in acik_t.iterrows():
        if pd.notna(r["Atanan"]):
            for uid in str(r["Atanan"]).split(";"):
                isim = umap.get(uid.strip())
                if isim:
                    kisi_detay.setdefault(isim, {"bitenler": [], "aciklar": []})
                    kisi_detay[isim]["aciklar"].append({
                        "baslik": str(r["Görev Adı"]).strip(), "kutu": r["kutu"],
                        "geciken": bool(r["Geciken"] == True)})  # noqa: E712
    for d in kisi_detay.values():
        d["aciklar"].sort(key=lambda x: not x["geciken"])

    v["hafta"] = {
        "baslangic": h_bas.isoformat(),
        "bitis": bugun.isoformat(),
        "tamamlanan": len(bu),
        "onceki_tamamlanan": len(onceki),
        "eklenen": len(yeni),
        "kisi": kisi_hafta.most_common(),
        "kisi_toplam": dict(kisi_toplam),
        "kisi_acan_hafta": dict(kisi_acan_hafta),
        "kisi_acan_toplam": dict(kisi_acan_toplam),
        "kisi_detay": kisi_detay,
        "org": org_hafta.most_common(),
    }
    return v


# --------------------------------------------------------------------------
def durum_sinifi(o: dict) -> tuple[str, str]:
    """(css sınıfı, samimi durum etiketi)"""
    if o["acik"] == 0:
        return "s-hazir", "her şey tamam"
    if o["geciken"] > 0:
        return "s-dikkat", f"{o['geciken']} geciken iş var"
    if 0 <= o["kalan_gun"] <= 14:
        return "s-dikkat", "tarih çok yakın!"
    if 0 <= o["kalan_gun"] <= 30 and o["acik"] >= 3:
        return "s-dikkat", "tarih yaklaşıyor, iş çok"
    if o["hafta_tamam"] > 0:
        return "s-yolunda", "yolunda gidiyor"
    if 0 <= o["kalan_gun"] <= 60:
        return "s-sessiz", "bu hafta ses yoktu"
    return "s-sessiz", "henüz sırası gelmedi"


def anlatim(v: dict) -> tuple[str, str]:
    """(başlık cümlesi, paragraf) — haftanın sohbet tadında özeti."""
    h, k = v["hafta"], v["kpi"]
    fark = h["tamamlanan"] - h["onceki_tamamlanan"]
    if h["tamamlanan"] == 0:
        baslik = "Sakin bir hafta geçti."
        para = "Bu hafta tamamlanan görev olmadı."
        if k["geciken"]:
            para += f" Ama {k['geciken']} geciken iş hâlâ bekliyor; pazartesi ilk iş onlara bakmakta fayda var."
        return baslik, para

    if fark > 5:
        baslik = f"Güçlü bir hafta: {h['tamamlanan']} iş bitti."
        tempo = f"geçen haftaki {h['onceki_tamamlanan']} görevin epey üzerinde — tempo yükseliyor"
    elif fark < -5:
        baslik = f"Bu hafta {h['tamamlanan']} iş bitti, tempo biraz düştü."
        tempo = f"geçen hafta {h['onceki_tamamlanan']} görev bitmişti"
    else:
        baslik = f"İstikrarlı bir hafta: {h['tamamlanan']} iş bitti."
        tempo = "geçen haftayla benzer tempo"
    para = f"Ekip bu hafta {h['tamamlanan']} görevi tamamladı ({tempo}). "
    if h["eklenen"]:
        para += f"Bu arada plana {h['eklenen']} yeni iş eklendi. "

    if h["kisi"]:
        isim, adet = h["kisi"][0]
        para += f"Haftanın en üretken ismi {adet} görevle {isim}"
        if len(h["kisi"]) > 1:
            i2, a2 = h["kisi"][1]
            para += f"; hemen ardından {a2} görevle {i2} geliyor"
        para += ". "
    if h["org"]:
        oad, oadet = h["org"][0]
        para += f"En çok mesafe alınan organizasyon {oad} oldu ({oadet} iş kapandı). "

    uyarilar = []
    yakin_risk = [o for o in v["orglar"] if o["risk"] and 0 <= o["kalan_gun"] <= 30]
    if yakin_risk:
        o = yakin_risk[0]
        uyarilar.append(f"{o['ad']} kapıda ({o['kalan_gun']} gün kaldı) ve {o['acik']} iş açık")
    if k["geciken"]:
        uyarilar.append(f"{k['geciken']} görev gecikmiş durumda")
    if k["atanmamis"]:
        uyarilar.append(f"{k['atanmamis']} açık işin sahibi yok")
    if uyarilar:
        para += "Gelecek haftaya not: " + "; ".join(uyarilar) + "."
    else:
        para += "Aciliyet gerektiren bir konu görünmüyor — temiz bir hafta."
    return baslik, para


# --------------------------------------------------------------------------
IKON = {
    "check": '<svg viewBox="0 0 16 16" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2.5 8.5l3.5 3.5 7-8"/></svg>',
    "clock": '<svg viewBox="0 0 16 16" width="13" height="13" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"><circle cx="8" cy="8" r="6.2"/><path d="M8 4.8V8l2.4 1.6"/></svg>',
    "alert": '<svg viewBox="0 0 16 16" width="13" height="13" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M8 2 14.5 13.5H1.5Z"/><path d="M8 6.5v3.2"/><circle cx="8" cy="11.9" r="0.4" fill="currentColor"/></svg>',
    "cal": '<svg viewBox="0 0 16 16" width="13" height="13" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"><rect x="2" y="3" width="12" height="11" rx="2"/><path d="M2 6.5h12M5.5 1.5v3M10.5 1.5v3"/></svg>',
}


def uret(v: dict) -> str:
    h, k = v["hafta"], v["kpi"]
    baslik, para = anlatim(v)
    d = date.fromisoformat(v["tarih"])

    # --- özet şeridi (kompakt, anlatının altında)
    fark = h["tamamlanan"] - h["onceki_tamamlanan"]
    fark_html = ""
    if h["onceki_tamamlanan"]:
        yon, cls = ("↑", "iyi") if fark > 0 else (("↓", "kotu") if fark < 0 else ("→", "notr"))
        fark_html = f'<span class="f-{cls}">{yon} geçen hafta {h["onceki_tamamlanan"]}</span>'
    serit = f"""
    <div class="serit">
      <div class="s-item"><b>{h['tamamlanan']}</b> iş bitti {fark_html}</div>
      <div class="s-item"><b>{h['eklenen']}</b> yeni iş</div>
      <div class="s-item"><b>{k['acik']}</b> açık iş</div>
      <div class="s-item{' s-kirmizi' if k['geciken'] else ''}"><b>{k['geciken']}</b> geciken</div>
      <div class="s-item"><b>{k['atanmamis']}</b> sahipsiz</div>
    </div>"""

    # --- organizasyon tablosu (samimi durum etiketli)
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
        hafta_txt = f"bu hafta {o['hafta_tamam']} iş bitti" if o["hafta_tamam"] else "bu hafta hareket yok"
        return f"""
        <tr class="{cls}">
          <td class="o-ad"><span class="dot"></span>{esc(o['ad'])}</td>
          <td class="o-zaman">{zaman}</td>
          <td class="o-durum">{etiket}</td>
          <td class="o-ilerleme" data-tip="{esc(o['ad'])}: {o['tamam']}/{o['toplam']} iş tamam · {hafta_txt}">
            <span class="mtrack"><span class="mfill" style="width:{oran}%"></span></span>
            <span class="mtxt">{o['acik']} açık</span></td>
        </tr>"""

    org_html = f"""
    <section class="bolum">
      <h2>Organizasyonlar ne durumda?</h2>
      <table class="org">
        <thead><tr><th>Organizasyon</th><th>Ne zaman?</th><th>Durum</th><th>İlerleme</th></tr></thead>
        <tbody>{''.join(org_satir(o) for o in ilk)}</tbody>
      </table>
      {f'<details class="devam"><summary>İleri tarihli {len(kalanlar)} organizasyon daha</summary><table class="org"><tbody>{"".join(org_satir(o) for o in kalanlar)}</tbody></table></details>' if kalanlar else ''}
    </section>"""

    # --- haftanın insanları: bu hafta biten + üzerindeki yük yan yana
    yuk = {x["isim"]: x["acik"] for x in v["kisi_yuku"]}
    tum_isimler = list(dict.fromkeys([i for i, _ in h["kisi"]] + list(yuk.keys())))
    maxb = max([a for _, a in h["kisi"]], default=1) or 1
    kisi_rows = ""
    for isim in tum_isimler:
        biten = dict(h["kisi"]).get(isim, 0)
        acik = yuk.get(isim, 0)
        w = round(100 * biten / maxb)
        kisi_rows += f"""
        <div class="k-satir" data-tip="{esc(isim)}: bu hafta {biten} iş bitirdi, üzerinde {acik} açık iş var">
          <span class="k-ad">{esc(isim)}</span>
          <span class="k-bar"><span class="k-fill" style="width:{w}%"></span></span>
          <span class="k-say">{biten if biten else '–'}</span>
          <span class="k-acik">{acik} açık</span>
        </div>"""
    kisi_html = f"""
    <section class="bolum">
      <h2>Bu hafta kim ne yaptı?</h2>
      <p class="alt">Mavi çubuk bu hafta bitirilen işleri gösteriyor; sağdaki sayı üzerindeki açık iş.</p>
      <div class="k-grid">{kisi_rows}</div>
      {f'<p class="not-kutu">{IKON["alert"]}<span>Ayrıca <b>{k["atanmamis"]} açık işin</b> üzerinde kimse yok — pazartesi dağıtmakta fayda var.</span></p>' if k['atanmamis'] else ''}
    </section>"""

    # --- geciken işler
    if v["gecikenler"]:
        rows = "".join(f"""
        <tr><td>{esc(g['baslik'])}</td><td class="soluk">{esc(g['kutu'])}</td>
        <td class="gec">{g['gun']} gündür</td><td>{esc(', '.join(ilk_ad(x) for x in g['kisiler']))}</td></tr>"""
            for g in v["gecikenler"])
        geciken_html = f"""
        <section class="bolum b-dikkat">
          <h2>{IKON['alert']} Takılan işler</h2>
          <p class="alt">Bunlar son tarihini geçmiş — küçük bir dokunuşla kapanabilirler.</p>
          <table class="duz"><tbody>{rows}</tbody></table>
        </section>"""
    else:
        geciken_html = f'<section class="bolum"><h2>{IKON["check"]} Takılan iş yok</h2><p class="alt">Hiçbir görev son tarihini geçmemiş. Böyle devam.</p></section>'

    # --- önümüzdeki hafta radarı
    radar = []
    for o in v["orglar"]:
        if 0 <= o["kalan_gun"] <= 21:
            radar.append(f'<li>{IKON["cal"]}<span class="r-txt"><b>{esc(o["ad"])}</b> — {o["kalan_gun"]} gün kaldı, {o["acik"]} iş açık</span></li>')
    for y in v["yaklasan"]:
        radar.append(f'<li>{IKON["clock"]}<span class="r-txt"><b>{kisa(y["son"])}:</b> {esc(y["baslik"])} <span class="soluk">({esc(", ".join(ilk_ad(x) for x in y["kisiler"]))})</span></span></li>')
    radar_html = f"""
    <section class="bolum">
      <h2>Önümüzdeki haftanın radarı</h2>
      <ul class="radar">{''.join(radar) if radar else '<li>Yakın vadede kritik tarih görünmüyor.</li>'}</ul>
    </section>"""

    hafta_araligi = f"{kisa(h['baslangic'])} – {kisa(h['bitis'])} {d.year}"

    return f"""<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(v['plan_adi'])} · Haftalık Rapor · {hafta_araligi}</title>
<style>
  .viz-root {{
    color-scheme: light;
    --page:#f9f9f7; --surface:#fcfcfb; --ink:#0b0b0b; --ink2:#52514e; --muted:#898781;
    --grid:#e1e0d9; --border:rgba(11,11,11,.10);
    --seq:#2a78d6; --seq-koyu:#1c5cab; --seq-track:#cde2fb;
    --critical:#d03b3b; --good:#006300; --warn-ink:#8a5a00;
    --sel:#cde2fb;
  }}
  @media (prefers-color-scheme: dark) {{
    :root:where(:not([data-theme="light"])) .viz-root {{
      color-scheme: dark;
      --page:#0d0d0d; --surface:#1a1a19; --ink:#fff; --ink2:#c3c2b7; --muted:#898781;
      --grid:#2c2c2a; --border:rgba(255,255,255,.10);
      --seq:#3987e5; --seq-koyu:#86b6ef; --seq-track:#0d366b;
      --critical:#e66767; --good:#0ca30c; --warn-ink:#fab219;
      --sel:#184f95;
    }}
  }}
  :root[data-theme="dark"] .viz-root {{
    color-scheme: dark;
    --page:#0d0d0d; --surface:#1a1a19; --ink:#fff; --ink2:#c3c2b7; --muted:#898781;
    --grid:#2c2c2a; --border:rgba(255,255,255,.10);
    --seq:#3987e5; --seq-koyu:#86b6ef; --seq-track:#0d366b;
    --critical:#e66767; --good:#0ca30c; --warn-ink:#fab219;
    --sel:#184f95;
  }}
  * {{ box-sizing:border-box; margin:0; }}
  ::selection {{ background:var(--sel); }}
  body.viz-root {{
    background:var(--page); color:var(--ink);
    font-family:system-ui,-apple-system,"Segoe UI",sans-serif;
    line-height:1.55; padding:clamp(20px,4vw,44px) 16px 56px;
  }}
  .wrap {{ max-width:860px; margin:0 auto; }}

  /* ---- giriş */
  .ust {{ margin-bottom:28px; }}
  .etiket {{ font-size:13px; color:var(--muted); }}
  h1 {{ font-size:clamp(24px,4.4vw,34px); font-weight:700; letter-spacing:-0.02em;
        line-height:1.2; margin:6px 0 14px; max-width:24ch; text-wrap:balance; }}
  .anlati {{ font-size:16.5px; color:var(--ink2); max-width:68ch; }}
  .anlati b {{ color:var(--ink); }}

  .serit {{ display:flex; flex-wrap:wrap; gap:8px 26px; margin:22px 0 34px;
            padding:14px 18px; background:var(--surface); border:1px solid var(--border);
            border-radius:14px; font-size:14px; color:var(--ink2); }}
  .s-item b {{ font-size:19px; font-weight:650; color:var(--ink); margin-right:3px; }}
  .s-kirmizi b {{ color:var(--critical); }}
  .f-iyi {{ color:var(--good); font-size:12.5px; }}
  .f-kotu {{ color:var(--critical); font-size:12.5px; }}
  .f-notr {{ color:var(--muted); font-size:12.5px; }}

  /* ---- bölümler */
  .bolum {{ background:var(--surface); border:1px solid var(--border); border-radius:14px;
            padding:22px 24px 20px; margin-bottom:18px; }}
  .bolum h2 {{ font-size:17.5px; font-weight:650; letter-spacing:-0.01em; margin-bottom:4px;
               display:flex; align-items:center; gap:7px; }}
  .bolum h2 svg {{ color:var(--muted); flex:none; }}
  .b-dikkat h2 svg {{ color:var(--critical); }}
  .alt {{ font-size:13.5px; color:var(--muted); margin-bottom:14px; max-width:66ch; }}

  /* ---- organizasyon tablosu */
  table {{ width:100%; border-collapse:collapse; }}
  .org th {{ text-align:left; font-size:11.5px; text-transform:uppercase; letter-spacing:.06em;
             color:var(--muted); font-weight:600; padding:10px 10px 8px;
             border-bottom:1px solid var(--grid); }}
  .org td {{ padding:11px 10px; border-bottom:1px solid var(--grid); font-size:14px;
             vertical-align:middle; }}
  .org tr:last-child td {{ border-bottom:none; }}
  .o-ad {{ font-weight:550; }}
  .dot {{ display:inline-block; width:8px; height:8px; border-radius:50%; margin-right:9px;
          vertical-align:1px; }}
  .s-hazir .dot   {{ background:var(--good); }}
  .s-yolunda .dot {{ background:var(--seq); }}
  .s-dikkat .dot  {{ background:var(--critical); }}
  .s-sessiz .dot  {{ background:var(--muted); }}
  .o-zaman {{ color:var(--ink2); white-space:nowrap; font-size:13.5px; }}
  .o-durum {{ color:var(--ink2); font-size:13.5px; }}
  .s-dikkat .o-durum {{ color:var(--critical); font-weight:550; }}
  .s-hazir .o-durum {{ color:var(--good); }}
  .o-ilerleme {{ white-space:nowrap; }}
  .mtrack {{ display:inline-block; width:74px; height:7px; border-radius:5px;
             background:var(--seq-track); vertical-align:middle; }}
  .mfill {{ display:block; height:100%; border-radius:5px; background:var(--seq); }}
  .mtxt {{ font-size:12.5px; color:var(--ink2); margin-left:8px;
           font-variant-numeric:tabular-nums; }}
  details.devam {{ margin-top:10px; }}
  details.devam summary {{ cursor:pointer; font-size:13.5px; color:var(--ink2);
                           padding:6px 2px; }}
  details.devam summary:hover {{ color:var(--ink); }}

  /* ---- kişiler */
  .k-grid {{ display:flex; flex-direction:column; gap:8px; }}
  .k-satir {{ display:grid; grid-template-columns:160px 1fr 30px 64px;
              align-items:center; gap:10px; }}
  .k-ad {{ font-size:13.5px; color:var(--ink2); text-align:right; white-space:nowrap;
           overflow:hidden; text-overflow:ellipsis; }}
  .k-bar {{ height:16px; }}
  .k-fill {{ display:block; height:16px; background:var(--seq);
             border-radius:0 4px 4px 0; min-width:2px; }}
  .k-satir:has(.k-fill[style="width:0%"]) .k-fill {{ background:transparent; }}
  .k-say {{ font-size:13px; font-variant-numeric:tabular-nums; }}
  .k-acik {{ font-size:12px; color:var(--muted); font-variant-numeric:tabular-nums;
             text-align:right; }}
  .not-kutu {{ margin-top:16px; font-size:13.5px; color:var(--ink2);
               border-top:1px solid var(--grid); padding-top:12px;
               display:flex; gap:8px; align-items:baseline; }}
  .not-kutu svg {{ color:var(--warn-ink); flex:none; transform:translateY(1.5px); }}

  /* ---- geciken + radar */
  .duz td {{ padding:9px 10px; border-bottom:1px solid var(--grid); font-size:14px; }}
  .duz tr:last-child td {{ border-bottom:none; }}
  .gec {{ color:var(--critical); font-weight:600; white-space:nowrap;
          font-variant-numeric:tabular-nums; }}
  .soluk {{ color:var(--muted); font-size:13px; }}
  .radar {{ list-style:none; padding:0; display:flex; flex-direction:column; gap:9px;
            margin-top:10px; }}
  .radar li {{ font-size:14px; color:var(--ink2); display:flex; gap:9px;
               align-items:baseline; }}
  .radar li b {{ color:var(--ink); font-weight:600; }}
  .radar svg {{ flex:none; color:var(--muted); transform:translateY(1.5px); }}
  .r-txt {{ flex:1; min-width:0; }}

  footer {{ text-align:center; color:var(--muted); font-size:12.5px; margin-top:30px; }}

  /* ---- tek hareket: bölümler sırayla belirir */
  @media (prefers-reduced-motion: no-preference) {{
    .ust, .serit, .bolum {{ opacity:0; transform:translateY(10px);
      animation:gel .55s cubic-bezier(.16,1,.3,1) forwards; }}
    .serit {{ animation-delay:.07s; }}
    .bolum:nth-of-type(1) {{ animation-delay:.14s; }}
    .bolum:nth-of-type(2) {{ animation-delay:.20s; }}
    .bolum:nth-of-type(3) {{ animation-delay:.26s; }}
    .bolum:nth-of-type(4) {{ animation-delay:.32s; }}
    @keyframes gel {{ to {{ opacity:1; transform:none; }} }}
  }}

  #tip {{ position:fixed; pointer-events:none; background:var(--ink); color:var(--page);
          font-size:12.5px; padding:6px 10px; border-radius:8px; max-width:320px;
          opacity:0; transition:opacity .12s; z-index:10; }}

  @media (max-width:640px) {{
    .org .o-durum {{ display:none; }}
    .org th:nth-child(3) {{ display:none; }}
    .k-satir {{ grid-template-columns:110px 1fr 26px 56px; }}
  }}
</style>
</head>
<body class="viz-root">
<div class="wrap">
  <header class="ust">
    <div class="etiket">{esc(v['plan_adi'])} · Haftalık Rapor · {hafta_araligi}</div>
    <h1>{esc(baslik)}</h1>
    <p class="anlati">{esc(para)}</p>
  </header>
  {serit}
  {org_html}
  {kisi_html}
  {geciken_html}
  {radar_html}
  <footer>Bu rapor Planner verilerinden otomatik hazırlandı · her pazar akşamı yenilenir</footer>
</div>
<div id="tip" role="tooltip"></div>
<script>
  const tip = document.getElementById('tip');
  document.querySelectorAll('[data-tip]').forEach(el => {{
    el.addEventListener('pointermove', e => {{
      tip.textContent = el.dataset.tip;
      tip.style.opacity = 1;
      const x = Math.min(e.clientX + 14, window.innerWidth - tip.offsetWidth - 8);
      const y = Math.min(e.clientY + 16, window.innerHeight - tip.offsetHeight - 8);
      tip.style.left = x + 'px'; tip.style.top = y + 'px';
    }});
    el.addEventListener('pointerleave', () => tip.style.opacity = 0);
  }});
</script>
</body>
</html>"""


if __name__ == "__main__":
    xlsx = sys.argv[1]
    cikti = sys.argv[2] if len(sys.argv) > 2 else "haftalik_rapor.html"
    v = haftalik_veri(xlsx)
    with open(cikti, "w", encoding="utf-8") as f:
        f.write(uret(v))
    print(f"✓ {cikti} üretildi — hafta: {v['hafta']['tamamlanan']} tamamlanan")
