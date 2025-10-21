# Farmer's Fresh LLC - Financial Dashboard

A comprehensive, interactive financial dashboard built with Plotly Dash that visualizes historical financial data and projects 2026 performance.

## Features

### 📊 Interactive Visualizations
- **Revenue vs Expenses Comparison** - Historical data with 2026 projections
- **Net Income Trend Analysis** - Track profitability over time with forecasting
- **Expense Breakdown** - Pie chart showing 2025 expense distribution by category
- **Revenue Sources** - Horizontal bar chart of revenue streams
- **Profit Margin Trend** - Monitor profitability percentage across years
- **Top 10 Expenses** - Compare 2025 actual vs 2026 projected expenses

### 🎯 Key Performance Indicators (KPIs)
- 2026 Projected Revenue with growth percentage
- 2026 Projected Net Income
- 2026 Profit Margin
- 2025 Actual Revenue

### 🔮 2026 Projections
The dashboard calculates 2026 projections using:
- Historical growth rate analysis (2023-2025)
- Category-level trend detection
- Intelligent fallback mechanisms for sparse data
- Conservative estimation to ensure realistic forecasts

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Ensure the Excel file is in the correct location:**
```
/home/esteban/tio cesar/Farmer's Fresh^J LLC_Profit and Loss Yearly.xlsx
```

## Usage

### Run the Dashboard

```bash
python3 financial_dashboard.py
```

The dashboard will start on `http://localhost:8050`

Open your web browser and navigate to:
```
http://localhost:8050
```

Or access from another device on the same network:
```
http://<your-ip-address>:8050
```

### Stop the Dashboard

Press `Ctrl+C` in the terminal where the dashboard is running.

## Dashboard Layout

### Header Section
- Company name and title
- Generation timestamp
- Navigation breadcrumb

### KPI Cards (Top Row)
Four key metrics displayed as cards:
1. **2026 Projected Revenue** - Shows revenue forecast and % change vs 2025
2. **2026 Projected Net Income** - Estimated profit for next year
3. **2026 Profit Margin** - Profitability percentage
4. **2025 Actual Revenue** - Latest confirmed revenue data

### Visualization Grid
Six comprehensive charts arranged in three rows:

**Row 1:**
- Revenue vs Expenses (grouped bar chart)
- Net Income Trend (line chart with projection)

**Row 2:**
- 2025 Expense Breakdown (donut chart)
- 2025 Revenue by Source (horizontal bar)

**Row 3:**
- Profit Margin Trend (area chart)
- Top 10 Expense Items comparison (grouped bar)

## Data Structure

The dashboard expects an Excel file with the following columns:
- `category` - Main financial category (Income, Expenses, etc.)
- `Distribution account` - Specific account/line item
- `2022` - 2022 financial data
- `2023` - 2023 financial data
- `2024` - 2024 financial data
- `2025` - 2025 financial data
- `Total` - Total across all years

## Customization

### Modify Colors
Edit the `colors` dictionary in `financial_dashboard.py`:
```python
colors = {
    'background': '#f8f9fa',
    'text': '#2c3e50',
    'primary': '#3498db',
    'success': '#2ecc71',
    # ... customize as needed
}
```

### Change Port
Modify the last line in `financial_dashboard.py`:
```python
app.run_server(debug=True, host='0.0.0.0', port=8050)  # Change port here
```

### Add New Visualizations
Add new chart functions following the pattern:
```python
def create_new_chart():
    fig = go.Figure()
    # Your chart logic here
    return fig
```

Then add to the layout within a `dbc.Card` component.

## Technical Details

### Projection Algorithm
1. Extract historical values for each line item (2023, 2024, 2025)
2. Calculate year-over-year growth rates
3. Compute average growth rate
4. Apply growth rate to most recent value
5. Ensure non-negative results
6. Fallback to average if insufficient data

### Technologies Used
- **Plotly** - Interactive charting library
- **Dash** - Web framework for Python analytics
- **Dash Bootstrap Components** - Professional UI components
- **Pandas** - Data manipulation and analysis
- **NumPy** - Numerical computing
- **OpenPyXL** - Excel file reading

### Performance
- Loads data once on startup
- Generates all charts on initialization
- Responsive design for mobile and desktop
- Optimized for datasets with 50-100 line items

## Troubleshooting

### Dashboard won't start
```bash
# Check if port 8050 is already in use
lsof -i :8050

# Kill process if needed
kill -9 <PID>
```

### Excel file not found
Ensure the file path matches exactly:
```python
file_path = "/home/esteban/tio cesar/Farmer's Fresh^J LLC_Profit and Loss Yearly.xlsx"
```

### Missing dependencies
```bash
pip install --upgrade -r requirements.txt
```

### Charts not displaying
- Clear browser cache
- Try a different browser (Chrome recommended)
- Check browser console for JavaScript errors

## Future Enhancements

Potential features to add:
- [ ] Export dashboard as PDF report
- [ ] Interactive date range selector
- [ ] Scenario planning (optimistic/pessimistic projections)
- [ ] Month-by-month breakdown
- [ ] Cash flow analysis
- [ ] Budget vs Actual comparison
- [ ] Year-over-year percentage changes table
- [ ] Quarterly performance tracking

## License

Proprietary - Farmer's Fresh LLC

## Support

For questions or issues, contact your system administrator.
