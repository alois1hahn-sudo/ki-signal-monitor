import streamlit as st
import yfinance as yf
from datetime import datetime

# 1. SETUP
st.set_page_config(page_title="KI-Invest", layout="wide")
st.title("🛡️ KI-Infrastruktur Strategie-Cockpit")

# 2. MARKT-AMPEL
st.subheader("🚦 Globale Markt-Ampel")
try:
    m_list = ["^VIX", "^TNX", "VGT", "URTH"]
    m_d = yf.download(m_list, period="5d", progress=False)['Close']
    vix, yld = m_d["^VIX"].iloc[-1], m_d["^TNX"].iloc[-1]
    c1, c2, c3 = st.columns(3)
    with c1:
        if vix < 20: st.success(f"VIX: {vix:.2f} (Ruhig)")
        else: st.warning(f"VIX: {vix:.2f} (Nervös)")
    with c2: st.info(f"US 10J Zinsen: {yld:.2f}%")
    with c3:
        rel = (m_d["VGT"].iloc[-1]/m_d["VGT"].iloc[0]) / (m_d["URTH"].iloc[-1]/m_d["URTH"].iloc[0])
        if rel > 1.02: st.success("Tech: Stark")
        else: st.warning("Tech: Schwach")
except: st.write("Lade Daten...")

st.markdown("---")

# 3. PORTFOLIO
st.header("1️⃣ Bestandsportfolio")
b_etfs = {"MSCI World": "URTH", "InfoTech": "VGT", "USA": "VTI", "EM IMI": "EIMI.L"}
cb = st.columns(4)
for i, (n, t) in enumerate(b_etfs.items()):
    url = "https://finance.yahoo.com/quote/" + t
    cb[i].markdown(f"### [{n}]({url})")

st.markdown("---")
st.header("2️⃣ KI-Ergänzungsblock")
erg = {"Hardware": "SMH", "Power": "XLU", "Supply": "EMXC", "Build": "XLI", "MidCaps": "MDY"}
ce = st.columns(5)
for i, (l, t) in enumerate(erg.items()):
    url = "https://finance.yahoo.com/quote/" + t
    ce[i].markdown(f"**{l}**\n#### [{t}]({url})")

st.markdown("---")

# 4. ANALYSE
st.sidebar.header("📝 Checkliste")
f1 = st.sidebar.checkbox("CapEx >20%?")
f2 = st.sidebar.checkbox("Strom-Deals?")
f3 = st.sidebar.checkbox("Bau-Boom?")

if st.button("Analyse starten", type="primary"):
    with st.spinner('Berechne...'):
        df = yf.download(["SMH", "XLU", "XLI", "MDY", "SPY"], period="1y", progress=False)['Close']
        s = {"Hardware": 0, "Power": 0, "Build": 0, "MidCaps": 0}
        
        # Scoring
        if (df['SMH'].iloc[-1]/df['SMH'].iloc[-126]) > 1.15: s["Hardware"] += 3
        if f1: s["Hardware"] += 4
        if (df['XLU'].iloc[-1]/df['XLU'].iloc[-126]) > (df['SPY'].iloc[-1]/df['SPY'].iloc[-126] + 0.05): s["Power"] += 3
        if f2: s["Power"] += 5
        if (df['XLI'].iloc[-1]/df['XLI'].iloc[-126]) > 1.10: s["Build"] += 3
        if f3: s["Build"] += 4
        if (df['MDY'].iloc[-1]/df['MDY'].iloc[0]) > (df['SPY'].iloc[-1]/df['SPY'].iloc[0] + 0.05): s["MidCaps"] += 6

        res = st.columns(4)
        for i, (k, v) in enumerate(s.items()):
            label_text = f"{v}/10"
            res[i].metric(k, label_text)
            res[i].progress(v/10.0)
        st.success(f"🎯 Empfehlung: {max(s, key=s.get)}")

st.caption(f"Update: {datetime.now().strftime('%H:%M:%S')}")
