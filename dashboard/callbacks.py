"""
Dashboard Callbacks — Interactive filtering, data loading, chart rendering.
"""

import os, sys
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from dash import Input, Output, State, html, callback_context, no_update

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_manager import execute_query, DB_PATH
from dashboard.layouts import COLORS, PLOT_LAYOUT, create_overview_page, create_quality_page, create_anomalies_page, create_reconciliation_page


def _fmt_number(n, decimals=0):
    """Format large numbers with K/M suffix."""
    if n is None:
        return '—'
    if abs(n) >= 1_000_000:
        return f'${n/1_000_000:,.{decimals}f}M'
    if abs(n) >= 1_000:
        return f'${n/1_000:,.{decimals}f}K'
    return f'${n:,.{decimals}f}'


def _fmt_count(n):
    if n is None:
        return '—'
    return f'{n:,}'


def _fmt_pct(n):
    if n is None:
        return '—'
    return f'{n:.1f}%'


def register_callbacks(app):
    """Register all Dash callbacks."""

    # ─────────────────────────────────────────────────────────
    # Page routing
    # ─────────────────────────────────────────────────────────
    @app.callback(
        Output('page-content', 'children'),
        Input('url', 'pathname'),
    )
    def display_page(pathname):
        if pathname == '/quality':
            return create_quality_page()
        elif pathname == '/anomalies':
            return create_anomalies_page()
        elif pathname == '/reconciliation':
            return create_reconciliation_page()
        return create_overview_page()

    # ─────────────────────────────────────────────────────────
    # Populate category filter
    # ─────────────────────────────────────────────────────────
    @app.callback(
        Output('category-filter', 'options'),
        Input('url', 'pathname'),
    )
    def populate_categories(_):
        try:
            df = execute_query("SELECT DISTINCT category FROM transactions ORDER BY category")
            return [{'label': c, 'value': c} for c in df['category'].tolist()]
        except Exception:
            return []

    # ─────────────────────────────────────────────────────────
    # OVERVIEW PAGE callbacks
    # ─────────────────────────────────────────────────────────
    @app.callback(
        [
            Output('kpi-total-records-value', 'children'),
            Output('kpi-total-volume-value', 'children'),
            Output('kpi-avg-transaction-value', 'children'),
            Output('kpi-completion-rate-value', 'children'),
            Output('kpi-anomaly-rate-value', 'children'),
            Output('kpi-quality-score-value', 'children'),
            Output('kpi-total-records-delta', 'children'),
            Output('kpi-total-volume-delta', 'children'),
            Output('kpi-avg-transaction-delta', 'children'),
            Output('kpi-completion-rate-delta', 'children'),
            Output('kpi-anomaly-rate-delta', 'children'),
            Output('kpi-quality-score-delta', 'children'),
        ],
        [Input('url', 'pathname')],
    )
    def update_overview_kpis(pathname):
        if pathname and pathname != '/':
            return ['—'] * 12
        try:
            tx = execute_query("SELECT COUNT(*) as cnt, SUM(amount) as total, AVG(amount) as avg_amt FROM transactions")
            completed = execute_query("SELECT COUNT(*) as cnt FROM transactions WHERE status='completed'")
            total_count = int(tx['cnt'].iloc[0])
            total_vol = float(tx['total'].iloc[0])
            avg_amt = float(tx['avg_amt'].iloc[0])
            comp_rate = (completed['cnt'].iloc[0] / total_count * 100) if total_count > 0 else 0

            anomaly_count = execute_query("SELECT COUNT(*) as cnt FROM anomaly_log")['cnt'].iloc[0]
            anomaly_rate = (anomaly_count / total_count * 100) if total_count > 0 else 0

            quality = execute_query("SELECT AVG(pass_rate) as avg_rate FROM quality_log")
            q_score = float(quality['avg_rate'].iloc[0]) if pd.notna(quality['avg_rate'].iloc[0]) else 0

            return [
                _fmt_count(total_count), _fmt_number(total_vol, 1), _fmt_number(avg_amt, 0),
                _fmt_pct(comp_rate), _fmt_pct(anomaly_rate), _fmt_pct(q_score),
                f'{total_count:,} processed', 'All currencies → USD', f'Median-imputed',
                f'{completed["cnt"].iloc[0]:,} completed', f'{anomaly_count:,} detected', 'Across all checks',
            ]
        except Exception as e:
            return ['—'] * 12

    @app.callback(
        Output('revenue-trend-chart', 'figure'),
        [Input('url', 'pathname'), Input('category-filter', 'value'), Input('status-filter', 'value')],
    )
    def update_revenue_trend(pathname, categories, statuses):
        if pathname and pathname != '/':
            return go.Figure()
        try:
            query = """
                SELECT strftime('%Y-%m', transaction_date) as month,
                       SUM(CASE WHEN transaction_type='credit' THEN amount ELSE 0 END) as revenue,
                       SUM(CASE WHEN transaction_type='debit' THEN amount ELSE 0 END) as expenses
                FROM transactions WHERE 1=1
            """
            if categories:
                cats = ','.join([f"'{c}'" for c in categories])
                query += f" AND category IN ({cats})"
            if statuses:
                sts = ','.join([f"'{s}'" for s in statuses])
                query += f" AND status IN ({sts})"
            query += " GROUP BY month ORDER BY month"

            df = execute_query(query)
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df['month'], y=df['revenue'], name='Revenue',
                mode='lines', line=dict(color=COLORS['green'], width=2.5),
                fill='tozeroy', fillcolor='rgba(16,185,129,0.08)',
            ))
            fig.add_trace(go.Scatter(
                x=df['month'], y=df['expenses'], name='Expenses',
                mode='lines', line=dict(color=COLORS['red'], width=2.5),
                fill='tozeroy', fillcolor='rgba(239,68,68,0.08)',
            ))
            fig.update_layout(**PLOT_LAYOUT, height=350, showlegend=True,
                            legend=dict(orientation='h', y=1.12, x=0.5, xanchor='center'))
            return fig
        except Exception:
            return go.Figure().update_layout(**PLOT_LAYOUT, height=350)

    @app.callback(
        Output('category-distribution-chart', 'figure'),
        [Input('url', 'pathname'), Input('category-filter', 'value')],
    )
    def update_category_dist(pathname, categories):
        if pathname and pathname != '/':
            return go.Figure()
        try:
            query = "SELECT category, SUM(amount) as total, COUNT(*) as cnt FROM transactions"
            if categories:
                cats = ','.join([f"'{c}'" for c in categories])
                query += f" WHERE category IN ({cats})"
            query += " GROUP BY category ORDER BY total DESC"

            df = execute_query(query)
            colors = [COLORS['blue'], COLORS['green'], COLORS['purple'],
                     COLORS['amber'], COLORS['red'], COLORS['cyan'], '#818cf8']

            fig = go.Figure(go.Bar(
                x=df['total'], y=df['category'], orientation='h',
                marker=dict(color=colors[:len(df)], cornerradius=5),
                text=df['total'].apply(lambda x: _fmt_number(x, 0)),
                textposition='auto', textfont=dict(size=11),
            ))
            fig.update_layout(**PLOT_LAYOUT, height=350, yaxis=dict(autorange='reversed', gridcolor=COLORS['grid']))
            return fig
        except Exception:
            return go.Figure().update_layout(**PLOT_LAYOUT, height=350)

    @app.callback(
        Output('status-pie-chart', 'figure'),
        [Input('url', 'pathname')],
    )
    def update_status_pie(pathname):
        if pathname and pathname != '/':
            return go.Figure()
        try:
            df = execute_query("SELECT status, COUNT(*) as cnt FROM transactions GROUP BY status")
            colors = ['#10b981', '#3b82f6', '#ef4444', '#f59e0b']
            fig = go.Figure(go.Pie(
                labels=df['status'], values=df['cnt'],
                hole=0.55, marker=dict(colors=colors),
                textinfo='label+percent', textfont=dict(size=12),
                hovertemplate='%{label}: %{value:,}<extra></extra>',
            ))
            fig.update_layout(**PLOT_LAYOUT, height=350, showlegend=False)
            return fig
        except Exception:
            return go.Figure().update_layout(**PLOT_LAYOUT, height=350)

    @app.callback(
        Output('top-counterparties-chart', 'figure'),
        [Input('url', 'pathname')],
    )
    def update_top_counterparties(pathname):
        if pathname and pathname != '/':
            return go.Figure()
        try:
            df = execute_query("""
                SELECT counterparty, SUM(amount) as total
                FROM transactions GROUP BY counterparty
                ORDER BY total DESC LIMIT 10
            """)
            fig = go.Figure(go.Bar(
                x=df['total'], y=df['counterparty'], orientation='h',
                marker=dict(
                    color=df['total'],
                    colorscale=[[0, '#3b82f6'], [1, '#8b5cf6']],
                    cornerradius=5,
                ),
                text=df['total'].apply(lambda x: _fmt_number(x, 0)),
                textposition='auto', textfont=dict(size=11),
            ))
            fig.update_layout(**PLOT_LAYOUT, height=350, yaxis=dict(autorange='reversed', gridcolor=COLORS['grid']))
            return fig
        except Exception:
            return go.Figure().update_layout(**PLOT_LAYOUT, height=350)

    # ─────────────────────────────────────────────────────────
    # QUALITY PAGE callbacks
    # ─────────────────────────────────────────────────────────
    @app.callback(
        [
            Output('kpi-quality-overall-value', 'children'),
            Output('kpi-quality-checks-value', 'children'),
            Output('kpi-quality-issues-value', 'children'),
            Output('kpi-quality-critical-value', 'children'),
            Output('kpi-quality-overall-delta', 'children'),
            Output('kpi-quality-checks-delta', 'children'),
            Output('kpi-quality-issues-delta', 'children'),
            Output('kpi-quality-critical-delta', 'children'),
        ],
        [Input('url', 'pathname')],
    )
    def update_quality_kpis(pathname):
        if pathname != '/quality':
            return ['—'] * 8
        try:
            df = execute_query("SELECT * FROM quality_log")
            avg_rate = df['pass_rate'].mean() if not df.empty else 0
            total_checks = len(df)
            total_issues = int(df['failed_records'].sum()) if not df.empty else 0
            critical = len(df[df['severity'] == 'critical']) if not df.empty else 0

            sev = 'Excellent' if avg_rate > 95 else 'Good' if avg_rate > 85 else 'Needs Review'
            return [
                _fmt_pct(avg_rate), str(total_checks), _fmt_count(total_issues), str(critical),
                sev, 'All checks passed', f'Across {total_checks} checks', 'High severity',
            ]
        except Exception:
            return ['—'] * 8

    @app.callback(
        Output('quality-checks-chart', 'figure'),
        [Input('url', 'pathname')],
    )
    def update_quality_chart(pathname):
        if pathname != '/quality':
            return go.Figure()
        try:
            df = execute_query("SELECT check_name, pass_rate, severity FROM quality_log ORDER BY pass_rate ASC")
            color_map = {'low': COLORS['green'], 'medium': COLORS['amber'],
                        'high': '#fb923c', 'critical': COLORS['red']}
            colors = [color_map.get(s, COLORS['blue']) for s in df['severity']]

            fig = go.Figure(go.Bar(
                x=df['pass_rate'], y=df['check_name'], orientation='h',
                marker=dict(color=colors, cornerradius=4),
                text=df['pass_rate'].apply(lambda x: f'{x:.1f}%'),
                textposition='auto', textfont=dict(size=11),
            ))
            fig.add_vline(x=95, line_dash='dash', line_color=COLORS['amber'], annotation_text='95% threshold')
            fig.update_layout(**PLOT_LAYOUT, height=400, yaxis=dict(gridcolor=COLORS['grid']))
            return fig
        except Exception:
            return go.Figure().update_layout(**PLOT_LAYOUT, height=400)

    @app.callback(
        Output('severity-distribution-chart', 'figure'),
        [Input('url', 'pathname')],
    )
    def update_severity_chart(pathname):
        if pathname != '/quality':
            return go.Figure()
        try:
            df = execute_query("SELECT severity, COUNT(*) as cnt, SUM(failed_records) as issues FROM quality_log GROUP BY severity")
            colors = {'low': COLORS['green'], 'medium': COLORS['amber'],
                     'high': '#fb923c', 'critical': COLORS['red']}
            fig = go.Figure(go.Pie(
                labels=df['severity'], values=df['issues'], hole=0.5,
                marker=dict(colors=[colors.get(s, COLORS['blue']) for s in df['severity']]),
                textinfo='label+percent', textfont=dict(size=12),
            ))
            fig.update_layout(**PLOT_LAYOUT, height=400, showlegend=False)
            return fig
        except Exception:
            return go.Figure().update_layout(**PLOT_LAYOUT, height=400)

    @app.callback(
        Output('quality-table-container', 'children'),
        [Input('url', 'pathname')],
    )
    def update_quality_table(pathname):
        if pathname != '/quality':
            return html.Div()
        try:
            df = execute_query("SELECT check_name, check_type, column_name, total_records, failed_records, pass_rate, severity, details FROM quality_log ORDER BY pass_rate ASC")
            from dash import dash_table
            return dash_table.DataTable(
                data=df.to_dict('records'),
                columns=[{'name': c.replace('_', ' ').title(), 'id': c} for c in df.columns],
                style_header={
                    'backgroundColor': 'rgba(22, 27, 45, 0.9)', 'color': '#8b9dc3',
                    'fontWeight': '600', 'fontSize': '0.78rem', 'border': '1px solid rgba(99,110,150,0.15)',
                    'textTransform': 'uppercase', 'letterSpacing': '0.5px',
                },
                style_cell={
                    'backgroundColor': 'rgba(22, 27, 45, 0.4)', 'color': '#e6edf3',
                    'fontSize': '0.82rem', 'border': '1px solid rgba(99,110,150,0.08)',
                    'padding': '10px 14px', 'textAlign': 'left', 'maxWidth': '200px',
                    'overflow': 'hidden', 'textOverflow': 'ellipsis',
                },
                style_data_conditional=[
                    {'if': {'filter_query': '{severity} = "critical"', 'column_id': 'severity'},
                     'color': '#f87171', 'fontWeight': '600'},
                    {'if': {'filter_query': '{severity} = "high"', 'column_id': 'severity'},
                     'color': '#fb923c', 'fontWeight': '600'},
                    {'if': {'filter_query': '{severity} = "medium"', 'column_id': 'severity'},
                     'color': '#fbbf24'},
                    {'if': {'filter_query': '{pass_rate} < 95', 'column_id': 'pass_rate'},
                     'color': '#f87171'},
                ],
                page_size=15,
                style_table={'borderRadius': '12px', 'overflow': 'hidden'},
            )
        except Exception:
            return html.Div("No quality data available", style={'color': COLORS['text_muted']})

    # ─────────────────────────────────────────────────────────
    # ANOMALY PAGE callbacks
    # ─────────────────────────────────────────────────────────
    @app.callback(
        [
            Output('kpi-anomaly-total-value', 'children'),
            Output('kpi-anomaly-zscore-value', 'children'),
            Output('kpi-anomaly-iqr-value', 'children'),
            Output('kpi-anomaly-category-value', 'children'),
            Output('kpi-anomaly-total-delta', 'children'),
            Output('kpi-anomaly-zscore-delta', 'children'),
            Output('kpi-anomaly-iqr-delta', 'children'),
            Output('kpi-anomaly-category-delta', 'children'),
        ],
        [Input('url', 'pathname')],
    )
    def update_anomaly_kpis(pathname):
        if pathname != '/anomalies':
            return ['—'] * 8
        try:
            df = execute_query("SELECT detection_method, COUNT(*) as cnt FROM anomaly_log GROUP BY detection_method")
            total = int(df['cnt'].sum())
            zscore = int(df[df['detection_method'] == 'z_score']['cnt'].sum()) if 'z_score' in df['detection_method'].values else 0
            iqr = int(df[df['detection_method'] == 'iqr']['cnt'].sum()) if 'iqr' in df['detection_method'].values else 0
            cat = int(df[df['detection_method'] == 'category_zscore']['cnt'].sum()) if 'category_zscore' in df['detection_method'].values else 0

            return [
                _fmt_count(total), _fmt_count(zscore), _fmt_count(iqr), _fmt_count(cat),
                'All methods combined', 'Threshold: 3.0σ', 'Multiplier: 1.5×IQR', 'Per-category analysis',
            ]
        except Exception:
            return ['—'] * 8

    @app.callback(
        Output('anomaly-scatter-chart', 'figure'),
        [Input('url', 'pathname')],
    )
    def update_anomaly_scatter(pathname):
        if pathname != '/anomalies':
            return go.Figure()
        try:
            df = execute_query("SELECT anomaly_score, actual_value, detection_method, category FROM anomaly_log")
            color_map = {'z_score': COLORS['purple'], 'iqr': COLORS['amber'], 'category_zscore': COLORS['blue']}

            fig = go.Figure()
            for method in df['detection_method'].unique():
                mdf = df[df['detection_method'] == method]
                fig.add_trace(go.Scatter(
                    x=mdf['anomaly_score'], y=mdf['actual_value'],
                    mode='markers', name=method.replace('_', ' ').title(),
                    marker=dict(size=6, color=color_map.get(method, COLORS['red']), opacity=0.7),
                    hovertemplate='Score: %{x:.2f}<br>Value: $%{y:,.0f}<extra></extra>',
                ))
            fig.update_layout(**PLOT_LAYOUT, height=380,
                            xaxis_title='Anomaly Score', yaxis_title='Transaction Amount',
                            legend=dict(orientation='h', y=1.12, x=0.5, xanchor='center'))
            return fig
        except Exception:
            return go.Figure().update_layout(**PLOT_LAYOUT, height=380)

    @app.callback(
        Output('anomaly-category-chart', 'figure'),
        [Input('url', 'pathname')],
    )
    def update_anomaly_by_cat(pathname):
        if pathname != '/anomalies':
            return go.Figure()
        try:
            df = execute_query("SELECT category, detection_method, COUNT(*) as cnt FROM anomaly_log GROUP BY category, detection_method")
            fig = px.bar(df, x='category', y='cnt', color='detection_method',
                        barmode='group', color_discrete_map={
                            'z_score': COLORS['purple'], 'iqr': COLORS['amber'], 'category_zscore': COLORS['blue']
                        })
            fig.update_layout(**PLOT_LAYOUT, height=380, xaxis_title='', yaxis_title='Count',
                            legend=dict(orientation='h', y=1.12, x=0.5, xanchor='center'))
            fig.update_traces(marker_cornerradius=5)
            return fig
        except Exception:
            return go.Figure().update_layout(**PLOT_LAYOUT, height=380)

    @app.callback(
        Output('anomaly-timeline-chart', 'figure'),
        [Input('url', 'pathname')],
    )
    def update_anomaly_timeline(pathname):
        if pathname != '/anomalies':
            return go.Figure()
        try:
            df = execute_query("""
                SELECT a.*, t.transaction_date
                FROM anomaly_log a
                LEFT JOIN transactions t ON a.transaction_id = t.transaction_id
                WHERE t.transaction_date IS NOT NULL
            """)
            df['transaction_date'] = pd.to_datetime(df['transaction_date'])
            monthly = df.groupby(df['transaction_date'].dt.to_period('M')).size().reset_index(name='count')
            monthly['month'] = monthly['transaction_date'].astype(str)

            fig = go.Figure(go.Scatter(
                x=monthly['month'], y=monthly['count'], mode='lines+markers',
                line=dict(color=COLORS['red'], width=2.5),
                marker=dict(size=5, color=COLORS['red']),
                fill='tozeroy', fillcolor='rgba(239,68,68,0.06)',
                hovertemplate='%{x}<br>Anomalies: %{y}<extra></extra>',
            ))
            fig.update_layout(**PLOT_LAYOUT, height=300, xaxis_title='Month', yaxis_title='Anomaly Count')
            return fig
        except Exception:
            return go.Figure().update_layout(**PLOT_LAYOUT, height=300)

    # ─────────────────────────────────────────────────────────
    # RECONCILIATION PAGE callbacks
    # ─────────────────────────────────────────────────────────
    @app.callback(
        [
            Output('kpi-recon-match-rate-value', 'children'),
            Output('kpi-recon-matched-value', 'children'),
            Output('kpi-recon-unmatched-value', 'children'),
            Output('kpi-recon-amount-mismatch-value', 'children'),
            Output('kpi-recon-match-rate-delta', 'children'),
            Output('kpi-recon-matched-delta', 'children'),
            Output('kpi-recon-unmatched-delta', 'children'),
            Output('kpi-recon-amount-mismatch-delta', 'children'),
        ],
        [Input('url', 'pathname')],
    )
    def update_recon_kpis(pathname):
        if pathname != '/reconciliation':
            return ['—'] * 8
        try:
            txn_count = execute_query("SELECT COUNT(*) as cnt FROM transactions WHERE status='completed'")['cnt'].iloc[0]
            led_count = execute_query("SELECT COUNT(*) as cnt FROM ledger_entries")['cnt'].iloc[0]
            matched = execute_query("""
                SELECT COUNT(*) as cnt FROM transactions t
                INNER JOIN ledger_entries l ON t.transaction_id = l.transaction_id
                WHERE t.status='completed'
            """)['cnt'].iloc[0]

            # Amount mismatches
            mismatches = execute_query("""
                SELECT COUNT(*) as cnt FROM transactions t
                INNER JOIN ledger_entries l ON t.transaction_id = l.transaction_id
                WHERE t.status='completed'
                AND ABS(t.amount - CASE WHEN l.debit_amount > 0 THEN l.debit_amount ELSE l.credit_amount END) > 0.01
            """)['cnt'].iloc[0]

            unmatched = txn_count - matched
            rate = (matched / txn_count * 100) if txn_count > 0 else 0

            return [
                _fmt_pct(rate), _fmt_count(matched), _fmt_count(unmatched), _fmt_count(mismatches),
                'Completed txns only', f'of {txn_count:,} transactions', 'No ledger entry found', 'Amount differs >$0.01',
            ]
        except Exception:
            return ['—'] * 8

    @app.callback(
        Output('recon-waterfall-chart', 'figure'),
        [Input('url', 'pathname')],
    )
    def update_recon_waterfall(pathname):
        if pathname != '/reconciliation':
            return go.Figure()
        try:
            txn_count = int(execute_query("SELECT COUNT(*) as cnt FROM transactions WHERE status='completed'")['cnt'].iloc[0])
            matched = int(execute_query("""
                SELECT COUNT(*) as cnt FROM transactions t
                INNER JOIN ledger_entries l ON t.transaction_id = l.transaction_id
                WHERE t.status='completed'
            """)['cnt'].iloc[0])
            mismatches = int(execute_query("""
                SELECT COUNT(*) as cnt FROM transactions t
                INNER JOIN ledger_entries l ON t.transaction_id = l.transaction_id
                WHERE t.status='completed'
                AND ABS(t.amount - CASE WHEN l.debit_amount > 0 THEN l.debit_amount ELSE l.credit_amount END) > 0.01
            """)['cnt'].iloc[0])
            perfect = matched - mismatches
            unmatched = txn_count - matched

            fig = go.Figure(go.Waterfall(
                x=['Total Txns', 'Perfect Match', 'Amount Mismatch', 'Unmatched'],
                y=[txn_count, -perfect, -mismatches, -unmatched],
                measure=['absolute', 'relative', 'relative', 'relative'],
                connector=dict(line=dict(color=COLORS['text_muted'], width=1, dash='dot')),
                decreasing=dict(marker=dict(color=COLORS['green'])),
                increasing=dict(marker=dict(color=COLORS['red'])),
                totals=dict(marker=dict(color=COLORS['blue'])),
                text=[f'{txn_count:,}', f'{perfect:,}', f'{mismatches:,}', f'{unmatched:,}'],
                textposition='auto',
            ))
            fig.update_layout(**PLOT_LAYOUT, height=380, showlegend=False)
            return fig
        except Exception:
            return go.Figure().update_layout(**PLOT_LAYOUT, height=380)

    @app.callback(
        Output('recon-status-chart', 'figure'),
        [Input('url', 'pathname')],
    )
    def update_recon_status(pathname):
        if pathname != '/reconciliation':
            return go.Figure()
        try:
            txn_count = int(execute_query("SELECT COUNT(*) as cnt FROM transactions WHERE status='completed'")['cnt'].iloc[0])
            matched = int(execute_query("""
                SELECT COUNT(*) as cnt FROM transactions t
                INNER JOIN ledger_entries l ON t.transaction_id = l.transaction_id
                WHERE t.status='completed'
            """)['cnt'].iloc[0])
            mismatches = int(execute_query("""
                SELECT COUNT(*) as cnt FROM transactions t
                INNER JOIN ledger_entries l ON t.transaction_id = l.transaction_id
                WHERE t.status='completed'
                AND ABS(t.amount - CASE WHEN l.debit_amount > 0 THEN l.debit_amount ELSE l.credit_amount END) > 0.01
            """)['cnt'].iloc[0])

            labels = ['Perfect Match', 'Amount Mismatch', 'Unmatched']
            values = [matched - mismatches, mismatches, txn_count - matched]
            colors = [COLORS['green'], COLORS['amber'], COLORS['red']]

            fig = go.Figure(go.Pie(
                labels=labels, values=values, hole=0.55,
                marker=dict(colors=colors),
                textinfo='label+percent', textfont=dict(size=12),
            ))
            fig.update_layout(**PLOT_LAYOUT, height=380, showlegend=False)
            return fig
        except Exception:
            return go.Figure().update_layout(**PLOT_LAYOUT, height=380)

    @app.callback(
        Output('recon-trend-chart', 'figure'),
        [Input('url', 'pathname')],
    )
    def update_recon_trend(pathname):
        if pathname != '/reconciliation':
            return go.Figure()
        try:
            df = execute_query("""
                SELECT strftime('%Y-%m', t.transaction_date) as month,
                       COUNT(*) as total,
                       SUM(CASE WHEN ABS(t.amount - CASE WHEN l.debit_amount > 0 THEN l.debit_amount ELSE l.credit_amount END) > 0.01 THEN 1 ELSE 0 END) as mismatches
                FROM transactions t
                INNER JOIN ledger_entries l ON t.transaction_id = l.transaction_id
                WHERE t.status='completed' AND t.transaction_date IS NOT NULL
                GROUP BY month ORDER BY month
            """)
            df['mismatch_rate'] = (df['mismatches'] / df['total'] * 100).round(2)

            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=df['month'], y=df['total'], name='Total Matched',
                marker=dict(color=COLORS['blue'], opacity=0.4, cornerradius=3),
            ))
            fig.add_trace(go.Scatter(
                x=df['month'], y=df['mismatch_rate'], name='Mismatch Rate %',
                mode='lines+markers', yaxis='y2',
                line=dict(color=COLORS['red'], width=2.5),
                marker=dict(size=5),
            ))
            fig.update_layout(
                **PLOT_LAYOUT, height=300,
                yaxis=dict(title='Matched Records', gridcolor=COLORS['grid']),
                yaxis2=dict(title='Mismatch Rate %', overlaying='y', side='right',
                           gridcolor='rgba(0,0,0,0)'),
                legend=dict(orientation='h', y=1.15, x=0.5, xanchor='center'),
                barmode='overlay',
            )
            return fig
        except Exception:
            return go.Figure().update_layout(**PLOT_LAYOUT, height=300)
