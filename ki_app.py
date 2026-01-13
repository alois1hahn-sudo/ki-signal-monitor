import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# 1. SETUP & CONFIG
st.set_page_config(page_title="AI Infra Monitor 2026", layout="wide")

# Deine Konfiguration als Datenstruktur
CONFIG = {
    "Hardware": {
        "etfs": ["SMH", "EMXC"],
        "top_stocks": ["NVDA", "TSM", "AVGO", "ASML"],
        "keywords": ["GPU demand", "Blackwell", "CoWoS", "foundry capacity"],
        "color": "#1E90FF"
    },
    "Power": {
        "etfs": ["XLU", "WUTI.SW"],
        "top_stocks": ["NEE", "CEG", "VST", "SO"],
        "keywords": ["nuclear PPA", "data center power", "grid connection"],
        "color": "#FFD700"
    },
    "Build": {
        "etfs": ["XLI"],
        "top_stocks": ["GE", "CAT", "ETN", "HON"],
        "keywords": ["construction backlog", "datacenter buildout", "HVAC"],
        "color": "#32CD32"
    },
    "MidCap": {
        "etfs": ["SPY4.DE"],
        "top_stocks": ["PSTG", "FLEX", "CIEN", "HUBB"],
        "keywords": ["liquid cooling", "optical interconnect", "rotation"],
        "color": "#FF4500"
    }
}

st.title("🛡️ AI Infrastructure Monitor 2026-2036")
st.caption("Echtzeit-Analyse basierend auf deiner Layer-Konfiguration")

# 2. MARKT-AMPEL (MAKRO)
with st.container():
    st.subheader("🚦 Globale Markt-Ampel")
    m_data = yf.download(["^VIX", "^TNX", "IWDA.AS", "^SP500-20"], period="5d", progress=False)['Close']
    vix, yld = m_data["^VIX"].iloc[-1], m_data["^TNX"].iloc[-1]
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Markt-Angst (VIX)", f"{vix:.2f}", delta="- Ruhig" if vix < 20 else "+ Nervös", delta_color="inverse")
    c2.metric("US 10J Zinsen", f"{yld:.2f}%")
    
    # Tech vs World Momentum
    tech_mom = (m_data["^SP500-20"].iloc[-1]/m_d_start if (m_d_start := m_data["^SP500-20"].iloc[0]) else 1)
    world_mom = (m_data["IWDA.AS"].iloc[-1]/m_w_start if (m_w_start := m_data["IWDA.AS"].iloc[0]) else 1)
    c3.metric("Tech Momentum", f"{(tech_mom/world_mom):.2f}x", help="Verhältnis Tech-Wachstum zu Weltmarkt")

st.markdown("---")

# 3. ANALYSIS ENGINE
st.sidebar.header("📝 Fundamentale Checkliste")
f_capex = st.sidebar.checkbox("Hardware: CapEx-Boom (>20%)?")
f_power = st.sidebar.checkbox("Power: Neue Nuclear/PPA Deals?")
f_build = st.sidebar.checkbox("Build: DC-Bau-Rekorde?")

if st.button("Strategie-Check ausführen", type="primary"):
    with st.spinner('Scanne Ticker und News-Sentiment...'):
        # Kurse laden für alle Layer
        all_tickers = ["SMH", "XLU", "XLI", "SPY4.DE", "IWDA.AS"]
        prices = yf.download(all_tickers, period="1y", progress=False)['Close']
        
        scores = {}
        analysis_log = {}

        for layer, cfg in CONFIG.items():
            score = 0
            log = []
            
            # A. Technisches Momentum (6 Monate)
            etf = cfg["etfs"][0]
            perf = (prices[etf].iloc[-1] / prices[etf].iloc[-126] - 1) * 100
            if perf > 10: 
                score += 3
                log.append(f"Momentum: +{perf:.1f}%")
            
            # B. Fundamentale Häkchen
            if layer == "Hardware" and f_capex: score += 4; log.append("News: CapEx-Hürde genommen")
            if layer == "Power" and f_power: score += 5; log.append("News: Energie-Vorteil")
            if layer == "Build" and f_build: score += 4; log.append("News: Bau-Volumen")
            
            scores[layer] = score
            analysis_log[layer] = log

        # Anzeige der Ergebnisse
        best = max(scores, key=scores.get)
        st.success(f"### 🎯 Primärer Fokus-Layer: {best}")
        
        cols = st.columns(4)
        for i, (layer, score) in enumerate(scores.items()):
            with cols[i]:
                st.markdown(f"<h3 style='color:{CONFIG[layer]['color']}'>{layer}</h3>", unsafe_allow_html=True)
                st.metric("Score", f"{score}/10")
                st.progress(score/10.0)
                for entry in analysis_log[layer]:
                    st.caption(f"✅ {entry}")

        # 4. DEEP DIVE: NEWS & FUNDAMENTALS FÜR DEN GEWINNER
        st.markdown("---")
        st.subheader(f"📑 Deep Dive: {best} Top-Positionen & News")
        
        d_col1, d_col2 = st.columns([1, 2])
        
        with d_col1:
            st.write("**Top-Holdings Check:**")
            for stock_sym in CONFIG[best]["top_stocks"]:
                s_info = yf.Ticker(stock_sym).info
                pe = s_info.get('forwardPE', 'N/A')
                st.write(f"- **{stock_sym}**: KGV {pe}")
        
        with d_col2:
            st.write("**Strategisches News-Radar (Keywords):**")
            st.caption(f"Scannt auf: {', '.join(CONFIG[best]['keywords'])}")
            news = yf.Ticker(CONFIG[best]["top_stocks"][0]).news
            for n in news[:3]:
                st.markdown(f"▫️ [{n['title']}]({n['link']})")

st.caption(f"Letztes Update: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')} | Konfiguration: AI_INFRA_2026")
