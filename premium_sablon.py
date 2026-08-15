# -*- coding: utf-8 -*-
"""Premium haftalık rapor şablonu v2 — aurora atmosfer + cam kartlar + lig tablosu.

Tasarım dünyası:
  * Derin gece mavisi zemin üzerinde yavaşça süzülen aurora ışıkları + film greni
  * Cam (glassmorphism) bölüm kartları, renkli bölüm rozetleri
  * Fraunces (display serif) + Inter — gömülü, Türkçe tam destek
  * GSAP + ScrollTrigger gömülü: scrollytelling, sayaçlar, yarış çubukları
  * Progressive enhancement + prefers-reduced-motion desteği
"""
TEMPLATE = r"""<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>__TITLE__</title>
<style>
__FONT_CSS__
</style>
<style>
  :root {
    color-scheme: dark;
    --page:#0a0d16;
    --cam:rgba(255,255,255,.045); --cam2:rgba(255,255,255,.07);
    --border:rgba(255,255,255,.10); --border2:rgba(255,255,255,.16);
    --ink:#f7f6f1; --ink2:#c9c7bd; --muted:#8f8d85;
    --grid:rgba(255,255,255,.09);
    --mavi:#4a90ea; --mavi-soft:#8ab8f2; --track:rgba(74,144,234,.18);
    --aqua:#22c58b; --mor:#9085e9; --amber:#f5b83d;
    --kirmizi:#ef6b6b; --yesil:#3ecf3e;
    --altin:#f5c04c; --gumus:#ccd0da; --bronz:#d08d55;
    --sel:#1d4f92;
    --serif:"Fraunces", Georgia, "Times New Roman", serif;
    --sans:"Inter", system-ui, -apple-system, "Segoe UI", sans-serif;
  }
  :root[data-theme="light"] {
    color-scheme: light;
    --page:#f2f3f6;
    --cam:rgba(255,255,255,.72); --cam2:rgba(255,255,255,.9);
    --border:rgba(15,23,42,.10); --border2:rgba(15,23,42,.18);
    --ink:#131722; --ink2:#454b5c; --muted:#7b8194;
    --grid:rgba(15,23,42,.10);
    --mavi:#2a6fd0; --mavi-soft:#1c56a8; --track:rgba(42,111,208,.16);
    --aqua:#0c9a68; --mor:#5f51c9; --amber:#a86d00;
    --kirmizi:#c94040; --yesil:#0e8a0e;
    --altin:#b8860b; --gumus:#6e7787; --bronz:#a0642f;
    --sel:#bcd7fa;
  }
  * { box-sizing:border-box; margin:0; }
  ::selection { background:var(--sel); color:var(--ink); }
  html { scroll-behavior:smooth; }
  body {
    background:var(--page); color:var(--ink);
    font-family:var(--sans); line-height:1.62; font-size:16px;
    -webkit-font-smoothing:antialiased; overflow-x:hidden;
  }
  ::-webkit-scrollbar { width:10px; }
  ::-webkit-scrollbar-thumb { background:rgba(140,150,180,.25); border-radius:6px;
                              border:2px solid var(--page); }
  ::-webkit-scrollbar-track { background:var(--page); }

  /* ================= ATMOSFER ================= */
  .gokyuzu { position:fixed; inset:0; z-index:-2; overflow:hidden; }
  .aurora { position:absolute; border-radius:50%; filter:blur(90px); opacity:.5;
            will-change:transform; }
  .a1 { width:56vw; height:56vw; left:-14vw; top:-18vw;
        background:radial-gradient(circle, rgba(58,110,220,.55), transparent 65%);
        animation:sus1 26s ease-in-out infinite alternate; }
  .a2 { width:44vw; height:44vw; right:-12vw; top:8vh;
        background:radial-gradient(circle, rgba(124,92,255,.42), transparent 65%);
        animation:sus2 32s ease-in-out infinite alternate; }
  .a3 { width:50vw; height:50vw; left:22vw; bottom:-28vw;
        background:radial-gradient(circle, rgba(27,175,122,.30), transparent 65%);
        animation:sus3 38s ease-in-out infinite alternate; }
  :root[data-theme="light"] .aurora { opacity:.34; }
  @keyframes sus1 { to { transform:translate(9vw,7vh) scale(1.12); } }
  @keyframes sus2 { to { transform:translate(-7vw,12vh) scale(.92); } }
  @keyframes sus3 { to { transform:translate(-9vw,-9vh) scale(1.1); } }
  .gren { position:fixed; inset:0; z-index:-1; pointer-events:none; opacity:.16;
          background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='140' height='140'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2'/%3E%3CfeColorMatrix type='saturate' values='0'/%3E%3C/filter%3E%3Crect width='140' height='140' filter='url(%23n)' opacity='0.5'/%3E%3C/svg%3E"); }
  :root[data-theme="light"] .gren { opacity:.07; }
  @media (prefers-reduced-motion: reduce) { .aurora { animation:none; } }

  #progress { position:fixed; top:0; left:0; height:2.5px; width:100%; z-index:50;
              background:linear-gradient(90deg,var(--mavi),var(--mor),var(--aqua));
              transform-origin:0 50%; transform:scaleX(0); }

  .tema { position:fixed; top:14px; right:16px; z-index:51;
          background:var(--cam2); backdrop-filter:blur(12px); border:1px solid var(--border);
          color:var(--ink2); width:38px; height:38px; border-radius:50%; cursor:pointer;
          display:grid; place-items:center; transition:color .2s, transform .2s; }
  .tema:hover { color:var(--ink); transform:scale(1.08) rotate(15deg); }
  .tema:active { transform:scale(.92); }
  .tema:focus-visible { outline:2px solid var(--mavi); outline-offset:2px; }

  .wrap { max-width:920px; margin:0 auto; padding:0 clamp(16px,4vw,32px); }

  /* ================= HERO ================= */
  .hero { padding:clamp(68px,11vh,120px) 0 clamp(34px,5vh,52px); position:relative; }
  .etiket { font-size:13px; letter-spacing:.15em; text-transform:uppercase;
            color:var(--ink2); font-weight:600; display:flex; align-items:center; gap:10px; }
  .etiket .isik { width:8px; height:8px; border-radius:50%; background:var(--aqua);
                  box-shadow:0 0 12px var(--aqua); }
  .etiket b { color:var(--mavi-soft); font-weight:700; }
  .kunye { font-size:12.5px; color:var(--muted); margin-top:10px;
           display:flex; align-items:center; gap:7px; flex-wrap:wrap; }
  .kunye svg { flex:none; }
  h1 { font-family:var(--serif); font-weight:560; font-optical-sizing:auto;
       font-size:clamp(38px,6.8vw,66px); line-height:1.05; letter-spacing:-0.015em;
       margin:22px 0 24px; max-width:17ch; text-wrap:balance; }
  h1 .vurgu { font-style:italic; color:var(--mavi-soft);
              text-shadow:0 0 34px rgba(74,144,234,.45); }
  .anlati { font-size:clamp(16px,2vw,18.5px); color:var(--ink2); max-width:62ch;
            line-height:1.75; }
  .anlati b { color:var(--ink); font-weight:600; }

  .sayilar { display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr));
             gap:12px; margin-top:clamp(36px,6vh,54px); }
  .sayi { background:var(--cam); backdrop-filter:blur(14px);
          border:1px solid var(--border); border-radius:18px; padding:20px 20px 16px;
          position:relative; overflow:hidden; transition:transform .25s, border-color .25s; }
  .sayi:hover { transform:translateY(-3px); border-color:var(--border2); }
  .sayi::before { content:""; position:absolute; inset:0 auto auto 0; width:100%; height:2px;
                  background:linear-gradient(90deg, var(--rk, var(--mavi)), transparent 80%); }
  .sayi-deger { font-family:var(--serif); font-weight:560; font-size:clamp(34px,4.6vw,46px);
                line-height:1.05; letter-spacing:-0.02em; }
  .sayi-ad { font-size:13px; color:var(--ink2); margin-top:7px; }
  .sayi-kiyas { font-size:12px; margin-top:2px; }
  .k-iyi { color:var(--yesil); } .k-kotu { color:var(--kirmizi); } .k-notr { color:var(--muted); }

  .devam-ipucu { display:flex; align-items:center; gap:10px; margin-top:clamp(36px,7vh,60px);
                 color:var(--muted); font-size:12.5px; letter-spacing:.09em; text-transform:uppercase; }
  .devam-ipucu::after { content:""; flex:1; height:1px;
                        background:linear-gradient(90deg,var(--grid),transparent); }
  .ok { animation:zipla 2.2s ease-in-out infinite; }
  @keyframes zipla { 0%,100%{transform:translateY(0)} 50%{transform:translateY(5px)} }
  @media (prefers-reduced-motion: reduce) { .ok { animation:none; } }

  /* ================= BÖLÜM KARTLARI ================= */
  section { margin:clamp(26px,4vh,40px) 0 0; }
  .kart { background:var(--cam); backdrop-filter:blur(16px);
          border:1px solid var(--border); border-radius:22px;
          padding:clamp(22px,4vw,34px); }
  .b-baslik { display:flex; align-items:center; gap:14px; margin-bottom:6px; }
  .b-no { font-size:12px; font-weight:700; letter-spacing:.05em; color:var(--page);
          background:var(--rk, var(--mavi)); border-radius:8px; padding:3px 9px;
          box-shadow:0 0 18px color-mix(in srgb, var(--rk, var(--mavi)) 45%, transparent); }
  h2 { font-family:var(--serif); font-weight:560; font-size:clamp(24px,3.5vw,31px);
       letter-spacing:-0.01em; line-height:1.15; }
  .b-alt { color:var(--muted); font-size:14px; max-width:62ch; margin:6px 0 24px; }

  /* organizasyonlar */
  .org-blok { border-bottom:1px solid var(--grid); border-radius:14px; }
  .org-blok:last-child { border-bottom:none; }
  .org-satir { display:grid; grid-template-columns:1fr auto auto; gap:4px 18px;
               padding:16px 12px 14px; border-radius:14px; cursor:pointer;
               transition:background .25s; position:relative; width:100%;
               border:none; background:none; color:inherit; font:inherit; text-align:left; }
  .org-satir:hover { background:var(--cam2); }
  .org-satir:focus-visible { outline:2px solid var(--mavi); outline-offset:-2px; }
  .cev { grid-column:3; grid-row:1 / span 2; align-self:center; color:var(--muted);
         transition:transform .3s cubic-bezier(.16,1,.3,1), color .25s; }
  .org-blok.acik .cev { transform:rotate(180deg); color:var(--mavi-soft); }
  .org-satir:hover .cev { color:var(--ink2); }
  .org-detay { display:grid; grid-template-rows:0fr; transition:grid-template-rows .45s cubic-bezier(.16,1,.3,1); }
  .org-blok.acik .org-detay { grid-template-rows:1fr; }
  .od-ic { overflow:hidden; min-height:0; }
  .od-kutu { margin:2px 12px 18px; padding:18px 20px; border-radius:16px;
             background:var(--cam2); border:1px solid var(--border); }
  .od-yorum { font-size:14.5px; line-height:1.7; color:var(--ink2); max-width:72ch; }
  .od-yorum::before { content:"Claude'un yorumu"; display:block; font-size:11px;
                      font-weight:700; letter-spacing:.1em; text-transform:uppercase;
                      color:var(--mavi-soft); margin-bottom:8px; }
  .od-listeler { display:grid; grid-template-columns:1fr 1fr; gap:18px; margin-top:16px; }
  @media (max-width:640px) { .od-listeler { grid-template-columns:1fr; } }
  .od-liste h4 { font-size:11px; font-weight:700; letter-spacing:.1em; text-transform:uppercase;
                 color:var(--muted); margin-bottom:8px; }
  .od-liste ul { list-style:none; padding:0; }
  .od-liste li { font-size:13px; color:var(--ink2); padding:5px 0 5px 16px; position:relative;
                 line-height:1.5; }
  .od-liste li::before { content:""; position:absolute; left:2px; top:12px; width:6px; height:6px;
                         border-radius:50%; background:var(--track); }
  .od-liste.aciklar li::before { background:var(--mavi); }
  .od-liste.bitenler li::before { background:var(--yesil); }
  .od-liste li.gec::before { background:var(--kirmizi); box-shadow:0 0 8px var(--kirmizi); }
  .od-liste li .kim { color:var(--muted); font-size:11.5px; }
  .od-liste li .tarih-gec { color:var(--kirmizi); font-weight:600; font-size:11.5px; }
  .o-ust { display:flex; align-items:baseline; gap:11px; min-width:0; flex-wrap:wrap; }
  .dot { width:9px; height:9px; border-radius:50%; flex:none; transform:translateY(-1px); }
  .s-hazir .dot{background:var(--yesil); box-shadow:0 0 10px var(--yesil);}
  .s-yolunda .dot{background:var(--mavi); box-shadow:0 0 10px var(--mavi);}
  .s-dikkat .dot{background:var(--kirmizi); box-shadow:0 0 10px var(--kirmizi);}
  .s-sessiz .dot{background:var(--muted);}
  .o-ad { font-weight:600; font-size:15.5px; }
  .o-zaman { color:var(--muted); font-size:13px; white-space:nowrap; }
  .o-alt { grid-column:1; padding-left:20px; }
  .o-durum { font-size:13px; color:var(--ink2); }
  .s-dikkat .o-durum { color:var(--kirmizi); font-weight:600; }
  .s-hazir .o-durum { color:var(--yesil); }
  .o-sag { grid-column:2; grid-row:1 / span 2; display:flex; flex-direction:column;
           align-items:flex-end; justify-content:center; gap:7px; }
  .mtrack { display:block; width:120px; height:6px; border-radius:5px; background:var(--track);
            overflow:hidden; }
  .mfill { display:block; height:100%; border-radius:5px; width:var(--w);
           background:linear-gradient(90deg,var(--mavi),var(--mavi-soft)); }
  .mtxt { font-size:12px; color:var(--ink2); font-variant-numeric:tabular-nums; }
  details.devam { margin-top:14px; }
  details.devam summary { cursor:pointer; font-size:13.5px; color:var(--ink2); padding:10px 12px;
                          list-style:none; display:flex; align-items:center; gap:8px;
                          border-radius:12px; transition:background .2s, color .2s; }
  details.devam summary:hover { background:var(--cam2); color:var(--ink); }
  details.devam summary::before { content:"+"; font-size:16px; color:var(--mavi-soft);
                                  transition:transform .25s; }
  details.devam[open] summary::before { transform:rotate(45deg); }

  /* kişiler (haftalık çubuklar) */
  .k-grid { display:flex; flex-direction:column; gap:13px; margin-top:4px; }
  .k-satir { display:grid; grid-template-columns:minmax(110px,170px) 1fr 40px 70px;
             align-items:center; gap:14px; }
  .k-ad { font-size:13.5px; color:var(--ink2); text-align:right; white-space:nowrap;
          overflow:hidden; text-overflow:ellipsis; }
  .k-bar { height:15px; background:var(--track); border-radius:4px; overflow:hidden; }
  .k-fill { display:block; height:100%; width:var(--w); min-width:2px; border-radius:4px;
            background:linear-gradient(90deg,var(--aqua), #57dfae); }
  .k-fill.sifir { background:transparent; min-width:0; }
  .k-say { font-size:14.5px; font-weight:650; font-variant-numeric:tabular-nums; }
  .k-acik { font-size:12px; color:var(--muted); text-align:right;
            font-variant-numeric:tabular-nums; white-space:nowrap; }
  .not-satir { margin-top:24px; padding:14px 18px; border:1px solid var(--border);
               border-radius:14px; background:var(--cam2); font-size:13.5px;
               color:var(--ink2); display:flex; gap:10px; align-items:baseline; }
  .not-satir svg { color:var(--amber); flex:none; transform:translateY(2px); }
  .not-satir b { color:var(--ink); }

  /* takılan işler */
  .gec-satir { display:grid; grid-template-columns:1fr auto; gap:2px 20px;
               padding:15px 12px 13px; border-bottom:1px solid var(--grid);
               border-radius:14px; transition:background .25s, transform .25s; }
  .gec-satir:last-child { border-bottom:none; }
  .gec-satir:hover { background:var(--cam2); transform:translateX(6px); }
  .g-baslik { font-weight:600; font-size:14.5px; }
  .g-meta { font-size:12.5px; color:var(--muted); }
  .g-sure { grid-column:2; grid-row:1 / span 2; align-self:center; text-align:right; }
  .g-gun { font-family:var(--serif); font-size:23px; font-weight:560; color:var(--kirmizi);
           line-height:1.1; text-shadow:0 0 22px rgba(239,107,107,.35); }
  .g-kisi { font-size:12px; color:var(--muted); }
  .temiz { color:var(--yesil); font-size:15px; display:flex; gap:9px; align-items:baseline; }

  /* radar */
  .radar { padding:0; }
  .radar li { list-style:none; display:flex; gap:14px; padding:14px 12px;
              border-bottom:1px solid var(--grid); font-size:14.5px; color:var(--ink2);
              align-items:baseline; border-radius:14px;
              transition:background .25s, transform .25s; }
  .radar li:last-child { border-bottom:none; }
  .radar li:hover { background:var(--cam2); transform:translateX(6px); }
  .radar b { color:var(--ink); font-weight:600; }
  .radar svg { flex:none; color:var(--amber); transform:translateY(2px); }
  .r-txt { flex:1; min-width:0; }
  .soluk { color:var(--muted); font-size:12.5px; }

  /* ================= HAFTANIN LİGİ ================= */
  .lig-tablo { width:100%; border-collapse:collapse; }
  .lig-tablo th { text-align:left; font-size:11px; text-transform:uppercase;
                  letter-spacing:.09em; color:var(--muted); font-weight:700;
                  padding:8px 10px; border-bottom:1px solid var(--grid); }
  .lig-tablo th.sag, .lig-tablo td.sag { text-align:right; }
  .lig-satir td { padding:13px 10px; border-bottom:1px solid var(--grid);
                  vertical-align:middle; }
  .lig-satir { transition:background .25s; cursor:pointer; }
  .lig-satir:hover { background:var(--cam2); }
  .lig-satir:focus-visible { outline:2px solid var(--mavi); outline-offset:-2px; }
  .lig-cev { width:30px; text-align:center; color:var(--muted); }
  .lig-cev svg { transition:transform .3s cubic-bezier(.16,1,.3,1); vertical-align:middle; }
  .lig-satir.acik .lig-cev svg { transform:rotate(180deg); color:var(--mavi-soft); }
  .lig-satir.acik td { border-bottom-color:transparent; }
  .lig-detay-tr td { padding:0; border-bottom:1px solid var(--grid); }
  .lig-detay-tr.kapali td { border-bottom:none; padding:0; }
  .lig-detay { display:grid; grid-template-rows:0fr;
               transition:grid-template-rows .45s cubic-bezier(.16,1,.3,1); }
  .lig-detay-tr.acik .lig-detay { grid-template-rows:1fr; }
  .lig-detay .od-ic { overflow:hidden; min-height:0; }
  .lig-detay .od-kutu { margin:2px 10px 18px; }
  .lig-satir.birinci { background:linear-gradient(90deg, rgba(245,192,76,.10), transparent 70%); }
  .siralama { width:44px; }
  .madalya { display:grid; place-items:center; }
  .rütbe { display:grid; place-items:center; width:26px; height:26px; border-radius:50%;
           background:var(--cam2); border:1px solid var(--border); font-size:12.5px;
           font-weight:700; color:var(--ink2); font-variant-numeric:tabular-nums; }
  .oyuncu { display:flex; align-items:center; gap:12px; min-width:0; }
  .avatar { width:38px; height:38px; border-radius:50%; flex:none;
            display:grid; place-items:center; font-size:13px; font-weight:700;
            color:#fff; letter-spacing:.02em;
            background:var(--av, var(--mavi));
            box-shadow:0 0 0 2px var(--page), 0 0 16px color-mix(in srgb, var(--av, var(--mavi)) 45%, transparent); }
  .o-isim { font-weight:650; font-size:14.5px; line-height:1.25; }
  .unvan { font-size:11.5px; color:var(--muted); display:flex; align-items:center; gap:5px; }
  .unvan svg { color:var(--amber); }
  .birinci .unvan { color:var(--altin); }
  .yaris { min-width:120px; }
  .y-track { display:block; height:12px; background:var(--track); border-radius:4px;
             overflow:hidden; }
  .y-fill { display:block; height:100%; width:var(--w); min-width:2px; border-radius:4px;
            background:linear-gradient(90deg,var(--mavi),var(--mor)); }
  .birinci .y-fill { background:linear-gradient(90deg,var(--altin),#f8d98a); }
  .y-fill.sifir { background:transparent; min-width:0; }
  .lig-buhafta { font-family:var(--serif); font-size:22px; font-weight:560;
                 font-variant-numeric:tabular-nums; line-height:1; }
  .lig-kucuk { font-size:13px; color:var(--ink2); font-variant-numeric:tabular-nums; }
  .cift { display:inline-flex; flex-direction:column; align-items:flex-end; gap:3px; }
  .cift .toplami { font-size:11.5px; color:var(--muted); font-variant-numeric:tabular-nums; }
  .cift.yesil .lig-buhafta { color:var(--aqua); }
  .lig-dip { margin-top:16px; font-size:12.5px; color:var(--muted); }

  footer { margin:clamp(44px,8vh,72px) 0 44px; padding-top:24px;
           border-top:1px solid var(--grid); display:flex; justify-content:space-between;
           gap:12px; flex-wrap:wrap; color:var(--muted); font-size:12.5px; }
  footer .marka { font-family:var(--serif); font-style:italic; color:var(--ink2); }

  #tip { position:fixed; pointer-events:none; background:#fff; color:#0b0b0b;
         font-family:var(--sans); font-size:12.5px; padding:7px 11px; border-radius:8px;
         max-width:320px; opacity:0; transition:opacity .12s; z-index:60;
         box-shadow:0 6px 24px rgba(0,0,0,.35); }

  @media (max-width:640px) {
    .k-satir { grid-template-columns:minmax(88px,116px) 1fr 30px 56px; gap:9px; }
    .lig-tablo th.gizle, .lig-satir td.gizle { display:none; }
    .yaris { min-width:70px; }
    .o-sag .mtrack { width:84px; }
  }
</style>
</head>
<body>
<div class="gokyuzu" aria-hidden="true"><div class="aurora a1"></div><div class="aurora a2"></div><div class="aurora a3"></div></div>
<div class="gren" aria-hidden="true"></div>
<div id="progress" aria-hidden="true"></div>
<button class="tema" id="temaBtn" aria-label="Tema değiştir" title="Açık/koyu tema">
  <svg width="15" height="15" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><circle cx="8" cy="8" r="3.4"/><path d="M8 1.2v1.6M8 13.2v1.6M1.2 8h1.6M13.2 8h1.6M3.2 3.2l1.1 1.1M11.7 11.7l1.1 1.1M12.8 3.2l-1.1 1.1M4.3 11.7l-1.1 1.1"/></svg>
</button>

<div class="wrap">

  <header class="hero">
    <p class="etiket" data-in><span class="isik"></span><b>__PLAN_ADI__</b> · haftalık rapor · __ARALIK__</p>
    <p class="kunye" data-in>__KUNYE__</p>
    <h1 id="baslik">__BASLIK__</h1>
    <p class="anlati" data-in>__ANLATI__</p>
    <div class="sayilar">__SAYILAR__</div>
    <p class="devam-ipucu" data-in>haftanın detayları <span class="ok">↓</span></p>
  </header>

  <section id="orglar">
    <div class="kart">
      <div class="b-baslik" data-in style="--rk:var(--mavi)"><span class="b-no">01</span><h2>Organizasyonlar ne durumda?</h2></div>
      <p class="b-alt" data-in>Tarihe göre sıralı. Bir satıra tıklayın — o organizasyon için yazdığım özet ve kritik notlar açılır.</p>
      <div class="org-liste">__ORGLAR__</div>
      __ORG_DEVAM__
    </div>
  </section>

  <section id="kisiler">
    <div class="kart">
      <div class="b-baslik" data-in style="--rk:var(--aqua)"><span class="b-no">02</span><h2>Bu hafta kim ne yaptı?</h2></div>
      <p class="b-alt" data-in>Yeşil çubuklar bu hafta bitirilen işler; sağdaki küçük sayı hâlâ üzerlerinde duran açık iş.</p>
      <div class="k-grid">__KISILER__</div>
      __SAHIPSIZ__
    </div>
  </section>

  <section id="geciken">
    <div class="kart">
      <div class="b-baslik" data-in style="--rk:var(--kirmizi)"><span class="b-no">03</span><h2>__GECIKEN_BASLIK__</h2></div>
      <p class="b-alt" data-in>__GECIKEN_ALT__</p>
      __GECIKENLER__
    </div>
  </section>

  <section id="radar">
    <div class="kart">
      <div class="b-baslik" data-in style="--rk:var(--amber)"><span class="b-no">04</span><h2>Önümüzdeki haftanın radarı</h2></div>
      <p class="b-alt" data-in>Pazartesi güne bunlara bakarak başlayın.</p>
      <ul class="radar">__RADAR__</ul>
    </div>
  </section>

  <section id="lig">
    <div class="kart">
      <div class="b-baslik" data-in style="--rk:var(--mor)"><span class="b-no">05</span><h2>Kişi Kişi Bu Hafta</h2></div>
      <p class="b-alt" data-in>Herkesin Planner'da açtığı ve tamamladığı görev sayıları — büyük sayı bu hafta, altındaki toplam. Bir kişiye tıklayın, o haftaki yorumum açılır.</p>
      <table class="lig-tablo">
        <thead><tr>
          <th class="siralama">#</th><th>Kişi</th>
          <th class="sag">Açtığı görev</th><th class="sag">Tamamladığı görev</th>
          <th class="sag gizle">Üzerindeki açık iş</th><th class="lig-cev"></th>
        </tr></thead>
        <tbody>__LIG__</tbody>
      </table>
      <p class="lig-dip">Not: Bu sayılar sıralama değil, fotoğraf — kimin haftası nasıl geçmiş, tek bakışta görmek için.</p>
    </div>
  </section>

  <footer>
    <span class="marka">__PLAN_ADI__ haftalık raporu</span>
    <span>__KUNYE_FOOT__</span>
  </footer>
</div>

<div id="tip" role="tooltip"></div>

<script>
__GSAP_JS__
</script>
<script>
(function () {
  const btn = document.getElementById('temaBtn');
  btn.addEventListener('click', () => {
    const r = document.documentElement;
    r.dataset.theme = r.dataset.theme === 'light' ? '' : 'light';
  });

  const tip = document.getElementById('tip');
  document.querySelectorAll('[data-tip]').forEach(el => {
    el.addEventListener('pointermove', e => {
      tip.textContent = el.dataset.tip;
      tip.style.opacity = 1;
      tip.style.left = Math.min(e.clientX + 14, innerWidth - tip.offsetWidth - 8) + 'px';
      tip.style.top = Math.min(e.clientY + 16, innerHeight - tip.offsetHeight - 8) + 'px';
    });
    el.addEventListener('pointerleave', () => tip.style.opacity = 0);
  });

  // organizasyon akordiyonu
  document.querySelectorAll('.org-satir').forEach(satir => {
    satir.addEventListener('click', () => {
      const blok = satir.closest('.org-blok');
      const acikti = blok.classList.contains('acik');
      blok.classList.toggle('acik', !acikti);
      satir.setAttribute('aria-expanded', String(!acikti));
      if (!acikti && window.ScrollTrigger) setTimeout(() => ScrollTrigger.refresh(), 480);
    });
  });

  // lig akordiyonu (tablo satırı → altındaki detay satırı)
  document.querySelectorAll('.lig-satir').forEach(satir => {
    const ac = () => {
      const detay = satir.nextElementSibling;
      if (!detay || !detay.classList.contains('lig-detay-tr')) return;
      const acikti = satir.classList.contains('acik');
      satir.classList.toggle('acik', !acikti);
      detay.classList.toggle('acik', !acikti);
      detay.classList.toggle('kapali', acikti);
      satir.setAttribute('aria-expanded', String(!acikti));
      if (!acikti && window.ScrollTrigger) setTimeout(() => ScrollTrigger.refresh(), 480);
    };
    satir.addEventListener('click', ac);
    satir.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); ac(); } });
  });

  if (!window.gsap) return;
  gsap.registerPlugin(ScrollTrigger);

  const mm = gsap.matchMedia();
  mm.add("(prefers-reduced-motion: no-preference)", () => {

    gsap.to('#progress', {
      scaleX: 1, ease: 'none',
      scrollTrigger: { trigger: document.body, start: 'top top', end: 'bottom bottom', scrub: 0.4 }
    });

    const tl = gsap.timeline({ defaults: { ease: 'expo.out' } });
    tl.from('.etiket', { y: 14, opacity: 0, duration: .8 })
      .from('#baslik', { y: 36, opacity: 0, duration: 1.1 }, '-=.55')
      .from('.hero .anlati', { y: 22, opacity: 0, duration: .9 }, '-=.75')
      .from('.sayi', { y: 26, opacity: 0, scale: .96, duration: .8, stagger: .09 }, '-=.6')
      .from('.devam-ipucu', { opacity: 0, duration: .7 }, '-=.3');

    document.querySelectorAll('[data-count]').forEach(el => {
      gsap.fromTo(el, { innerText: 0 }, {
        innerText: +el.dataset.count, duration: 1.6, delay: .45, ease: 'expo.out',
        snap: { innerText: 1 }
      });
    });

    gsap.utils.toArray('section [data-in]').forEach(el => {
      gsap.from(el, {
        y: 26, opacity: 0, duration: .85, ease: 'expo.out',
        scrollTrigger: { trigger: el, start: 'top 88%' }
      });
    });

    [['.org-liste .org-satir'], ['.k-grid .k-satir'], ['.gec-satir'], ['.radar li'], ['.lig-satir']].forEach(([sel]) => {
      const items = gsap.utils.toArray(sel);
      if (!items.length) return;
      gsap.from(items, {
        y: 22, opacity: 0, duration: .6, ease: 'power3.out', stagger: .07,
        scrollTrigger: { trigger: items[0], start: 'top 90%' }
      });
    });

    gsap.utils.toArray('.mfill, .k-fill:not(.sifir), .y-fill:not(.sifir)').forEach(bar => {
      const w = getComputedStyle(bar).getPropertyValue('--w').trim() || '0%';
      gsap.fromTo(bar, { width: 0 }, {
        width: w, duration: 1.2, ease: 'expo.out',
        scrollTrigger: { trigger: bar, start: 'top 92%' }
      });
    });

    gsap.from('.g-gun', {
      scale: .6, opacity: 0, duration: .7, ease: 'back.out(2.2)', stagger: .1,
      scrollTrigger: { trigger: '#geciken', start: 'top 80%' }
    });

    // lig: sayılar sayarak gelir, madalyalar zıplar
    document.querySelectorAll('[data-count-scroll]').forEach(el => {
      gsap.fromTo(el, { innerText: 0 }, {
        innerText: +el.dataset.countScroll, duration: 1.3, ease: 'expo.out',
        snap: { innerText: 1 },
        scrollTrigger: { trigger: el, start: 'top 90%' }
      });
    });

  });
})();
</script>
</body>
</html>"""
