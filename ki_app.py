import streamlit as st
import yfinance as yf
from datetime import datetime

st.set_page_config(page_title="KI-Infrastruktur Monitor", page_icon="🤖", layout="wide")

st.title("🤖 KI-Infrastruktur Signal-Monitor")
st.markdown("**Echtzeit-Analyse für deinen Flex-Puffer (300 €/Monat)**")

if st.button("🔄 Signale jetzt prüfen", type="primary"):
    progress = st.progress(0)
    status = st.empty()

    signals = {'Hardware': 0, 'Power': 0, 'Build': 0, 'MidCaps': 0}

    # Hardware
    status.text("🔍 Prüfe Hardware...")
    progress.progress(0.25)
    try:
        nvda = yf.Ticker("NVDA")
        hist = nvda.history(period="6mo")
        if len(hist) > 0:
            perf = (hist['Close'].iloc[-1] / hist['Close'].iloc[0] - 1) * 100
            if perf > 20:
                signals['Hardware'] += 3
                st.success(f"✅ NVIDIA: +{perf:.1f}%")
    except:
        st.warning("⚠️ Hardware-Daten nicht verfügbar")

    # Power
    status.text("🔍 Prüfe Power...")
    progress.progress(0.5)
    try:
        xlu = yf.Ticker("XLU")
        spy = yf.Ticker("SPY")
        xlu_hist = xlu.history(period="6mo")
        spy_hist = spy.history(period="6mo")
        if len(xlu_hist) > 0 and len(spy_hist) > 0:
            xlu_perf = (xlu_hist['Close'].iloc[-1] / xlu_hist['Close'].iloc[0] - 1) * 100
            spy_perf = (spy_hist['Close'].iloc[-1] / spy_hist['Close'].iloc[0] - 1) * 100
            diff = xlu_perf - spy_perf
            if diff > 5:
                signals['Power'] += 4
                st.success(f"✅ Utilities: +{diff:.1f}% vs S&P 500")
    except:
        st.warning("⚠️ Power-Daten nicht verfügbar")

    # Build
    status.text("🔍 Prüfe Build & Defence...")
    progress.progress(0.75)
    try:
        xli = yf.Ticker("XLI")
        hist = xli.history(period="6mo")
        if len(hist) > 0:
            perf = (hist['Close'].iloc[-1] / hist['Close'].iloc[0] - 1) * 100
            if perf > 15:
                signals['Build'] += 3
                st.success(f"✅ Industrials: +{perf:.1f}%")
    except:
        st.warning("⚠️ Build-Daten nicht verfügbar")

    # MidCaps
    status.text("🔍 Prüfe MidCaps...")
    progress.progress(1.0)
    try:
        mdy = yf.Ticker("MDY")
        spy = yf.Ticker("SPY")
        mdy_hist = mdy.history(period="1y")
        spy_hist = spy.history(period="1y")
        if len(mdy_hist) > 0 and len(spy_hist) > 0:
            mdy_perf = (mdy_hist['Close'].iloc[-1] / mdy_hist['Close'].iloc[0] - 1) * 100
            spy_perf = (spy_hist['Close'].iloc[-1] / spy_hist['Close'].iloc[0] - 1) * 100
            diff = mdy_perf - spy_perf
            if diff > 5:
                signals['MidCaps'] += 5
                st.success(f"✅ MidCaps: +{diff:.1f}% vs S&P 500")
    except:
        st.warning("⚠️ MidCap-Daten nicht verfügbar")

    status.empty()
    progress.empty()

    # Empfehlung
    st.markdown("---")
    etf_map = {'Hardware': 'SOXQ/SMH', 'Power': 'XLU/VPU', 'Build': 'XLI', 'MidCaps': 'MDY'}
    best = max(signals, key=signals.get)

    st.success(f"### ✅ Investiere 300 € in: {etf_map[best]}")
    st.metric("Signalstärke", f"{signals[best]}/10")

    for layer, score in sorted(signals.items(), key=lambda x: x[1], reverse=True):
        st.progress(score / 10)
        st.caption(f"{etf_map[layer]}: {score}/10")

else:
    st.info("👆 Klicke auf den Button, um die Analyse zu starten")
