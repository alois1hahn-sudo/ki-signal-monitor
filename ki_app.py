import streamlit as st
import yfinance as yf
from datetime import datetime

# 1. Konfiguration
st.set_page_config(page_title="KI-Invest Cockpit", layout="wide", page_icon="📈")

st.title("🛡️ KI-Infrastruktur Strategie-Cockpit")

# --- 2. MARKT-AMPEL (MAKRO-SIGNALE) ---
st.subheader("🚦 Globale Markt-Ampel")
try:
    macro = yf.download(["^VIX", "^TNX"], period="5d", progress=False)['Close']
    vix = macro["^VIX"].iloc[-1]
    yields = macro["^TNX"].iloc[-1]

    m_col1, m_col2, m_col3 = st.columns(3)
    with m_col1:
        if vix < 20: st.success(f"VIX: {vix:.2f} (Markt-Angst: Niedrig)")
        elif vix < 30: st.warning(f"VIX: {vix:.2f} (Markt-Angst: Erhöht)")
        else: st.error(f"VIX: {vix:.2f} (Panik-Modus!)")
            
    with m_col2:
        st.info(f"US 10J Zinsen: {yields:.2f}%")
        st.caption("Wichtig für Refinanzierung von Infrastruktur")

    with m_col3:
        rel_data = yf.download(["VGT", "URTH"], period="1mo", progress=False)['Close']
        tech_rel = (rel_data["VGT"].iloc[-1]/rel_data["VGT"].iloc[0]) / (rel_data["URTH"].iloc[-1]/rel_data["URTH"].iloc[0])
        if tech_rel > 1.02: st.success("Tech-Momentum: Stark")
        else: st.warning("Tech-Momentum: Schwach")
except:
    st.write("Warte auf Marktdaten...")

st.markdown("---")

# --- 3. BESTANDSPORTFOLIO ---
st.header("1️⃣ Bestandsportfolio")
bestands_etfs = {"MSCI World": "URTH", "InfoTech ETF": "VGT", "USA ETF": "VTI", "EM IMI": "EIMI.L"}
cols_b = st.columns(len(bestands_etfs))
for i, (name, ticker) in enumerate(bestands_etfs.items()):
    with cols_b[i]:
        url = "https://finance.yahoo.com/quote/" + ticker
        st.markdown(f"### [{name}]({url})")

st.markdown("---")

# --- 4. ERGÄNZUNGSBLOCK ---
st.header("2️⃣ KI-Infrastruktur Ergänzungsblock")
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
        st.markdown(f"**{layer}**\n#### [{info['name']}]({url})")

st.markdown("---")

# --- 5. SIGNAL-CHECK ---
st.sidebar.header("📝 Fundamentale Signale")
capex_ok = st.sidebar.checkbox("KI-CapEx Hyperscaler >20% YoY?")
power_ok = st.sidebar.checkbox("Neue Strom-Großverträge?")
build_ok = st.sidebar.checkbox("Datacenter Bau-Boom?")

if st.button("Strategische Analyse starten", type="primary"):
    with st.spinner('Berechne Scores...'):
        t_list = ["SMH", "XLU", "XLI", "MDY", "SPY"]
        data = yf.download(t_list, period="1y", progress=False)['Close']
        scores = {'Hardware': 0, 'Power': 0, 'Build &
