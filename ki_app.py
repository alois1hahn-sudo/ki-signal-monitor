# ZUSATZ-LOGIK FÜR EXPERTEN-INDIKATOREN (Vorschau für deinen Code)

# 1. BREITEN-CHECK (Anteil Aktien über 200-Tage-Linie)
# (Simuliert über das Verhältnis S&P 500 Equal Weight zu S&P 500 Market Cap)
rsp_spy_ratio = (df['RSP'].iloc[-1]/df['RSP'].iloc[0]) / (df['SPY'].iloc[-1]/df['SPY'].iloc[0])

if rsp_spy_ratio > 1.02:
    st.success("✅ Marktbreite nimmt zu: Positives Signal für MidCaps & Industrials.")
elif rsp_spy_ratio < 0.98:
    st.warning("⚠️ Enge Marktbreite: Rally wird nur von wenigen Tech-Giganten getragen.")

# 2. ZINS-SENSITIVITÄT (Für Power & Build)
yield_change = df['^TNX'].iloc[-1] - df['^TNX'].iloc[-20] # Veränderung über 1 Monat

if yield_change > 0.5:
    st.error("🚨 Zins-Schock: Starker Gegenwind für Power (WUTI) & Build (XLI).")
