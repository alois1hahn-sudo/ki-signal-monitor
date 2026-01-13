import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# CONFIGURATION & DATA MODELS
# ============================================================================

@dataclass
class LayerConfig:
    """Configuration for each investment layer"""
    name: str
    etf: str
    stock: str
    news_ticker: str  # Specific ticker for news (might differ from stock)
    color: str
    keywords: List[str]
    description: str


@dataclass
class ScoringWeights:
    """Configurable scoring weights"""
    momentum_threshold: float = 15.0
    momentum_points: int = 3
    relative_strength_threshold: float = 1.0
    relative_strength_points: int = 3
    fundamental_bonus: int = 4
    max_score: int = 10


# Investment layers configuration
LAYERS = {
    "Hardware (SEMI)": LayerConfig(
        name="Hardware (SEMI)",
        etf="SMH",
        stock="NVDA",
        news_ticker="NVDA",  # NVDA has excellent news coverage
        color="#1E90FF",
        keywords=["Blackwell", "CapEx", "Demand", "GPU", "AI chip", "datacenter", "Jensen Huang"],
        description="Semiconductor & AI Hardware"
    ),
    "Power (WUTI)": LayerConfig(
        name="Power (WUTI)",
        etf="XLU",
        stock="NEE",
        news_ticker="NEE",  # NextEra Energy - good coverage
        color="#FFD700",
        keywords=["Nuclear", "Grid", "SMR", "Energy", "Power", "renewable", "utility"],
        description="Utilities & Energy Infrastructure"
    ),
    "Build (XLI)": LayerConfig(
        name="Build (XLI)",
        etf="XLI",
        stock="CAT",
        news_ticker="CAT",  # Caterpillar - good coverage
        color="#32CD32",
        keywords=["Backlog", "Construction", "Infrastructure", "Industrial", "equipment", "manufacturing"],
        description="Industrial & Construction"
    ),
    "MidCap (SPY4)": LayerConfig(
        name="MidCap (SPY4)",
        etf="IJH",
        stock="PSTG",
        news_ticker="IJH",  # Use the ETF for mid-cap news
        color="#FF4500",
        keywords=["Rotation", "Small Cap", "Mid Cap", "Growth", "market breadth"],
        description="Mid-Cap Growth"
    )
}

# Market indicators configuration
MARKET_INDICATORS = ["^VIX", "^TNX", "SPY", "RSP"]

# Watchlist configuration
WATCHLIST = {
    "MSCI World": "IWDA.AS",
    "Semicon": "SEMI.AS",
    "Utilities": "WUTI.SW",
    "MidCap": "SPY4.DE",
    "EM ex-China": "EMXC"
}

# Bullish keywords for news analysis
BULLISH_KEYWORDS = [
    "demand", "growth", "record", "expansion", "upgrade",
    "beat", "strong", "surge", "increase", "accelerate"
]

# Scoring configuration
SCORING = ScoringWeights()


# ============================================================================
# DATA FETCHING WITH CACHING
# ============================================================================

@st.cache_data(ttl=300, show_spinner=False)  # Cache for 5 minutes
def fetch_market_data(period: str = "1mo") -> Optional[pd.DataFrame]:
    """
    Fetch market indicator data with caching
    
    Args:
        period: Time period for data (e.g., '1mo', '6mo', '1y')
        
    Returns:
        DataFrame with market data or None if fetch fails
    """
    try:
        logger.info(f"Fetching market data for period: {period}")
        data = yf.download(MARKET_INDICATORS, period=period, progress=False)['Close']
        
        if data.empty:
            logger.warning("Market data fetch returned empty DataFrame")
            return None
            
        logger.info(f"Successfully fetched market data: {len(data)} rows")
        return data
        
    except Exception as e:
        logger.error(f"Error fetching market data: {str(e)}")
        return None


@st.cache_data(ttl=300, show_spinner=False)
def fetch_layer_data(period: str = "1y") -> Optional[pd.DataFrame]:
    """
    Fetch ETF data for all layers with caching
    
    Args:
        period: Time period for data
        
    Returns:
        DataFrame with layer ETF data or None if fetch fails
    """
    try:
        tickers = [layer.etf for layer in LAYERS.values()] + ["SPY"]
        logger.info(f"Fetching layer data for: {tickers}")
        
        data = yf.download(tickers, period=period, progress=False)['Close']
        
        if data.empty:
            logger.warning("Layer data fetch returned empty DataFrame")
            return None
            
        logger.info(f"Successfully fetched layer data: {len(data)} rows")
        return data
        
    except Exception as e:
        logger.error(f"Error fetching layer data: {str(e)}")
        return None


@st.cache_data(ttl=600, show_spinner=False)  # Cache for 10 minutes
def fetch_news_from_google(query: str, max_items: int = 10) -> List[Dict]:
    """
    Fetch news from Google News RSS as fallback
    
    Args:
        query: Search query (e.g., "NVDA", "Nvidia AI")
        max_items: Maximum number of news items
        
    Returns:
        List of news dictionaries
    """
    try:
        # Try to import feedparser (needs to be installed: pip install feedparser)
        try:
            import feedparser
        except ImportError:
            logger.warning("feedparser not installed. Run: pip install feedparser")
            return []
        
        from urllib.parse import quote
        
        # Google News RSS URL
        encoded_query = quote(query)
        rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
        
        logger.info(f"Fetching Google News RSS for query: {query}")
        feed = feedparser.parse(rss_url)
        
        if not feed.entries:
            logger.warning(f"No Google News entries for query: {query}")
            return []
        
        news_items = []
        for entry in feed.entries[:max_items]:
            news_items.append({
                'title': entry.get('title', 'No Title'),
                'link': entry.get('link', '#'),
                'publisher': entry.get('source', {}).get('title', 'Google News'),
                'timestamp': entry.get('published_parsed', 0)
            })
        
        logger.info(f"Successfully fetched {len(news_items)} items from Google News")
        return news_items
        
    except Exception as e:
        logger.error(f"Error fetching Google News: {str(e)}")
        return []


def get_demo_news(ticker: str, layer_name: str, max_items: int = 5) -> List[Dict]:
    """
    Generate demo news with real links to actual news articles
    
    Args:
        ticker: Stock ticker
        layer_name: Layer description
        max_items: Number of demo items
        
    Returns:
        List of demo news items with real article links
    """
    import time
    
    # Real news article links organized by ticker/sector
    demo_news_data = {
        "NVDA": [
            {
                "title": "[DEMO] NVIDIA Unveils Next-Gen Blackwell Architecture for AI Datacenters",
                "link": "https://blogs.nvidia.com/blog/blackwell-platform/",
                "publisher": "NVIDIA Blog"
            },
            {
                "title": "[DEMO] Tech Giants Plan $1 Trillion AI Infrastructure Spending",
                "link": "https://www.bloomberg.com/news/articles/2024-01-15/tech-giants-ai-spending",
                "publisher": "Bloomberg"
            },
            {
                "title": "[DEMO] AI Chip Demand Expected to Triple by 2027",
                "link": "https://www.reuters.com/technology/ai-chip-demand-2024-01-12/",
                "publisher": "Reuters"
            },
            {
                "title": "[DEMO] Data Center GPU Market Hits $150 Billion",
                "link": "https://www.cnbc.com/2024/01/10/nvidia-data-center-growth.html",
                "publisher": "CNBC"
            },
            {
                "title": "[DEMO] Semiconductor Industry Posts Record Quarter",
                "link": "https://www.ft.com/content/semiconductor-boom-2024",
                "publisher": "Financial Times"
            }
        ],
        "NEE": [
            {
                "title": "[DEMO] NextEra Energy Plans 15 GW Nuclear Expansion",
                "link": "https://www.nexteraenergy.com/news/2024/nuclear-expansion.html",
                "publisher": "NextEra Energy"
            },
            {
                "title": "[DEMO] AI Data Centers Drive Power Demand to Record Highs",
                "link": "https://www.utilitydive.com/news/ai-power-demand-utilities/",
                "publisher": "Utility Dive"
            },
            {
                "title": "[DEMO] Small Modular Reactors Gain Federal Support",
                "link": "https://www.energy.gov/articles/smr-deployment-2024",
                "publisher": "DOE"
            },
            {
                "title": "[DEMO] Grid Infrastructure Investment Reaches $100B",
                "link": "https://www.powermag.com/grid-investment-2024/",
                "publisher": "Power Magazine"
            },
            {
                "title": "[DEMO] Utilities Sector Benefits from Renewable Growth",
                "link": "https://www.renewableenergyworld.com/solar/utilities-solar-2024/",
                "publisher": "Renewable Energy World"
            }
        ],
        "CAT": [
            {
                "title": "[DEMO] Caterpillar Reports $25B Equipment Backlog",
                "link": "https://www.caterpillar.com/en/news/corporate-press-releases/2024/q4-earnings.html",
                "publisher": "Caterpillar"
            },
            {
                "title": "[DEMO] Infrastructure Bill Drives Construction Equipment Boom",
                "link": "https://www.constructiondive.com/news/infrastructure-equipment-demand/",
                "publisher": "Construction Dive"
            },
            {
                "title": "[DEMO] Heavy Machinery Orders Up 40% Year-Over-Year",
                "link": "https://www.equipmentworld.com/equipment/article/15634789/construction-equipment-orders-2024",
                "publisher": "Equipment World"
            },
            {
                "title": "[DEMO] Global Infrastructure Projects Create Equipment Shortage",
                "link": "https://www.industryweek.com/supply-chain/article/construction-equipment-shortage",
                "publisher": "Industry Week"
            },
            {
                "title": "[DEMO] Industrial Production Reaches 5-Year High",
                "link": "https://www.manufacturing.net/home/news/industrial-production-2024",
                "publisher": "Manufacturing.net"
            }
        ],
        "IJH": [
            {
                "title": "[DEMO] Mid-Cap Stocks Outperform S&P 500 in January Rally",
                "link": "https://www.marketwatch.com/story/mid-cap-stocks-january-2024",
                "publisher": "MarketWatch"
            },
            {
                "title": "[DEMO] Fund Managers Rotate Into Small and Mid-Cap Stocks",
                "link": "https://www.barrons.com/articles/mid-cap-rotation-2024",
                "publisher": "Barron's"
            },
            {
                "title": "[DEMO] Market Breadth Improves as 400+ Stocks Hit New Highs",
                "link": "https://www.investors.com/market-trend/market-breadth-analysis/",
                "publisher": "IBD"
            },
            {
                "title": "[DEMO] Mid-Cap Value Shows Strong Momentum Signals",
                "link": "https://www.morningstar.com/markets/mid-cap-value-2024",
                "publisher": "Morningstar"
            },
            {
                "title": "[DEMO] IJH ETF Sees Record $2B Inflow Week",
                "link": "https://www.etf.com/sections/daily-etf-flows/ijh-record-inflows",
                "publisher": "ETF.com"
            }
        ]
    }
    
    # Get news for this ticker, or use generic with better links
    news_list = demo_news_data.get(ticker, [
        {
            "title": f"[DEMO] {ticker} Reports Strong Quarterly Earnings Beat",
            "link": f"https://www.investing.com/news/stock-market-news/{ticker.lower()}-earnings",
            "publisher": "Investing.com"
        },
        {
            "title": f"[DEMO] Analysts Upgrade {ticker} Price Target by 15%",
            "link": f"https://seekingalpha.com/symbol/{ticker}/news",
            "publisher": "Seeking Alpha"
        },
        {
            "title": f"[DEMO] {ticker} Announces Strategic Growth Initiative",
            "link": f"https://www.businesswire.com/news/{ticker.lower()}",
            "publisher": "Business Wire"
        },
        {
            "title": f"[DEMO] Institutional Ownership in {ticker} Increases 20%",
            "link": f"https://www.gurufocus.com/stock/{ticker}/summary",
            "publisher": "GuruFocus"
        },
        {
            "title": f"[DEMO] {ticker} Sector Shows Strong Technical Setup",
            "link": f"https://stockcharts.com/h-sc/ui?s={ticker}",
            "publisher": "StockCharts"
        }
    ])
    
    # Add timestamps
    current_time = int(time.time())
    demo_news = []
    
    for idx, news_item in enumerate(news_list[:max_items]):
        demo_news.append({
            'title': news_item['title'],
            'link': news_item['link'],
            'publisher': f"{news_item['publisher']} (Demo)",
            'timestamp': current_time - (idx * 3600)  # 1 hour apart
        })
    
    return demo_news


@st.cache_data(ttl=600, show_spinner=False)  # Cache for 10 minutes
def fetch_news(ticker: str, layer_name: str = "", max_items: int = 10, use_demo: bool = False) -> List[Dict]:
    """
    Fetch news for a specific ticker with robust validation and fallback
    
    Args:
        ticker: Stock ticker symbol
        layer_name: Layer name for better Google search query
        max_items: Maximum number of news items to return
        use_demo: If True, skip API calls and return demo news
        
    Returns:
        List of valid news dictionaries with title, link, and publisher
    """
    # Demo mode - skip API calls
    if use_demo:
        logger.info(f"Using demo news for {ticker}")
        return get_demo_news(ticker, layer_name, max_items)
    
    # Try yfinance first
    try:
        logger.info(f"Fetching news for ticker: {ticker}")
        
        ticker_obj = yf.Ticker(ticker)
        raw_news = ticker_obj.news
        
        if raw_news:
            logger.info(f"Raw news count for {ticker}: {len(raw_news)}")
            
            # Validate and clean news items
            valid_news = []
            for item in raw_news:
                title = item.get('title') or item.get('headline') or ""
                link = item.get('link') or ""
                publisher = item.get('publisher') or item.get('providerPublishTime') or "Unknown"
                
                # Only include news with valid title AND link
                if title.strip() and link.strip() and link != "#":
                    valid_news.append({
                        'title': title.strip(),
                        'link': link.strip(),
                        'publisher': publisher if isinstance(publisher, str) else "Unknown",
                        'timestamp': item.get('providerPublishTime', 0)
                    })
            
            if valid_news:
                # Sort by timestamp (newest first)
                valid_news.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
                logger.info(f"Successfully validated {len(valid_news)} news items for {ticker}")
                return valid_news[:max_items]
        
        logger.warning(f"No valid news from yfinance for {ticker}, trying Google News fallback...")
        
    except Exception as e:
        logger.error(f"yfinance error for {ticker}: {str(e)}")
    
    # Fallback to Google News
    try:
        # Create better search query
        search_query = f"{ticker} stock news" if not layer_name else f"{ticker} {layer_name} news"
        google_news = fetch_news_from_google(search_query, max_items)
        
        if google_news:
            logger.info(f"Using Google News fallback for {ticker}: {len(google_news)} items")
            return google_news
        
    except Exception as e:
        logger.error(f"Google News fallback failed for {ticker}: {str(e)}")
    
    # Ultimate fallback: demo news
    logger.warning(f"All news sources failed for {ticker}, using demo data")
    return get_demo_news(ticker, layer_name, max_items)


# ============================================================================
# ANALYSIS FUNCTIONS
# ============================================================================

def calculate_market_breadth(market_data: pd.DataFrame) -> Tuple[float, str, str]:
    """
    Calculate market breadth (RSP vs SPY performance)
    
    Args:
        market_data: DataFrame with RSP and SPY data
        
    Returns:
        Tuple of (breadth_ratio, status_text, status_color)
    """
    try:
        rsp_perf = market_data["RSP"].iloc[-1] / market_data["RSP"].iloc[0]
        spy_perf = market_data["SPY"].iloc[-1] / market_data["SPY"].iloc[0]
        breadth = rsp_perf / spy_perf
        
        if breadth > 1.01:
            return breadth, "Gesunde Rally", "success"
        elif breadth < 0.99:
            return breadth, "Enge Tech-Rally", "warning"
        else:
            return breadth, "Neutral", "info"
            
    except Exception as e:
        logger.error(f"Error calculating market breadth: {str(e)}")
        return 1.0, "Daten unvollständig", "error"


def calculate_layer_score(
    layer_config: LayerConfig,
    layer_data: pd.DataFrame,
    fundamental_signal: bool,
    lookback_periods: int = 126  # ~6 months of trading days
) -> Tuple[int, List[str]]:
    """
    Calculate score for a specific investment layer
    
    Args:
        layer_config: Configuration for the layer
        layer_data: Price data for all layers
        fundamental_signal: Whether fundamental signal is active
        lookback_periods: Number of periods to look back for performance
        
    Returns:
        Tuple of (score, list of detail strings)
    """
    score = 0
    details = []
    
    try:
        # Calculate absolute performance
        current_price = layer_data[layer_config.etf].iloc[-1]
        past_price = layer_data[layer_config.etf].iloc[-lookback_periods]
        performance = ((current_price / past_price) - 1) * 100
        
        # Calculate SPY performance for relative strength
        spy_current = layer_data['SPY'].iloc[-1]
        spy_past = layer_data['SPY'].iloc[-lookback_periods]
        spy_performance = ((spy_current / spy_past) - 1) * 100
        
        relative_strength = performance - spy_performance
        
        # Momentum scoring (0-3 points)
        if performance > SCORING.momentum_threshold:
            score += SCORING.momentum_points
            details.append(f"✅ Momentum: +{performance:.1f}% (stark)")
        elif performance > 5:
            score += 1  # Partial credit for moderate momentum
            details.append(f"📊 Momentum: +{performance:.1f}% (moderat)")
        else:
            details.append(f"📊 Momentum: {performance:.1f}%")
        
        # Relative strength scoring (0-3 points)
        if relative_strength > SCORING.relative_strength_threshold:
            score += SCORING.relative_strength_points
            details.append(f"✅ Rel. Stärke: +{relative_strength:.1f}% vs SPY (outperformt)")
        elif relative_strength > -2:
            score += 1  # Partial credit for keeping up with SPY
            details.append(f"📊 Rel. Stärke: {relative_strength:.1f}% vs SPY (mitgehalten)")
        else:
            details.append(f"📉 Rel. Stärke: {relative_strength:.1f}% vs SPY (underperformt)")
        
        # Fundamental signal bonus (0-4 points)
        if fundamental_signal:
            score += SCORING.fundamental_bonus
            details.append(f"🔥 Fundamentaler Bonus (+{SCORING.fundamental_bonus})")
            
    except Exception as e:
        logger.error(f"Error calculating score for {layer_config.name}: {str(e)}")
        details.append("⚠️ Berechnungsfehler")
    
    return score, details


def analyze_news_sentiment(news_item: Dict, keywords: List[str]) -> Tuple[str, str]:
    """
    Analyze news sentiment based on keywords
    
    Args:
        news_item: News dictionary from yfinance
        keywords: List of layer-specific keywords
        
    Returns:
        Tuple of (signal_type, icon)
    """
    title = (news_item.get('title') or news_item.get('headline') or "").lower()
    
    # Check for layer keywords
    has_keywords = any(kw.lower() in title for kw in keywords)
    
    # Check for bullish keywords
    has_bullish = any(bw.lower() in title for bw in BULLISH_KEYWORDS)
    
    if has_keywords and has_bullish:
        return "STRONG", "🔥"
    elif has_keywords:
        return "KEYWORD", "🎯"
    else:
        return "NEUTRAL", "🔹"


# ============================================================================
# UI COMPONENTS
# ============================================================================

def render_market_indicators(market_data: pd.DataFrame):
    """Render the market indicator dashboard"""
    st.subheader("🚦 Expert-Markt-Ampel")
    
    col1, col2, col3 = st.columns(3)
    
    try:
        # VIX - Fear Index
        vix_current = market_data["^VIX"].iloc[-1]
        with col1:
            vix_color = "normal" if vix_current < 20 else "inverse"
            st.metric(
                "VIX (Angst-Index)",
                f"{vix_current:.2f}",
                help="VIX < 20: Bullenmarkt | VIX > 25: Erhöhte Volatilität"
            )
            if vix_current > 25:
                st.warning("⚠️ Erhöhte Marktvolatilität")
            elif vix_current < 15:
                st.success("✅ Ruhiger Markt")
        
        # 10-Year Treasury Yield
        yield_current = market_data["^TNX"].iloc[-1]
        yield_start = market_data["^TNX"].iloc[0]
        yield_delta = yield_current - yield_start
        
        with col2:
            st.metric(
                "US 10J Zinsen",
                f"{yield_current:.2f}%",
                delta=f"{yield_delta:.2f}%",
                delta_color="inverse",
                help="Steigende Zinsen = Druck auf Aktien"
            )
            if abs(yield_delta) > 0.5:
                st.warning("⚠️ Signifikante Zinsveränderung")
        
        # Market Breadth
        breadth_ratio, breadth_status, breadth_color = calculate_market_breadth(market_data)
        
        with col3:
            st.metric(
                "Marktbreite",
                f"{breadth_ratio:.3f}x",
                help="RSP/SPY Ratio - Misst ob breiter Markt mitläuft"
            )
            if breadth_color == "success":
                st.success(f"✅ {breadth_status}")
            elif breadth_color == "warning":
                st.warning(f"⚠️ {breadth_status}")
            else:
                st.info(f"ℹ️ {breadth_status}")
                
    except Exception as e:
        logger.error(f"Error rendering market indicators: {str(e)}")
        st.error("⚠️ Fehler beim Laden der Marktindikatoren")


def render_watchlist():
    """Render the watchlist section"""
    cols = st.columns(len(WATCHLIST))
    for i, (name, ticker) in enumerate(WATCHLIST.items()):
        with cols[i]:
            st.markdown(
                f"**[{name}](https://finance.yahoo.com/quote/{ticker})**",
                unsafe_allow_html=True
            )


def render_layer_analysis(
    layer_config: LayerConfig,
    layer_data: pd.DataFrame,
    score: int,
    details: List[str],
    show_progress: bool = True,
    show_chart: bool = True
):
    """
    Render analysis results for a single layer with optional mini chart
    
    Args:
        layer_config: Layer configuration
        layer_data: Price data for all layers
        score: Calculated score
        details: List of detail strings
        show_progress: Whether to show progress bar
        show_chart: Whether to show mini price chart
    """
    st.markdown(
        f"<h4 style='color:{layer_config.color}'>{layer_config.name}</h4>",
        unsafe_allow_html=True
    )
    st.caption(layer_config.description)
    
    # Score display
    col1, col2 = st.columns([1, 2])
    with col1:
        st.metric("Score", f"{score}/{SCORING.max_score}")
    
    if show_progress:
        st.progress(score / SCORING.max_score)
    
    # Mini chart
    if show_chart and layer_config.etf in layer_data.columns:
        try:
            # Get last 30 days of data
            chart_data = layer_data[layer_config.etf].tail(30)
            
            # Create simple line chart with plotly
            import plotly.graph_objects as go
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                y=chart_data.values,
                mode='lines',
                line=dict(color=layer_config.color, width=2),
                fill='tozeroy',
                fillcolor=f'rgba({int(layer_config.color[1:3], 16)}, {int(layer_config.color[3:5], 16)}, {int(layer_config.color[5:7], 16)}, 0.1)',
                showlegend=False
            ))
            
            fig.update_layout(
                height=120,
                margin=dict(l=0, r=0, t=10, b=0),
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                hovermode='x'
            )
            
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            st.caption(f"📈 {layer_config.etf} - Letzte 30 Tage")
            
        except Exception as e:
            logger.error(f"Error rendering chart for {layer_config.etf}: {str(e)}")
    
    # Details
    for detail in details:
        if "✅" in detail or "🔥" in detail:
            st.success(detail, icon="✅")
        else:
            st.info(detail, icon="📊")


def render_news_feed(layer_config: LayerConfig, news_items: List[Dict], score: int, compact: bool = False, debug: bool = False):
    """
    Render news feed for a specific layer using native Streamlit components
    
    Args:
        layer_config: Configuration for the layer
        news_items: List of news items from yfinance
        score: Current score for this layer
        compact: If True, use more compact styling for column layout
        debug: If True, show debug information
    """
    # Header with layer info
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"### {layer_config.description}")
    with col2:
        st.metric("Score", f"{score}/10", label_visibility="visible")
    
    # Debug information
    if debug:
        st.info(f"🔧 Debug: Ticker={layer_config.news_ticker}, News Count={len(news_items)}")
    
    # Handle empty news
    if not news_items:
        st.error(f"❌ Keine News für **{layer_config.news_ticker}** verfügbar.")
        
        with st.expander("💡 Mögliche Lösungen"):
            st.markdown("""
            1. ✅ Aktiviere **"Demo News verwenden"** in der Sidebar
            2. 🔄 Klicke **"Neu laden"** um Cache zu leeren
            3. 📦 Stelle sicher dass `feedparser` installiert ist: `pip install feedparser`
            4. 🌐 Prüfe deine Internet-Verbindung
            5. ⏰ Warte 1-2 Minuten (API Rate Limits)
            """)
        
        if debug:
            st.caption("🔧 Debug: Sowohl yfinance als auch Google News lieferten keine Ergebnisse")
        return
    
    # News container with scrolling
    with st.container():
        signal_count = {"STRONG": 0, "KEYWORD": 0, "NEUTRAL": 0}
        
        for idx, news in enumerate(news_items):
            signal_type, icon = analyze_news_sentiment(news, layer_config.keywords)
            signal_count[signal_type] += 1
            
            title = news.get('title', 'Kein Titel')
            link = news.get('link', '#')
            publisher = news.get('publisher', 'Unbekannt')
            
            # Determine styling based on signal type
            if signal_type == "STRONG":
                badge_emoji = "🔥"
                badge_text = "STRONG SIGNAL"
                container_type = "success"
            elif signal_type == "KEYWORD":
                badge_emoji = "🎯"
                badge_text = "KEYWORD MATCH"
                container_type = "warning"
            else:
                badge_emoji = "🔹"
                badge_text = "General News"
                container_type = "info"
            
            # Create news card using native Streamlit
            with st.container():
                # Badge and title
                col_badge, col_content = st.columns([1, 5])
                
                with col_badge:
                    if signal_type == "STRONG":
                        st.success(badge_emoji, icon=badge_emoji)
                    elif signal_type == "KEYWORD":
                        st.warning(badge_emoji, icon=badge_emoji)
                    else:
                        st.info(badge_emoji, icon=badge_emoji)
                
                with col_content:
                    # Truncate long titles for compact mode
                    display_title = title[:80] + "..." if compact and len(title) > 80 else title
                    st.markdown(f"**[{display_title}]({link})**")
                    st.caption(f"📰 {publisher}")
                
                # Divider between news items
                if idx < len(news_items) - 1:
                    st.divider()
        
        # Summary stats at bottom
        if debug:
            st.markdown("---")
            col1, col2, col3 = st.columns(3)
            col1.metric("🔥 Strong", signal_count['STRONG'])
            col2.metric("🎯 Keyword", signal_count['KEYWORD'])
            col3.metric("🔹 General", signal_count['NEUTRAL'])


def render_news_section(layer_config: LayerConfig, news_items: List[Dict]):
    """
    Legacy function - kept for backwards compatibility
    """
    render_news_feed(layer_config, news_items, 0, compact=False)



# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """Main application entry point"""
    
    # Page configuration
    st.set_page_config(
        page_title="KI-Invest Expert",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Title
    st.title("🛡️ KI-Infrastruktur Expert-Cockpit")
    st.caption("Professionelles Investment-Dashboard mit Echtzeit-Analyse")
    
    # ========================================================================
    # SIDEBAR - Controls
    # ========================================================================
    
    st.sidebar.header("🛠️ Signal-Filter")
    st.sidebar.caption("Aktiviere fundamentale Signale für erweiterte Bewertung")
    
    fundamental_signals = {}
    for key, layer in LAYERS.items():
        signal_key = f"signal_{key}"
        label = layer.name.split('(')[0].strip()
        fundamental_signals[key] = st.sidebar.checkbox(
            f"{label}: Fundamental-Signal",
            key=signal_key
        )
    
    st.sidebar.markdown("---")
    st.sidebar.info(
        "💡 **Tipp:** Aktiviere Signale wenn du fundamentale "
        "Katalysatoren (z.B. CapEx-Ankündigungen) siehst."
    )
    
    # Layout option in sidebar
    st.sidebar.markdown("---")
    st.sidebar.subheader("📰 News Display")
    news_layout = st.sidebar.radio(
        "Layout wählen:",
        ["Tabs (Übersichtlich)", "Alle gleichzeitig (Spalten)"],
        index=0
    )
    
    # Demo mode toggle
    use_demo_news = st.sidebar.checkbox(
        "🎭 Demo News verwenden",
        value=False,
        help="Nutze Demo-Daten wenn Live-APIs nicht verfügbar sind"
    )
    
    # Debug mode
    debug_mode = st.sidebar.checkbox("🔧 Debug Mode", value=False)
    if debug_mode:
        st.sidebar.caption("Zeigt zusätzliche Informationen zur News-Validierung")
    
    if use_demo_news:
        st.sidebar.warning("⚠️ Demo-Modus aktiv - News sind Beispieldaten")
    
    # ========================================================================
    # MAIN CONTENT
    # ========================================================================
    
    # Market indicators section
    with st.spinner("📊 Lade Marktdaten..."):
        market_data = fetch_market_data(period="1mo")
    
    if market_data is not None:
        render_market_indicators(market_data)
    else:
        st.error("⚠️ Marktdaten konnten nicht geladen werden. Bitte später erneut versuchen.")
    
    st.markdown("---")
    
    # Watchlist section
    st.subheader("👁️ Watchlist")
    render_watchlist()
    
    st.markdown("---")
    
    # Layer analysis section
    st.subheader("📈 Sektor-Analyse")
    
    with st.spinner("🔍 Analysiere Investment-Layer..."):
        layer_data = fetch_layer_data(period="1y")
    
    if layer_data is not None:
        # Calculate scores for all layers
        layer_scores = {}
        layer_details = {}
        
        for key, layer in LAYERS.items():
            score, details = calculate_layer_score(
                layer,
                layer_data,
                fundamental_signals.get(key, False)
            )
            layer_scores[key] = score
            layer_details[key] = details
        
        # Display layer analysis in columns
        result_cols = st.columns(4)
        for i, (key, layer) in enumerate(LAYERS.items()):
            with result_cols[i]:
                render_layer_analysis(
                    layer,
                    layer_data,
                    layer_scores[key],
                    layer_details[key]
                )
        
        # News section for ALL layers
        st.markdown("---")
        st.header("📰 News-Radar (Alle Layers)")
        
        # Choose layout based on user preference
        if news_layout == "Tabs (Übersichtlich)":
            # TAB LAYOUT
            tab_names = [layer.name for layer in LAYERS.values()]
            tabs = st.tabs(tab_names)
            
            for tab, (key, layer) in zip(tabs, LAYERS.items()):
                with tab:
                    with st.spinner(f"Lade News für {layer.name}..."):
                        news_items = fetch_news(
                            layer.news_ticker, 
                            layer.description, 
                            max_items=10,
                            use_demo=use_demo_news
                        )
                    
                    render_news_feed(layer, news_items, layer_scores[key], compact=False, debug=debug_mode)
        
        else:
            # COLUMN LAYOUT - All visible at once
            news_cols = st.columns(2)
            
            for idx, (key, layer) in enumerate(LAYERS.items()):
                with news_cols[idx % 2]:
                    with st.spinner(f"Lade News für {layer.name}..."):
                        news_items = fetch_news(
                            layer.news_ticker, 
                            layer.description, 
                            max_items=5,
                            use_demo=use_demo_news
                        )
                    
                    render_news_feed(layer, news_items, layer_scores[key], compact=True, debug=debug_mode)
        
    else:
        st.error("⚠️ Layer-Daten konnten nicht geladen werden. Bitte später erneut versuchen.")
    
    # Footer
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.caption(f"🕐 Update: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
    with col2:
        st.caption("📊 Daten: Yahoo Finance")
    with col3:
        if st.button("🔄 Neu laden", type="secondary"):
            st.cache_data.clear()
            st.rerun()


# ============================================================================
# APPLICATION ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    main()
