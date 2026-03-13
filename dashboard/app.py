"""
Plotly Dash Application — Financial Data Analytics Dashboard
Premium dark-theme UI with glassmorphism elements.
"""

import os
import sys
import dash
from dash import html, dcc

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dashboard.layouts import create_layout
from dashboard.callbacks import register_callbacks

# Initialize Dash app
app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True,
    title='Financial Data Analytics Dashboard',
    update_title='Loading...',
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0"}
    ],
)

# Apply custom CSS
app.index_string = '''<!DOCTYPE html>
<html>
<head>
    {%metas%}
    <title>{%title%}</title>
    {%favicon%}
    {%css%}
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: 'Inter', -apple-system, sans-serif;
            background: linear-gradient(135deg, #0a0a1a 0%, #0d1117 50%, #0a0e1a 100%);
            color: #e6edf3;
            min-height: 100vh;
        }

        /* Glassmorphism cards */
        .glass-card {
            background: rgba(22, 27, 45, 0.7);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(99, 110, 150, 0.15);
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 16px;
            transition: all 0.3s ease;
        }
        .glass-card:hover {
            border-color: rgba(99, 110, 150, 0.35);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            transform: translateY(-2px);
        }

        /* KPI Cards */
        .kpi-card {
            background: rgba(22, 27, 45, 0.8);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(99, 110, 150, 0.15);
            border-radius: 14px;
            padding: 20px 24px;
            text-align: center;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        .kpi-card::before {
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 3px;
            border-radius: 14px 14px 0 0;
        }
        .kpi-card.accent-blue::before { background: linear-gradient(90deg, #3b82f6, #60a5fa); }
        .kpi-card.accent-green::before { background: linear-gradient(90deg, #10b981, #34d399); }
        .kpi-card.accent-purple::before { background: linear-gradient(90deg, #8b5cf6, #a78bfa); }
        .kpi-card.accent-amber::before { background: linear-gradient(90deg, #f59e0b, #fbbf24); }
        .kpi-card.accent-red::before { background: linear-gradient(90deg, #ef4444, #f87171); }
        .kpi-card.accent-cyan::before { background: linear-gradient(90deg, #06b6d4, #22d3ee); }

        .kpi-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4);
        }
        .kpi-value {
            font-size: 2rem;
            font-weight: 700;
            margin: 8px 0 4px;
            background: linear-gradient(135deg, #e6edf3, #8b9dc3);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .kpi-label {
            font-size: 0.78rem;
            font-weight: 500;
            color: #8b9dc3;
            text-transform: uppercase;
            letter-spacing: 0.8px;
        }
        .kpi-delta {
            font-size: 0.82rem;
            font-weight: 600;
            margin-top: 4px;
        }
        .kpi-delta.positive { color: #34d399; }
        .kpi-delta.negative { color: #f87171; }

        /* Navigation */
        .nav-container {
            background: rgba(13, 17, 23, 0.95);
            backdrop-filter: blur(16px);
            border-bottom: 1px solid rgba(99, 110, 150, 0.12);
            padding: 0 32px;
            position: sticky;
            top: 0;
            z-index: 1000;
        }
        .nav-inner {
            max-width: 1400px;
            margin: 0 auto;
            display: flex;
            align-items: center;
            height: 64px;
            gap: 40px;
        }
        .nav-brand {
            font-size: 1.15rem;
            font-weight: 700;
            background: linear-gradient(135deg, #3b82f6, #8b5cf6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            white-space: nowrap;
        }
        .nav-links { display: flex; gap: 4px; }
        .nav-link {
            padding: 8px 16px;
            border-radius: 8px;
            font-size: 0.85rem;
            font-weight: 500;
            color: #8b9dc3;
            cursor: pointer;
            transition: all 0.2s ease;
            text-decoration: none;
            border: none;
            background: transparent;
        }
        .nav-link:hover { color: #e6edf3; background: rgba(99, 110, 150, 0.1); }
        .nav-link.active {
            color: #e6edf3;
            background: rgba(59, 130, 246, 0.15);
            border: 1px solid rgba(59, 130, 246, 0.25);
        }

        /* Page container */
        .page-container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 24px 32px;
        }
        .page-header {
            margin-bottom: 24px;
        }
        .page-title {
            font-size: 1.8rem;
            font-weight: 700;
            background: linear-gradient(135deg, #e6edf3, #8b9dc3);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .page-subtitle {
            font-size: 0.9rem;
            color: #8b9dc3;
            margin-top: 4px;
        }

        /* Grid */
        .grid-row { display: flex; gap: 16px; flex-wrap: wrap; }
        .grid-col-2 { flex: 1; min-width: 280px; }
        .grid-col-3 { flex: 1; min-width: 200px; }
        .grid-col-4 { flex: 1; min-width: 160px; }

        /* Table styling */
        .dash-table {
            border-radius: 12px !important;
            overflow: hidden;
        }

        /* Filter bar */
        .filter-bar {
            background: rgba(22, 27, 45, 0.5);
            border: 1px solid rgba(99, 110, 150, 0.12);
            border-radius: 12px;
            padding: 16px 20px;
            margin-bottom: 20px;
            display: flex;
            gap: 16px;
            align-items: flex-end;
            flex-wrap: wrap;
        }
        .filter-group { display: flex; flex-direction: column; gap: 6px; }
        .filter-label {
            font-size: 0.72rem;
            font-weight: 600;
            color: #8b9dc3;
            text-transform: uppercase;
            letter-spacing: 0.8px;
        }

        /* Dropdown styling */
        .Select-control { background: rgba(22, 27, 45, 0.8) !important; border-color: rgba(99,110,150,0.2) !important; color: #e6edf3 !important; }
        .Select-menu-outer { background: #161b2d !important; }
        .Select-option { background: #161b2d !important; color: #e6edf3 !important; }
        .Select-option:hover { background: rgba(59,130,246,0.15) !important; }
        .Select-value-label { color: #e6edf3 !important; }

        /* DatePickerRange */
        .DateInput_input { background: rgba(22,27,45,0.8) !important; color: #e6edf3 !important; border-color: rgba(99,110,150,0.2) !important; font-size: 0.85rem !important; }

        /* Section title */
        .section-title {
            font-size: 1.05rem;
            font-weight: 600;
            color: #e6edf3;
            margin-bottom: 16px;
        }

        /* Status badges */
        .badge {
            display: inline-block;
            padding: 3px 10px;
            border-radius: 6px;
            font-size: 0.72rem;
            font-weight: 600;
            letter-spacing: 0.5px;
        }
        .badge-success { background: rgba(16,185,129,0.15); color: #34d399; }
        .badge-warning { background: rgba(245,158,11,0.15); color: #fbbf24; }
        .badge-danger { background: rgba(239,68,68,0.15); color: #f87171; }

        /* Scrollbar */
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: rgba(99,110,150,0.3); border-radius: 3px; }
        ::-webkit-scrollbar-thumb:hover { background: rgba(99,110,150,0.5); }
    </style>
</head>
<body>
    {%app_entry%}
    <footer>{%config%}{%scripts%}{%renderer%}</footer>
</body>
</html>'''

# Set layout
app.layout = create_layout()

# Register callbacks
register_callbacks(app)


def run_dashboard(debug: bool = False, port: int = 8050):
    """Launch the dashboard server."""
    print(f"\n  🚀 Dashboard running at http://127.0.0.1:{port}")
    print(f"  Press Ctrl+C to stop\n")
    app.run(debug=debug, port=port, host='127.0.0.1')


if __name__ == '__main__':
    run_dashboard(debug=True)
