import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# 1. SETUP & CONFIG (Deine Keywords sind hier hinterlegt)
st.set_page_config(page_title="AI Infra Monitor", layout="wide")

CONFIG = {
    "Hardware (SEMI)": {
        "etf": "SMH", "stock": "NVDA", "color": "#1E90FF",
        "keywords": ["Blackwell", "CapEx", "TSMC", "HBM", "GPU", "Demand"],
        "info": "Fokus: Rechenpower & Chip-Nachfrage"},
    "Power (WUTI)": {
        "etf": "XLU", "stock": "NEE", "color": "#FFD700",
        "keywords": ["Nuclear", "PPA", "Grid", "SMR", "Electricity", "Data Center"],
        "info": "Fokus: Energie-Infrastruktur & Deals"},
    "Build (XLI)": {
        "etf": "XLI", "stock": "CAT", "color": "#32CD32",
        "keywords": ["Backlog", "Construction", "Data Center", "Cooling", "HVAC"],
        "info": "Fokus: Physische Errichtung & Kühlung"},
    "MidCap (SPY4)": {
        "etf": "IJH", "stock": "PSTG", "color": "#FF4500",
        "keywords": ["Rotation", "Small Cap", "Broadening", "Specialist"],
        "info": "Fokus: Nischen-Anbieter & Marktbreite"}
}

st.title("🛡️ Strategisches KI-Invest Cockpit")

# 2. MARKT-AMPEL & PORTFOLIO
with st.expander("📊 Markt-Ampel & Portfolio-Links"):
    m_d = yf.download(["^VIX", "^TNX", "SPY"], period="5d", progress=False)['Close']
    c1, c2, c3 = st.columns(3)
    c1.metric("VIX", f"{m_d['^VIX'].iloc[-1]:.2f}")
    c2.metric("Zinsen 10J", f"{m_d['^TNX'].iloc[-1]:.2f}%")
    st.markdown("---")
    watchlist = {"MSCI World": "IWDA.AS", "InfoTech": "TNOW.PA", "Industrials": "XLI", "Semicon": "SEMI.AS", "Utilities": "WUTI.SW", "MidCap": "SPY4.DE"}
    cols = st.columns(len(watchlist))
    for i, (n, t) in enumerate(watchlist.items()):
        cols[i].markdown(f"**[{n}](https://finance.yahoo.com/quote/{t})**")

# 3. ANALYSE-ENGINE
st.sidebar.header("🛠️ Strategie-Parameter")
f1 = st.sidebar.checkbox("Hardware: CapEx-Boom")
f2 = st.sidebar.checkbox("Power: Energie-Deals")
f3 = st.sidebar.checkbox("Build: Bau-Boom")

if st.button("Komplett-Analyse & News-Scan starten", type="primary"):
    with st.spinner('Berechne Scores und scanne News nach Keywords...'):
        df = yf.download(["SMH", "XLU", "XLI", "IJH", "SPY"], period="1y", progress=False)['Close']
        
        # Performance-Messung (Maßstab: 6 Monate vs S&P 500)
        p_spy = (df['SPY'].iloc[-1]/df['SPY'].iloc[-126]-1)*100
        
        scores = {k: 0 for k in CONFIG.keys()}
        results_data = {}

        for layer, cfg in CONFIG.items():
            etf_perf = (df[cfg['etf']].iloc[-1]/df[cfg['etf']].iloc[-126]-1)*100
            rel_strength = etf_perf - p_spy
            
            # Scoring
            if etf_perf > 15: scores[layer] += 3
            if rel_strength > 1: scores[layer] += 3
            if (layer == "Hardware (SEMI)" and f1) or (layer == "Power (WUTI)" and f2) or (layer == "Build (XLI)" and f3):
                scores[layer] += 4
            
            results_data[layer] = {"perf": etf_perf, "rel": rel_strength}

        # ANZEIGE DER SCORES
        st.header("1️⃣ Analyse-Ergebnisse")
        res_cols = st.columns(4)
        for i, (layer, score) in enumerate(scores.items()):
            with res_cols[i]:
                st.markdown(f"<h4 style='color:{CONFIG[layer]['color']}'>{layer}</h4>", unsafe_allow_html=True)
                st.metric("Score", f"{score}/10")
                st.progress(score/10.0)
                st.caption(f"Momentum: {results_data[layer]['perf']:.1f}%")
                st.caption(f"Rel. Stärke: {results_data[layer]['rel']:.1f}%")

        # 4. KEYWORD NEWS SCANNER
        st.markdown("---")
        best_layer = max(scores, key=scores.get)
        st.header(f"2️⃣ Strategisches News-Radar: {best_layer}")
        
        target_stock = CONFIG[best_layer]["stock"]
        keywords = CONFIG[best_layer]["keywords"]
        
        try:
            news_items = yf.Ticker(target_stock).news
            if news_items:
                found_news = 0
                for n in news_items:
                    title = n.get('title', '')
                    # Checke, ob Keywords im Titel vorkommen
                    match = [word for word in keywords if word.lower() in title.lower()]
                    
                    # Anzeige der News
                    col_a, col_b = st.columns([1, 4])
                    with col_a:
                        if match: st.warning(f"🎯 {match[0]}")
                        else: st.write("🔹 News")
                    with col_b:
                        st.markdown(f"**[{title}]({n.get('link', '#')})**")
                        st.caption(f"Quelle: {n.get('publisher', 'Unbekannt')}")
                    
                    found_news += 1
                    if found_news >= 5: break
            else:
                st.write("Keine aktuellen Nachrichten gefunden.")
        except:
            st.write("Fehler beim Abruf der News-Schnittstelle.")

st.caption(f"Referenz-Maßstab: S&P 500 (SPY) | Stand: {datetime.now().strftime('%d.%m.%Y')}")
