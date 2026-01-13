import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="KI-Invest Cockpit", layout="wide", page_icon="📈")

# --- HEADER ---
st.title("🛡️ KI-Infrastruktur Strategie-Cockpit 2026-2036")
st.caption(f"Status: Aktiv | Letzter Check: {datetime.now().strftime('%d.%m.%Y %H:%M')}")

# --- 1️⃣ BESTANDSPORTFOLIO (STATISCH) ---
st.header("1️⃣ Bestandsportfolio (170.000 €)")
st.info("💡 Strategie: Halten, nicht weiter aufstocken. Wachstum erfolgt organisch.")

bestands_data = {
    "Position": ["MSCI World", "InfoTech ETF", "USA ETF", "EM IMI"],
    "Symbol": ["URTH", "VGT", "VTI", "EIMI.L"],
    "Anteil": ["50,19%", "29,95%", "15,80%", "4,06%"]
}

cols = st.columns(4)
for i, (pos, sym, ant) in enumerate(zip(bestands_data["Position"], bestands_data["Symbol"], bestands_data["Anteil"])):
    with cols[i]:
        url = f"https://finance.yahoo.com/quote/{sym}"
        st.markdown(f"### [{pos}]({url})")
        st.write(f"**Anteil:** {ant}")
        st.caption(f"Ticker: {sym}")

st.markdown("---")

# --- 2️⃣ ERGÄNZUNGSBLOCK & SIGNALE ---
st.header("2️⃣ KI-Infrastruktur Ergänzungsblock (40.000 €)")
st.markdown("**Marktsignale für den monatlichen 300 € Flex-Puffer:**")

# Sidebar für fundamentale Signale
st.sidebar.header("📝 Fundamentale Signale")
capex_ok = st.sidebar.checkbox("KI-CapEx Hyperscaler >20% YoY?")
power_ok = st.sidebar.checkbox("Neue Strom-Großverträge (Kernkraft)?")
build_ok = st.sidebar.checkbox("Datacenter Bau-Boom (Reports)?")

# Liste der Ergänzungs-ETFs
ergaenzung = {
    "Hardware": {"sym": "SMH", "name": "MSCI Semiconductors"},
    "Power": {"sym": "XLU", "name": "MSCI Utilities"},
    "Supply": {"sym": "EMXC", "name": "EM ex-China"},
    "Build": {"sym": "XLI", "name": "S&P 500 Industrials"},
    "MidCaps": {"sym": "MDY", "name": "S&P 400 MidCap"}
}

if st.button("🔄 Analyse der KI-Layer starten", type="primary"):
    with st.spinner('Berechne technische Signale aus Markt-Echtzeitdaten...'):
        # Daten-Download
        tickers = ["SMH", "XLU", "EMXC", "XLI", "MDY", "SPY"]
        data = yf.download(tickers, period="1y")['Close']
        
        scores = {'Hardware': 0, 'Power': 0, 'Build': 0, 'MidCaps': 0}
        
        # LOGIK-ENGINE (6-Monats-Performance)
        # Hardware (SMH & EMXC Kombi)
        hw_perf = (data['SMH'].iloc[-1] / data['SMH'].iloc[-126] - 1) * 100
        if hw_perf > 15: scores['Hardware'] += 3
        if capex_ok: scores['Hardware'] += 4

        # Power (Relativ zu Markt)
        xlu_rel = (data['XLU'].iloc[-1]/data['XLU'].iloc[-126]) - (data['SPY'].iloc[-1]/data['SPY'].iloc[-126])
        if xlu_rel > 0.05: scores['Power'] += 3
        if power_ok: scores['Power'] += 5

        # Build & Defence
        xli_perf = (data['XLI'].iloc[-1] / data['XLI'].iloc[-126] - 1) * 100
        if xli_perf > 10: scores['Build'] += 3
        if build_ok: scores['Build'] += 4

        # MidCaps
        mdy_rel = (data['MDY'].iloc[-1]/data['MDY'].iloc[0]) - (data['SPY'].iloc[-1]/data['SPY'].iloc[0])
        if mdy_rel > 0.05: scores['MidCaps'] += 6

        # Anzeige der Ergebnisse
        best_layer = max(scores, key=scores.get)
        st.success(f"## 🎯 Empfehlung Flex-Puffer: **{best_layer} ({ergaenzung[best_layer]['sym']})**")
        
        # Spalten für Details
        res_cols = st.columns(5)
        for i, (layer, info) in enumerate(ergaenzung.items()):
            # Da MidCaps in 'scores' aber Supply/EMXC extra ist, mappen wir kurz
            score_val = scores.get(layer, 0)
            with res_cols[i]:
                url = f"https://finance.yahoo.com/quote/{info['sym']}"
                st.markdown(f"**[{info['name']}]({url})**")
                if layer in scores:
                    st.metric(layer, f"{score_val}/10")
                    st.progress(score_val/10)
                else:
                    st.caption("Feste Sparplan-Komponente")

else:
    st.info("Klicke auf den Button, um die Signale für deine Kaufentscheidung zu prüfen.")
