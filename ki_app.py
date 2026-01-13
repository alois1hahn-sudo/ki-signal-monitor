import streamlit as st
import yfinance as yf
from datetime import datetime

st.set_page_config(page_title="KI-Invest Cockpit", layout="wide", page_icon="📈")

st.title("🛡️ KI-Infrastruktur Strategie-Cockpit")

# --- 1️⃣ BESTANDSPORTFOLIO (STATISCH) ---
st.header("1️⃣ Bestandsportfolio")
st.markdown("💡 *Strategie: Halten & organisches Wachstum.*")

# Liste der Bestands-ETFs mit Ticker-Symbolen für die Verlinkung
bestands_etfs = {
    "MSCI World": "URTH",
    "InfoTech ETF": "VGT",
    "USA ETF": "VTI",
    "EM IMI": "EIMI.L"
}

cols_b = st.columns(len(bestands_etfs))
for i, (name, ticker) in enumerate(bestands_etfs.items()):
    with cols_b[i]:
        url = f"https://finance.yahoo.com/quote/{ticker}"
        st.markdown(f"### [{name}]({url})")
        st.caption(f"Ticker: {ticker}")

st.markdown("---")

# --- 2️⃣ ERGÄNZUNGSBLOCK ---
st.header("2️⃣ KI-Infrastruktur Ergänzungsblock")
st.markdown("🎯 *Strategie: Aktiver Aufbau via Sparplan & Flex-Puffer.*")

# Hier definieren wir die Ziel-ETFs für die Layer
ergaenzung = {
    "Hardware": {"name": "MSCI Semiconductors", "sym": "SMH"},
    "Power": {"name": "MSCI Utilities", "sym": "XLU"},
    "Global Supply": {"name": "EM ex-China", "sym": "EMXC"},
    "Build & Defence": {"name": "S&P 500 Industrials", "sym": "XLI"},
    "MidCaps": {"name": "S&P 400 MidCap", "sym": "MDY"}
}

cols_e = st.columns(len(ergaenzung))
for i, (layer, info) in enumerate(ergaenzung.items()):
    with cols_e[i]:
        url = f"
