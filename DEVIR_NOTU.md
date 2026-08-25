# DALYA Haftalık Planner Raporu — Devir Notu
*(Bu notu yeni Cowork görevinin ilk mesajına ekle. Görevi açarken `Dalyamice/rapor-dalya` deposunu KAYNAK olarak seçmeyi unutma — o zaman terminalden git push çalışır.)*

## Ne yapıyoruz
Yusuf (DALYA — kongre/organizasyon şirketi, 11 kişilik ekip) Microsoft Planner'daki "PLAN" panosunu Excel'e aktarıp buraya yüklüyor. Sen bu Excel'den haftalık premium bir HTML rapor üretiyorsun, sohbete gönderiyorsun ve şifreli olarak **rapor.micelink.online** sitesine yayınlıyorsun. Akış tamamen MANUEL: Excel gelince çalış, kendi kendine hiçbir şey zamanlama.

## Kurallar (Yusuf'la yerleşik anlaşma)
- Planner'daki her kutu (bucket) bir kongre/organizasyondur; yorumları bu sektör bağlamında yaz.
- **Sadece son 1 haftayı yorumla; geçmiş işlerin tarihçesini anlatma** (Yusuf'un açık talimatı).
- Ton: samimi, sıcak Türkçe. Kişi yorumlarında YARIŞ/ŞAMPİYON dili YASAK; herkese adil ol (sahada olan, 0 kapanışlı kişileri ezme). Kişi başına açtığı + tamamladığı görev sayıları (haftalık) gösterilir.
- Her yeni Excel'de yorumlar SIFIRDAN yazılır (yorumlar.json + kisi_yorumlar.json).
- Raporda künye zorunlu: verinin çekildiği tarih-saat + rapor üretim zamanı. Excel'i yüklediği an = veri zamanı say (veri_zamani.txt'ye TRT ISO yaz, ör. 2026-08-24T21:22:23+03:00).
- Sakin haftalarda rapor kısa olur (adaptif uzunluk).

## İlk iş: depoyu klonla
Tüm motor dosyaları depoda (public): `git clone https://github.com/Dalyamice/rapor-dalya.git`
- `analiz.py`, `haftalik_rapor.py` — Excel'den analiz (haftalık pencere = son 7 gün)
- `premium_sablon.py`, `premium_rapor.py` — premium HTML (aurora koyu tema — simsiyah DEĞİL, cam kartlar, Fraunces+Inter, GSAP sayaç/kaydırma animasyonları, org ve kişi tablolarında tıkla-aç yorum kutuları). `WEB_CDN=1` ortam değişkeni site sürümü için (fontlar/GSAP CDN'den, küçük dosya); değişkensiz sürüm sohbet için (her şey gömülü).
- `json_kaynak.py`, `kullanicilar.json` — JSON→Excel çevirici + kullanıcı GUID→isim haritası (yeni ekip üyesi gelirse Excel'in Kullanıcılar sayfasından güncelle)
- Excel şeması: sayfalar Plan / Görevler / Kutular / Kullanıcılar; Görevler'de Kutu=bucket ID, Atanan/Oluşturan=GUID (";" ile ayrık)
- Gömülü sürümün fontları ve GSAP'ı depoda DEĞİL (.gitignore'da). Yeni bir makinede önce:
  `npm pack @fontsource-variable/fraunces@5.3.0 @fontsource-variable/inter@5.3.0 gsap@3.12.5`
  → fraunces'ı `f_fontsource-variable-fraunces-5.3.0/`, inter'i `f_fontsource-variable-inter-5.3.0/`,
  gsap'ı kök dizine aç (`package/dist/...`). `WEB_CDN=1` sürümü bunlara ihtiyaç duymaz.

## Haftalık akış (Excel gelince)
1. `veri_zamani.txt` yaz (şimdiki TRT zamanı).
2. `haftalik_rapor.haftalik_veri("PLAN.xlsx")` ile analiz; org ve kişi detaylarını dök.
3. `yorumlar.json` (her kutu için taze yorum + `"_veri_zamani"` anahtarı = veri_zamani.txt içeriği — künye buradan gelir) ve `kisi_yorumlar.json` (11 kişi) yaz. Kutu ve kişi adları analizdeki adlarla BİREBİR aynı olmalı.
4. `python premium_rapor.py PLAN.xlsx haftalik_rapor_premium.html` → SendUserFile ile sohbete gönder.
   Hafta ortasında çekilmiş bir Excel ile geçmiş bir haftayı raporlayacaksan haftanın
   BİTİŞ gününü 3. argüman olarak ver (ya da `RAPOR_TARIHI` değişkeniyle), ör.
   `python premium_rapor.py PLAN.xlsx cikti.html 2026-08-23` → pencere 17–23 Ağustos.
   Argüman verilmezse Excel'in "Dışarı aktarma tarihi" kullanılır (son 7 gün).
5. Site: `WEB_CDN=1 python premium_rapor.py PLAN.xlsx rapor_duz.html [hafta-bitis]` sonra:
   `npx -y staticrypt rapor_duz.html -d _sifreli -p "19211921" --short --remember 30 --template-title "DALYA Haftalık Rapor" --template-instructions "Bu sayfa şifrelidir. Ekip parolasını girin." --template-button "Raporu Aç" --template-placeholder "Parola" --template-error "Parola hatalı, tekrar deneyin" --template-remember "30 gün beni hatırla" --template-color-primary "#1c5cab" --template-color-secondary "#0a0d16"`
   `_sifreli/rapor_duz.html` → depoda `index.html` olarak commit + `arsiv/YYYY-MM-DD.html` kopyası → `git push` (depo kaynak olarak eklendiyse terminalden çalışır; çalışmazsa yedek yol: kullanıcının Chrome'u üzerinden github.com "Upload files").
6. **Yayın için izin sorma.** Yusuf'un açık talimatı (25 Ağustos 2026): rapor hazır olunca
   doğrudan yayına al. Çalışma branch'i varsa onu `main`'e merge edip `main`'i pushla —
   GitHub Pages `main`'den yayınlıyor, branch'te kalan rapor siteye çıkmaz.
7. Site parolası: **19211921**. Alan adı CNAME dosyasında (rapor.micelink.online), GitHub Pages otomatik yayınlar — push yeterli.

## Bilinmesi gerekenler / tuzaklar
- Otomatik zamanlama YOK: workflow'daki pazar cron'u bilerek kaldırıldı (Yusuf istedi). `.github/workflows/rapor.yml` sadece workflow_dispatch — ONU DA KULLANMA, eski OneDrive yolundan derliyor ve o verileri artık kimse güncellemiyor.
- OneDrive/Power Automate eski otomasyonun kalıntısı: PA her pazar 19:30'da OneDrive'a JSON atmaya devam ediyor olabilir; yok say. OneDrive'a MCP ile dosya yazarken 1 MB / tek çağrı sınırı var; büyük görev dosyası tek çağrıya sığmaz (~30k token çıktı tavanı) — bu yüzden zaten site verisini artık depo üzerinden taşıyoruz.
- MCP ile OneDrive'daki sabit dosyaları ASLA silip yeniden oluşturma (paylaşım linkleri itemId'ye bağlı) — gerekirse yalnızca sharepoint_update_file.
- Rapordaki tablolar: organizasyon satırına tıklayınca senin yorumun + açık işler + bu hafta bitenler açılır; kişi satırında haftalık yorumun görünür.
- Yusuf ara sıra hafta ortası da Excel atıp anlık rapor isteyebilir — aynı akış.

## Kimlikler
- Site: rapor.micelink.online (parola 19211921), depo: github.com/Dalyamice/rapor-dalya (GitHub hesabı: Dalyamice)
- Yusuf'un M365 hesabı: yusuf@dalyatur.com (Microsoft 365 bağlayıcısı bağlı)
