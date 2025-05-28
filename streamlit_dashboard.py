import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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
    }
    .excellent { border-left-color: #2e7d32 !important; }
    .good { border-left-color: #1976d2 !important; }
    .average { border-left-color: #f57c00 !important; }
    .poor { border-left-color: #d32f2f !important; }
    
    .stSelectbox > div > div > select {
        background-color: white;
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
    except:
        st.error("Please upload your 'scwatchlist.csv' file to the repository")
        return pd.DataFrame()

def get_rating_and_color(stock):
    """Calculate overall rating for a stock"""
    score = 0
    factors = 0
    
    # ROE Score
    roe = stock.get('Return on equity', 0)
    if roe >= 15:
        score += 2
    elif roe >= 10:
        score += 1
    factors += 2
    
    # Debt to Equity Score
    de = stock.get('Debt to equity', 999)
    if de <= 0.5:
        score += 2
    elif de <= 1:
        score += 1
    factors += 2
    
    # PE Score
    pe = stock.get('Price to Earning', 999)
    if pe <= 15:
        score += 2
    elif pe <= 25:
        score += 1
    factors += 2
    
    # Growth Score
    sales_growth = stock.get('Sales growth 5Years', 0)
    profit_growth = stock.get('Profit growth 5Years', 0)
    if sales_growth >= 15:
        score += 1
    if profit_growth >= 15:
        score += 1
    factors += 2
    
    # FCF Score
    fcf = stock.get('Free cash flow last year', -999)
    if fcf > 0:
        score += 1
    factors += 1
    
    rating_score = (score / factors) * 5 if factors > 0 else 0
    
    if rating_score >= 4:
        return "Excellent", "#2e7d32"
    elif rating_score >= 3:
        return "Good", "#1976d2"
    elif rating_score >= 2:
        return "Average", "#f57c00"
    elif rating_score >= 1:
        return "Below Average", "#ff6f00"
    else:
        return "Poor", "#d32f2f"

def format_currency(value):
    """Format currency values"""
    if pd.isna(value):
        return "N/A"
    if value >= 100:
        return f"₹{value/100:.0f}Cr"
    else:
        return f"₹{value:.2f}Cr"

def format_percentage(value):
    """Format percentage values"""
    if pd.isna(value):
        return "N/A"
    return f"{value:.1f}%"

def main():
    st.title("📈 Equity Research Dashboard")
    st.markdown("**Analyze your stock watchlist with advanced filtering and insights**")
    
    # Load data
    data = load_data()
    
    if data.empty:
        st.warning("Please upload your CSV file to get started!")
        return
    
    # Sidebar filters
    st.sidebar.header("🔍 Filters")
    
    # Search
    search_term = st.sidebar.text_input("Search Company/NSE Code", "")
    
    # Industry filter
    industries = ['All'] + sorted(data['Industry'].dropna().unique().tolist())
    selected_industry = st.sidebar.selectbox("Industry", industries)
    
    # Advanced filters
    st.sidebar.subheader("Advanced Filters")
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        pe_min = st.number_input("Min P/E", min_value=0.0, value=0.0, step=1.0)
        roe_min = st.number_input("Min ROE (%)", min_value=0.0, value=0.0, step=1.0)
        sales_growth_min = st.number_input("Min Sales Growth (%)", min_value=0.0, value=0.0, step=1.0)
    
    with col2:
        pe_max = st.number_input("Max P/E", min_value=0.0, value=100.0, step=1.0)
        de_max = st.number_input("Max D/E", min_value=0.0, value=5.0, step=0.1)
        mcap_min = st.number_input("Min Market Cap (Cr)", min_value=0.0, value=0.0, step=100.0)
    
    # Boolean filters
    fcf_positive = st.sidebar.checkbox("Positive FCF Only")
    dividend_paying = st.sidebar.checkbox("Dividend Paying Only")
    
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
    if selected_industry != 'All':
        filtered_data = filtered_data[filtered_data['Industry'] == selected_industry]
    
    # Numerical filters
    filtered_data = filtered_data[
        (filtered_data['Price to Earning'] >= pe_min) &
        (filtered_data['Price to Earning'] <= pe_max) &
        (filtered_data['Return on equity'] >= roe_min) &
        (filtered_data['Debt to equity'] <= de_max) &
        (filtered_data['Market Capitalization'] >= mcap_min) &
        (filtered_data['Sales growth 5Years'] >= sales_growth_min)
    ]
    
    # Boolean filters
    if fcf_positive:
        filtered_data = filtered_data[filtered_data['Free cash flow last year'] > 0]
    
    if dividend_paying:
        filtered_data = filtered_data[filtered_data['Dividend yield'] > 0]
    
    # Display summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Stocks", len(data))
    with col2:
        st.metric("Filtered Results", len(filtered_data))
    with col3:
        avg_roe = filtered_data['Return on equity'].mean()
        st.metric("Avg ROE", f"{avg_roe:.1f}%" if not pd.isna(avg_roe) else "N/A")
    with col4:
        avg_pe = filtered_data['Price to Earning'].mean()
        st.metric("Avg P/E", f"{avg_pe:.1f}" if not pd.isna(avg_pe) else "N/A")
    
    # Add ratings to filtered data
    ratings_colors = []
    for _, stock in filtered_data.iterrows():
        rating, color = get_rating_and_color(stock)
        ratings_colors.append((rating, color))
    
    filtered_data['Rating'] = [rc[0] for rc in ratings_colors]
    filtered_data['Rating_Color'] = [rc[1] for rc in ratings_colors]
    
    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Stock List", "📈 Analytics", "🎯 Top Picks", "📋 Details"])
    
    with tab1:
        st.subheader("Stock Analysis")
        
        # Sorting options
        sort_options = ['Name', 'Current Price', 'Market Capitalization', 'Price to Earning', 
                       'Return on equity', 'Sales growth 5Years', 'Return over 1year']
        sort_by = st.selectbox("Sort by", sort_options)
        sort_ascending = st.checkbox("Ascending", value=True)
        
        # Sort data
        display_data = filtered_data.sort_values(by=sort_by, ascending=sort_ascending)
        
        # Display table
        for idx, stock in display_data.iterrows():
            with st.container():
                col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 1])
                
                with col1:
                    rating, color = stock['Rating'], stock['Rating_Color']
                    st.markdown(f"""
                    <div class="metric-card" style="border-left-color: {color} !important;">
                        <h4>{stock['Name']}</h4>
                        <p><strong>{stock['NSE Code']}</strong> • {stock['Industry']}</p>
                        <span style="background-color: {color}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 12px;">
                            {rating}
                        </span>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.metric("Price", f"₹{stock['Current Price']:.2f}")
                
                with col3:
                    st.metric("P/E", f"{stock['Price to Earning']:.1f}")
                
                with col4:
                    st.metric("ROE", f"{stock['Return on equity']:.1f}%")
                
                with col5:
                    st.metric("1Y Return", f"{stock['Return over 1year']:.1f}%" if not pd.isna(stock['Return over 1year']) else "N/A")
                
                st.markdown("---")
    
    with tab2:
        st.subheader("📈 Market Analytics")
        
        if len(filtered_data) > 0:
            # Industry distribution
            col1, col2 = st.columns(2)
            
            with col1:
                industry_counts = filtered_data['Industry'].value_counts()
                fig_pie = px.pie(values=industry_counts.values, names=industry_counts.index, 
                               title="Industry Distribution")
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with col2:
                rating_counts = filtered_data['Rating'].value_counts()
                fig_bar = px.bar(x=rating_counts.index, y=rating_counts.values, 
                               title="Rating Distribution",
                               color=rating_counts.index,
                               color_discrete_map={
                                   'Excellent': '#2e7d32',
                                   'Good': '#1976d2', 
                                   'Average': '#f57c00',
                                   'Below Average': '#ff6f00',
                                   'Poor': '#d32f2f'
                               })
                st.plotly_chart(fig_bar, use_container_width=True)
            
            # Scatter plots
            col1, col2 = st.columns(2)
            
            with col1:
                fig_scatter1 = px.scatter(filtered_data, x='Price to Earning', y='Return on equity',
                                        color='Rating', hover_name='Name',
                                        title="P/E vs ROE Analysis",
                                        color_discrete_map={
                                            'Excellent': '#2e7d32',
                                            'Good': '#1976d2', 
                                            'Average': '#f57c00',
                                            'Below Average': '#ff6f00',
                                            'Poor': '#d32f2f'
                                        })
                st.plotly_chart(fig_scatter1, use_container_width=True)
            
            with col2:
                fig_scatter2 = px.scatter(filtered_data, x='Market Capitalization', y='Sales growth 5Years',
                                        color='Rating', hover_name='Name',
                                        title="Market Cap vs Sales Growth",
                                        color_discrete_map={
                                            'Excellent': '#2e7d32',
                                            'Good': '#1976d2', 
                                            'Average': '#f57c00',
                                            'Below Average': '#ff6f00',
                                            'Poor': '#d32f2f'
                                        })
                st.plotly_chart(fig_scatter2, use_container_width=True)
    
    with tab3:
        st.subheader("🎯 Top Investment Picks")
        
        # Top stocks by rating
        excellent_stocks = filtered_data[filtered_data['Rating'] == 'Excellent']
        good_stocks = filtered_data[filtered_data['Rating'] == 'Good']
        
        if len(excellent_stocks) > 0:
            st.markdown("### ⭐ Excellent Stocks")
            for _, stock in excellent_stocks.head(5).iterrows():
                with st.expander(f"{stock['Name']} ({stock['NSE Code']})"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Current Price", f"₹{stock['Current Price']:.2f}")
                        st.metric("Market Cap", format_currency(stock['Market Capitalization']))
                    with col2:
                        st.metric("ROE", format_percentage(stock['Return on equity']))
                        st.metric("P/E", f"{stock['Price to Earning']:.1f}")
                    with col3:
                        st.metric("D/E", f"{stock['Debt to equity']:.2f}")
                        st.metric("Sales Growth", format_percentage(stock['Sales growth 5Years']))
        
        if len(good_stocks) > 0:
            st.markdown("### 👍 Good Stocks")
            for _, stock in good_stocks.head(5).iterrows():
                with st.expander(f"{stock['Name']} ({stock['NSE Code']})"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Current Price", f"₹{stock['Current Price']:.2f}")
                        st.metric("Market Cap", format_currency(stock['Market Capitalization']))
                    with col2:
                        st.metric("ROE", format_percentage(stock['Return on equity']))
                        st.metric("P/E", f"{stock['Price to Earning']:.1f}")
                    with col3:
                        st.metric("D/E", f"{stock['Debt to equity']:.2f}")
                        st.metric("Sales Growth", format_percentage(stock['Sales growth 5Years']))
    
    with tab4:
        st.subheader("📋 Detailed Stock Analysis")
        
        if len(filtered_data) > 0:
            stock_names = filtered_data['Name'].tolist()
            selected_stock_name = st.selectbox("Select a stock for detailed analysis", stock_names)
            
            stock_data = filtered_data[filtered_data['Name'] == selected_stock_name].iloc[0]
            
            # Stock header
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.markdown(f"## {stock_data['Name']}")
                st.markdown(f"**{stock_data['NSE Code']}** • {stock_data['Industry']}")
            with col2:
                rating, color = get_rating_and_color(stock_data)
                st.markdown(f"""
                <div style="background-color: {color}; color: white; padding: 8px 16px; border-radius: 20px; text-align: center; margin: 10px 0;">
                    <strong>{rating}</strong>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                st.metric("Current Price", f"₹{stock_data['Current Price']:.2f}")
            
            # Detailed metrics
            st.markdown("### Key Financial Metrics")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Market Cap", format_currency(stock_data['Market Capitalization']))
                st.metric("P/E Ratio", f"{stock_data['Price to Earning']:.1f}")
            with col2:
                st.metric("ROE", format_percentage(stock_data['Return on equity']))
                st.metric("ROIC", format_percentage(stock_data['Return on invested capital']))
            with col3:
                st.metric("Debt/Equity", f"{stock_data['Debt to equity']:.2f}")
                st.metric("NPM", format_percentage(stock_data['NPM last year']))
            with col4:
                st.metric("Sales Growth (5Y)", format_percentage(stock_data['Sales growth 5Years']))
                st.metric("Dividend Yield", format_percentage(stock_data['Dividend yield']))
            
            # Performance metrics
            st.markdown("### Performance Metrics")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("1Y Return", format_percentage(stock_data['Return over 1year']))
            with col2:
                st.metric("3Y Return", format_percentage(stock_data['Return over 3years']))
            with col3:
                st.metric("5Y Return", format_percentage(stock_data['Return over 5years']))
            with col4:
                st.metric("FCF", format_currency(stock_data['Free cash flow last year']))
            
            # Investment thesis
            st.markdown("### Investment Analysis")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### ✅ Strengths")
                strengths = []
                if stock_data['Return on equity'] >= 15:
                    strengths.append(f"Strong ROE ({stock_data['Return on equity']:.1f}%)")
                if stock_data['Debt to equity'] <= 0.5:
                    strengths.append(f"Low debt levels (D/E: {stock_data['Debt to equity']:.2f})")
                if stock_data['Sales growth 5Years'] >= 15:
                    strengths.append(f"Strong sales growth ({stock_data['Sales growth 5Years']:.1f}%)")
                if stock_data['Free cash flow last year'] > 0:
                    strengths.append("Positive free cash flow")
                if stock_data['Dividend yield'] > 0:
                    strengths.append("Dividend paying stock")
                
                for strength in strengths:
                    st.markdown(f"• {strength}")
                if not strengths:
                    st.markdown("• No major strengths identified")
            
            with col2:
                st.markdown("#### ⚠️ Concerns")
                concerns = []
                if stock_data['Price to Earning'] > 25:
                    concerns.append(f"High P/E ratio ({stock_data['Price to Earning']:.1f})")
                if stock_data['Debt to equity'] > 1:
                    concerns.append(f"High debt levels (D/E: {stock_data['Debt to equity']:.2f})")
                if stock_data['Return on equity'] < 10:
                    concerns.append(f"Low ROE ({stock_data['Return on equity']:.1f}%)")
                if stock_data['Free cash flow last year'] < 0:
                    concerns.append("Negative free cash flow")
                if stock_data['Sales growth 5Years'] < 5:
                    concerns.append("Slow sales growth")
                
                for concern in concerns:
                    st.markdown(f"• {concern}")
                if not concerns:
                    st.markdown("• No major concerns identified")

if __name__ == "__main__":
    main()