"""
Dashboard Layouts — Four pages: Overview, Quality, Anomalies, Reconciliation
"""

from dash import html, dcc, dash_table
import plotly.graph_objects as go


# Color palette
COLORS = {
    'bg': '#0a0a1a',
    'card': 'rgba(22, 27, 45, 0.7)',
    'border': 'rgba(99, 110, 150, 0.15)',
    'text': '#e6edf3',
    'text_muted': '#8b9dc3',
    'blue': '#3b82f6',
    'green': '#10b981',
    'purple': '#8b5cf6',
    'amber': '#f59e0b',
    'red': '#ef4444',
    'cyan': '#06b6d4',
    'grid': 'rgba(99, 110, 150, 0.08)',
}

PLOT_LAYOUT = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family='Inter, sans-serif', color=COLORS['text'], size=12),
    margin=dict(l=40, r=20, t=40, b=40),
    xaxis=dict(gridcolor=COLORS['grid'], zeroline=False),
    yaxis=dict(gridcolor=COLORS['grid'], zeroline=False),
    legend=dict(
        bgcolor='rgba(0,0,0,0)',
        font=dict(size=11, color=COLORS['text_muted']),
    ),
)


def create_nav():
    """Create navigation bar."""
    return html.Div(className='nav-container', children=[
        html.Div(className='nav-inner', children=[
            html.Div('📊 FinAnalytics', className='nav-brand'),
            html.Div(className='nav-links', children=[
                dcc.Link('Overview', href='/', className='nav-link', id='nav-overview'),
                dcc.Link('Data Quality', href='/quality', className='nav-link', id='nav-quality'),
                dcc.Link('Anomalies', href='/anomalies', className='nav-link', id='nav-anomalies'),
                dcc.Link('Reconciliation', href='/reconciliation', className='nav-link', id='nav-reconciliation'),
            ]),
        ]),
    ])


def create_filter_bar():
    """Create the global filter bar."""
    return html.Div(className='filter-bar', id='filter-bar', children=[
        html.Div(className='filter-group', children=[
            html.Label('Date Range', className='filter-label'),
            dcc.DatePickerRange(
                id='date-range-filter',
                start_date='2023-01-01',
                end_date='2025-12-31',
                display_format='MMM D, YYYY',
            ),
        ]),
        html.Div(className='filter-group', children=[
            html.Label('Category', className='filter-label'),
            dcc.Dropdown(
                id='category-filter',
                options=[],
                multi=True,
                placeholder='All Categories',
                style={'width': '220px', 'fontSize': '0.85rem'},
            ),
        ]),
        html.Div(className='filter-group', children=[
            html.Label('Status', className='filter-label'),
            dcc.Dropdown(
                id='status-filter',
                options=[
                    {'label': 'Completed', 'value': 'completed'},
                    {'label': 'Pending', 'value': 'pending'},
                    {'label': 'Failed', 'value': 'failed'},
                    {'label': 'Reversed', 'value': 'reversed'},
                ],
                multi=True,
                placeholder='All Statuses',
                style={'width': '200px', 'fontSize': '0.85rem'},
            ),
        ]),
    ])


def create_kpi_card(card_id, label, accent='blue'):
    """Create a KPI card component."""
    return html.Div(className=f'kpi-card accent-{accent}', children=[
        html.Div(label, className='kpi-label'),
        html.Div('—', className='kpi-value', id=f'kpi-{card_id}-value'),
        html.Div('', className='kpi-delta', id=f'kpi-{card_id}-delta'),
    ])


def create_overview_page():
    """Executive Overview page layout."""
    return html.Div([
        html.Div(className='page-header', children=[
            html.H1('Executive Overview', className='page-title'),
            html.P('High-level financial metrics and trends across 50,000+ records', className='page-subtitle'),
        ]),

        # KPI Row
        html.Div(className='grid-row', children=[
            create_kpi_card('total-records', 'Total Records', 'blue'),
            create_kpi_card('total-volume', 'Total Volume (USD)', 'green'),
            create_kpi_card('avg-transaction', 'Avg Transaction', 'purple'),
            create_kpi_card('completion-rate', 'Completion Rate', 'amber'),
            create_kpi_card('anomaly-rate', 'Anomaly Rate', 'red'),
            create_kpi_card('quality-score', 'Quality Score', 'cyan'),
        ]),

        # Charts Row 1
        html.Div(className='grid-row', style={'marginTop': '16px'}, children=[
            html.Div(className='glass-card grid-col-2', children=[
                html.H3('Monthly Revenue Trend', className='section-title'),
                dcc.Graph(id='revenue-trend-chart', config={'displayModeBar': False}),
            ]),
            html.Div(className='glass-card grid-col-2', children=[
                html.H3('Transaction Volume by Category', className='section-title'),
                dcc.Graph(id='category-distribution-chart', config={'displayModeBar': False}),
            ]),
        ]),

        # Charts Row 2
        html.Div(className='grid-row', style={'marginTop': '0px'}, children=[
            html.Div(className='glass-card grid-col-2', children=[
                html.H3('Status Distribution', className='section-title'),
                dcc.Graph(id='status-pie-chart', config={'displayModeBar': False}),
            ]),
            html.Div(className='glass-card grid-col-2', children=[
                html.H3('Top 10 Counterparties by Volume', className='section-title'),
                dcc.Graph(id='top-counterparties-chart', config={'displayModeBar': False}),
            ]),
        ]),
    ])


def create_quality_page():
    """Data Quality page layout."""
    return html.Div([
        html.Div(className='page-header', children=[
            html.H1('Data Quality', className='page-title'),
            html.P('Validation results, quality scorecard, and issue distribution', className='page-subtitle'),
        ]),

        # Quality KPIs
        html.Div(className='grid-row', children=[
            create_kpi_card('quality-overall', 'Overall Score', 'green'),
            create_kpi_card('quality-checks', 'Checks Run', 'blue'),
            create_kpi_card('quality-issues', 'Issues Found', 'red'),
            create_kpi_card('quality-critical', 'Critical Issues', 'amber'),
        ]),

        # Quality Charts
        html.Div(className='grid-row', style={'marginTop': '16px'}, children=[
            html.Div(className='glass-card grid-col-2', children=[
                html.H3('Quality Check Results', className='section-title'),
                dcc.Graph(id='quality-checks-chart', config={'displayModeBar': False}),
            ]),
            html.Div(className='glass-card grid-col-2', children=[
                html.H3('Issue Severity Distribution', className='section-title'),
                dcc.Graph(id='severity-distribution-chart', config={'displayModeBar': False}),
            ]),
        ]),

        # Quality Log Table
        html.Div(className='glass-card', style={'marginTop': '0px'}, children=[
            html.H3('Quality Check Details', className='section-title'),
            html.Div(id='quality-table-container'),
        ]),
    ])


def create_anomalies_page():
    """Anomaly Detection page layout."""
    return html.Div([
        html.Div(className='page-header', children=[
            html.H1('Anomaly Detection', className='page-title'),
            html.P('Statistical outliers detected via Z-score and IQR analysis', className='page-subtitle'),
        ]),

        # Anomaly KPIs
        html.Div(className='grid-row', children=[
            create_kpi_card('anomaly-total', 'Total Anomalies', 'red'),
            create_kpi_card('anomaly-zscore', 'Z-Score Outliers', 'purple'),
            create_kpi_card('anomaly-iqr', 'IQR Outliers', 'amber'),
            create_kpi_card('anomaly-category', 'Category Outliers', 'blue'),
        ]),

        # Anomaly Charts
        html.Div(className='grid-row', style={'marginTop': '16px'}, children=[
            html.Div(className='glass-card grid-col-2', children=[
                html.H3('Anomaly Score Distribution', className='section-title'),
                dcc.Graph(id='anomaly-scatter-chart', config={'displayModeBar': False}),
            ]),
            html.Div(className='glass-card grid-col-2', children=[
                html.H3('Anomalies by Category', className='section-title'),
                dcc.Graph(id='anomaly-category-chart', config={'displayModeBar': False}),
            ]),
        ]),

        html.Div(className='glass-card', children=[
            html.H3('Anomaly Time Series', className='section-title'),
            dcc.Graph(id='anomaly-timeline-chart', config={'displayModeBar': False}),
        ]),
    ])


def create_reconciliation_page():
    """Reconciliation page layout."""
    return html.Div([
        html.Div(className='page-header', children=[
            html.H1('Reconciliation', className='page-title'),
            html.P('Transaction-to-ledger matching results and discrepancy analysis', className='page-subtitle'),
        ]),

        # Reconciliation KPIs
        html.Div(className='grid-row', children=[
            create_kpi_card('recon-match-rate', 'Match Rate', 'green'),
            create_kpi_card('recon-matched', 'Matched Records', 'blue'),
            create_kpi_card('recon-unmatched', 'Unmatched', 'amber'),
            create_kpi_card('recon-amount-mismatch', 'Amount Mismatches', 'red'),
        ]),

        # Reconciliation Charts
        html.Div(className='grid-row', style={'marginTop': '16px'}, children=[
            html.Div(className='glass-card grid-col-2', children=[
                html.H3('Reconciliation Waterfall', className='section-title'),
                dcc.Graph(id='recon-waterfall-chart', config={'displayModeBar': False}),
            ]),
            html.Div(className='glass-card grid-col-2', children=[
                html.H3('Match Status Breakdown', className='section-title'),
                dcc.Graph(id='recon-status-chart', config={'displayModeBar': False}),
            ]),
        ]),

        html.Div(className='glass-card', children=[
            html.H3('Discrepancy Trend', className='section-title'),
            dcc.Graph(id='recon-trend-chart', config={'displayModeBar': False}),
        ]),
    ])


def create_layout():
    """Create the full app layout with navigation and page content."""
    return html.Div([
        dcc.Location(id='url', refresh=False),
        create_nav(),
        html.Div(className='page-container', children=[
            create_filter_bar(),
            html.Div(id='page-content'),
        ]),

        # Data stores
        dcc.Store(id='transactions-store'),
        dcc.Store(id='quality-store'),
        dcc.Store(id='anomaly-store'),
        dcc.Store(id='reconciliation-store'),
        dcc.Store(id='benchmarks-store'),
    ])
