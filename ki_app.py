import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="KI-Strategie Monitor", page_icon="🤖", layout="wide")

st.title("🤖 KI-Infrastruktur Signal-Monitor")
st.markdown("### Strategie-Check für den 20% Flex-Puffer (2026–2036)")

# --- ERKLÄRUNG DER SIGNALE ---
with st.expander("ℹ️ Welche Signale werden geprüft? (Hier klicken)"):
    st.markdown("""
    | Sektor | Automatisches Signal (Preis) | Fundamentales Signal (Manuell) |
    | :--- | :--- | :--- |
    | **Hardware** | NVDA > 15% Performance (6 Monate) | KI-CapEx der Hyperscaler > 20% YoY |
    | **Power** | Utilities (XLU) schlägt S&P 500 um > 5% | Neue Strom-Großverträge (z.B. Kernkraft/Amazon) |
    | **Build** | Industrials (XLI) > 10% Performance (6 Monate) | Rekord-Bauvolumen bei Datacentern |
    | **MidCaps** | S&P 400 (MDY) schlägt S&P 500 um > 5% | Kapitalrotation weg von Big Tech |
    """)

# --- SIDEBAR: FUNDAMENTALE DATEN ---
st.sidebar.header("📝 Fundamentale Signale")
st.sidebar.info("Prüfe Nachrichten & Berichte:")
capex_high = st.sidebar.checkbox("KI-CapEx Hyperscaler >20%?", value=True)
power_deals = st.sidebar.checkbox("Neue Power-Deals / Stromverträge?")
build_boom = st.sidebar.checkbox("Baubeginn neuer Mega-Datacenter?")

# --- INDIVIDUAL CHECK ---
st.sidebar.header("🔍 Einzelwert-Check")
user_ticker = st.sidebar.text_input("Ticker-Symbol (z.B. MSFT, ASML)", "").upper()

# --- ANALYSE ---
if st.button("🔄 Analyse & Strategie-Check starten", type="primary"):
    signals = {'Hardware': 0, 'Power': 0, 'Build': 0, 'MidCaps': 0}
    reasons = {k: [] for k in signals.keys()} # Speichert die Gründe für die Punkte
    
    with st.spinner('Marktdaten werden geladen...'):
        # 1. Hardware
        nvda_h = yf.Ticker("NVDA").history(period="6mo")
        nvda_p = ((nvda_h['Close'].iloc[-1] / nvda_h['Close'].iloc[0]) - 1) * 100
        if nvda_p > 15:
            signals['Hardware'] += 3
            reasons['Hardware'].append(f"✅ Preis-Momentum NVDA (+{nvda_p:.1f}%)")
        if capex_high:
            signals['Hardware'] += 4
            reasons['Hardware'].append("✅ Hoher KI-CapEx bestätigt")

        # 2. Power
        xlu_h = yf.Ticker("XLU").history(period="6mo")
        spy_h = yf.Ticker("SPY").history(period="6mo")
        xlu_p = (xlu_h['Close'].iloc[-1] / xlu_h['Close'].iloc[0] - 1) * 100
        spy_p = (spy_h['Close'].iloc[-1] / spy_h['Close'].iloc[0] - 1) * 100
        if (xlu_p - spy_p) > 5:
            signals['Power'] += 3
            reasons['Power'].append(f"✅ Outperformance vs. Markt (+{(xlu_p-spy_p):.1f}%)")
        if power_deals:
            signals['Power'] += 5
            reasons['Power'].append("✅ Neue Stromverträge/Power-Deals")

        # 3. Build & Defence
        xli_h = yf.Ticker("XLI").history(period="6mo")
        xli_p = (xli_h['Close'].iloc[-1] / xli_h['Close'].iloc[0] - 1) * 100
        if xli_p > 10:
            signals['Build'] += 3
            reasons['Build'].append(f"✅ Industrials Trend (+{xli_p:.1f}%)")
        if build_boom:
            signals['Build'] += 4
            reasons['Build'].append("✅ Datacenter Bauboom")

        # 4. MidCaps (Rotation)
        mdy_h = yf.Ticker("MDY").history(period="1y")
        spy_h_1y = yf.Ticker("SPY").history(period="1y")
        mdy_p = (mdy_h['Close'].iloc[-1] / mdy_h['Close'].iloc[0] - 1) * 100
        spy_p_1y = (spy_h_1y['Close'].iloc[-1] / spy_h_1y['Close'].iloc[0] - 1) * 100
        if (mdy_p - spy_p_1y) > 5:
            signals['MidCaps'] += 6
            reasons['MidCaps'].append(f"✅ Relative Stärke MidCaps (+{(mdy_p-spy_p_1y):.1f}%)")

    # --- AUSGABE ---
    best = max(signals, key=signals.get)
    etf_map = {'Hardware': 'SOXQ/SMH', 'Power': 'XLU/VPU', 'Build': 'XLI', 'MidCaps': 'MDY'}
    
    st.success(f"## 🏆 Empfehlung für Flex-Puffer: **{etf_map[best]}** ({best})")
    
    cols = st.columns(4)
    for i, (layer, score) in enumerate(signals.items()):
        with cols[i]:
            st.metric(layer, f"{score}/10")
            for reason in reasons[layer]:
                st.caption(reason)
            st.progress(min(score / 10, 1.0))

    # --- Einzelwert Check ---
    if user_ticker:
        st.markdown("---")
        st.subheader(f"Zusatz-Check: {user_ticker}")
        t_data = yf.Ticker(user_ticker).history(period="6mo")
        if not t_data.empty:
            perf = ((t_data['Close'].iloc[-1] / t_data['Close'].iloc[0]) - 1) * 100
            st.line_chart(t_data['Close'])
            st.write(f"Performance von {user_ticker} über 6 Monate: **{perf:.1f}%**")

st.caption(f"Letzte Analyse: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
