import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# 1. SETUP
st.set_page_config(page_title="KI-Invest Expert", layout="wide")

CONFIG = {
    "Hardware (SEMI)": {"etf": "SMH", "stock": "NVDA", "color": "#1E90FF", "keywords": ["Blackwell", "CapEx", "Demand"]},
    "Power (WUTI)": {"etf": "XLU", "stock": "NEE", "color": "#FFD700", "keywords": ["Nuclear", "Grid", "SMR"]},
    "Build (XLI)": {"etf": "XLI", "stock": "CAT", "color": "#32CD32", "keywords": ["Backlog", "Construction"]},
    "MidCap (SPY4)": {"etf": "IJH", "stock": "PSTG", "color": "#FF4500", "keywords": ["Rotation", "Small Cap"]}
}

st.title("🛡️ KI-Infrastruktur Expert-Cockpit")

# 2. EXPERT-MARKT-AMPEL (Die neuen Indikatoren)
st.subheader("🚦 Expert-Markt-Ampel")
try:
    # Wir laden RSP (Equal Weight) um die Marktbreite zu messen
    m_list = ["^VIX", "^TNX", "SPY", "RSP"]
    m_d = yf.download(m_list, period="1mo", progress=False)['Close']
    
    c1, c2, c3 = st.columns(3)
    
    # Indikator 1: Angst-Check
    vix_now = m_d["^VIX"].iloc[-1]
    c1.metric("VIX (Angst)", f"{vix_now:.2f}", help="VIX < 20: Bullenmarkt | VIX > 25: Gefahr")
    
    # Indikator 2: Zins-Schock (Veränderung 1 Monat)
    yield_now = m_d["^TNX"].iloc[-1]
    yield_delta = yield_now - m_d["^TNX"].iloc[0]
    c2.metric("US 10J Zinsen", f"{yield_now:.2f}%", delta=f"{yield_delta:.2f}%", delta_color="inverse")
    
    # Indikator 3: Marktbreite (RSP vs SPY)
    # Wenn RSP (alle Aktien gleich gewichtet) besser läuft als SPY (nur Schwergewichte), ist der Markt gesund.
    rsp_perf = (m_d["RSP"].iloc[-1] / m_d["RSP"].iloc[0])
    spy_perf = (m_d["SPY"].iloc[-1] / m_d["SPY"].iloc[0])
    breadth = rsp_perf / spy_perf
    
    if breadth > 1.01:
        c3.success(f"Breite: {breadth:.2f}x (Gesunde Rally)")
    elif breadth < 0.99:
        c3.warning(f"Breite: {breadth:.2f}x (Enge Tech-Rally)")
    else:
        c3.info(f"Breite: {breadth:.2f}x (Neutral)")
        
except:
    st.write("Marktdaten werden synchronisiert...")

st.markdown("---")

# 3. WATCHLIST
watchlist = {"MSCI World": "IWDA.AS", "Semicon": "SEMI.AS", "Utilities": "WUTI.SW", "MidCap": "SPY4.DE", "EM ex-China": "EMXC"}
cols = st.columns(len(watchlist))
for i, (n, t) in enumerate(watchlist.items()):
    cols[i].markdown(f"**[{n}](https://finance.yahoo.com/quote/{t})**")

st.markdown("---")

# 4. SIDEBAR & ANALYSE
st.sidebar.header("🛠️ Signale")
f1 = st.sidebar.checkbox("Hardware: CapEx-Boom")
f2 = st.sidebar.checkbox("Power: Energie-Deals")
f3 = st.sidebar.checkbox("Build: Bau-Boom")

if st.button("Analyse & News-Scan starten", type="primary"):
    with st.spinner('Analysiere Sektor-Dynamik...'):
        data = yf.download(["SMH", "XLU", "XLI", "IJH", "SPY"], period="1y", progress=False)['Close']
        p_spy = (data['SPY'].iloc[-1]/data['SPY'].iloc[-126]-1)*100
        
        scores = {k: 0 for k in CONFIG.keys()}
        details = {k: [] for k in CONFIG.keys()}

        for layer, cfg in CONFIG.items():
            perf = (data[cfg['etf']].iloc[-1]/data[cfg['etf']].iloc[-126]-1)*100
            rel = perf - p_spy
            
            if perf > 15: 
                scores[layer] += 3
                details[layer].append(f"Momentum: +{perf:.1f}%")
            if rel > 1: 
                scores[layer] += 3
                details[layer].append(f"Rel. Stärke: +{rel:.1f}%")
            
            check = {"Hardware (SEMI)": f1, "Power (WUTI)": f2, "Build (XLI)": f3, "MidCap (SPY4)": False}[layer]
            if check:
                scores[layer] += 4
                details[layer].append("Fundamentaler Bonus")

        res_cols = st.columns(4)
        for i, (layer, score) in enumerate(scores.items()):
            with res_cols[i]:
                st.markdown(f"<h4 style='color:{CONFIG[layer]['color']}'>{layer}</h4>", unsafe_allow_html=True)
                st.metric("Score", f"{score}/10")
                st.progress(score/10.0)
                for d in details[layer]: st.info(d)

        # 5. NEWS RADAR MIT SIGNAL-FILTER
        st.markdown("---")
        best = max(scores, key=scores.get)
        st.header(f"📰 News-Radar (Signal-Check): {best}")
        
        try:
            news = yf.Ticker(CONFIG[best]["stock"]).news
            keywords = CONFIG[best]["keywords"]
            bullish = ["demand", "growth", "record", "expansion", "upgrade"]
            
            for n in news[:5]:
                t = (n.get('title') or n.get('headline') or "").lower()
                link = n.get('link') or "#"
                
                has_key = [w for w in keywords if w.lower() in t]
                has_bull = [w for w in bullish if w.lower() in t]
                
                c_n1, c_n2 = st.columns([1, 5])
                with c_n1:
                    if has_key and has_bull: st.success("🔥 SIGNAL")
                    elif has_key: st.warning("🎯 KEYWORD")
                    else: st.caption("🔹 News")
                with c_n2:
                    st.markdown(f"**[{n.get('title')}]({link})**")
        except:
            st.write("News aktuell nicht verfügbar.")

st.caption(f"Update: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
