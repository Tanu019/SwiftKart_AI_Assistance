import plotly.graph_objects as go
import streamlit as st

def _is_dark():
    return st.session_state.get("theme", "Dark") == "Dark"

def _apply_theme(fig):
    dark = _is_dark()
    font_color = '#94A3B8' if dark else '#475569'
    grid_color = 'rgba(255, 255, 255, 0.06)' if dark else 'rgba(15, 23, 42, 0.06)'
    tt_bg = '#0F172A' if dark else '#FFFFFF'
    tt_border = 'rgba(99, 102, 241, 0.4)' if dark else 'rgba(99, 102, 241, 0.3)'
    tt_color = '#F8FAFC' if dark else '#0F172A'
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=font_color, family='Plus Jakarta Sans, Inter, sans-serif', size=11),
        margin=dict(l=12, r=12, t=14, b=12),
        height=250,
        xaxis=dict(
            showgrid=False, 
            zeroline=False, 
            color=font_color,
            tickfont=dict(size=10, family='Plus Jakarta Sans, sans-serif', color=font_color)
        ),
        yaxis=dict(
            showgrid=True, 
            gridcolor=grid_color, 
            zeroline=False, 
            color=font_color,
            tickfont=dict(size=10, family='Plus Jakarta Sans, sans-serif', color=font_color)
        ),
        hovermode='x unified',
        hoverlabel=dict(
            bgcolor=tt_bg,
            bordercolor=tt_border,
            font=dict(color=tt_color, family='Plus Jakarta Sans, sans-serif', size=12)
        )
    )
    return fig

def plot_revenue_by_city(df):
    if df is None or df.empty:
        return None
    dark = _is_dark()
    colors = ['#6366F1', '#818CF8', '#A5B4FC', '#C7D2FE', '#E0E7FF'] if dark else ['#4F46E5', '#6366F1', '#818CF8', '#93C5FD', '#BFDBFE']
    fig = go.Figure(go.Bar(
        x=df['city'],
        y=df['revenue'],
        marker=dict(
            color=colors[:len(df)] if len(df) <= len(colors) else '#6366F1',
            line=dict(color='rgba(255,255,255,0.1)' if dark else 'rgba(0,0,0,0.05)', width=1)
        ),
        hovertemplate='<b>%{x}</b><br>Revenue: ₹%{y:,.0f}<extra></extra>'
    ))
    return _apply_theme(fig)

def plot_orders_trend(df):
    if df is None or df.empty:
        return None
    dark = _is_dark()
    line_color = '#6366F1' if dark else '#4F46E5'
    fill_color = 'rgba(99, 102, 241, 0.22)' if dark else 'rgba(79, 70, 229, 0.12)'
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['dt'], 
        y=df['orders'],
        mode='lines',
        name='Orders',
        line=dict(color=line_color, width=3, shape='spline'),
        fill='tozeroy',
        fillcolor=fill_color,
        hovertemplate='<b>%{x}</b><br>Orders: %{y:,}<extra></extra>'
    ))
    return _apply_theme(fig)

def plot_persona_dist(df):
    if df is None or df.empty:
        return None
    dark = _is_dark()
    palette = ['#6366F1', '#8B5CF6', '#06B6D4', '#10B981', '#F59E0B'] if dark else ['#4F46E5', '#7C3AED', '#0891B2', '#059669', '#D97706']
    stroke_color = '#0B0F19' if dark else '#FFFFFF'
    legend_color = '#94A3B8' if dark else '#475569'
    
    fig = go.Figure(go.Pie(
        labels=df['persona'],
        values=df['count'],
        hole=0.68,
        marker=dict(
            colors=palette[:len(df)],
            line=dict(color=stroke_color, width=2.5)
        ),
        textinfo='percent',
        textposition='inside',
        insidetextfont=dict(color='#FFFFFF', size=11, family='Plus Jakarta Sans, sans-serif'),
        hovertemplate='<b>%{label}</b><br>%{value:,} Customers (%{percent})<extra></extra>'
    ))
    fig.update_layout(
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.28,
            xanchor="center",
            x=0.5,
            font=dict(size=10, color=legend_color, family='Plus Jakarta Sans, sans-serif')
        )
    )
    return _apply_theme(fig)

def plot_delivery_vs_sat(df):
    if df is None or df.empty:
        return None
    dark = _is_dark()
    bar_color = '#06B6D4' if dark else '#0891B2'
    fig = go.Figure(go.Bar(
        x=df['delivery_bucket'].astype(str) + 'm',
        y=df['avg_sat'],
        marker=dict(
            color=bar_color,
            line=dict(color='rgba(255,255,255,0.1)' if dark else 'rgba(0,0,0,0.05)', width=1)
        ),
        hovertemplate='<b>%{x}</b><br>Avg CSAT: %{y:.2f} / 5<extra></extra>'
    ))
    fig.update_layout(yaxis=dict(range=[0, 5]))
    return _apply_theme(fig)

def plot_churn_by_persona(df):
    if df is None or df.empty:
        return None
    dark = _is_dark()
    bar_color = '#F43F5E' if dark else '#E11D48'
    fig = go.Figure(go.Bar(
        x=df['persona'],
        y=df['avg_churn'],
        marker=dict(
            color=bar_color,
            line=dict(color='rgba(255,255,255,0.1)' if dark else 'rgba(0,0,0,0.05)', width=1)
        ),
        hovertemplate='<b>%{x}</b><br>Avg Churn: %{y:.1f}%<extra></extra>'
    ))
    return _apply_theme(fig)

def plot_cat_revenue(df):
    if df is None or df.empty:
        return None
    dark = _is_dark()
    palette = ['#8B5CF6', '#6366F1', '#06B6D4', '#3B82F6', '#10B981'] if dark else ['#7C3AED', '#4F46E5', '#0891B2', '#2563EB', '#059669']
    stroke_color = '#0B0F19' if dark else '#FFFFFF'
    legend_color = '#94A3B8' if dark else '#475569'
    
    fig = go.Figure(go.Pie(
        labels=df['category'],
        values=df['revenue'],
        hole=0.68,
        marker=dict(
            colors=palette[:len(df)],
            line=dict(color=stroke_color, width=2.5)
        ),
        textinfo='percent',
        textposition='inside',
        insidetextfont=dict(color='#FFFFFF', size=11, family='Plus Jakarta Sans, sans-serif'),
        hovertemplate='<b>%{label}</b><br>Revenue: ₹%{value:,.0f} (%{percent})<extra></extra>'
    ))
    fig.update_layout(
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.28,
            xanchor="center",
            x=0.5,
            font=dict(size=10, color=legend_color, family='Plus Jakarta Sans, sans-serif')
        )
    )
    return _apply_theme(fig)
