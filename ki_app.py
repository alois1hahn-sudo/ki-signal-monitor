import streamlit as st
import yfinance as yf
from datetime import datetime

st.set_page_config(page_title="KI-Invest Cockpit", layout="wide", page_icon="📈")

st.title("🛡️ KI-Infrastruktur Strategie-Cockpit")

# --- 1️⃣ BESTANDSPORTFOLIO ---
st.header("1️⃣ Bestandsportfolio")
st.markdown("💡 *Strategie: Halten & organisches Wachstum.*")

bestands_etfs = {
    "MSCI World": "URTH",
    "InfoTech ETF": "VGT",
    "USA ETF": "VTI",
    "EM IMI": "EIMI.L"
}

cols_b = st.columns(len(bestands_etfs))
for i, (name, ticker) in enumerate(bestands_etfs.items()):
    with cols_b[i]:
        url = "https://finance.yahoo.com/quote/" + ticker
        st.markdown(f"### [{name}]({url})")
        st.caption(f"Ticker: {ticker}")

st.markdown("---")

# --- 2️⃣ ERGÄNZUNGSBLOCK ---
st.header("2️⃣ KI-Infrastruktur Ergänzungsblock")
st.markdown("🎯 *Strategie: Aktiver Aufbau via Sparplan & Flex-Puffer.*")

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
        url = "https://finance.yahoo.com/quote/" + info['sym']
        st.markdown(f"**{layer}**")
        st.markdown(f"#### [{info['name']}]({url})")
        st.caption(f"Ticker: {info['sym']}")

st.markdown("---")

# --- 3️⃣ SIGNAL-PRÜFUNG ---
st.header("🔍 Marktsignal-Check")

st.sidebar.header("📝 Fundamentale Signale")
capex_ok = st.sidebar.checkbox("KI-CapEx Hyperscaler >20% YoY?")
power_ok = st.sidebar.checkbox("Neue Strom-Großverträge?")
build_ok = st.sidebar.checkbox("Datacenter Bau-Boom?")

if st.button("Signale jetzt analysieren", type="primary"):
    with st.spinner('Lade Marktdaten von Yahoo Finance...'):
        tickers = ["SMH", "XLU", "XLI", "MDY",
