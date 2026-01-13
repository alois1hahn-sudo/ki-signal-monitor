import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# 1. SETUP
st.set_page_config(page_title="KI-Invest Cockpit", layout="wide")

CONFIG = {
    "Hardware": {"etfs": ["SEMI.AS", "EMXC"], "stocks": ["NVDA", "TSM", "ASML"], "color": "#1E90FF"},
    "Power": {"etfs": ["WUTI.SW"], "stocks": ["NEE", "CEG", "VST"], "color": "#FFD700"},
    "Build": {"etfs": ["XLI"], "stocks": ["GE", "CAT", "ETN"], "color": "#32CD32"},
    "MidCap": {"etfs": ["SPY4.DE"], "stocks": ["PSTG", "FLEX", "HUBB"], "color": "#FF4500"}
}

st.title("🛡️ KI-Infrastruktur Strategie-Cockpit")

# 2. MARKT-AMPEL (Immer sichtbar)
st.subheader("🚦 Globale Markt-Ampel")
try:
    m_data = yf.download(["^VIX", "^TNX", "IWDA.AS", "^SP500-20"], period="5d", progress=False)['Close']
    vix, yld = m_data["^VIX"].iloc[-1], m_data["^TNX"].iloc[-1]
    c1, c2, c3 = st.columns(3)
    c1.metric("VIX (Angst)", f"{vix:.2f}")
    c2.metric("US 10J Zinsen", f"{yld:.2f}%")
    tech_rel = (m_data["^SP500-20"].iloc[-1]/m_data["^SP500-20"].iloc[0]) / (m_data["IWDA.AS"].iloc[-1]/m_data["IWDA.AS"].iloc[0])
    c3.metric("Tech vs World", f"{tech_rel:.2f}x")
except: st.write("Lade Makro-Daten...")

st.markdown("---")

# 3. PORTFOLIO & WATCHLIST (Diese war verschwunden - jetzt fest verankert)
st.header("1️⃣ Portfolio & ETF-Watchlist")
watchlist = {
    "MSCI World": "IWDA.AS", "InfoTech": "TNOW.PA", "USA": "AYEWD.XD",
    "Semicon": "SEMI.AS", "Utilities": "WUTI.SW", "MidCap": "SPY4.DE", "EM ex-China": "EMXC"
}
cols_w = st.columns(len(watchlist))
for i, (name, ticker) in enumerate(watchlist.items()):
    url = f"https://finance.yahoo.com/quote/{ticker}"
    cols_w[i].markdown(f"**[{name}]({url})**")

st.markdown("---")

# 4. ANALYSE-BEREICH
st.sidebar.header("📝 Fundamentale Checkliste")
f1 = st.sidebar.checkbox("Hardware: CapEx >20%?")
f2 = st.sidebar.checkbox("Power: Neue Nuclear Deals?")
f3 = st.sidebar.checkbox("Build: Bau-Rekorde?")

if st.button("Strategie-Check ausführen", type="primary"):
    with st.spinner('Berechne Scores und scanne News...'):
        # Daten für Transparenz laden
        t_list = ["SEMI.AS", "WUTI.SW", "SPY4.DE", "EMXC", "IWDA.AS"]
        df = yf.download(t_list, period="1y", progress=False)['Close']
        
        # Performance-Werte für Transparenz
        p_semi = (df['SEMI.AS'].iloc[-1]/df['SEMI.AS'].iloc[-126] - 1) * 100
        p_wuti = (df['WUTI.SW'].iloc[-1]/df['WUTI.SW'].iloc[-126] - 1) * 100
        p_mid = (df['SPY4.DE'].iloc[-1]/df['SPY4.DE'].iloc[-126] - 1) * 100
        p_world = (df['IWDA.AS'].iloc[-1]/df['IWDA.AS'].iloc[-126] - 1) * 100

        scores = {"Hardware": 0, "Power": 0, "Build": 0, "MidCap": 0}
        details = {k: [] for k in scores.keys()}

        # Scoring & Transparenz-Logik
        if p_semi > 15: 
            scores["Hardware"] += 3
            details["Hardware"].append(f"Momentum: +{p_semi:.1f}%")
        if f1: 
            scores["Hardware"] += 4
            details["Hardware"].append("Fundamentaler CapEx-Check")

        if (p_wuti - p_world) > 5:
            scores["Power"] += 3
            details["Power"].append(f"Outperf: +{(p_wuti-p_world):.1f}%")
        if f2:
            scores["Power"] += 5
            details["Power"].append("Kernkraft/PPA News")

        if p_mid > 10:
            scores["Build"] += 3
            details["Build"].append(f"Trend: +{p_mid:.1f}%")
        if f3:
            scores["Build"] += 4
            details["Build"].append("Infrastruktur-Häkchen")

        # Anzeige Scores
        st.header("2️⃣ Analyse-Ergebnis")
        res_cols = st.columns(4)
        for i, (layer, score) in enumerate(scores.items()):
            with res_cols[i]:
                st.markdown(f"<h3 style='color:{CONFIG[layer]['color']}'>{layer}</h3>", unsafe_allow_html=True)
                st.metric("Score", f"{score}/10")
                st.progress(score/10.0)
                for d in details[layer]: st.caption(f"✅ {d}")

        # 5. DEEP DIVE & NEWS-FEED (Hier sind die Feeds!)
        st.markdown("---")
        best = max(scores, key=scores.get)
        st.subheader(f"📑 Deep Dive & News: {best}")
        
        c_n1, c_n2 = st.columns([1, 2])
        with c_n1:
            st.write("**Top-Positionen:**")
            for s in CONFIG[best]["stocks"]:
                px = yf.Ticker(s).fast_info['last_price']
                st.write(f"- {s}: ${px:.2f}")
        
        with c_n2:
            st.write("**Aktuelle Feeds:**")
            news = yf.Ticker(CONFIG[best]["stocks"][0]).news
            if news:
                for n in news[:3]:
                    t = n.get('title') or n.get('headline')
                    l = n.get('link') or n.get('url')
                    st.markdown(f"▫️ [{t}]({l})")
            else: st.write("Keine aktuellen Feeds gefunden.")

st.caption(f"Update: {datetime.now().strftime('%d.%m.%Y %H:%M')} | Config: MASTER_v1")
