import streamlit as st
import pandas as pd
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Equity Research Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin-bottom: 1rem;
    }
    .excellent { 
        border-left-color: #2e7d32 !important; 
        background-color: #e8f5e8 !important;
    }
    .good { 
        border-left-color: #1976d2 !important; 
        background-color: #e3f2fd !important;
    }
    .average { 
        border-left-color: #f57c00 !important; 
        background-color: #fff3e0 !important;
    }
    .poor { 
        border-left-color: #d32f2f !important; 
        background-color: #ffebee !important;
    }
    .rating-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        color: white;
        font-weight: bold;
        font-size: 12px;
        margin-top: 8px;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load and process the equity data"""
    try:
        # Try to load the uploaded file
        data = pd.read_csv('scwatchlist.csv')
        return data
    except FileNotFoundError:
        st.error("❌ Please upload your 'scwatchlist.csv' file to the repository root directory")
        st.info("The file should be in the same folder as your app.py file")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame()

def get_rating_and_color(stock):
    """Calculate overall rating for a stock"""
    score = 0
    factors = 0
    
    # ROE Score (most important)
    roe = stock.get('Return on equity', 0)
    if pd.notna(roe):
        if roe >= 20:
            score += 3
        elif roe >= 15:
            score += 2
        elif roe >= 10:
            score += 1
        factors += 3
    
    # Debt to Equity Score
    de = stock.get('Debt to equity', 999)
    if pd.notna(de):
        if de <= 0.3:
            score += 2
        elif de <= 0.7:
            score += 1
        factors += 2
    
    # PE Score
    pe = stock.get('Price to Earning', 999)
    if pd.notna(pe) and pe > 0:
        if pe <= 12:
            score += 2
        elif pe <= 20:
            score += 1
        factors += 2
    
    # Growth Score
    sales_growth = stock.get('Sales growth 5Years', 0)
    profit_growth = stock.get('Profit growth 5Years', 0)
    if pd.notna(sales_growth) and sales_growth >= 15:
        score += 1
    if pd.notna(profit_growth) and profit_growth >= 15:
        score += 1
    factors += 2
    
    # FCF Score
    fcf = stock.get('Free cash flow last year', -999)
    if pd.notna(fcf) and fcf > 0:
        score += 1
    factors += 1
    
    rating_score = (score / factors) * 5 if factors > 0 else 0
    
    if rating_score >= 4:
        return "Excellent", "#2e7d32", "excellent"
    elif rating_score >= 3:
        return "Good", "#1976d2", "good"
    elif rating_score >= 2:
        return "Average", "#f57c00", "average"
    elif rating_score >= 1:
        return "Below Average", "#ff6f00", "average"
    else:
        return "Poor", "#d32f2f", "poor"

def format_currency(value):
    """Format currency values"""
    if pd.isna(value) or value == 0:
        return "N/A"
    if value >= 10000:
        return f"₹{value:.0f}Cr"
    elif value >= 1000:
        return f"₹{value:.1f}Cr"
    elif value >= 100:
        return f"₹{value:.0f}Cr"
    else:
        return f"₹{value:.2f}Cr"

def format_number(value, suffix=""):
    """Format numerical values"""
    if pd.isna(value):
        return "N/A"
    return f"{value:.1f}{suffix}"

def color_code_value(value, thresholds, good_high=True):
    """Return color based on value and thresholds"""
    if pd.isna(value):
        return "⚪"
    
    if good_high:
        if value >= thresholds[1]:
            return "🟢"
        elif value >= thresholds[0]:
            return "🟡"
        else:
            return "🔴"
    else:
        if value <= thresholds[0]:
            return "🟢"
        elif value <= thresholds[1]:
            return "🟡"
        else:
            return "🔴"

def main():
    st.title("📈 Equity Research Dashboard")
    st.markdown("**Comprehensive analysis of your equity watchlist with smart filtering and insights**")
    
    # Load data
    data = load_data()
    
    if data.empty:
        st.warning("⚠️ No data available. Please check your CSV file.")
        st.markdown("""
        ### Setup Instructions:
        1. Upload your `scwatchlist.csv` file to your GitHub repository
        2. Ensure the file contains required columns: Name, NSE Code, Current Price, etc.
        3. Redeploy your Streamlit app
        """)
        return
    
    # Data validation
    required_cols = ['Name', 'NSE Code', 'Current Price', 'Return on equity', 'Price to Earning']
    missing_cols = [col for col in required_cols if col not in data.columns]
    if missing_cols:
        st.error(f"❌ Missing required columns: {', '.join(missing_cols)}")
        st.info("Please check your CSV file format")
        return
    
    # Sidebar filters
    st.sidebar.header("🔍 Smart Filters")
    
    # Search
    search_term = st.sidebar.text_input("🔎 Search Company/NSE Code", "")
    
    # Industry filter
    if 'Industry' in data.columns:
        industries = ['All'] + sorted(data['Industry'].dropna().unique().tolist())
        selected_industry = st.sidebar.selectbox("🏭 Industry", industries)
    else:
        selected_industry = 'All'
    
    # Quick filters
    st.sidebar.markdown("### ⚡ Quick Filters")
    quality_filter = st.sidebar.checkbox("✨ Quality Stocks Only (ROE>15%, D/E<0.5)")
    growth_filter = st.sidebar.checkbox("📈 High Growth (Sales Growth >15%)")
    value_filter = st.sidebar.checkbox("💰 Value Stocks (P/E <20)")
    dividend_filter = st.sidebar.checkbox("💎 Dividend Stocks")
    
    # Advanced filters
    with st.sidebar.expander("🔧 Advanced Filters"):
        col1, col2 = st.columns(2)
        with col1:
            pe_range = st.slider("P/E Range", 0.0, 100.0, (0.0, 50.0), step=1.0)
            roe_min = st.number_input("Min ROE (%)", min_value=0.0, value=0.0, step=1.0)
        with col2:
            de_max = st.number_input("Max D/E", min_value=0.0, value=5.0, step=0.1)
            mcap_min = st.number_input("Min Market Cap (Cr)", min_value=0.0, value=0.0, step=100.0)
    
    # Apply filters
    filtered_data = data.copy()
    
    # Search filter
    if search_term:
        mask = (
            filtered_data['Name'].str.contains(search_term, case=False, na=False) |
            filtered_data['NSE Code'].str.contains(search_term, case=False, na=False)
        )
        filtered_data = filtered_data[mask]
    
    # Industry filter
    if selected_industry != 'All' and 'Industry' in filtered_data.columns:
        filtered_data = filtered_data[filtered_data['Industry'] == selected_industry]
    
    # Quick filters
    if quality_filter:
        filtered_data = filtered_data[
            (filtered_data['Return on equity'] >= 15) & 
            (filtered_data['Debt to equity'] <= 0.5)
        ]
    
    if growth_filter and 'Sales growth 5Years' in filtered_data.columns:
        filtered_data = filtered_data[filtered_data['Sales growth 5Years'] >= 15]
    
    if value_filter:
        filtered_data = filtered_data[filtered_data['Price to Earning'] <= 20]
    
    if dividend_filter and 'Dividend yield' in filtered_data.columns:
        filtered_data = filtered_data[filtered_data['Dividend yield'] > 0]
    
    # Advanced filters
    filtered_data = filtered_data[
        (filtered_data['Price to Earning'] >= pe_range[0]) &
        (filtered_data['Price to Earning'] <= pe_range[1]) &
        (filtered_data['Return on equity'] >= roe_min) &
        (filtered_data['Debt to equity'] <= de_max)
    ]
    
    if 'Market Capitalization' in filtered_data.columns:
        filtered_data = filtered_data[filtered_data['Market Capitalization'] >= mcap_min]
    
    # Add ratings
    ratings_data = []
    for _, stock in filtered_data.iterrows():
        rating, color, css_class = get_rating_and_color(stock)
        ratings_data.append({
            'rating': rating,
            'color': color,
            'css_class': css_class
        })
    
    ratings_df = pd.DataFrame(ratings_data)
    filtered_data = pd.concat([filtered_data.reset_index(drop=True), ratings_df], axis=1)
    
    # Summary metrics
    st.markdown("### 📊 Portfolio Overview")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("📈 Total Stocks", len(data), help="Total stocks in watchlist")
    with col2:
        st.metric("🎯 Filtered Results", len(filtered_data), help="Stocks matching your filters")
    with col3:
        avg_roe = filtered_data['Return on equity'].mean()
        st.metric("⚡ Avg ROE", f"{avg_roe:.1f}%" if not pd.isna(avg_roe) else "N/A", help="Average Return on Equity")
    with col4:
        avg_pe = filtered_data['Price to Earning'].mean()
        st.metric("💰 Avg P/E", f"{avg_pe:.1f}" if not pd.isna(avg_pe) else "N/A", help="Average Price to Earnings")
    with col5:
        excellent_count = len(filtered_data[filtered_data['rating'] == 'Excellent'])
        st.metric("⭐ Excellent", excellent_count, help="Stocks rated as Excellent")
    
    # Rating distribution
    if len(filtered_data) > 0:
        st.markdown("### 🏆 Rating Distribution")
        rating_counts = filtered_data['rating'].value_counts()
        
        cols = st.columns(len(rating_counts))
        colors = {'Excellent': '🟢', 'Good': '🔵', 'Average': '🟡', 'Below Average': '🟠', 'Poor': '🔴'}
        
        for i, (rating, count) in enumerate(rating_counts.items()):
            with cols[i]:
                st.markdown(f"""
                <div style="text-align: center; padding: 10px; background-color: #f0f0f0; border-radius: 10px;">
                    <div style="font-size: 24px;">{colors.get(rating, '⚪')}</div>
                    <div style="font-weight: bold;">{count}</div>
                    <div style="font-size: 12px; color: #666;">{rating}</div>
                </div>
                """, unsafe_allow_html=True)
    
    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Stock Analysis", "📈 Market Overview", "🎯 Top Picks", "📋 Detailed View"])
    
    with tab1:
        st.subheader("📊 Stock Analysis & Screening")
        
        if len(filtered_data) == 0:
            st.warning("No stocks match your current filters. Try adjusting the filter criteria.")
            return
        
        # Sorting
        sort_cols = ['Name', 'Current Price', 'Return on equity', 'Price to Earning', 'rating']
        if 'Market Capitalization' in filtered_data.columns:
            sort_cols.insert(2, 'Market Capitalization')
        if 'Sales growth 5Years' in filtered_data.columns:
            sort_cols.append('Sales growth 5Years')
        
        col1, col2 = st.columns([3, 1])
        with col1:
            sort_by = st.selectbox("📈 Sort by", sort_cols)
        with col2:
            sort_order = st.selectbox("Order", ["Descending", "Ascending"])
        
        ascending = sort_order == "Ascending"
        display_data = filtered_data.sort_values(by=sort_by, ascending=ascending)
        
        # Display stocks
        for idx, stock in display_data.iterrows():
            rating_class = stock['css_class']
            
            with st.container():
                st.markdown(f"""
                <div class="metric-card {rating_class}">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                        <div style="flex: 1;">
                            <h3 style="margin: 0; color: #333;">{stock['Name']}</h3>
                            <p style="margin: 5px 0; color: #666; font-size: 14px;">
                                <strong>{stock['NSE Code']}</strong> • {stock.get('Industry', 'N/A')}
                            </p>
                            <div class="rating-badge" style="background-color: {stock['color']};">
                                {stock['rating']}
                            </div>
                        </div>
                        <div style="text-align: right;">
                            <div style="font-size: 24px; font-weight: bold; color: #333;">
                                ₹{stock['Current Price']:.2f}
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Key metrics in columns
                col1, col2, col3, col4, col5 = st.columns(5)
                
                with col1:
                    pe_color = color_code_value(stock['Price to Earning'], [15, 25], good_high=False)
                    st.markdown(f"**P/E:** {pe_color} {format_number(stock['Price to Earning'])}")
                
                with col2:
                    roe_color = color_code_value(stock['Return on equity'], [10, 15], good_high=True)
                    st.markdown(f"**ROE:** {roe_color} {format_number(stock['Return on equity'], '%')}")
                
                with col3:
                    de_color = color_code_value(stock['Debt to equity'], [0.5, 1.0], good_high=False)
                    st.markdown(f"**D/E:** {de_color} {format_number(stock['Debt to equity'])}")
                
                with col4:
                    if 'Market Capitalization' in stock and pd.notna(stock['Market Capitalization']):
                        st.markdown(f"**MCap:** {format_currency(stock['Market Capitalization'])}")
                    else:
                        st.markdown("**MCap:** N/A")
                
                with col5:
                    if 'Return over 1year' in stock and pd.notna(stock['Return over 1year']):
                        ret_color = color_code_value(stock['Return over 1year'], [0, 15], good_high=True)
                        st.markdown(f"**1Y Ret:** {ret_color} {format_number(stock['Return over 1year'], '%')}")
                    else:
                        st.markdown("**1Y Ret:** N/A")
                
                st.markdown("---")
    
    with tab2:
        st.subheader("📈 Market Overview")
        
        if len(filtered_data) > 0:
            # Industry analysis
            if 'Industry' in filtered_data.columns:
                st.markdown("#### 🏭 Industry Distribution")
                industry_counts = filtered_data['Industry'].value_counts().head(10)
                st.bar_chart(industry_counts)
            
            # Rating distribution chart
            st.markdown("#### 🏆 Rating Breakdown")
            rating_counts = filtered_data['rating'].value_counts()
            st.bar_chart(rating_counts)
            
            # Key statistics
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 📊 Valuation Metrics")
                pe_stats = filtered_data['Price to Earning'].describe()
                st.dataframe(pe_stats.round(2))
            
            with col2:
                st.markdown("#### 💪 Profitability Metrics")  
                roe_stats = filtered_data['Return on equity'].describe()
                st.dataframe(roe_stats.round(2))
        
        else:
            st.info("📊 Apply filters to see market overview")
    
    with tab3:
        st.subheader("🎯 Top Investment Picks")
        
        # Separate by ratings
        excellent_stocks = filtered_data[filtered_data['rating'] == 'Excellent'].copy()
        good_stocks = filtered_data[filtered_data['rating'] == 'Good'].copy()
        
        if len(excellent_stocks) > 0:
            st.markdown("### ⭐ Excellent Rated Stocks")
            st.markdown("*Stocks with strong fundamentals across all key metrics*")
            
            for _, stock in excellent_stocks.head(10).iterrows():
                with st.expander(f"🌟 {stock['Name']} ({stock['NSE Code']})", expanded=False):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Current Price", f"₹{stock['Current Price']:.2f}")
                        if 'Market Capitalization' in stock:
                            st.metric("Market Cap", format_currency(stock['Market Capitalization']))
                    
                    with col2:
                        st.metric("ROE", f"{stock['Return on equity']:.1f}%")
                        st.metric("P/E Ratio", f"{stock['Price to Earning']:.1f}")
                    
                    with col3:
                        st.metric("Debt/Equity", f"{stock['Debt to equity']:.2f}")
                        if 'Sales growth 5Years' in stock and pd.notna(stock['Sales growth 5Years']):
                            st.metric("Sales Growth", f"{stock['Sales growth 5Years']:.1f}%")
        
        if len(good_stocks) > 0:
            st.markdown("### 👍 Good Rated Stocks")
            st.markdown("*Solid investment opportunities with good fundamentals*")
            
            for _, stock in good_stocks.head(8).iterrows():
                with st.expander(f"👍 {stock['Name']} ({stock['NSE Code']})", expanded=False):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Current Price", f"₹{stock['Current Price']:.2f}")
                        if 'Market Capitalization' in stock:
                            st.metric("Market Cap", format_currency(stock['Market Capitalization']))
                    
                    with col2:
                        st.metric("ROE", f"{stock['Return on equity']:.1f}%")
                        st.metric("P/E Ratio", f"{stock['Price to Earning']:.1f}")
                    
                    with col3:
                        st.metric("Debt/Equity", f"{stock['Debt to equity']:.2f}")
                        if 'Sales growth 5Years' in stock and pd.notna(stock['Sales growth 5Years']):
                            st.metric("Sales Growth", f"{stock['Sales growth 5Years']:.1f}%")
        
        if len(excellent_stocks) == 0 and len(good_stocks) == 0:
            st.info("🔍 No excellent or good rated stocks found with current filters. Try adjusting your criteria.")
            
            # Show best available
            if len(filtered_data) > 0:
                st.markdown("### 🥈 Best Available Options")
                best_stocks = filtered_data.nlargest(5, 'Return on equity')
                
                for _, stock in best_stocks.iterrows():
                    st.markdown(f"**{stock['Name']}** - ROE: {stock['Return on equity']:.1f}%, Rating: {stock['rating']}")
    
    with tab4:
        st.subheader("📋 Detailed Stock Analysis")
        
        if len(filtered_data) > 0:
            stock_names = filtered_data['Name'].tolist()
            selected_stock_name = st.selectbox("🔍 Select a stock for detailed analysis", stock_names)
            
            stock_data = filtered_data[filtered_data['Name'] == selected_stock_name].iloc[0]
            
            # Header section
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"## 🏢 {stock_data['Name']}")
                st.markdown(f"**NSE:** {stock_data['NSE Code']} | **Industry:** {stock_data.get('Industry', 'N/A')}")
            
            with col2:
                st.markdown(f"""
                <div style="background-color: {stock_data['color']}; color: white; padding: 15px; 
                           border-radius: 15px; text-align: center; margin: 10px 0;">
                    <div style="font-size: 18px; font-weight: bold;">{stock_data['rating']}</div>
                    <div style="font-size: 24px; margin-top: 5px;">₹{stock_data['Current Price']:.2f}</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Key metrics
            st.markdown("### 💼 Financial Scorecard")
            
            col1, col2, col3, col4 = st.columns(4)
            
            metrics = [
                ("Market Cap", format_currency(stock_data.get('Market Capitalization', 0)), col1),
                ("P/E Ratio", format_number(stock_data['Price to Earning']), col2),
                ("ROE", format_number(stock_data['Return on equity'], '%'), col3),
                ("Debt/Equity", format_number(stock_data['Debt to equity']), col4)
            ]
            
            for metric_name, metric_value, col in metrics:
                with col:
                    st.metric(metric_name, metric_value)
            
            # Additional metrics if available
            additional_metrics = []
            for col_name, display_name, format_func in [
                ('Return on invested capital', 'ROIC', lambda x: format_number(x, '%')),
                ('NPM last year', 'Net Profit Margin', lambda x: format_number(x, '%')),
                ('Sales growth 5Years', 'Sales Growth (5Y)', lambda x: format_number(x, '%')),
                ('Dividend yield', 'Dividend Yield', lambda x: format_number(x, '%'))
            ]:
                if col_name in stock_data and pd.notna(stock_data[col_name]):
                    additional_metrics.append((display_name, format_func(stock_data[col_name])))
            
            if additional_metrics:
                st.markdown("### 📈 Additional Metrics")
                cols = st.columns(len(additional_metrics))
                for i, (name, value) in enumerate(additional_metrics):
                    with cols[i]:
                        st.metric(name, value)
            
            # Investment analysis
            st.markdown("### 🎯 Investment Analysis")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### ✅ **Strengths**")
                strengths = []
                
                if stock_data['Return on equity'] >= 15:
                    strengths.append(f"Strong profitability (ROE: {stock_data['Return on equity']:.1f}%)")
                if stock_data['Debt to equity'] <= 0.5:
                    strengths.append(f"Conservative debt levels (D/E: {stock_data['Debt to equity']:.2f})")
                if stock_data['Price to Earning'] <= 20:
                    strengths.append(f"Reasonable valuation (P/E: {stock_data['Price to Earning']:.1f})")
                if 'Sales growth 5Years' in stock_data and pd.notna(stock_data['Sales growth 5Years']) and stock_data['Sales growth 5Years'] >= 15:
                    strengths.append(f"Strong growth trajectory ({stock_data['Sales growth 5Years']:.1f}% sales growth)")
                if 'Free cash flow last year' in stock_data and pd.notna(stock_data['Free cash flow last year']) and stock_data['Free cash flow last year'] > 0:
                    strengths.append("Positive cash generation")
                
                if strengths:
                    for strength in strengths:
                        st.markdown(f"• {strength}")
                else:
                    st.markdown("• Limited strengths identified with current metrics")
            
            with col2:
                st.markdown("#### ⚠️ **Risk Factors**")
                risks = []
                
                if stock_data['Price to Earning'] > 25:
                    risks.append(f"High valuation (P/E: {stock_data['Price to Earning']:.1f})")
                if stock_data['Debt to equity'] > 1:
                    risks.append(f"High debt burden (D/E: {stock_data['Debt to equity']:.2f})")
                if stock_data['Return on equity'] < 10:
                    risks.append(f"Below-average profitability (ROE: {stock_data['Return on equity']:.1f}%)")
                if 'Sales growth 5Years' in stock_data and pd.notna(stock_data['Sales growth 5Years']) and stock_data['Sales growth 5Years'] < 5:
                    risks.append("Slow growth trajectory")
                if 'Free cash flow last year' in stock_data and pd.notna(stock_data['Free cash flow last year']) and stock_data['Free cash flow last year'] < 0:
                    risks.append("Negative cash flow")
                
                if risks:
                    for risk in risks:
                        st.markdown(f"• {risk}")
                else:
                    st.markdown("• No major risk factors identified")
            
            # Performance data if available
            performance_cols = ['Return over 1year', 'Return over 3years', 'Return over 5years']
            available_performance = [col for col in performance_cols if col in stock_data and pd.notna(stock_data[col])]
            
            if available_performance:
                st.markdown("### 📊 Historical Performance")
                perf_cols = st.columns(len(available_performance))
                
                for i, col_name in enumerate(available_performance):
                    with perf_cols[i]:
                        period = col_name.replace('Return over ', '').replace('year', 'Y').replace('years', 'Y')
                        value = stock_data[col_name]
                        delta_color = "normal" if value >= 0 else "inverse"
                        st.metric(f"{period} Return", f"{value:.1f}%", delta=f"{value:.1f}%", delta_color=delta_color)

if __name__ == "__main__":
    main()
