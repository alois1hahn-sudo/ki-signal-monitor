import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# 1. SETUP
st.set_page_config(page_title="KI-Invest", layout="wide")

# Zuordnung der Layer
CONFIG = {
    "Hardware (SEMI)": {"etfs": ["SMH"], 
        "stocks": ["NVDA", "TSM", "ASML"], "color": "#1E90FF"},
    "Power (WUTI)": {"etfs": ["XLU"], 
        "stocks": ["NEE", "CEG", "VST"], "color": "#FFD700"},
    "Build (XLI)": {"etfs": ["XLI"], 
        "stocks": ["GE", "CAT", "ETN"], "color": "#32CD32"},
    "MidCap (SPY4)": {"etfs": ["IJH"], 
        "stocks": ["PSTG", "FLEX", "HUBB"], "color": "#FF4500"}
}

st.title("🛡️ KI-Infrastruktur Strategie-Cockpit")

# 2. MARKT-AMPEL
st.subheader("🚦 Globale Markt-Ampel")
try:
    m_list = ["^VIX", "^TNX", "SPY", "^SP500-20"]
    m_d = yf.download(m_list, period="5d", progress=False)['Close']
    vix, yld = m_d["^VIX"].iloc[-1], m_d["^TNX"].iloc[-1]
    c1, c2, c3 = st.columns(3)
    c1.metric("VIX (Angst)", f"{vix:.2f}")
    c2.metric("US 10J Zinsen", f"{yld:.2f}%")
    t_r = (m_d["^SP500-20"].iloc[-1]/m_d["^SP500-20"].iloc[0])
    s_r = (m_d["SPY"].iloc[-1]/m_d["SPY"].iloc[0])
    c3.metric("Tech vs S&P 500", f"{(t_r/s_r):.2f}x")
except: st.write("Lade Makro-Daten...")

st.markdown("---")

# 3. PORTFOLIO & WATCHLIST
st.header("1️⃣ Portfolio & ETF-Watchlist")
watchlist = {
    "MSCI World": "IWDA.AS", "InfoTech": "TNOW.PA", 
    "S&P 500 Industrials": "%5ESP500-20", "Semicon (SEMI)": "SEMI.AS", 
    "Utilities (WUTI)": "WUTI.SW", "MidCap (SPY4)": "SPY4.DE", 
    "EM ex-China": "EMXC"
}
cols_w = st.columns(len(watchlist))
for i, (name, ticker) in enumerate(watchlist.items()):
    url = "https://finance.yahoo.com/quote/" + ticker
    cols_w[i].markdown(f"**[{name}]({url})**")

st.markdown("---")

# 4. ANALYSE-BEREICH
st.sidebar.header("📝 Checkliste")
f1 = st.sidebar.checkbox("Hardware: CapEx >20%?")
f2 = st.sidebar.checkbox("Power: Neue Nuclear Deals?")
f3 = st.sidebar.checkbox("Build: Bau-Rekorde?")

if st.button("Strategie-Check ausführen", type="primary"):
    with st.spinner('Analysiere Daten...'):
        t_list = ["SMH", "XLU", "XLI", "IJH", "SPY"]
        df = yf.download(t_list, period="1y", progress=False)['Close']
        
        # Performance-Berechnung (Kompakt gegen Copy-Fehler)
        p_semi = (df['SMH'].iloc[-1]/df['SMH'].iloc[-126]-1)*100
        p_pwr = (df['XLU'].iloc[-1]/df['XLU'].iloc[-126]-1)*100
        p_mid = (df['IJH'].iloc[-1]/df['IJH'].iloc[-126]-1)*100
        p_spy = (df['SPY'].iloc[-1]/df['SPY'].iloc[-126]-1)*100
        p_bld = (df['XLI'].iloc[-1]/df['XLI'].iloc[-126]-1)*100

        scores = {"Hardware (SEMI)": 0, "Power (WUTI)": 0, 
                  "Build (XLI)": 0, "MidCap (SPY4)": 0}
        details = {k: [] for k in scores.keys()}

        # Hardware
        if p_semi > 15: 
            scores["Hardware (SEMI)"] += 3
            details["Hardware (SEMI)"].append(f"Momentum: +{p_semi:.1f}%")
        if f1: scores["Hardware (SEMI)"] += 4

        # Power
        if (p_pwr - p_spy) > 5:
            scores["Power (WUTI)"] += 3
            details["Power (WUTI)"].append(f"Rel. Stärke: +{p_pwr-p_spy:.1f}%")
        if f2: scores["Power (WUTI)"] += 5

        # Build
        if p_bld > 10:
            scores["Build (XLI)"] += 3
            details["Build (XLI)"].append(f"Industrials: +{p_bld:.1f}%")
        if f3: scores["Build (XLI)"] += 4

        # MidCap
        if (p_mid - p_spy) > 5:
            scores["MidCap (SPY4)"] += 6
            details["MidCap (SPY4)"].append(f"Rel. Stärke: +{p_mid-p_spy:.1f}%")

        # Anzeige
        st.header("2️⃣ Analyse-Ergebnis")
        res_cols = st.columns(4)
        for i, (layer, score) in enumerate(scores.items()):
            with res_cols[i]:
                st.markdown(f"<h3 style='color:{CONFIG[layer]['color']}'>{layer}</h3>", unsafe_allow_html=True)
                st.metric("Score", f"{score}/10")
                st.progress(score/10.0)
                for d in details[layer]: st.caption(f"✅ {d}")

        # 5. NEWS
        st.markdown("---")
        best = max(scores, key=scores.get)
        st.subheader(f"📑 Fokus: {best}")
        news = yf.Ticker(CONFIG[best]["stocks"][0]).news
        if news:
            for n in news[:3]:
                t = n.get('title') or n.get('headline')
                l = n.get('link') or n.get('url')
                st.markdown(f"▫️ [{t}]({l})")

st.caption(f"Stand: {datetime.now().strftime('%d.%m.%Y')}")
