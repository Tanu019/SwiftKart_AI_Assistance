import pandas as pd
import duckdb

def get_kpis(dataframes):
    kpis = {
        "total_revenue": 0.0,
        "total_orders": 0,
        "active_customers": 0,
        "avg_order_value": 0.0,
        "repeat_purchase_rate": 0.0,
        "churn_risk_avg": 0.0,
        "customer_satisfaction": 0.0
    }
    
    orders = dataframes.get("orders")
    customers = dataframes.get("customers")
    
    if orders is not None and not orders.empty:
        kpis["total_orders"] = len(orders)
        
        if 'basket_value' in orders.columns:
            kpis["total_revenue"] = float(orders['basket_value'].sum())
            
        if kpis["total_orders"] > 0:
            kpis["avg_order_value"] = kpis["total_revenue"] / kpis["total_orders"]
            
        if 'repeat_purchase_30d' in orders.columns and kpis["total_orders"] > 0:
            repeat_orders = orders['repeat_purchase_30d'].sum()
            kpis["repeat_purchase_rate"] = float((repeat_orders / kpis["total_orders"]) * 100)
            
        if 'customer_satisfaction_score' in orders.columns and kpis["total_orders"] > 0:
            kpis["customer_satisfaction"] = float(orders['customer_satisfaction_score'].mean())
            
    if customers is not None and not customers.empty:
        kpis["active_customers"] = len(customers)
        if 'churn_risk_profile' in customers.columns:
            # churn_risk_profile is 1.0 - 10.0 score; convert mean to 0-100% risk percentage
            mean_score = pd.to_numeric(customers['churn_risk_profile'], errors='coerce').mean()
            kpis["churn_risk_avg"] = float(mean_score * 10) if pd.notnull(mean_score) else 0.0

    return kpis

def format_currency(value):
    if value >= 1_000_000_000:
        return f"₹{value / 1_000_000_000:.1f}B"
    elif value >= 1_000_000:
        return f"₹{value / 1_000_000:.2f}M"
    elif value >= 100_000:
        return f"₹{value / 1_000:.1f}K"
    return f"₹{value:,.2f}"

def format_number(value):
    if isinstance(value, float):
        return f"{value:,.1f}"
    if value >= 1_000_000_000:
        return f"{value / 1_000_000_000:.1f}B"
    elif value >= 1_000_000:
        return f"{value / 1_000_000:.2f}M"
    elif value >= 100_000:
        return f"{value / 1_000:.1f}K"
    return f"{value:,}"

def apply_global_filters(dataframes, filters):
    """
    Applies filters (like City, Persona, etc.) to the raw DataFrames using Pandas.
    Returns a new dict of filtered DataFrames.
    """
    filtered = {}
    for name, df in dataframes.items():
        if df.empty:
            filtered[name] = df
            continue
            
        f_df = df.copy()
        
        # Apply City filter (assuming orders and customers have 'city')
        if filters.get("city") and "city" in f_df.columns:
            if filters["city"] != "All":
                f_df = f_df[f_df["city"] == filters["city"]]
                
        # Apply Persona filter (only on customers for now, or join if needed)
        if filters.get("persona") and "persona" in f_df.columns:
            if filters["persona"] != "All":
                f_df = f_df[f_df["persona"] == filters["persona"]]
                
        # Apply Time filter (Specific Month or Quarter or Total)
        if name == "orders" and "order_timestamp" in f_df.columns:
            time_filter_type = filters.get("time_filter_type", "Total")
            temp_dt = pd.to_datetime(f_df["order_timestamp"], errors="coerce")
            
            if time_filter_type == "Month" and filters.get("selected_month"):
                month_val = filters["selected_month"]
                if month_val != "All Months":
                    month_str = temp_dt.dt.strftime("%B %Y")
                    f_df = f_df[month_str == month_val]
            elif time_filter_type == "Quarter" and filters.get("selected_quarter"):
                q_val = filters["selected_quarter"]
                if q_val != "All Quarters":
                    q_str = "Q" + temp_dt.dt.quarter.astype(str) + " " + temp_dt.dt.year.astype(str)
                    f_df = f_df[q_str == q_val]
                
        filtered[name] = f_df
        
    # Also sync order_items if orders are filtered
    if "orders" in filtered and "order_items" in filtered and not filtered["orders"].empty:
        valid_order_ids = set(filtered["orders"]["order_id"])
        filtered["order_items"] = filtered["order_items"][filtered["order_items"]["order_id"].isin(valid_order_ids)]
        
    return filtered

def generate_management_briefing(dataframes, role="Business Head"):
    briefing = {
        "needs_attention": "No critical alerts found.",
        "watch": "Keep an eye on generic trends.",
        "positive": "Overall operations are stable.",
        "priority": "Continue executing on current plan."
    }
    con = duckdb.connect(database=':memory:')
    for name, df in dataframes.items():
        con.register(name, df)
    try:
        if "customers" in dataframes and "orders" in dataframes:
            try:
                high_churn = con.execute("SELECT city, COUNT(*) as c FROM customers WHERE CAST(churn_risk_profile AS DOUBLE) >= 7.0 GROUP BY city ORDER BY c DESC LIMIT 1").fetchone()
                if high_churn: briefing["needs_attention"] = f"Customer churn risk is elevated in {high_churn[0]} ({high_churn[1]:,} high-risk customers)."
            except: pass
            
            try:
                low_rep = con.execute("SELECT city, AVG(repeat_purchase_30d) as r FROM orders GROUP BY city ORDER BY r ASC LIMIT 1").fetchone()
                if low_rep: briefing["watch"] = f"Repeat purchase rates are underperforming in {low_rep[0]}."
            except: pass
            
            try:
                hi_aov = con.execute("SELECT city, AVG(basket_value) as a FROM orders GROUP BY city ORDER BY a DESC LIMIT 1").fetchone()
                if hi_aov: briefing["positive"] = f"Average order value is strong in {hi_aov[0]} at {format_currency(hi_aov[1])}."
            except: pass
    except: pass
    return briefing

def generate_management_report(dataframes):
    kpis = get_kpis(dataframes)
    report = f"""## Executive Summary
SwiftKart AI Management Report. Active customers: {format_number(kpis['active_customers'])}.

## KPI Overview
- **Total Revenue**: {format_currency(kpis['total_revenue'])}
- **Total Orders**: {format_number(kpis['total_orders'])}
- **Average Order Value**: {format_currency(kpis['avg_order_value'])}
- **Repeat Purchase Rate**: {format_number(kpis['repeat_purchase_rate'])}%
- **Avg Churn Risk**: {format_number(kpis['churn_risk_avg'])}%
"""
    return report

def get_dashboard_queries(dataframes, section):
    """
    Runs rapid DuckDB aggregations for various dashboard charts.
    """
    con = duckdb.connect(database=':memory:')
    for name, df in dataframes.items():
        con.register(name, df)
        
    results = {}
    try:
        if section == "executive":
            if "orders" in dataframes:
                try:
                    results["revenue_by_city"] = con.execute("SELECT city, SUM(basket_value) as revenue FROM orders GROUP BY city ORDER BY revenue DESC").df()
                except: pass
                
                try:
                    results["orders_trend"] = con.execute("SELECT CAST(order_timestamp AS DATE) as dt, COUNT(order_id) as orders, SUM(basket_value) as revenue FROM orders GROUP BY CAST(order_timestamp AS DATE) ORDER BY dt").df()
                except: pass
                
                try:
                    results["delivery_vs_sat"] = con.execute("SELECT ROUND(delivery_time_minutes / 10) * 10 as delivery_bucket, AVG(customer_satisfaction_score) as avg_sat FROM orders GROUP BY delivery_bucket ORDER BY delivery_bucket").df()
                except: pass
                
            if "customers" in dataframes:
                try:
                    results["persona_dist"] = con.execute("SELECT persona, COUNT(*) as count FROM customers GROUP BY persona ORDER BY count DESC").df()
                except: pass
                
            if "customers" in dataframes:
                try:
                    results["churn_by_persona"] = con.execute("SELECT persona, AVG(CAST(churn_risk_profile AS DOUBLE)) * 10 as avg_churn FROM customers GROUP BY persona ORDER BY avg_churn DESC").df()
                except: pass
                
            if "products" in dataframes and "order_items" in dataframes:
                try:
                    results["cat_revenue"] = con.execute("SELECT p.category, SUM(oi.final_price) as revenue FROM products p JOIN order_items oi ON p.product_id = oi.product_id GROUP BY p.category ORDER BY revenue DESC").df()
                except: pass
                
    except Exception as e:
        print(f"DuckDB error in get_dashboard_queries: {e}")
        
    return results
