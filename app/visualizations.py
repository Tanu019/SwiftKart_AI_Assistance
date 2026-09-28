import plotly.graph_objects as go
import streamlit as st

def _apply_theme(fig):
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#64748b', family='Inter, -apple-system, BlinkMacSystemFont, sans-serif', size=11),
        margin=dict(l=10, r=10, t=10, b=10),
        height=240,
        xaxis=dict(
            showgrid=False, 
            zeroline=False, 
            color='#94a3b8',
            tickfont=dict(size=10)
        ),
        yaxis=dict(
            showgrid=True, 
            gridcolor='rgba(226, 232, 240, 0.6)', 
            zeroline=False, 
            color='#94a3b8',
            tickfont=dict(size=10)
        ),
        hovermode='x unified',
        hoverlabel=dict(
            bgcolor='#ffffff',
            bordercolor='#e2e8f0',
            font=dict(color='#0f172a', family='Inter, sans-serif', size=12)
        )
    )
    return fig

def plot_revenue_by_city(df):
    if df is None or df.empty:
        return None
    # Sleek corporate steel-blue bar chart matching Image 2
    fig = go.Figure(go.Bar(
        x=df['city'],
        y=df['revenue'],
        marker=dict(
            color='#2b5c7a',
            line=dict(color='rgba(255,255,255,0)', width=0)
        ),
        hovertemplate='<b>%{x}</b><br>Revenue: ₹%{y:,.0f}<extra></extra>'
    ))
    return _apply_theme(fig)

def plot_orders_trend(df):
    if df is None or df.empty:
        return None
    # Sleek modern spline area chart matching Image 2 Pageviews / Sessions
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['dt'], 
        y=df['orders'],
        mode='lines',
        name='Orders',
        line=dict(color='#2b5c7a', width=2.5, shape='spline'),
        fill='tozeroy',
        fillcolor='rgba(43, 92, 122, 0.12)',
        hovertemplate='<b>%{x}</b><br>Orders: %{y:,}<extra></extra>'
    ))
    return _apply_theme(fig)

def plot_persona_dist(df):
    if df is None or df.empty:
        return None
    # Modern donut chart with slate/corporate palette
    palette = ['#2b5c7a', '#3b82f6', '#60a5fa', '#93c5fd', '#cbd5e1']
    fig = go.Figure(go.Pie(
        labels=df['persona'],
        values=df['count'],
        hole=0.62,
        marker=dict(
            colors=palette[:len(df)],
            line=dict(color='#ffffff', width=2.5)
        ),
        textinfo='percent',
        textposition='inside',
        hovertemplate='<b>%{label}</b><br>%{value:,} Customers (%{percent})<extra></extra>'
    ))
    fig.update_layout(
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.25,
            xanchor="center",
            x=0.5,
            font=dict(size=10, color='#64748b')
        )
    )
    return _apply_theme(fig)

def plot_delivery_vs_sat(df):
    if df is None or df.empty:
        return None
    fig = go.Figure(go.Bar(
        x=df['delivery_bucket'].astype(str) + 'm',
        y=df['avg_sat'],
        marker=dict(color='#3b82f6'),
        hovertemplate='<b>%{x}</b><br>Avg CSAT: %{y:.2f} / 5<extra></extra>'
    ))
    fig.update_layout(yaxis=dict(range=[0, 5]))
    return _apply_theme(fig)

def plot_churn_by_persona(df):
    if df is None or df.empty:
        return None
    fig = go.Figure(go.Bar(
        x=df['persona'],
        y=df['avg_churn'],
        marker=dict(
            color='#334155',
            line=dict(color='rgba(255,255,255,0)', width=0)
        ),
        hovertemplate='<b>%{x}</b><br>Avg Churn: %{y:.1f}%<extra></extra>'
    ))
    return _apply_theme(fig)

def plot_cat_revenue(df):
    if df is None or df.empty:
        return None
    palette = ['#2b5c7a', '#3b82f6', '#0ea5e9', '#06b6d4', '#94a3b8']
    fig = go.Figure(go.Pie(
        labels=df['category'],
        values=df['revenue'],
        hole=0.62,
        marker=dict(
            colors=palette[:len(df)],
            line=dict(color='#ffffff', width=2.5)
        ),
        textinfo='percent',
        textposition='inside',
        hovertemplate='<b>%{label}</b><br>Revenue: ₹%{value:,.0f} (%{percent})<extra></extra>'
    ))
    fig.update_layout(
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.25,
            xanchor="center",
            x=0.5,
            font=dict(size=10, color='#64748b')
        )
    )
    return _apply_theme(fig)
