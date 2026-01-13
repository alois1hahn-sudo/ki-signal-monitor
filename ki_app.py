# 5. KEYWORD NEWS SCANNER (REPAIR VERSION)
        st.markdown("---")
        best = max(scores, key=scores.get)
        st.header(f"📰 Strategischer News-Radar: {best}")
        
        # Keywords für den Abgleich laden
        keywords = CONFIG[best]["keywords"]
        
        try:
            # Wir holen die News für den Top-Stock des Gewinner-Sektors
            ticker_obj = yf.Ticker(CONFIG[best]["stock"])
            news_data = ticker_obj.news
            
            if news_data and len(news_data) > 0:
                for n in news_data[:5]:
                    # SICHERER ABFRAGE-MODUS: Wir prüfen alle möglichen Felder
                    t = n.get('title') or n.get('headline') or n.get('summary') or "Nachricht ohne Titel"
                    l = n.get('link') or n.get('url') or "https://finance.yahoo.com"
                    p = n.get('publisher') or "Finanzquelle"
                    
                    # Keyword-Check
                    match = [w for w in keywords if w.lower() in t.lower()]
                    
                    col_n1, col_n2 = st.columns([1, 5])
                    with col_n1:
                        if match: 
                            st.warning(f"🎯 {match[0]}")
                        else: 
                            st.caption("🔹 News")
                    with col_n2:
                        st.markdown(f"**[{t}]({l})**")
                        st.caption(f"Quelle: {p}")
            else:
                st.info("Momentan keine spezifischen News für diesen Sektor gefunden.")
        except Exception as e:
            st.error(f"News-Radar aktuell gestört. Grund: {e}")
