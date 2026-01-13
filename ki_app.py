# --- MARKT-AMPEL (Zusatz-Signale) ---
st.header("🚦 Globale Markt-Ampel")
with st.spinner('Prüfe Makro-Lage...'):
    # Wir prüfen VIX (Angst) und TNX (Zinsen)
    macro_data = yf.download(["^VIX", "^TNX"], period="5d", progress=False)['Close']
    vix = macro_data["^VIX"].iloc[-1]
    yields = macro_data["^TNX"].iloc[-1]

    m_col1, m_col2 = st.columns(2)
    with m_col1:
        if vix < 20:
            st.success(f"VIX: {vix:.2f} (Markt ist ruhig)")
        else:
            st.warning(f"VIX: {vix:.2f} (Hohe Volatilität!)")
            
    with m_col2:
        st.info(f"US 10J Zinsen: {yields:.2f}%")
