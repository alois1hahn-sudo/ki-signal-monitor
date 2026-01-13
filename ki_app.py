import streamlit as st
import yfinance as yf
from datetime import datetime

# 1. SETUP
st.set_page_config(page_title="KI-Invest Cockpit", layout="wide")
st.title("🛡️ Strategisches KI-Invest Cockpit")

# 2. MARKT-AMPEL
st.subheader("🚦 Globale Markt-Ampel")
try:
    m_list = ["^SP500-20", "^TNX", "^VIX", "IWDA.AS"]
    m_d = yf.download(m_list, period="5d", progress=False)['Close']
    vix, yld = m_d["^VIX"].iloc[-1], m_d["^TNX"].iloc[-1]
    
    c1, c2, c3 = st.columns(3)
    with c1:
        if vix < 20: st.success(f"VIX: {vix:.2f} (Ruhig)")
        else: st.warning(f"VIX: {vix:.2f} (Erhöht)")
    with c2: st.info(f"US 10J Zinsen: {yld:.2f}%")
    with c3:
        rel = (m_d["^SP500-20"].iloc[-1]/m_d["^SP500-20"].iloc[0]) / (m_d["IWDA.AS"].iloc[-1]/m_d["IWDA.AS"].iloc[0])
        if rel > 1.01: st.success("Tech-Momentum: Stark")
        else: st.warning("Tech-Momentum: Neutral/Schwach")
except: st.write("Warte auf Live-Daten...")

st.markdown("---")

# 3. PORTFOLIO ÜBERSICHT
st.header("1️⃣ Portfolio & Watchlist")
pos = {
    "MSCI World (IWDA)": "IWDA.AS", "InfoTech (TNOW)": "TNOW.PA",
    "USA (AYEWD)": "AYEWD.XD", "Semicon (SEMI)": "SEMI.AS",
    "Utilities (WUTI)": "WUTI.SW", "MidCap (SP40)": "SP40.DE", "EM ex-China": "EMXC"
}
c_p = st.columns(4)
for i, (n, t) in enumerate(pos.items()):
    url = f"https://finance.yahoo.com/quote/{t}"
    c_p[i % 4].markdown(f"**[{n}]({url})**")

st.markdown("---")

# 4. SIGNAL-ANALYSE & TRANSPARENZ
st.sidebar.header("📝 Fundamentale Signale")
f1 = st.sidebar.checkbox("KI-CapEx Hyperscaler >20%?")
f2 = st.sidebar.checkbox("Neue Strom-Deals?")
f3 = st.sidebar.checkbox("Datacenter Bau-Boom?")

if st.button("Strategie-Check ausführen", type="primary"):
    with st.spinner('Analysiere Sektoren...'):
        df = yf.download(["SEMI.AS", "WUTI.SW", "SP40.DE", "EMXC", "IWDA.AS"], period="1y", progress=False)['Close']
        
        # Berechnung der Performance-Werte (6 Monate = ca. 126 Handelstage)
        perf_semi = (df['SEMI.AS'].iloc[-1]/df['SEMI.AS'].iloc[-126] - 1) * 100
        perf_wuti = (df['WUTI.SW'].iloc[-1]/df['WUTI.SW'].iloc[-126] - 1) * 100
        perf_world = (df['IWDA.AS'].iloc[-1]/df['IWDA.AS'].iloc[-126] - 1) * 100
        perf_mid = (df['SP40.DE'].iloc[-1]/df['SP40.DE'].iloc[-126] - 1) * 100
        perf_emxc = (df['EMXC'].iloc[-1]/df['EMXC'].iloc[-126] - 1) * 100

        s = {"Hardware": 0, "Power": 0, "Build": 0, "Global Supply": 0}
        details = {k: [] for k in s.keys()}

        # LOGIK TRANSPARENT MACHEN
        # Hardware
        if perf_semi > 15: 
            s["Hardware"] += 3
            details["Hardware"].append(f"Kurs-Stärke: +{perf_semi:.1f}% (>15%)")
        if f1: 
            s["Hardware"] += 4
            details["Hardware"].append("Fundamentaler CapEx-Boom")
        
        # Power
        if (perf_wuti - perf_world) > 5:
            s["Power"] += 3
            details["Power"].append(f"Outperformance: +{(perf_wuti-perf_world):.1f}%")
        if f2:
            s["Power"] += 5
            details["Power"].append("Strategische Energie-Deals")
        
        # Build
        if perf_mid > 10:
            s["Build"] += 3
            details["Build"].append(f"Infrastruktur-Trend: +{perf_mid:.1f}%")
        if f3:
            s["Build"] += 4
            details["Build"].append("Bau-Boom bestätigt")

        # Supply
        if perf_emxc > 5:
            s["Global Supply"] += 3
            details["Global Supply"].append(f"Supply-Chain Momentum: +{perf_emxc:.1f}%")

        # Anzeige der Ergebnisse
        st.success(f"### 🎯 Empfehlung: {max(s, key=s.get)}")
        
        res = st.columns(4)
        for i, (k, v) in enumerate(s.items()):
            with res[i]:
                st.metric(k, f"{v}/10")
                st.progress(min(v/10.0, 1.0))
                # Der neue Transparenz-Layer:
                for line in details[k]:
                    st.caption(line)

st.caption(f"Datenquelle: Yahoo Finance | Stand: {datetime.now().strftime('%H:%M:%S')}")
