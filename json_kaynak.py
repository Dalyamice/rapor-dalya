# -*- coding: utf-8 -*-
"""Power Automate'in OneDrive'a yazdığı Planner JSON çiftini, rapor motorunun
anladığı Excel yapısına dönüştürür.

Kullanım:
    python3 json_kaynak.py gorevler_20260815.json kutular_20260815.json [cikti.xlsx]

Kullanıcı adları kullanicilar.json haritasından çözülür (Excel dışa
aktarımından bir kez üretildi). Haritada olmayan kimlikler "Yeni Üye ####"
olarak işaretlenir — yeni biri katılırsa taze bir Excel dışa aktarımı
haritayı günceller.
"""
from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone

import pandas as pd

TRT = timezone(timedelta(hours=3))
_BURASI = os.path.dirname(os.path.abspath(__file__))


def _tarih(iso: str | None):
    """ISO UTC damgasını TRT gününe çevirir (Excel'deki gibi salt tarih)."""
    if not iso:
        return None
    iso = iso.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(iso).astimezone(TRT).date()
    except ValueError:
        return None


def _oncelik(p) -> str:
    p = p if isinstance(p, int) else 5
    if p <= 1:
        return "Acil"
    if p <= 4:
        return "Önemli"
    if p <= 7:
        return "Orta"
    return "Düşük"


def cevir(gorevler_yolu: str, kutular_yolu: str, cikti: str = "PLAN_json.xlsx",
          bugun=None) -> str:
    with open(gorevler_yolu, encoding="utf-8") as f:
        gorevler = json.load(f)["value"]
    with open(kutular_yolu, encoding="utf-8") as f:
        kutular = json.load(f)["value"]

    # dışa aktarma tarihi: dosya adındaki YYYYMMDD, yoksa bugün (TRT)
    if bugun is None:
        m = re.search(r"(\d{4})(\d{2})(\d{2})", os.path.basename(gorevler_yolu))
        bugun = (datetime(int(m.group(1)), int(m.group(2)), int(m.group(3))).date()
                 if m else datetime.now(TRT).date())

    with open(os.path.join(_BURASI, "kullanicilar.json"), encoding="utf-8") as f:
        umap = json.load(f)

    def kisi_adi(uid: str) -> str:
        return umap.get(uid, {}).get("ad", f"Yeni Üye {uid[:4]}")

    satirlar = []
    for t in gorevler:
        tamam = t.get("percentComplete", 0) == 100
        due = _tarih(t.get("dueDateTime"))
        cb = (t.get("completedBy") or {}).get("user", {}).get("id")
        satirlar.append({
            "Görev Kimliği": t["id"],
            "Görev Adı": t.get("title", ""),
            "Kutu": t.get("bucketId"),
            "Hedef": None,
            "Durum": ("Tamamlandı" if tamam else
                      ("Devam ediyor" if t.get("percentComplete", 0) > 0 else "Başlatılmadı")),
            "Öncelik": _oncelik(t.get("priority")),
            "Atanan": ";".join((t.get("assignments") or {}).keys()) or None,
            "Oluşturan": (t.get("createdBy") or {}).get("user", {}).get("id"),
            "Oluşturma Tarihi": _tarih(t.get("createdDateTime")),
            "Son tarih": due,
            "Başlangıç tarihi": _tarih(t.get("startDateTime")),
            "Yinelenen": None,
            "Geciken": bool(due and not tamam and due < bugun),
            "Tamamlanma Tarihi": _tarih(t.get("completedDateTime")),
            "Tarafından tamamlanmıştır": cb,
            "Tamamlanan Denetim Listesi Öğeleri": None,
            "Denetim Listesi Öğeleri": None,
            "Etiketler": None,
            "Notlar": None,
        })

    plan_id = kutular[0]["planId"] if kutular else ""
    with pd.ExcelWriter(cikti, engine="openpyxl") as w:
        pd.DataFrame([{"Plan Kimliği": plan_id, "Plan adı": "PLAN",
                       "Dışarı aktarma tarihi": bugun}]).to_excel(w, sheet_name="Plan", index=False)
        pd.DataFrame(satirlar).to_excel(w, sheet_name="Görevler", index=False)
        pd.DataFrame([{"Kutu Kimliği": b["id"], "Demet Adı": b["name"].strip()}
                      for b in kutular]).to_excel(w, sheet_name="Kutular", index=False)
        pd.DataFrame([{"Kullanıcı Kimliği": uid, "Kullanıcı Adı": v["ad"],
                       "E-posta": v.get("eposta", "")}
                      for uid, v in umap.items()]).to_excel(w, sheet_name="Kullanıcılar", index=False)
    return cikti


if __name__ == "__main__":
    g, k = sys.argv[1], sys.argv[2]
    cikti = sys.argv[3] if len(sys.argv) > 3 else "PLAN_json.xlsx"
    print("✓", cevir(g, k, cikti), "üretildi")
