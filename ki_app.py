import streamlit as st
import yfinance as yf
from datetime import datetime

st.set_page_config(page_title="KI-Infrastruktur Monitor", page_icon="🤖")

st.title("🤖 KI-Infrastruktur Signal-Monitor")
st.markdown("**Echtzeit-Analyse & Strategie-Check für den Flex-Puffer**")

# Checkliste in der Seitenleiste
st.sidebar.header("📊 Strategie-Check")
capex_high = st.sidebar.checkbox("KI-CapEx Hyperscaler >20%?", value=True)
power_deals = st.sidebar.checkbox("Neue Stromverträge (Amazon/MSFT)?")

if st.button("🔄 Analyse starten", type="primary"):
    signals = {'Hardware': 0, 'Power': 0, 'Build': 0, 'MidCaps': 0}
    
    # Daten abrufen
    with st.spinner('Analysiere Marktdaten...'):
        # Hardware
        nvda = yf.Ticker("NVDA").history(period="6mo")
        if (nvda['Close'].iloc[-1] / nvda['Close'].iloc[0]) > 1.15: signals['Hardware'] += 3
        if capex_high: signals['Hardware'] += 4

        # Power
        xlu = yf.Ticker("XLU").history(period="6mo")
        if (xlu['Close'].iloc[-1] / xlu['Close'].iloc[0]) > 1.05: signals['Power'] += 3
        if power_deals: signals['Power'] += 5

    # Ergebnis
    best = max(signals, key=signals.get)
    etf_map = {'Hardware': 'SOXQ/SMH', 'Power': 'XLU/VPU', 'Build': 'XLI', 'MidCaps': 'MDY'}
    
    st.success(f"### ✅ Empfehlung: Investiere in {etf_map[best]}")
    for k, v in signals.items():
        st.write(f"{k}: {v}/10")
        st.progress(v/10)

st.caption(f"Stand: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
