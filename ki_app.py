import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# 1. SETUP & CONFIG
st.set_page_config(page_title="AI Infra Monitor 2026", layout="wide")

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
st.subheader("🚦 Globale Markt-Ampel")
try:
    m_list = ["^VIX", "^TNX", "IWDA.AS", "^SP500-20"]
    m_data = yf.download(m_list, period="5d", progress=False)['Close']
    vix = m_data["^VIX"].iloc[-1]
    yld = m_data["^TNX"].iloc[-1]
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Markt-Angst (VIX)", f"{vix:.2f}")
    c2.metric("US 10J Zinsen", f"{yld:.2f}%")
    
    tech_mom = (m_data["^SP500-20"].iloc[-1]/m_data["^SP500-20"].iloc[0])
    world_mom = (m_data["IWDA.AS"].iloc[-1]/m_d_w if (m_d_w := m_data["IWDA.AS"].iloc[0]) else 1)
    c3.metric("Tech Momentum", f"{(tech_mom/world_mom):.2f}x")
except:
    st.info("Marktdaten werden geladen...")

st.markdown("---")

# 3. ANALYSIS ENGINE
st.sidebar.header("📝 Fundamentale Checkliste")
f_capex = st.sidebar.checkbox("Hardware: CapEx-Boom (>20%)?")
f_power = st.sidebar.checkbox("Power: Neue Nuclear/PPA Deals?")
f_build = st.sidebar.checkbox("Build: DC-Bau-Rekorde?")

if st.button("Strategie-Check ausführen", type="primary"):
    with st.spinner('Scanne Ticker und News-Sentiment...'):
        all_tickers = ["SMH", "XLU", "XLI", "SPY4.DE", "IWDA.AS"]
        prices = yf.download(all_tickers, period="1y", progress=False)['Close']
        
        scores = {}
        analysis_log = {}

        for layer, cfg in CONFIG.items():
            score = 0
            log = []
            
            # Momentum
            etf = cfg["etfs"][0]
            if etf in prices:
                perf = (prices[etf].iloc[-1] / prices[etf].iloc[-126] - 1) * 100
                if perf > 10: 
                    score += 3
                    log.append(f"Momentum: +{perf:.1f}%")
            
            # Manual Signals
            if layer == "Hardware" and f_capex: score += 4; log.append("News: CapEx-Boom")
            if layer == "Power" and f_power: score += 5; log.append("News: Energie-Vorteil")
            if layer == "Build" and f_build: score += 4; log.append("News: Bau-Volumen")
            
            scores[layer] = score
            analysis_log[layer] = log

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

        # 4. DEEP DIVE & NEWS (KORRIGIERT)
        st.markdown("---")
        st.subheader(f"📑 Deep Dive: {best} Top-Positionen & News")
        
        d_col1, d_col2 = st.columns([1, 2])
        
        with d_col1:
            st.write("**Top-Holdings Check:**")
            for stock_sym in CONFIG[best]["top_stocks"]:
                try:
                    s_info = yf.Ticker(stock_sym).fast_info
                    last_price = s_info['last_price']
                    st.write(f"- **{stock_sym}**: ${last_price:.2f}")
                except:
                    st.write(f"- **{stock_sym}**: Daten laden...")
        
        with d_col2:
            st.write("**Strategisches News-Radar:**")
            try:
                # Wir nehmen den ersten Ticker der Top-Stocks für News
                news_data = yf.Ticker(CONFIG[best]["top_stocks"][0]).news
                if news_data:
                    for n in news_data[:3]:
                        # Sicherer Zugriff auf Felder
                        title = n.get('title') or n.get('headline') or "Kein Titel"
                        link = n.get('link') or n.get('url') or "#"
                        st.markdown(f"▫️ [{title}]({link})")
                else:
                    st.write("Keine aktuellen News gefunden.")
            except:
                st.write("News-Schnittstelle antwortet nicht. Bitte erneut versuchen.")

st.caption(f"Update: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')} | Config: AI_INFRA_2026")
