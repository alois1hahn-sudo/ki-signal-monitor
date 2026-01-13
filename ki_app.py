import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# 1. SETUP
st.set_page_config(page_title="KI-Invest Cockpit", layout="wide")

CONFIG = {
    "Hardware": {"etfs": ["SMH", "EMXC"], "stocks": ["NVDA", "TSM", "ASML"], "color": "#1E90FF"},
    "Power": {"etfs": ["XLU"], "stocks": ["NEE", "CEG", "VST"], "color": "#FFD700"},
    "Build": {"etfs": ["XLI"], "stocks": ["GE", "CAT", "ETN"], "color": "#32CD32"},
    "MidCap": {"etfs": ["IJH"], "stocks": ["PSTG", "FLEX", "HUBB"], "color": "#FF4500"}
}

st.title("🛡️ KI-Infrastruktur Strategie-Cockpit")

# 2. MARKT-AMPEL
st.subheader("🚦 Globale Markt-Ampel")
try:
    # Wir nutzen IJH für MidCaps und ^SP500-20 für Tech
    m_list = ["^VIX", "^TNX", "SPY", "^SP500-20"]
    m_data = yf.download(m_list, period="5d", progress=False)['Close']
    vix, yld = m_data["^VIX"].iloc[-1], m_data["^TNX"].iloc[-1]
    c1, c2, c3 = st.columns(3)
    c1.metric("VIX (Angst)", f"{vix:.2f}")
    c2.metric("US 10J Zinsen", f"{yld:.2f}%")
    # Tech-Stärke relativ zum breiten S&P 500
    tech_rel = (m_data["^SP500-20"].iloc[-1]/m_data["^SP500-20"].iloc[0]) / (m_data["SPY"].iloc[-1]/m_data["SPY"].iloc[0])
    c3.metric("Tech vs S&P 500", f"{tech_rel:.2f}x")
except: st.write("Lade Makro-Daten...")

st.markdown("---")

# 3. PORTFOLIO & WATCHLIST (Korrekt verlinkt)
st.header("1️⃣ Portfolio & ETF-Watchlist")
watchlist = {
    "MSCI World": "IWDA.AS", 
    "InfoTech": "TNOW.PA", 
    "S&P 500 Industrials": "%5ESP500-20", 
    "Semicon": "SEMI.AS", 
    "Utilities": "WUTI.SW", 
    "S&P 400 MidCap": "SPY4.DE", # Link bleibt, Messung unten via IJH
    "EM ex-China": "EMXC"
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
    with st.spinner('Extrahiere Daten von stabilen US-Quellen...'):
        # IJH ist der S&P 400 Proxy, XLU für Power, XLI für Industrials, SMH für Hardware
        t_list = ["SMH", "XLU", "XLI", "IJH", "SPY"]
        df = yf.download(t_list, period="1y", progress=False)['Close']
        
        # Berechnung (6 Monate)
        p_semi = (df['SMH'].iloc[-1]/df['SMH'].iloc[-126] - 1) * 100
        p_power = (df['XLU'].iloc[-1]/df['XLU'].iloc[-126] - 1) * 100
        p_mid = (df['IJH'].iloc[-1]/df['IJH'].iloc[-126] - 1) * 100
        p_spy = (df['SPY'].iloc[-1]/df['SPY'].iloc[-126] - 1) * 100
        p_build = (df['XLI'].iloc[-1]/df['XLI'].iloc[-126] - 1) * 100

        scores = {"Hardware": 0, "Power": 0, "Build": 0, "MidCap": 0}
        details = {k: [] for k in scores.keys()}

        # Logik mit stabilen Daten
        if p_semi > 15: 
            scores["Hardware"] += 3
            details["Hardware"].append(f"Momentum: +{p_semi:.1f}%")
        if f1: scores["Hardware"] += 4

        if (p_power - p_spy) > 5:
            scores["Power"] += 3
            details["Power"].append(f"Outperf vs Markt: +{(p_power-p_spy):.1f}%")
        if f2: scores["Power"] += 5

        if p_build > 10:
            scores["Build"] += 3
            details["Build"].append(f"Industrials Trend: +{p_build:.1f}%")
        if f3: scores["Build"] += 4

        if (p_mid - p_spy) > 5:
            scores["MidCap"] += 6
            details["MidCap"].append(f"Relative Stärke: +{(p_mid-p_spy):.1f}%")

        # Anzeige Scores
        st.header("2️⃣ Analyse-Ergebnis")
        res_cols = st.columns(4)
        for i, (layer, score) in enumerate(scores.items()):
            with res_cols[i]:
                st.markdown(f"<h3 style='color:{CONFIG[layer]['color']}'>{layer}</h3>", unsafe_allow_html=True)
                st.metric("Score", f"{score}/10")
                st.progress(score/10.0)
                for d in details[layer]: st.caption(f"✅ {d}")

        # 5. DEEP DIVE & NEWS
        st.markdown("---")
        best = max(scores, key=scores.get)
        st.subheader(f"📑 Deep Dive & News: {best}")
        
        c_n1, c_n2 = st.columns([1, 2])
        with c_n1:
            st.write("**Top-Holdings Check:**")
            for s in CONFIG[best]["stocks"]:
                try:
                    px = yf.Ticker(s).fast_info['last_price']
                    st.write(f"- {s}: ${px:.2f}")
                except: st.write(f"- {s}: Daten laden...")
        
        with c_n2:
            st.write("**Aktuelle Feeds:**")
            news = yf.Ticker(CONFIG[best]["stocks"][0]).news
            if news:
                for n in news[:3]:
                    t = n.get('title') or n.get('headline')
                    l = n.get('link') or n.get('url')
                    st.markdown(f"▫️ [{t}]({l})")

st.caption(f"Daten: Yahoo Finance US-Proxy | Stand: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
