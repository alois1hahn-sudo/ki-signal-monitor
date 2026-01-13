import streamlit as st
import yfinance as yf
from datetime import datetime

# 1. SETUP
st.set_page_config(page_title="KI-Invest Cockpit", layout="wide")
st.title("🛡️ Strategisches KI-Invest Cockpit")

# 2. MARKT-AMPEL (MAKRO)
st.subheader("🚦 Globale Markt-Ampel")
try:
    # ^SP500-20 = S&P 500 InfoTech | ^TNX = Zinsen | ^VIX = Angst
    m_list = ["^SP500-20", "^TNX", "^VIX", "IWDA.AS"]
    m_d = yf.download(m_list, period="5d", progress=False)['Close']
    vix, yld = m_d["^VIX"].iloc[-1], m_d["^TNX"].iloc[-1]
    
    c1, c2, c3 = st.columns(3)
    with c1:
        if vix < 20: st.success(f"VIX: {vix:.2f} (Ruhig)")
        else: st.warning(f"VIX: {vix:.2f} (Erhöht)")
    with c2: st.info(f"US 10J Zinsen: {yld:.2f}%")
    with c3:
        # Tech-Sektor Momentum vs. Welt-Index (IWDA)
        rel = (m_d["^SP500-20"].iloc[-1]/m_d["^SP500-20"].iloc[0]) / (m_d["IWDA.AS"].iloc[-1]/m_d["IWDA.AS"].iloc[0])
        if rel > 1.01: st.success("Tech-Momentum: Stark")
        else: st.warning("Tech-Momentum: Neutral/Schwach")
except: st.write("Warte auf Live-Daten...")

st.markdown("---")

# 3. PORTFOLIO ÜBERSICHT (DEINE LINKS)
st.header("1️⃣ Bestandsportfolio & Ergänzung")
# Mapping deiner gewünschten Links
pos = {
    "MSCI World (IWDA)": "IWDA.AS",
    "InfoTech (TNOW)": "TNOW.PA",
    "USA (AYEWD)": "AYEWD.XD",
    "Semicon (SEMI)": "SEMI.AS",
    "Utilities (WUTI)": "WUTI.SW",
    "MidCap (SP40)": "SP40.DE",
    "EM ex-China": "EMXC"
}

c_p = st.columns(4)
for i, (n, t) in enumerate(pos.items()):
    url = f"https://finance.yahoo.com/quote/{t}"
    c_p[i % 4].markdown(f"**[{n}]({url})**")

st.markdown("---")

# 4. SIGNAL-ANALYSE
st.sidebar.header("📝 Fundamentale Signale")
f1 = st.sidebar.checkbox("KI-CapEx Hyperscaler >20%?")
f2 = st.sidebar.checkbox("Neue Strom-Deals?")
f3 = st.sidebar.checkbox("Datacenter Bau-Boom?")

if st.button("Strategie-Check ausführen", type="primary"):
    with st.spinner('Analysiere Sektoren...'):
        # Die Ticker für die Messung der Layer
        df = yf.download(["SEMI.AS", "WUTI.SW", "SP40.DE", "EMXC", "IWDA.AS"], period="1y", progress=False)['Close']
        s = {"Hardware": 0, "Power": 0, "Build": 0, "Global Supply": 0}
        
        # Hardware (SEMI)
        if (df['SEMI.AS'].iloc[-1]/df['SEMI.AS'].iloc[-126]) > 1.15: s["Hardware"] += 3
        if f1: s["Hardware"] += 4
        
        # Power (WUTI vs Weltmarkt IWDA)
        if (df['WUTI.SW'].iloc[-1]/df['WUTI.SW'].iloc[-126]) > (df['IWDA.AS'].iloc[-1]/df['IWDA.AS'].iloc[-126] + 0.05):
            s["Power"] += 3
        if f2: s["Power"] += 5
        
        # Build (Hier nehmen wir MidCaps als Indikator für Infrastruktur-Wachstum)
        if (df['SP40.DE'].iloc[-1]/df['SP40.DE'].iloc[-126]) > 1.10: s["Build"] += 3
        if f3: s["Build"] += 4

        # Global Supply (EMXC)
        if (df['EMXC'].iloc[-1]/df['EMXC'].iloc[-126]) > 1.05: s["Global Supply"] += 3

        # Anzeige
        res = st.columns(4)
        for i, (k, v) in enumerate(s.items()):
            res[i].metric(k, f"{v}/10")
            res[i].progress(min(v/10.0, 1.0))
        
        st.success(f"🎯 Empfehlung für den 300€ Flex-Puffer: **{max(s, key=s.get)}**")

st.caption(f"Datenquelle: Yahoo Finance | Stand: {datetime.now().strftime('%H:%M:%S')}")
