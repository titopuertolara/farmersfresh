import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc
from datetime import datetime

# Read the Excel file
file_path = "Farmers FreshLLC_Profit and Loss Yearly.xlsx"
df = pd.read_excel(file_path)

# Clean data
df = df.fillna(0)

# Create summary by category and year
years = ['2022', '2023', '2024', '2025', '2026']

# Calculate projections for 2026
def calculate_projection(row):
    """Calculate 2026 projection based on growth trends"""
    values = [row['2023'], row['2024'], row['2025']]
    values = [v for v in values if v != 0]

    if len(values) >= 2:
        # Calculate average growth rate
        growth_rates = []
        for i in range(1, len(values)):
            if values[i-1] != 0:
                growth_rates.append((values[i] - values[i-1]) / abs(values[i-1]))

        if growth_rates:
            avg_growth = np.mean(growth_rates)
            # Apply growth rate to last known value
            last_value = row['2025'] if row['2025'] != 0 else (row['2024'] if row['2024'] != 0 else row['2023'])
            projection = last_value * (1 + avg_growth)
            return max(0, projection)  # Ensure non-negative

    # Fallback: use average of available years
    if len(values) > 0:
        return np.mean(values)
    return 0

df['2026_Projection'] = df.apply(calculate_projection, axis=1)

# Aggregate by major categories
category_summary = df.groupby('category')[['2022', '2023', '2024', '2025', '2026_Projection']].sum().reset_index()

# Calculate revenue and expenses
revenue_categories = ['Income', 'Other income']
expense_categories = ['Cost of Goods Sold', 'Inventory Shrinkage', 'Expenses', 'Insurance',
                     'Interest paid', 'Legal & accounting services', 'Meals', 'Office expenses',
                     'Payroll expenses', 'Payroll Processing Fees', 'Taxes paid', 'Travel',
                     'Utilities', 'Other Expenses', 'Vehicle expenses']

# Calculate yearly totals
yearly_totals = {
    'Year': ['2022', '2023', '2024', '2025', '2026 (Projected)'],
    'Revenue': [],
    'Expenses': [],
    'Net Income': []
}

for year, year_label in zip(['2022', '2023', '2024', '2025', '2026_Projection'],
                           ['2022', '2023', '2024', '2025', '2026 (Projected)']):
    revenue = df[df['category'].isin(revenue_categories)][year].sum()
    expenses = df[df['category'].isin(expense_categories)][year].sum()
    net_income = revenue - expenses

    yearly_totals['Revenue'].append(revenue)
    yearly_totals['Expenses'].append(expenses)
    yearly_totals['Net Income'].append(net_income)

yearly_df = pd.DataFrame(yearly_totals)

# Initialize Dash app with Bootstrap theme
app = Dash(__name__, external_stylesheets=[dbc.themes.LUX])
server = app.server
# Define color scheme
colors = {
    'background': '#f8f9fa',
    'text': '#2c3e50',
    'primary': '#3498db',
    'success': '#2ecc71',
    'danger': '#e74c3c',
    'warning': '#f39c12',
    'revenue': '#27ae60',
    'expense': '#e67e22',
    'profit': '#3498db',
    'card_bg': '#ffffff'
}

# Create visualizations
def create_revenue_expense_chart():
    """Revenue vs Expenses comparison with projection"""
    fig = go.Figure()

    fig.add_trace(go.Bar(
        name='Revenue',
        x=yearly_df['Year'],
        y=yearly_df['Revenue'],
        marker_color=colors['revenue'],
        text=yearly_df['Revenue'].apply(lambda x: f'${x:,.0f}'),
        textposition='outside',
        hovertemplate='<b>Revenue</b><br>%{x}<br>$%{y:,.2f}<extra></extra>'
    ))

    fig.add_trace(go.Bar(
        name='Expenses',
        x=yearly_df['Year'],
        y=yearly_df['Expenses'],
        marker_color=colors['expense'],
        text=yearly_df['Expenses'].apply(lambda x: f'${x:,.0f}'),
        textposition='outside',
        hovertemplate='<b>Expenses</b><br>%{x}<br>$%{y:,.2f}<extra></extra>'
    ))

    fig.update_layout(
        title='Revenue vs Expenses (2022-2026: Historical & Projected)',
        barmode='group',
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family="Arial, sans-serif", size=12, color=colors['text']),
        xaxis=dict(showgrid=False, title='Year'),
        yaxis=dict(title='Amount ($)', showgrid=True, gridcolor='#ecf0f1'),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode='x unified',
        height=400,
        margin=dict(l=60, r=40, t=80, b=60)
    )

    return fig

def create_net_income_chart():
    """Net Income trend with projection"""
    fig = go.Figure()

    # Split historical and projected (first 4 years are historical: 2022, 2023, 2024, 2025)
    historical_years = yearly_df['Year'][:4]
    historical_income = yearly_df['Net Income'][:4]
    projected_year = yearly_df['Year'][4:]
    projected_income = yearly_df['Net Income'][4:]

    fig.add_trace(go.Scatter(
        name='Historical Net Income (2022-2025)',
        x=historical_years,
        y=historical_income,
        mode='lines+markers+text',
        line=dict(color=colors['profit'], width=3),
        marker=dict(size=12, symbol='circle'),
        text=historical_income.apply(lambda x: f'${x:,.0f}'),
        textposition='top center',
        hovertemplate='<b>Net Income</b><br>%{x}<br>$%{y:,.2f}<extra></extra>'
    ))

    # Add projection
    all_years = list(historical_years) + list(projected_year)
    all_income = list(historical_income) + list(projected_income)

    fig.add_trace(go.Scatter(
        name='Projected Net Income (2026)',
        x=all_years[-2:],
        y=all_income[-2:],
        mode='lines+markers+text',
        line=dict(color=colors['warning'], width=3, dash='dash'),
        marker=dict(size=12, symbol='diamond'),
        text=[f'${all_income[-2]:,.0f}', f'${all_income[-1]:,.0f}'],
        textposition='top center',
        hovertemplate='<b>Projected Net Income</b><br>%{x}<br>$%{y:,.2f}<extra></extra>'
    ))

    fig.update_layout(
        title='Net Income Trend & 2026 Projection (2022-2026)',
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family="Arial, sans-serif", size=12, color=colors['text']),
        xaxis=dict(showgrid=False, title='Year'),
        yaxis=dict(title='Net Income ($)', showgrid=True, gridcolor='#ecf0f1', zeroline=True),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode='x unified',
        height=400,
        margin=dict(l=60, r=40, t=80, b=60)
    )

    return fig

def create_expense_breakdown():
    """Expense breakdown by category for 2025"""
    expense_breakdown = df[df['category'].isin(expense_categories)].copy()
    expense_2025 = expense_breakdown.groupby('category')['2025'].sum().reset_index()
    expense_2025 = expense_2025[expense_2025['2025'] > 0].sort_values('2025', ascending=False)

    fig = go.Figure(data=[go.Pie(
        labels=expense_2025['category'],
        values=expense_2025['2025'],
        hole=.4,
        marker=dict(colors=px.colors.qualitative.Set3),
        textinfo='label+percent',
        hovertemplate='<b>%{label}</b><br>$%{value:,.2f}<br>%{percent}<extra></extra>'
    )])

    fig.update_layout(
        title='2025 Expense Breakdown by Category',
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family="Arial, sans-serif", size=12, color=colors['text']),
        showlegend=True,
        legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.05),
        height=450,
        margin=dict(l=40, r=200, t=60, b=40)
    )

    return fig

def create_revenue_breakdown():
    """Revenue breakdown by source for 2025"""
    revenue_breakdown = df[df['category'].isin(revenue_categories)].copy()
    revenue_2025 = revenue_breakdown[revenue_breakdown['2025'] > 0][['Distribution account', '2025']]
    revenue_2025 = revenue_2025.sort_values('2025', ascending=True)

    fig = go.Figure(data=[go.Bar(
        y=revenue_2025['Distribution account'],
        x=revenue_2025['2025'],
        orientation='h',
        marker_color=colors['success'],
        text=revenue_2025['2025'].apply(lambda x: f'${x:,.0f}'),
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>$%{x:,.2f}<extra></extra>'
    )])

    fig.update_layout(
        title='2025 Revenue by Source',
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family="Arial, sans-serif", size=12, color=colors['text']),
        xaxis=dict(title='Amount ($)', showgrid=True, gridcolor='#ecf0f1'),
        yaxis=dict(showgrid=False),
        height=350,
        margin=dict(l=150, r=100, t=60, b=60)
    )

    return fig

def create_top_expenses_chart():
    """Top 10 expense items for 2025 and 2026 projection"""
    expense_items = df[df['category'].isin(expense_categories)].copy()
    # Group by both category and distribution account to handle duplicates correctly
    expense_items = expense_items.groupby(['category', 'Distribution account'])[['2025', '2026_Projection']].sum().reset_index()
    # IMPORTANT: Only show items that have 2025 data to avoid mixing historical years
    expense_items = expense_items[expense_items['2025'] > 0]
    expense_items['Total'] = expense_items['2025'] + expense_items['2026_Projection']
    expense_items = expense_items.sort_values('Total', ascending=False).head(10)

    fig = go.Figure()

    fig.add_trace(go.Bar(
        name='2025 Actual',
        x=expense_items['Distribution account'],
        y=expense_items['2025'],
        marker_color='#e74c3c',  # Bright red for actual
        text=expense_items['2025'].apply(lambda x: f'${x:,.0f}'),
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Category: ' + expense_items['category'] + '<br>2025: $%{y:,.2f}<extra></extra>',
        customdata=expense_items['category']
    ))

    fig.add_trace(go.Bar(
        name='2026 Projected',
        x=expense_items['Distribution account'],
        y=expense_items['2026_Projection'],
        marker_color='#3498db',  # Blue for projection
        text=expense_items['2026_Projection'].apply(lambda x: f'${x:,.0f}'),
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Category: ' + expense_items['category'] + '<br>2026 Proj: $%{y:,.2f}<extra></extra>',
        customdata=expense_items['category']
    ))

    fig.update_layout(
        title='Top 10 Expense Items: 2025 vs 2026 Projection',
        barmode='group',
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family="Arial, sans-serif", size=12, color=colors['text']),
        xaxis=dict(showgrid=False, tickangle=-45),
        yaxis=dict(title='Amount ($)', showgrid=True, gridcolor='#ecf0f1'),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=450,
        margin=dict(l=60, r=40, t=80, b=120)
    )

    return fig

def create_profit_margin_chart():
    """Profit margin trend"""
    yearly_df['Profit Margin (%)'] = (yearly_df['Net Income'] / yearly_df['Revenue'] * 100).round(2)

    fig = go.Figure()

    # Historical data (2022-2025)
    fig.add_trace(go.Scatter(
        name='Historical Profit Margin',
        x=yearly_df['Year'][:4],
        y=yearly_df['Profit Margin (%)'][:4],
        mode='lines+markers+text',
        line=dict(color=colors['primary'], width=3),
        marker=dict(size=12, symbol='circle'),
        text=yearly_df['Profit Margin (%)'][:4].apply(lambda x: f'{x:.1f}%'),
        textposition='top center',
        fill='tozeroy',
        fillcolor='rgba(52, 152, 219, 0.1)',
        hovertemplate='<b>Profit Margin</b><br>%{x}<br>%{y:.2f}%<extra></extra>'
    ))

    # Projected data (2025-2026 connection)
    fig.add_trace(go.Scatter(
        name='Projected Profit Margin',
        x=[yearly_df['Year'].iloc[3], yearly_df['Year'].iloc[4]],
        y=[yearly_df['Profit Margin (%)'].iloc[3], yearly_df['Profit Margin (%)'].iloc[4]],
        mode='lines+markers+text',
        line=dict(color=colors['warning'], width=3, dash='dash'),
        marker=dict(size=12, symbol='diamond'),
        text=['', f'{yearly_df["Profit Margin (%)"].iloc[4]:.1f}%'],
        textposition='top center',
        hovertemplate='<b>Projected Profit Margin</b><br>%{x}<br>%{y:.2f}%<extra></extra>'
    ))

    fig.update_layout(
        title='Profit Margin Trend (2022-2026)',
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family="Arial, sans-serif", size=12, color=colors['text']),
        xaxis=dict(showgrid=False, title='Year'),
        yaxis=dict(title='Profit Margin (%)', showgrid=True, gridcolor='#ecf0f1'),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=350,
        margin=dict(l=60, r=40, t=80, b=60)
    )

    return fig

# Create KPI cards
def create_kpi_card(title, value, subtitle, icon, color):
    """Create a KPI card component"""
    return dbc.Card([
        dbc.CardBody([
            html.Div([
                html.I(className=f"bi bi-{icon} fs-1", style={'color': color}),
            ], className="text-center mb-2"),
            html.H3(value, className="text-center mb-1", style={'color': color, 'fontWeight': 'bold'}),
            html.P(title, className="text-center mb-0", style={'fontSize': '0.9rem', 'color': colors['text']}),
            html.P(subtitle, className="text-center text-muted", style={'fontSize': '0.75rem'}),
        ])
    ], className="shadow-sm h-100", style={'backgroundColor': colors['card_bg']})

# Calculate KPIs
revenue_2026 = yearly_df[yearly_df['Year'] == '2026 (Projected)']['Revenue'].values[0]
net_income_2026 = yearly_df[yearly_df['Year'] == '2026 (Projected)']['Net Income'].values[0]
profit_margin_2026 = (net_income_2026 / revenue_2026 * 100) if revenue_2026 > 0 else 0
revenue_growth = ((revenue_2026 - yearly_df[yearly_df['Year'] == '2025']['Revenue'].values[0]) /
                  yearly_df[yearly_df['Year'] == '2025']['Revenue'].values[0] * 100)

# App layout
app.layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col([
            html.H1("Farmer's Fresh LLC - Financial Dashboard",
                   className="text-center my-4",
                   style={'color': colors['primary'], 'fontWeight': 'bold'}),
            html.P(f"Financial Analysis & 2026 Projections | Generated on {datetime.now().strftime('%B %d, %Y')}",
                  className="text-center text-muted mb-4"),
        ])
    ]),

    # KPI Cards
    dbc.Row([
        dbc.Col([
            create_kpi_card(
                "2026 Projected Revenue",
                f"${revenue_2026:,.0f}",
                f"{revenue_growth:+.1f}% vs 2025",
                "graph-up-arrow",
                colors['success']
            )
        ], xs=12, sm=6, md=3, className="mb-3"),

        dbc.Col([
            create_kpi_card(
                "2026 Projected Net Income",
                f"${net_income_2026:,.0f}",
                "Based on trend analysis",
                "currency-dollar",
                colors['profit']
            )
        ], xs=12, sm=6, md=3, className="mb-3"),

        dbc.Col([
            create_kpi_card(
                "2026 Profit Margin",
                f"{profit_margin_2026:.1f}%",
                "Net Income / Revenue",
                "percent",
                colors['warning']
            )
        ], xs=12, sm=6, md=3, className="mb-3"),

        dbc.Col([
            create_kpi_card(
                "2025 Actual Revenue",
                f"${yearly_df[yearly_df['Year'] == '2025']['Revenue'].values[0]:,.0f}",
                "Latest available data",
                "cash-stack",
                colors['revenue']
            )
        ], xs=12, sm=6, md=3, className="mb-3"),
    ], className="mb-4"),

    # Main Charts Row 1
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(figure=create_revenue_expense_chart())
                ])
            ], className="shadow-sm h-100", style={'backgroundColor': colors['card_bg']})
        ], xs=12, lg=6, className="mb-4"),

        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(figure=create_net_income_chart())
                ])
            ], className="shadow-sm h-100", style={'backgroundColor': colors['card_bg']})
        ], xs=12, lg=6, className="mb-4"),
    ]),

    # Main Charts Row 2
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(figure=create_expense_breakdown())
                ])
            ], className="shadow-sm h-100", style={'backgroundColor': colors['card_bg']})
        ], xs=12, lg=6, className="mb-4"),

        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(figure=create_revenue_breakdown())
                ])
            ], className="shadow-sm h-100", style={'backgroundColor': colors['card_bg']})
        ], xs=12, lg=6, className="mb-4"),
    ]),

    # Main Charts Row 3
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(figure=create_profit_margin_chart())
                ])
            ], className="shadow-sm h-100", style={'backgroundColor': colors['card_bg']})
        ], xs=12, lg=6, className="mb-4"),

        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(figure=create_top_expenses_chart())
                ])
            ], className="shadow-sm h-100", style={'backgroundColor': colors['card_bg']})
        ], xs=12, lg=6, className="mb-4"),
    ]),

    # Footer
    dbc.Row([
        dbc.Col([
            html.Hr(),
            html.P("Note: 2026 projections are calculated based on historical growth trends and should be used for planning purposes only.",
                  className="text-center text-muted small mb-4"),
        ])
    ]),

], fluid=True, style={'backgroundColor': colors['background'], 'minHeight': '100vh', 'padding': '20px'})

# Run the app
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8050)
