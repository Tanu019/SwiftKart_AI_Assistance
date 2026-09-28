import plotly.graph_objects as go
import streamlit as st

def _is_dark():
    return st.session_state.get("theme", "Dark") == "Dark"

def _apply_theme(fig):
    dark = _is_dark()
    font_color = '#B3B7BA' if dark else '#475569'
    grid_color = 'rgba(211, 209, 206, 0.08)' if dark else 'rgba(0, 0, 0, 0.06)'
    tt_bg = '#121A24' if dark else '#ffffff'
    tt_border = '#2A3848' if dark else '#cbd5e1'
    tt_color = '#D3D1CE' if dark else '#0f172a'
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=font_color, family='Manrope, -apple-system, BlinkMacSystemFont, sans-serif', size=11),
        margin=dict(l=10, r=10, t=10, b=10),
        height=240,
        xaxis=dict(
            showgrid=False, 
            zeroline=False, 
            color=font_color,
            tickfont=dict(size=10, family='Manrope, sans-serif')
        ),
        yaxis=dict(
            showgrid=True, 
            gridcolor=grid_color, 
            zeroline=False, 
            color=font_color,
            tickfont=dict(size=10, family='Manrope, sans-serif')
        ),
        hovermode='x unified',
        hoverlabel=dict(
            bgcolor=tt_bg,
            bordercolor=tt_border,
            font=dict(color=tt_color, family='Manrope, sans-serif', size=12)
        )
    )
    return fig

def plot_revenue_by_city(df):
    if df is None or df.empty:
        return None
    dark = _is_dark()
    bar_color = '#D3D1CE' if dark else '#1e293b'
    fig = go.Figure(go.Bar(
        x=df['city'],
        y=df['revenue'],
        marker=dict(
            color=bar_color,
            line=dict(color='rgba(255,255,255,0)', width=0)
        ),
        hovertemplate='<b>%{x}</b><br>Revenue: ₹%{y:,.0f}<extra></extra>'
    ))
    return _apply_theme(fig)

def plot_orders_trend(df):
    if df is None or df.empty:
        return None
    dark = _is_dark()
    line_color = '#7C83FD' if dark else '#4f46e5'
    fill_color = 'rgba(124, 131, 253, 0.14)' if dark else 'rgba(79, 70, 229, 0.10)'
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['dt'], 
        y=df['orders'],
        mode='lines',
        name='Orders',
        line=dict(color=line_color, width=2.5, shape='spline'),
        fill='tozeroy',
        fillcolor=fill_color,
        hovertemplate='<b>%{x}</b><br>Orders: %{y:,}<extra></extra>'
    ))
    return _apply_theme(fig)

def plot_persona_dist(df):
    if df is None or df.empty:
        return None
    dark = _is_dark()
    palette = ['#D3D1CE', '#7C83FD', '#B3B7BA', '#6C6D74', '#38bdf8'] if dark else ['#1e293b', '#4f46e5', '#3b82f6', '#64748b', '#94a3b8']
    stroke_color = '#090F15' if dark else '#ffffff'
    legend_color = '#B3B7BA' if dark else '#475569'
    
    fig = go.Figure(go.Pie(
        labels=df['persona'],
        values=df['count'],
        hole=0.62,
        marker=dict(
            colors=palette[:len(df)],
            line=dict(color=stroke_color, width=2)
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
            font=dict(size=10, color=legend_color, family='Manrope, sans-serif')
        )
    )
    return _apply_theme(fig)

def plot_delivery_vs_sat(df):
    if df is None or df.empty:
        return None
    dark = _is_dark()
    bar_color = '#7C83FD' if dark else '#3b82f6'
    fig = go.Figure(go.Bar(
        x=df['delivery_bucket'].astype(str) + 'm',
        y=df['avg_sat'],
        marker=dict(color=bar_color),
        hovertemplate='<b>%{x}</b><br>Avg CSAT: %{y:.2f} / 5<extra></extra>'
    ))
    fig.update_layout(yaxis=dict(range=[0, 5]))
    return _apply_theme(fig)

def plot_churn_by_persona(df):
    if df is None or df.empty:
        return None
    dark = _is_dark()
    bar_color = '#B3B7BA' if dark else '#475569'
    fig = go.Figure(go.Bar(
        x=df['persona'],
        y=df['avg_churn'],
        marker=dict(
            color=bar_color,
            line=dict(color='rgba(255,255,255,0)', width=0)
        ),
        hovertemplate='<b>%{x}</b><br>Avg Churn: %{y:.1f}%<extra></extra>'
    ))
    return _apply_theme(fig)

def plot_cat_revenue(df):
    if df is None or df.empty:
        return None
    dark = _is_dark()
    palette = ['#D3D1CE', '#7C83FD', '#B3B7BA', '#6C6D74', '#38BDF8'] if dark else ['#1e293b', '#4f46e5', '#0ea5e9', '#0d9488', '#64748b']
    stroke_color = '#090F15' if dark else '#ffffff'
    legend_color = '#B3B7BA' if dark else '#475569'
    
    fig = go.Figure(go.Pie(
        labels=df['category'],
        values=df['revenue'],
        hole=0.62,
        marker=dict(
            colors=palette[:len(df)],
            line=dict(color=stroke_color, width=2)
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
            font=dict(size=10, color=legend_color, family='Manrope, sans-serif')
        )
    )
    return _apply_theme(fig)
