# 5. NEWS RADAR (REPARIERTE & FUNKTIONALE LOGIK)
        st.markdown("---")
        best = max(scores, key=scores.get)
        st.header(f"📰 Strategischer News-Radar: {best}")
        
        try:
            ticker_obj = yf.Ticker(CONFIG[best]["stock"])
            # Wir fordern die News explizit neu an
            news_items = ticker_obj.news
            keywords = CONFIG[best]["keywords"]
            
            if news_items and len(news_items) > 0:
                for n in news_items[:5]:
                    # NEU: Mehrstufige Suche nach Inhalten
                    title = n.get('title') or n.get('headline') or n.get('summary')
                    link = n.get('link') or n.get('url')
                    
                    # Falls absolut kein Titel findbar ist, nimm die Quelle als Text
                    if not title:
                        title = f"Nachricht von {n.get('publisher', 'Finanzquelle')}"
                    
                    if link:
                        # Keyword Check
                        match = [w for w in keywords if w.lower() in title.lower()]
                        
                        c_n1, c_n2 = st.columns([1, 5])
                        with c_n1:
                            if match: 
                                st.warning(f"🎯 {match[0]}")
                            else: 
                                st.caption("🔹 News")
                        with c_n2:
                            # Der Link wird jetzt fett und klickbar gerendert
                            st.markdown(f"**[{title}]({link})**")
                            st.caption(f"Quelle: {n.get('publisher', 'Yahoo Finance')}")
            else:
                st.info("Momentan keine News-Einträge für diesen Ticker gefunden.")
        except Exception as e:
            st.error(f"Schnittstelle konnte nicht gelesen werden. Bitte Seite neu laden.")
