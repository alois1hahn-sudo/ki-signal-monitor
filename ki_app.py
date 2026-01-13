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
        color="#1E90FF",
        keywords=["Blackwell", "CapEx", "Demand", "GPU", "AI chip"],
        description="Semiconductor & AI Hardware"
    ),
    "Power (WUTI)": LayerConfig(
        name="Power (WUTI)",
        etf="XLU",
        stock="NEE",
        color="#FFD700",
        keywords=["Nuclear", "Grid", "SMR", "Energy", "Power"],
        description="Utilities & Energy Infrastructure"
    ),
    "Build (XLI)": LayerConfig(
        name="Build (XLI)",
        etf="XLI",
        stock="CAT",
        color="#32CD32",
        keywords=["Backlog", "Construction", "Infrastructure", "Industrial"],
        description="Industrial & Construction"
    ),
    "MidCap (SPY4)": LayerConfig(
        name="MidCap (SPY4)",
        etf="IJH",
        stock="PSTG",
        color="#FF4500",
        keywords=["Rotation", "Small Cap", "Mid Cap", "Growth"],
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
def fetch_news(ticker: str, max_items: int = 5) -> List[Dict]:
    """
    Fetch news for a specific ticker with caching
    
    Args:
        ticker: Stock ticker symbol
        max_items: Maximum number of news items to return
        
    Returns:
        List of news dictionaries
    """
    try:
        logger.info(f"Fetching news for ticker: {ticker}")
        news = yf.Ticker(ticker).news
        
        if not news:
            logger.warning(f"No news found for ticker: {ticker}")
            return []
            
        logger.info(f"Successfully fetched {len(news)} news items for {ticker}")
        return news[:max_items]
        
    except Exception as e:
        logger.error(f"Error fetching news for {ticker}: {str(e)}")
        return []


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
        
        # Momentum scoring
        if performance > SCORING.momentum_threshold:
            score += SCORING.momentum_points
            details.append(f"✅ Momentum: +{performance:.1f}%")
        else:
            details.append(f"📊 Momentum: {performance:.1f}%")
        
        # Relative strength scoring
        if relative_strength > SCORING.relative_strength_threshold:
            score += SCORING.relative_strength_points
            details.append(f"✅ Rel. Stärke: +{relative_strength:.1f}% vs SPY")
        else:
            details.append(f"📊 Rel. Stärke: {relative_strength:.1f}% vs SPY")
        
        # Fundamental signal bonus
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
    score: int,
    details: List[str],
    show_progress: bool = True
):
    """Render analysis results for a single layer"""
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
    
    # Details
    for detail in details:
        if "✅" in detail or "🔥" in detail:
            st.success(detail, icon="✅")
        else:
            st.info(detail, icon="📊")


def render_news_section(layer_config: LayerConfig, news_items: List[Dict]):
    """Render news section for a specific layer"""
    st.markdown("---")
    st.header(f"📰 News-Radar: {layer_config.name}")
    
    if not news_items:
        st.info("Keine aktuellen News verfügbar.")
        return
    
    for news in news_items:
        signal_type, icon = analyze_news_sentiment(news, layer_config.keywords)
        
        col1, col2 = st.columns([1, 5])
        
        with col1:
            if signal_type == "STRONG":
                st.success(f"{icon} SIGNAL")
            elif signal_type == "KEYWORD":
                st.warning(f"{icon} KEYWORD")
            else:
                st.caption(f"{icon} News")
        
        with col2:
            title = news.get('title') or news.get('headline') or "Kein Titel"
            link = news.get('link') or "#"
            publisher = news.get('publisher', 'Unbekannt')
            
            st.markdown(f"**[{title}]({link})**")
            st.caption(f"Quelle: {publisher}")


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
        if key != "MidCap (SPY4)":  # MidCap has no fundamental checkbox
            signal_key = f"signal_{key}"
            fundamental_signals[key] = st.sidebar.checkbox(
                f"{layer.name.split('(')[0].strip()}: Fundamental-Signal",
                key=signal_key
            )
        else:
            fundamental_signals[key] = False
    
    st.sidebar.markdown("---")
    st.sidebar.info(
        "💡 **Tipp:** Aktiviere Signale wenn du fundamentale "
        "Katalysatoren (z.B. CapEx-Ankündigungen) siehst."
    )
    
    # Auto-refresh option
    auto_refresh = st.sidebar.checkbox("🔄 Auto-Refresh (5 Min)", value=False)
    if auto_refresh:
        st.sidebar.caption("Dashboard aktualisiert sich automatisch")
    
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
                    layer_scores[key],
                    layer_details[key]
                )
        
        # News section for top-scoring layer
        best_layer_key = max(layer_scores, key=layer_scores.get)
        best_layer = LAYERS[best_layer_key]
        
        with st.spinner(f"📰 Lade News für {best_layer.name}..."):
            news_items = fetch_news(best_layer.stock, max_items=5)
        
        render_news_section(best_layer, news_items)
        
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
