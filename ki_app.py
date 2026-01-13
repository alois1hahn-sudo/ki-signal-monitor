import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# 1. SETUP & KONFIGURATION
st.set_page_config(page_title="KI-Invest Cockpit 2026", layout="wide")

CONFIG = {
    "Hardware (SEMI)": {"etf": "SMH", "stock": "NVDA", "color": "#1E90FF", 
        "info": "Chips & Hardware: Ohne GPUs keine KI."},
    "Power (WUTI)": {"etf": "XLU", "stock": "NEE", "color": "#FFD700", 
        "info": "Energie & Netz: KI-Zentren fressen Strom."},
    "Build (XLI)": {"etf": "XLI", "stock": "CAT", "color": "#32CD32", 
        "info": "Bau & Industrie: Physische Infrastruktur."},
    "MidCap (SPY4)": {"etf": "IJH", "stock": "PSTG", "color": "#FF4500", 
        "info": "Nische & Spezialisten: Die zweite Reihe."}
}

st.title("🛡️ Strategisches KI-Invest Cockpit")

# 2. MARKT-AMPEL
st.subheader("🚦 Globale Markt-Ampel")
try:
    m_d = yf.download(["^VIX", "^TNX", "SPY"], period="5d", progress=False)['Close']
    c1, c2, c3 = st.columns(3)
    c1.metric("Angst-Index (VIX)", f"{m_d['^VIX'].iloc[-1]:.2f}", help="VIX > 25 = Panikgefahr")
    c2.metric("US 10J Zinsen", f"{m_d['^TNX'].iloc[-1]:.2f}%", help="Steigende Zinsen belasten Tech")
    c3.info("Die Ampel dient der allgemeinen Risikoeinschätzung.")
except: st.write("Warte auf Marktdaten...")

st.markdown("---")

# 3. INTERAKTIVE SIGNAL-STEUERUNG (Sidebar)
st.sidebar.header("🛠️ Analyse-Einstellungen")
st.sidebar.subheader("Signal-Module zuschalten")
use_mom = st.sidebar.toggle("Momentum (Trendfolge)", value=True)
use_rel = st.sidebar.toggle("Relative Stärke (Outperformance)", value=True)
use_fund = st.sidebar.toggle("Fundamentale Häkchen", value=True)

st.sidebar.markdown("---")
st.sidebar.subheader("Manuelle Signale")
f1 = st.sidebar.checkbox("CapEx-Boom (Hardware)")
f2 = st.sidebar.checkbox("Energie-Deals (Power)")
f3 = st.sidebar.checkbox("Bau-Rekorde (Build)")

# 4. PORTFOLIO ÜBERSICHT
st.header("1️⃣ Portfolio & Links")
watchlist = {"MSCI World": "IWDA.AS", "InfoTech": "TNOW.PA", "Industrials": "XLI", 
             "Semicon": "SEMI.AS", "Utilities": "WUTI.SW", "MidCap": "SPY4.DE"}
cols_w = st.columns(len(watchlist))
for i, (n, t) in enumerate(watchlist.items()):
    cols_w[i].markdown(f"**[{n}](https://finance.yahoo.com/quote/{t})**")

st.markdown("---")

# 5. ANALYSE & ERKLÄRUNG
st.header("2️⃣ Strategische Auswertung")

if st.button("Analyse mit gewählten Signalen starten", type="primary"):
    with st.spinner('Berechne gewählte Signal-Module...'):
        df = yf.download(["SMH", "XLU", "XLI", "IJH", "SPY"], period="1y", progress=False)['Close']
        
        scores = {k: 0 for k in CONFIG.keys()}
        details = {k: [] for k in CONFIG.keys()}

        # Berechnung der Rohdaten
        p_semi = (df['SMH'].iloc[-1]/df['SMH'].iloc[-126]-1)*100
        p_pwr = (df['XLU'].iloc[-1]/df['XLU'].iloc[-126]-1)*100
        p_bld = (df['XLI'].iloc[-1]/df['XLI'].iloc[-126]-1)*100
        p_mid = (df['IJH'].iloc[-1]/df['IJH'].iloc[-126]-1)*100
        p_spy = (df['SPY'].iloc[-1]/df['SPY'].iloc[-126]-1)*100

        # SIGNAL-LOGIK (Nur wenn zugeschaltet)
        for layer in CONFIG.keys():
            # A. MOMENTUM (Trend)
            if use_mom:
                val = {"Hardware (SEMI)": p_semi, "Power (WUTI)": p_pwr, 
                       "Build (XLI)": p_bld, "MidCap (SPY4)": p_mid}[layer]
                if val > 15:
                    scores[layer] += 3
                    details[layer].append(f"📈 Momentum (+{val:.1f}%): Der Sektor hat einen starken Aufwärtstrend.")

            # B. RELATIVE STÄRKE (vs Markt)
            if use_rel:
                rel_val = {"Hardware (SEMI)": p_semi - p_spy, "Power (WUTI)": p_pwr - p_spy, 
                           "Build (XLI)": p_bld - p_spy, "MidCap (SPY4)": p_mid - p_spy}[layer]
                if rel_val > 5:
                    scores[layer] += 3
                    details[layer].append(f"📊 Rel. Stärke (+{rel_val:.1f}%): Schlägt den S&P 500 deutlich.")

            # C. FUNDAMENTALS (Häkchen)
            if use_fund:
                check = {"Hardware (SEMI)": f1, "Power (WUTI)": f2, "Build (XLI)": f3, "MidCap (SPY4)": False}[layer]
                if check:
                    scores[layer] += 4
                    details[layer].append("💎 Fundamental: Deine manuellen News-Daten bestätigen den Trend.")

        # ANZEIGE DER ERGEBNISSE
        res_cols = st.columns(4)
        for i, (layer, score) in enumerate(scores.items()):
            with res_cols[i]:
                st.markdown(f"<h4 style='color:{CONFIG[layer]['color']}'>{layer}</h4>", unsafe_allow_html=True)
                st.caption(CONFIG[layer]['info'])
                st.metric("Score", f"{score}/10")
                st.progress(score/10.0)
                for d in details[layer]:
                    st.info(d)

        # NEWS FEEDS
        st.markdown("---")
        best = max(scores, key=scores.get)
        st.subheader(f"📑 Fokus-News für den Top-Sektor: {best}")
        try:
            news_list = yf.Ticker(CONFIG[best]["stock"]).news
            if news_list:
                for n in news_list[:3]:
                    t = n.get('title') or n.get('headline') or "Kein Titel"
                    l = n.get('link') or n.get('url') or "#"
                    st.write(f"🔹 [{t}]({l})")
        except: st.write("Fehler beim Abruf der News.")

st.caption(f"Update: {datetime.now().strftime('%d.%m.%Y %H:%M')} | Strategie: INTERACTIVE_v3")
