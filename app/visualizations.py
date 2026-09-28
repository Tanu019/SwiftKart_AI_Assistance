import plotly.graph_objects as go
import streamlit as st

def _apply_theme(fig):
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#B3B7BA', family='Manrope, -apple-system, BlinkMacSystemFont, sans-serif', size=11),
        margin=dict(l=10, r=10, t=10, b=10),
        height=240,
        xaxis=dict(
            showgrid=False, 
            zeroline=False, 
            color='#B3B7BA',
            tickfont=dict(size=10, family='Manrope, sans-serif')
        ),
        yaxis=dict(
            showgrid=True, 
            gridcolor='rgba(211, 209, 206, 0.08)', 
            zeroline=False, 
            color='#B3B7BA',
            tickfont=dict(size=10, family='Manrope, sans-serif')
        ),
        hovermode='x unified',
        hoverlabel=dict(
            bgcolor='#121A24',
            bordercolor='#2A3848',
            font=dict(color='#D3D1CE', family='Manrope, sans-serif', size=12)
        )
    )
    return fig

def plot_revenue_by_city(df):
    if df is None or df.empty:
        return None
    # Alpine Twilight Primary (#D3D1CE) & Twilight Indigo Accent Bar Chart
    fig = go.Figure(go.Bar(
        x=df['city'],
        y=df['revenue'],
        marker=dict(
            color='#D3D1CE',
            line=dict(color='rgba(255,255,255,0)', width=0)
        ),
        hovertemplate='<b>%{x}</b><br>Revenue: ₹%{y:,.0f}<extra></extra>'
    ))
    return _apply_theme(fig)

def plot_orders_trend(df):
    if df is None or df.empty:
        return None
    # Alpine Twilight Indigo & Silver Spline Area Chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['dt'], 
        y=df['orders'],
        mode='lines',
        name='Orders',
        line=dict(color='#7C83FD', width=2.5, shape='spline'),
        fill='tozeroy',
        fillcolor='rgba(124, 131, 253, 0.12)',
        hovertemplate='<b>%{x}</b><br>Orders: %{y:,}<extra></extra>'
    ))
    return _apply_theme(fig)

def plot_persona_dist(df):
    if df is None or df.empty:
        return None
    # Alpine Twilight Donut with Primary, Secondary, Tertiary & Accent
    palette = ['#D3D1CE', '#7C83FD', '#B3B7BA', '#6C6D74', '#38bdf8']
    fig = go.Figure(go.Pie(
        labels=df['persona'],
        values=df['count'],
        hole=0.62,
        marker=dict(
            colors=palette[:len(df)],
            line=dict(color='#090F15', width=2)
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
            font=dict(size=10, color='#B3B7BA', family='Manrope, sans-serif')
        )
    )
    return _apply_theme(fig)

def plot_delivery_vs_sat(df):
    if df is None or df.empty:
        return None
    fig = go.Figure(go.Bar(
        x=df['delivery_bucket'].astype(str) + 'm',
        y=df['avg_sat'],
        marker=dict(color='#7C83FD'),
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
            color='#B3B7BA',
            line=dict(color='rgba(255,255,255,0)', width=0)
        ),
        hovertemplate='<b>%{x}</b><br>Avg Churn: %{y:.1f}%<extra></extra>'
    ))
    return _apply_theme(fig)

def plot_cat_revenue(df):
    if df is None or df.empty:
        return None
    palette = ['#D3D1CE', '#7C83FD', '#B3B7BA', '#6C6D74', '#38BDF8']
    fig = go.Figure(go.Pie(
        labels=df['category'],
        values=df['revenue'],
        hole=0.62,
        marker=dict(
            colors=palette[:len(df)],
            line=dict(color='#090F15', width=2)
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
            font=dict(size=10, color='#B3B7BA', family='Manrope, sans-serif')
        )
    )
    return _apply_theme(fig)
