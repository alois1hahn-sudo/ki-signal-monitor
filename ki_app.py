import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# 1. SETUP & CONFIGURATION
st.set_page_config(page_title="KI-Invest Cockpit", layout="wide")

CONFIG = {
    "Hardware (SEMI)": {
        "etf": "SMH", "stock": "NVDA", "color": "#1E90FF",
        "keywords": ["Blackwell", "CapEx", "TSMC", "HBM", "GPU", "Demand"],
        "info": "Prüfe: Chip-Zyklen & Hyperscaler-Budgets."},
    "Power (WUTI)": {
        "etf": "XLU", "stock": "NEE", "color": "#FFD700",
        "keywords": ["Nuclear", "PPA", "Grid", "SMR", "Electricity", "Data Center"],
        "info": "Prüfe: Stromanschluss-Warteschlangen & Realzinsen."},
    "Build (XLI)": {
        "etf": "XLI", "stock": "CAT", "color": "#32CD32",
        "keywords": ["Backlog", "Construction", "Data Center", "Cooling", "HVAC"],
        "info": "Prüfe: Auftragsbestände der Industrie-Giganten."},
    "MidCap (SPY4)": {
        "etf": "IJH", "stock": "PSTG", "color": "#FF4500",
        "keywords": ["Rotation", "Mid Cap", "Broadening", "Specialist"],
        "info": "Prüfe: Marktbreite & Zinswende."}
}

# 2. HEADER & MAKRO-AMPEL
st.title("🛡️ Strategisches KI-Invest Cockpit")

with st.expander("📊 Markt-Zustand & Profi-Analyse-Tools", expanded=True):
    try:
        m_d = yf.download(["^VIX", "^TNX", "SPY"], period="5d", progress=False)['Close']
        c1, c2, c3 = st.columns(3)
        c1.metric("VIX (Angst)", f"{m_d['^VIX'].iloc[-1]:.2f}")
        c2.metric("US 10J Zinsen", f"{m_d['^TNX'].iloc[-1]:.2f}%")
        c3.info("Maßstab: S&P 500 (SPY) ist die Benchmark.")
    except:
        st.write("Warte auf Marktdaten...")
    
    st.markdown("---")
    # Watchlist mit EM ex-China
    watchlist = {"MSCI World": "IWDA.AS", "InfoTech": "TNOW.PA", "Industrials": "XLI", 
                 "Semicon": "SEMI.AS", "Utilities": "WUTI.SW", "MidCap": "SPY4.DE", "EM ex-China": "EMXC"}
    cols = st.columns(len(watchlist))
    for i, (n, t) in enumerate(watchlist.items()):
        with cols[i]:
            st.write(f"**{n}**")
            st.caption(f"[Yahoo](https://finance.yahoo.com/quote/{t})")

st.markdown("---")

# 3. SIDEBAR STEUERUNG
st.sidebar.header("🛠️ Signal-Module")
use_mom = st.sidebar.toggle("Momentum (6 Mon. > 15%)", value=True)
use_rel = st.sidebar.toggle("Rel. Stärke (vs. S&P 500)", value=True)

st.sidebar.markdown("---")
f1 = st.sidebar.checkbox("Hardware: CapEx-Boom")
f2 = st.sidebar.checkbox("Power: Energie-Deals")
f3 = st.sidebar.checkbox("Build: Bau-Boom")
f4 = st.sidebar.checkbox("EM: Schwellenländer-Stärke")

# 4. ANALYSE-ENGINE
if st.button("Komplett-Analyse starten", type="primary"):
    with st.spinner('Daten werden extrahiert...'):
        df = yf.download(["SMH", "XLU", "XLI", "IJH", "SPY"], period="1y", progress=False)['Close']
        p_spy = (df['SPY'].iloc[-1]/df['SPY'].iloc[-126]-1)*100
        
        scores = {k: 0 for k in CONFIG.keys()}
        details = {k: [] for k in CONFIG.keys()}

        for layer, cfg in CONFIG.items():
            perf = (df[cfg['etf']].iloc[-1]/df[cfg['etf']].iloc[-126]-1)*100
            rel = perf - p_spy
            
            if use_mom and perf > 15:
                scores[layer] += 3
                details[layer].append(f"📈 Momentum: +{perf:.1f}%")
            if use_rel and rel > 1:
                scores[layer] += 3
                details[layer].append(f"📊 Rel. Stärke: +{rel:.1f}%")
            
            # Manuelle Signale
            check = {"Hardware (SEMI)": f1, "Power (WUTI)": f2, "Build (XLI)": f3, "MidCap (SPY4)": f4}[layer]
            if check:
                scores[layer] += 4
                details[layer].append("💎 Fundamentaler Bonus")

        # ANZEIGE
        res_cols = st.columns(4)
        for i, (layer, score) in enumerate(scores.items()):
            with res_cols[i]:
                st.markdown(f"<h4 style='color:{CONFIG[layer]['color']}'>{layer}</h4>", unsafe_allow_html=True)
                st.metric("Score", f"{score}/10")
                st.progress(score/10.0)
                for d in details[layer]: st.info(d)

        # 5. NEWS RADAR (REPARIERTE LOGIK)
        st.markdown("---")
        best = max(scores, key=scores.get)
        st.header(f"📰 News-Radar: {best}")
        
        try:
            ticker_obj = yf.Ticker(CONFIG[best]["stock"])
            news_items = ticker_obj.news
            keywords = CONFIG[best]["keywords"]
            
            if news_items:
                for n in news_items[:5]:
                    # Hole Titel oder Headline
                    t = n.get('title') or n.get('headline') or "Kein Titel verfügbar"
                    l = n.get('link') or n.get('url') or "#"
                    
                    # Keyword Check
                    match = [w for w in keywords if w.lower() in t.lower()]
                    
                    c_n1, c_n2 = st.columns([1, 5])
                    with c_n1:
                        if match: st.warning(f"🎯 {match[0]}")
                        else: st.caption("🔹 News")
                    with c_n2:
                        st.markdown(f"**[{t}]({l})**")
            else:
                st.write("Keine aktuellen Nachrichten gefunden.")
        except Exception as e:
            st.write(f"News konnten nicht geladen werden.")

st.caption(f"Update: {datetime.now().strftime('%d.%m.%Y %H:%M')} | System: All-In-One_vFinal_Stable")
