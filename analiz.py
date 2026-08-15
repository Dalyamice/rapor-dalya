# -*- coding: utf-8 -*-
"""Planner Excel dışa aktarımını okuyup analiz sözlüğü üretir.

Kullanım:  from analiz import analiz_et
           veri = analiz_et("PLAN 1.xlsx")
"""
from __future__ import annotations

import re
from collections import Counter, defaultdict
from datetime import date, timedelta

import pandas as pd

AYLAR = {
    "ocak": 1, "şubat": 2, "subat": 2, "mart": 3, "nisan": 4, "mayıs": 5,
    "mayis": 5, "haziran": 6, "temmuz": 7, "ağustos": 8, "agustos": 8,
    "eylül": 9, "eylul": 9, "ekim": 10, "kasım": 11, "kasim": 11,
    "aralık": 12, "aralik": 12,
}

# Organizasyon olmayan (operasyonel) kutular — etkinlik takvimine girmez
OPERASYONEL = {"DALYA", "MUHASEBE", "FİRMALAR", "EZBER BOZAN",
               "KAYIT SİSTEMİ Güncelleme Notları", "Bildiri Sistemi"}


def etkinlik_tarihi(kutu_adi: str, bugun: date) -> tuple[date, date] | None:
    """Kutu adından etkinlik tarih aralığını çıkarır.

    Örn: '18-20 Ağustos SONOVA' → (2026-08-18, 2026-08-20)
         '29 Mart-1 Nisan BİPOLAR 2027' → (2027-03-29, 2027-04-01)
    """
    s = kutu_adi.strip()
    yil_m = re.search(r"\b(20\d\d)\b", s)
    yil = int(yil_m.group(1)) if yil_m else None

    ay_re = "|".join(AYLAR)
    # '29 Mart - 1 Nisan'  (iki ay)
    m = re.search(rf"(\d{{1,2}})\s*({ay_re})\s*[-–]\s*(\d{{1,2}})\s*({ay_re})", s, re.I)
    if m:
        g1, a1, g2, a2 = int(m.group(1)), AYLAR[m.group(2).lower()], int(m.group(3)), AYLAR[m.group(4).lower()]
    else:
        # '18-20 Ağustos'  (tek ay)
        m = re.search(rf"(\d{{1,2}})\s*[-–]\s*(\d{{1,2}})\s+({ay_re})", s, re.I)
        if m:
            g1, g2, a1 = int(m.group(1)), int(m.group(2)), AYLAR[m.group(3).lower()]
            a2 = a1
        else:
            # '18 Ağustos' (tek gün)
            m = re.search(rf"(\d{{1,2}})\s+({ay_re})", s, re.I)
            if not m:
                return None
            g1 = g2 = int(m.group(1))
            a1 = a2 = AYLAR[m.group(2).lower()]
    if yil is None:
        # Yıl yazılmamışsa: ay bugünden önceyse bir sonraki yıl kabul et
        yil = bugun.year if (a1, g1) >= (bugun.month, 1) else bugun.year + 1
    yil2 = yil + 1 if a2 < a1 else yil
    try:
        return date(yil, a1, g1), date(yil2, a2, g2)
    except ValueError:
        return None


def _isimler(atanan, umap) -> list[str]:
    if pd.isna(atanan):
        return []
    return [umap.get(x.strip(), "?") for x in str(atanan).split(";") if x.strip()]


def analiz_et(xlsx_yolu: str, bugun: date | None = None) -> dict:
    xl = pd.ExcelFile(xlsx_yolu)
    plan = xl.parse("Plan")
    t = xl.parse("Görevler")
    k = xl.parse("Kutular")
    u = xl.parse("Kullanıcılar")
    for df in (plan, t, k, u):
        df.columns = [c.strip() for c in df.columns]

    if bugun is None:
        bugun = pd.to_datetime(plan["Dışarı aktarma tarihi"].iloc[0]).date()

    kmap = {r["Kutu Kimliği"]: str(r["Demet Adı"]).strip() for _, r in k.iterrows()}
    umap = {r["Kullanıcı Kimliği"]: re.sub(r"\s+", " ", str(r["Kullanıcı Adı"])).strip()
            for _, r in u.iterrows()}

    t["kutu"] = t["Kutu"].map(kmap)
    t["ct"] = pd.to_datetime(t["Tamamlanma Tarihi"], errors="coerce").dt.date
    t["cr"] = pd.to_datetime(t["Oluşturma Tarihi"], errors="coerce").dt.date
    t["son"] = pd.to_datetime(t["Son tarih"], errors="coerce").dt.date
    t["tamam"] = t["Durum"] == "Tamamlandı"

    acik = t[~t["tamam"]]
    dun = bugun - timedelta(days=1)
    hafta = bugun - timedelta(days=7)

    # --- Günlük hareketler -------------------------------------------------
    bugun_tamam = t[t["ct"] == bugun]
    dun_tamam = t[t["ct"] == dun]
    bugun_yeni = t[t["cr"] == bugun]
    hafta_tamam = t[(t["ct"].notna()) & (t["ct"] > hafta)]

    def gorev_listesi(df):
        out = []
        for _, r in df.iterrows():
            kisi = umap.get(str(r.get("Tarafından tamamlanmıştır", "")).strip())
            out.append({
                "baslik": str(r["Görev Adı"]).strip(),
                "kutu": r["kutu"],
                "kisi": kisi or ", ".join(_isimler(r["Atanan"], umap)) or "Atanmamış",
            })
        return out

    # --- Gecikenler --------------------------------------------------------
    gec_df = t[(t["Geciken"] == True) & (~t["tamam"])]  # noqa: E712
    gecikenler = [{
        "baslik": str(r["Görev Adı"]).strip(),
        "kutu": r["kutu"],
        "son": r["son"].isoformat() if r["son"] else None,
        "gun": (bugun - r["son"]).days if r["son"] else None,
        "kisiler": _isimler(r["Atanan"], umap) or ["Atanmamış"],
    } for _, r in gec_df.iterrows()]
    gecikenler.sort(key=lambda x: -(x["gun"] or 0))

    # --- Yaklaşan son tarihler (7 gün) ------------------------------------
    yak = acik[acik["son"].notna() & (acik["son"] >= bugun)
               & (acik["son"] <= bugun + timedelta(days=7))]
    yaklasan = sorted([{
        "baslik": str(r["Görev Adı"]).strip(),
        "kutu": r["kutu"],
        "son": r["son"].isoformat(),
        "kisiler": _isimler(r["Atanan"], umap) or ["Atanmamış"],
    } for _, r in yak.iterrows()], key=lambda x: x["son"])

    # --- Kişi yükü ---------------------------------------------------------
    yuk = Counter()
    for a in acik["Atanan"].dropna():
        for isim in _isimler(a, umap):
            yuk[isim] += 1
    kisi_yuku = [{"isim": i, "acik": n} for i, n in yuk.most_common()]
    atanmamis = int(acik["Atanan"].isna().sum())

    # --- Organizasyonlar ---------------------------------------------------
    orglar, operasyonel = [], []
    for kutu, grp in t.groupby("kutu"):
        acik_grp = grp[~grp["tamam"]]
        acik_isler = sorted([{
            "baslik": str(r["Görev Adı"]).strip(),
            "kisiler": _isimler(r["Atanan"], umap) or ["Atanmamış"],
            "son": r["son"].isoformat() if pd.notna(r["son"]) else None,
            "geciken": bool(r["Geciken"] == True),  # noqa: E712
        } for _, r in acik_grp.iterrows()],
            key=lambda x: (not x["geciken"], x["son"] or "9999"))
        bitenler_hafta = [str(r["Görev Adı"]).strip()
                          for _, r in grp[(grp["ct"].notna()) & (grp["ct"] > hafta)].iterrows()]
        kayit = {
            "ad": kutu,
            "toplam": len(grp),
            "tamam": int(grp["tamam"].sum()),
            "acik": int((~grp["tamam"]).sum()),
            "geciken": int(((grp["Geciken"] == True) & (~grp["tamam"])).sum()),  # noqa: E712
            "bugun_tamam": int((grp["ct"] == bugun).sum()),
            "hafta_tamam": int(((grp["ct"].notna()) & (grp["ct"] > hafta)).sum()),
            "acik_isler": acik_isler,
            "bitenler_hafta": bitenler_hafta,
        }
        tarih = etkinlik_tarihi(kutu, bugun) if kutu not in OPERASYONEL else None
        if tarih:
            kayit["baslangic"] = tarih[0].isoformat()
            kayit["bitis"] = tarih[1].isoformat()
            kayit["kalan_gun"] = (tarih[0] - bugun).days
            orglar.append(kayit)
        else:
            operasyonel.append(kayit)
    orglar.sort(key=lambda x: x["baslangic"])
    operasyonel.sort(key=lambda x: -x["acik"])

    # Risk işareti: etkinliğe ≤30 gün var ve açık iş oranı yüksek ya da geciken var
    for o in orglar:
        oran = o["tamam"] / o["toplam"] if o["toplam"] else 1
        o["risk"] = (0 <= o["kalan_gun"] <= 30 and (o["acik"] >= 3 or o["geciken"] > 0)) \
                    or o["geciken"] > 0

    # --- Günlük tamamlama serisi (son 14 gün) ------------------------------
    seri = []
    for i in range(13, -1, -1):
        d = bugun - timedelta(days=i)
        seri.append({
            "tarih": d.isoformat(),
            "tamamlanan": int((t["ct"] == d).sum()),
            "eklenen": int((t["cr"] == d).sum()),
        })

    # --- Aktivite seviyesi & özet cümlesi ----------------------------------
    hareket = len(bugun_tamam) + len(bugun_yeni)
    if hareket == 0:
        seviye = "sessiz"
    elif hareket <= 3:
        seviye = "az"
    else:
        seviye = "normal"

    return {
        "plan_adi": str(plan["Plan adı"].iloc[0]).strip(),
        "tarih": bugun.isoformat(),
        "seviye": seviye,
        "kpi": {
            "toplam": len(t),
            "acik": len(acik),
            "bugun_tamam": len(bugun_tamam),
            "dun_tamam": len(dun_tamam),
            "hafta_tamam": len(hafta_tamam),
            "bugun_yeni": len(bugun_yeni),
            "geciken": len(gecikenler),
            "atanmamis": atanmamis,
            "aktif_org": sum(1 for o in orglar if o["acik"] > 0),
        },
        "bugun_tamamlanan": gorev_listesi(bugun_tamam),
        "bugun_eklenen": gorev_listesi(bugun_yeni),
        "gecikenler": gecikenler,
        "yaklasan": yaklasan,
        "kisi_yuku": kisi_yuku,
        "orglar": orglar,
        "operasyonel": operasyonel,
        "seri": seri,
    }
