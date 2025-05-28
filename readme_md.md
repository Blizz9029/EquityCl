# 📈 Equity Research Dashboard

A comprehensive Streamlit dashboard for analyzing equity investments with advanced filtering, ratings, and insights.

## Features

- **Smart Rating System**: Automatically rates stocks as Excellent, Good, Average, Below Average, or Poor
- **Advanced Filtering**: Filter by P/E, ROE, Debt/Equity, Market Cap, Growth rates, and more
- **Interactive Analytics**: Visual charts and graphs for market analysis
- **Detailed Stock Analysis**: Complete financial metrics and investment thesis for each stock
- **Top Picks**: Automatically identifies best investment opportunities

## Quick Start

### Local Development

1. Clone the repository:
```bash
git clone <your-repo-url>
cd equity-research-dashboard
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Add your CSV file:
   - Place your `scwatchlist.csv` file in the root directory
   - Ensure it has the required columns (Name, Current Price, ROE, P/E, etc.)

4. Run the dashboard:
```bash
streamlit run app.py
```

### Deployment on Streamlit Cloud

1. Fork this repository on GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click "New app"
4. Connect your GitHub repository
5. Select this repository and the `app.py` file
6. Click "Deploy"

## File Structure

```
equity-research-dashboard/
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies  
├── scwatchlist.csv    # Your equity data (add this file)
└── README.md          # This file
```

## CSV Format

Your `scwatchlist.csv` should contain these columns:
- Name
- NSE Code
- Industry
- Current Price
- Market Capitalization
- Price to Earning
- Return on equity
- Debt to equity
- Sales growth 5Years
- Profit growth 5Years
- Free cash flow last year
- Dividend yield
- Return over 1year
- And other financial metrics...

## Rating System

Stocks are automatically rated based on:
- **ROE**: ≥15% (Excellent), ≥10% (Good), <10% (Poor)
- **Debt/Equity**: ≤0.5 (Excellent), ≤1.0 (Good), >1.0 (Poor)  
- **P/E Ratio**: ≤15 (Excellent), ≤25 (Good), >25 (Poor)
- **Growth**: Sales/Profit growth ≥15% (Bonus points)
- **Cash Flow**: Positive FCF (Bonus points)

## Usage Tips

1. **Start with Top Picks**: Check the "Top Picks" tab for best opportunities
2. **Use Filters**: Filter for ROE >15% and D/E <0.5 to find quality stocks
3. **Analyze Details**: Click on individual stocks for complete analysis
4. **Visual Analytics**: Use charts to understand market distribution and correlations

## Support

For issues or questions, please create an issue in the GitHub repository.

## License

MIT License - feel free to modify and use for your investment research!