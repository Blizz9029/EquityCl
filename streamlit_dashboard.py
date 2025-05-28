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
    """Format currency values - values are already in Crores"""
    if pd.isna(value) or value == 0:
        return "N/A"
    
    # Values are already in Crores, so just format them nicely
    if value >= 100000:  # 1 Lakh Crores and above
        return f"₹{value/1000:.0f}K Cr"
    elif value >= 10000:  # 10,000 Cr and above  
        return f"₹{value:,.0f}Cr"
    elif value >= 1000:   # 1,000 Cr and above
        return f"₹{value:,.0f}Cr"
    else:                 # Below 1,000 Cr
        return f"₹{value:.0f}Cr"

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
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Stock Analysis", "📈 Market Overview", "📊 Performance Charts", "🎯 Top Picks", "📋 Detailed View"])
    
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
        st.subheader("📊 Performance Charts & Analysis")
        
        if len(filtered_data) > 0:
            # Growth & Returns Ranking
            st.markdown("### 🏆 Growth & Returns Ranking")
            st.markdown("*Comprehensive ranking based on growth metrics and returns*")
            
            # Create ranking based on growth and returns
            ranking_data = filtered_data.copy()
            
            # Calculate composite growth score
            def calculate_growth_score(row):
                score = 0
                weights = 0
                
                # 1Y Return (30% weight)
                if pd.notna(row.get('Return over 1year', 0)):
                    score += row['Return over 1year'] * 0.3
                    weights += 0.3
                
                # 3Y Return (25% weight)  
                if pd.notna(row.get('Return over 3years', 0)):
                    score += row['Return over 3years'] * 0.25
                    weights += 0.25
                
                # Sales Growth (20% weight)
                if pd.notna(row.get('Sales growth 5Years', 0)):
                    score += row['Sales growth 5Years'] * 0.2
                    weights += 0.2
                
                # Profit Growth (15% weight)
                if pd.notna(row.get('Profit growth 5Years', 0)):
                    score += row['Profit growth 5Years'] * 0.15
                    weights += 0.15
                
                # ROE (10% weight)
                if pd.notna(row.get('Return on equity', 0)):
                    score += row['Return on equity'] * 0.1
                    weights += 0.1
                
                return score / weights if weights > 0 else 0
            
            ranking_data['Growth_Score'] = ranking_data.apply(calculate_growth_score, axis=1)
            ranking_data = ranking_data.sort_values('Growth_Score', ascending=False)
            
            # Display top 15 ranked stocks
            st.markdown("#### 🥇 Top Growth & Returns Champions")
            
            for i, (_, stock) in enumerate(ranking_data.head(15).iterrows(), 1):
                medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"#{i}"
                
                col1, col2, col3, col4, col5 = st.columns([1, 3, 1.5, 1.5, 1.5])
                
                with col1:
                    st.markdown(f"**{medal}**")
                
                with col2:
                    st.markdown(f"**{stock['Name']}**")
                    st.caption(f"{stock['NSE Code']} • {stock.get('Industry', 'N/A')}")
                
                with col3:
                    if pd.notna(stock.get('Return over 1year')):
                        ret_1y = stock['Return over 1year']
                        color = "🟢" if ret_1y > 20 else "🟡" if ret_1y > 0 else "🔴"
                        st.markdown(f"{color} **1Y:** {ret_1y:.1f}%")
                    else:
                        st.markdown("**1Y:** N/A")
                
                with col4:
                    if pd.notna(stock.get('Return over 3years')):
                        ret_3y = stock['Return over 3years']
                        color = "🟢" if ret_3y > 15 else "🟡" if ret_3y > 5 else "🔴"
                        st.markdown(f"{color} **3Y:** {ret_3y:.1f}%")
                    else:
                        st.markdown("**3Y:** N/A")
                
                with col5:
                    roe = stock['Return on equity']
                    color = "🟢" if roe > 20 else "🟡" if roe > 15 else "🔴"
                    st.markdown(f"{color} **ROE:** {roe:.1f}%")
                
                st.markdown("---")
            
            # Individual Performance Charts
            st.markdown("### 📈 Performance Analysis Charts")
            
            # 1. Returns Comparison Charts
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 🚀 1-Year Returns Leaders")
                returns_1y = filtered_data[['Name', 'Return over 1year']].dropna()
                if len(returns_1y) > 0:
                    returns_1y = returns_1y.sort_values('Return over 1year', ascending=True).tail(15)
                    
                    # Create horizontal bar chart
                    fig_data = []
                    colors = []
                    for _, row in returns_1y.iterrows():
                        ret = row['Return over 1year']
                        if ret > 50:
                            colors.append('#2e7d32')  # Dark green
                        elif ret > 20:
                            colors.append('#66bb6a')  # Light green  
                        elif ret > 0:
                            colors.append('#ffb74d')  # Orange
                        else:
                            colors.append('#f44336')  # Red
                        fig_data.append({'Name': row['Name'][:20], 'Return': ret})
                    
                    chart_df = pd.DataFrame(fig_data)
                    
                    # Display as horizontal bar chart using Streamlit
                    st.bar_chart(chart_df.set_index('Name')['Return'], height=400)
                else:
                    st.info("No 1-year return data available")
            
            with col2:
                st.markdown("#### 📊 3-Year Returns Leaders")  
                returns_3y = filtered_data[['Name', 'Return over 3years']].dropna()
                if len(returns_3y) > 0:
                    returns_3y = returns_3y.sort_values('Return over 3years', ascending=True).tail(15)
                    
                    fig_data = []
                    for _, row in returns_3y.iterrows():
                        fig_data.append({'Name': row['Name'][:20], 'Return': row['Return over 3years']})
                    
                    chart_df = pd.DataFrame(fig_data)
                    st.bar_chart(chart_df.set_index('Name')['Return'], height=400)
                else:
                    st.info("No 3-year return data available")
            
            # 2. Profitability Charts
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 💪 ROE Champions")
                roe_data = filtered_data[['Name', 'Return on equity']].sort_values('Return on equity', ascending=True).tail(15)
                
                fig_data = []
                for _, row in roe_data.iterrows():
                    fig_data.append({'Name': row['Name'][:20], 'ROE': row['Return on equity']})
                
                chart_df = pd.DataFrame(fig_data)
                st.bar_chart(chart_df.set_index('Name')['ROE'], height=400)
            
            with col2:
                st.markdown("#### 🎯 ROIC Leaders")
                roic_data = filtered_data[['Name', 'Return on invested capital']].dropna().sort_values('Return on invested capital', ascending=True).tail(15)
                
                if len(roic_data) > 0:
                    fig_data = []
                    for _, row in roic_data.iterrows():
                        fig_data.append({'Name': row['Name'][:20], 'ROIC': row['Return on invested capital']})
                    
                    chart_df = pd.DataFrame(fig_data)
                    st.bar_chart(chart_df.set_index('Name')['ROIC'], height=400)
                else:
                    st.info("No ROIC data available")
            
            # 3. Margin Analysis
            col1, col2 = st.columns(2)
            
            with col1:
                if 'NPM last year' in filtered_data.columns:
                    st.markdown("#### 💰 Net Profit Margin Leaders")
                    npm_data = filtered_data[['Name', 'NPM last year']].dropna().sort_values('NPM last year', ascending=True).tail(15)
                    
                    if len(npm_data) > 0:
                        fig_data = []
                        for _, row in npm_data.iterrows():
                            fig_data.append({'Name': row['Name'][:20], 'NPM': row['NPM last year']})
                        
                        chart_df = pd.DataFrame(fig_data)
                        st.bar_chart(chart_df.set_index('Name')['NPM'], height=400)
                    else:
                        st.info("No NPM data available")
            
            with col2:
                # Calculate Operating Profit Margin if possible
                if 'Operating profit' in filtered_data.columns and 'Sales' in filtered_data.columns:
                    st.markdown("#### 🏭 Operating Profit Margin Leaders")
                    
                    # Calculate OPM
                    opm_data = filtered_data.copy()
                    opm_data['OPM'] = (opm_data['Operating profit'] / opm_data['Sales']) * 100
                    opm_data = opm_data[['Name', 'OPM']].dropna()
                    opm_data = opm_data[opm_data['OPM'] > 0].sort_values('OPM', ascending=True).tail(15)
                    
                    if len(opm_data) > 0:
                        fig_data = []
                        for _, row in opm_data.iterrows():
                            fig_data.append({'Name': row['Name'][:20], 'OPM': row['OPM']})
                        
                        chart_df = pd.DataFrame(fig_data)
                        st.bar_chart(chart_df.set_index('Name')['OPM'], height=400)
                    else:
                        st.info("No OPM data available")
                else:
                    st.info("Operating profit data not available for OPM calculation")
            
            # 4. Growth Charts
            col1, col2 = st.columns(2)
            
            with col1:
                if 'Sales growth 5Years' in filtered_data.columns:
                    st.markdown("#### 📈 Sales Growth Champions")
                    sales_growth = filtered_data[['Name', 'Sales growth 5Years']].dropna().sort_values('Sales growth 5Years', ascending=True).tail(15)
                    
                    if len(sales_growth) > 0:
                        fig_data = []
                        for _, row in sales_growth.iterrows():
                            fig_data.append({'Name': row['Name'][:20], 'Sales_Growth': row['Sales growth 5Years']})
                        
                        chart_df = pd.DataFrame(fig_data)
                        st.bar_chart(chart_df.set_index('Name')['Sales_Growth'], height=400)
                    else:
                        st.info("No sales growth data available")
            
            with col2:
                if 'Profit growth 5Years' in filtered_data.columns:
                    st.markdown("#### 💹 Profit Growth Champions")
                    profit_growth = filtered_data[['Name', 'Profit growth 5Years']].dropna().sort_values('Profit growth 5Years', ascending=True).tail(15)
                    
                    if len(profit_growth) > 0:
                        fig_data = []
                        for _, row in profit_growth.iterrows():
                            fig_data.append({'Name': row['Name'][:20], 'Profit_Growth': row['Profit growth 5Years']})
                        
                        chart_df = pd.DataFrame(fig_data)
                        st.bar_chart(chart_df.set_index('Name')['Profit_Growth'], height=400)
                    else:
                        st.info("No profit growth data available")
            
            # 5. Valuation vs Performance Scatter
            st.markdown("### 🎯 Valuation vs Performance Analysis")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### P/E vs ROE Analysis")
                pe_roe_data = filtered_data[['Name', 'Price to Earning', 'Return on equity']].dropna()
                
                if len(pe_roe_data) > 0:
                    # Create scatter plot data
                    scatter_data = pe_roe_data.copy()
                    scatter_data = scatter_data[(scatter_data['Price to Earning'] > 0) & (scatter_data['Price to Earning'] < 100)]
                    
                    if len(scatter_data) > 0:
                        # Since we can't use plotly, show a simple table of best value stocks
                        st.markdown("**Best Value Picks (Low P/E, High ROE):**")
                        
                        # Calculate value score (ROE/PE ratio)
                        scatter_data['Value_Score'] = scatter_data['Return on equity'] / scatter_data['Price to Earning']
                        top_value = scatter_data.nlargest(10, 'Value_Score')
                        
                        for i, (_, stock) in enumerate(top_value.iterrows(), 1):
                            st.markdown(f"{i}. **{stock['Name']}** - P/E: {stock['Price to Earning']:.1f}, ROE: {stock['Return on equity']:.1f}%")
            
            with col2:
                st.markdown("#### Market Cap vs Growth")
                if 'Market Capitalization' in filtered_data.columns and 'Sales growth 5Years' in filtered_data.columns:
                    mcap_growth = filtered_data[['Name', 'Market Capitalization', 'Sales growth 5Years']].dropna()
                    
                    # Show small cap high growth stocks
                    st.markdown("**Small Cap High Growth Stocks:**")
                    small_cap_growth = mcap_growth[mcap_growth['Market Capitalization'] < 10000]  # Less than 10K Cr
                    small_cap_growth = small_cap_growth[small_cap_growth['Sales growth 5Years'] > 15]  # >15% growth
                    small_cap_growth = small_cap_growth.sort_values('Sales growth 5Years', ascending=False)
                    
                    if len(small_cap_growth) > 0:
                        for i, (_, stock) in enumerate(small_cap_growth.head(8).iterrows(), 1):
                            st.markdown(f"{i}. **{stock['Name']}** - MCap: {format_currency(stock['Market Capitalization'])}, Growth: {stock['Sales growth 5Years']:.1f}%")
                    else:
                        st.info("No small cap high growth stocks found")
            
            # Summary Statistics
            st.markdown("### 📊 Performance Summary Statistics")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown("#### 🚀 Returns Summary")
                returns_1y_avg = filtered_data['Return over 1year'].mean()
                returns_1y_max = filtered_data['Return over 1year'].max()
                st.metric("Avg 1Y Return", f"{returns_1y_avg:.1f}%" if pd.notna(returns_1y_avg) else "N/A")
                st.metric("Best 1Y Return", f"{returns_1y_max:.1f}%" if pd.notna(returns_1y_max) else "N/A")
            
            with col2:
                st.markdown("#### 💪 Profitability Summary")
                roe_avg = filtered_data['Return on equity'].mean()
                roe_max = filtered_data['Return on equity'].max()
                st.metric("Avg ROE", f"{roe_avg:.1f}%")
                st.metric("Best ROE", f"{roe_max:.1f}%")
            
            with col3:
                st.markdown("#### 📈 Growth Summary")
                if 'Sales growth 5Years' in filtered_data.columns:
                    sales_avg = filtered_data['Sales growth 5Years'].mean()
                    sales_max = filtered_data['Sales growth 5Years'].max()
                    st.metric("Avg Sales Growth", f"{sales_avg:.1f}%" if pd.notna(sales_avg) else "N/A")
                    st.metric("Best Sales Growth", f"{sales_max:.1f}%" if pd.notna(sales_max) else "N/A")
                
            with col4:
                st.markdown("#### 💰 Valuation Summary")
                pe_avg = filtered_data['Price to Earning'].mean()
                pe_min = filtered_data['Price to Earning'].min()
                st.metric("Avg P/E", f"{pe_avg:.1f}")
                st.metric("Lowest P/E", f"{pe_min:.1f}")
        
        else:
            st.info("📊 Apply filters to see performance charts")

    with tab5:
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
