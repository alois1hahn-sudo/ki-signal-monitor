import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# 1. SETUP
st.set_page_config(page_title="KI-Invest Cockpit", layout="wide")

CONFIG = {
    "Hardware (SEMI)": {"etf": "SMH", "stock": "NVDA", "color": "#1E90FF", 
        "info": "Hardware-Infrastruktur"},
    "Power (WUTI)": {"etf": "XLU", "stock": "NEE", "color": "#FFD700", 
        "info": "Energie-Versorgung"},
    "Build (XLI)": {"etf": "XLI", "stock": "CAT", "color": "#32CD32", 
        "info": "Physischer Bau"},
    "MidCap (SPY4)": {"etf": "IJH", "stock": "PSTG", "color": "#FF4500", 
        "info": "Markt-Rotation"}
}

st.title("🛡️ Strategisches KI-Invest Cockpit")

# NEU: Maßstab-Erklärung ganz oben
with st.expander("ℹ️ Verwendete Maßstäbe & Logik"):
    st.write("**Zeit-Maßstab:** Alle Prozentwerte beziehen sich auf die Performance der letzten **6 Monate**.")
    st.write("**Markt-Maßstab:** Die relative Stärke wird im Vergleich zum **S&P 500 (SPY)** gemessen.")
    st.write("**Schwellenwerte:** Momentum > 15% | Relative Stärke > 1%.")

st.markdown("---")

# 2. MARKT-AMPEL
st.subheader("🚦 Globale Markt-Ampel")
try:
    m_d = yf.download(["^VIX", "^TNX", "SPY"], period="5d", progress=False)['Close']
    c1, c2, c3 = st.columns(3)
    c1.metric("Markt-Angst (VIX)", f"{m_d['^VIX'].iloc[-1]:.2f}", help="Maßstab: <20 ist ruhig")
    c2.metric("US 10J Zinsen", f"{m_d['^TNX'].iloc[-1]:.2f}%", help="Maßstab: Referenz für Kreditkosten")
    c3.info("Maßstab: Der S&P 500 (SPY) dient als Benchmark für alle Berechnungen.")
except: st.write("Lade Daten...")

st.markdown("---")

# 3. SIDEBAR & MANUELLE SIGNALE
st.sidebar.header("🛠️ Analyse-Parameter")
use_mom = st.sidebar.toggle("Momentum (6 Mon. > 15%)", value=True)
use_rel = st.sidebar.toggle("Rel. Stärke (vs. S&P 500)", value=True)

st.sidebar.markdown("---")
st.sidebar.subheader("Manuelle Signale")
f1 = st.sidebar.checkbox("Hardware: CapEx-Boom")
f2 = st.sidebar.checkbox("Power: Energie-Verträge")
f3 = st.sidebar.checkbox("Build: Bau-Aufträge")
f4 = st.sidebar.checkbox("MidCap: Breite Erholung")

# 4. ANALYSE
if st.button("Analyse mit Maßstab SPY ausführen", type="primary"):
    with st.spinner('Berechne Relative Stärke...'):
        df = yf.download(["SMH", "XLU", "XLI", "IJH", "SPY"], period="1y", progress=False)['Close']
        
        # Performance Rohdaten (6 Monate = 126 Tage)
        p_semi = (df['SMH'].iloc[-1]/df['SMH'].iloc[-126]-1)*100
        p_pwr = (df['XLU'].iloc[-1]/df['XLU'].iloc[-126]-1)*100
        p_bld = (df['XLI'].iloc[-1]/df['XLI'].iloc[-126]-1)*100
        p_mid = (df['IJH'].iloc[-1]/df['IJH'].iloc[-126]-1)*100
        p_spy = (df['SPY'].iloc[-1]/df['SPY'].iloc[-126]-1)*100

        scores = {k: 0 for k in CONFIG.keys()}
        details = {k: [] for k in CONFIG.keys()}

        for layer in CONFIG.keys():
            # A. Momentum (Absolut)
            if use_mom:
                val = {"Hardware (SEMI)": p_semi, "Power (WUTI)": p_pwr, 
                       "Build (XLI)": p_bld, "MidCap (SPY4)": p_mid}[layer]
                if val > 15:
                    scores[layer] += 3
                    details[layer].append(f"📈 Momentum: +{val:.1f}% (Maßstab >15% Erreicht)")

            # B. Rel. Stärke (vs S&P 500)
            if use_rel:
                rel_val = {"Hardware (SEMI)": p_semi - p_spy, "Power (WUTI)": p_pwr - p_spy, 
                           "Build (XLI)": p_bld - p_spy, "MidCap (SPY4)": p_mid - p_spy}[layer]
                if rel_val > 1:
                    scores[layer] += 3
                    details[layer].append(f"📊 Rel. zum Markt: +{rel_val:.1f}% (Besser als S&P 500)")

            # C. Manuelle Signale
            check = {"Hardware (SEMI)": f1, "Power (WUTI)": f2, 
                     "Build (XLI)": f3, "MidCap (SPY4)": f4}[layer]
            if check:
                scores[layer] += 4
                details[layer].append("💎 Fundamentaler Bonus (Manuelles Signal)")

        # ANZEIGE
        res_cols = st.columns(4)
        for i, (layer, score) in enumerate(scores.items()):
            with res_cols[i]:
                st.markdown(f"<h4 style='color:{CONFIG[layer]['color']}'>{layer}</h4>", unsafe_allow_html=True)
                st.metric("Gesamt-Score", f"{score}/10")
                st.progress(score/10.0)
                for d in details[layer]: st.info(d)

st.caption(f"Update: {datetime.now().strftime('%d.%m.%Y')} | Referenzmarkt: S&P 500 Index")
