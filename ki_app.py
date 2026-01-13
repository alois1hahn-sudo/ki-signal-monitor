import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# 1. SETUP
st.set_page_config(page_title="KI-Invest Cockpit", layout="wide")

# Zuordnung deiner Layer zu den Mess-Tickern und Top-Stocks
CONFIG = {
    "Hardware (SEMI)": {"etfs": ["SMH"], "stocks": ["NVDA", "TSM", "ASML"], "color": "#1E90FF"},
    "Power (WUTI)": {"etfs": ["XLU"], "stocks": ["NEE", "CEG", "VST"], "color": "#FFD700"},
    "Build (XLI)": {"etfs": ["XLI"], "stocks": ["GE", "CAT", "ETN"], "color": "#32CD32"},
    "MidCap (SPY4)": {"etfs": ["IJH"], "stocks": ["PSTG", "FLEX", "HUBB"], "color": "#FF4500"}
}

st.title("🛡️ KI-Infrastruktur Strategie-Cockpit")

# 2. MARKT-AMPEL
st.subheader("🚦 Globale Markt-Ampel")
try:
    m_list = ["^VIX", "^TNX", "SPY", "^SP500-20"]
    m_data = yf.download(m_list, period="5d", progress=False)['Close']
    vix, yld = m_data["^VIX"].iloc[-1], m_data["^TNX"].iloc[-1]
    c1, c2, c3 = st.columns(3)
    c1.metric("VIX (Angst)", f"{vix:.2f}")
    c2.metric("US 10J Zinsen", f"{yld:.2f}%")
    tech_rel = (m_data["^SP500-20"].iloc[-1]/m_data["^SP500-20"].iloc[0]) / (m_data["SPY"].iloc[-1]/m_data["SPY"].iloc[0])
    c3.metric("Tech vs S&P 500", f"{tech_rel:.2f}x")
except: st.write("Lade Makro-Daten...")

st.markdown("---")

# 3. PORTFOLIO & WATCHLIST
st.header("1️⃣ Portfolio & ETF-Watchlist")
watchlist = {
    "MSCI World": "IWDA.AS", 
    "InfoTech": "TNOW.PA", 
    "S&P 500 Industrials": "%5ESP500-20", 
    "Semicon (SEMI)": "SEMI.AS", 
    "Utilities (WUTI)": "WUTI.SW", 
    "MidCap (SPY4)": "SPY4.DE", 
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
    with st.spinner('Extrahiere Daten und berechne Signale...'):
        # Stabile Ticker für die Messung
        t_list = ["SMH", "XLU", "XLI", "IJH", "SPY"]
        df = yf.download(t_list, period="1y", progress=False)['Close']
        
        # Performance-Berechnung (6 Monate)
        p_semi = (df['SMH'].iloc[-1]/
