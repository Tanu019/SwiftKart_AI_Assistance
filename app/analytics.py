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
    city = filters.get("city", "All")
    persona = filters.get("persona", "All")
    time_filter_type = filters.get("time_filter_type", "Total")
    
    # Fast bypass when no filters are active
    if city in ("All", None) and persona in ("All", None) and time_filter_type == "Total":
        return dataframes

    filtered = {}
    for name, df in dataframes.items():
        if df.empty:
            filtered[name] = df
            continue
            
        f_df = df
        
        # Apply City filter
        if filters.get("city") and "city" in f_df.columns:
            if filters["city"] != "All":
                f_df = f_df[f_df["city"] == filters["city"]]
                
        # Apply Persona filter
        if filters.get("persona") and "persona" in f_df.columns:
            if filters["persona"] != "All":
                f_df = f_df[f_df["persona"] == filters["persona"]]
                
        # Apply Time filter (Instant using precomputed columns)
        if name == "orders":
            if time_filter_type == "Month" and filters.get("selected_month") and filters["selected_month"] != "All Months":
                month_val = filters["selected_month"]
                if "order_month" in f_df.columns:
                    f_df = f_df[f_df["order_month"] == month_val]
                elif "order_timestamp" in f_df.columns:
                    f_df = f_df[pd.to_datetime(f_df["order_timestamp"], errors="coerce").dt.strftime("%B %Y") == month_val]
                    
            elif time_filter_type == "Quarter" and filters.get("selected_quarter") and filters["selected_quarter"] != "All Quarters":
                q_val = filters["selected_quarter"]
                if "order_quarter" in f_df.columns:
                    f_df = f_df[f_df["order_quarter"] == q_val]
                elif "order_timestamp" in f_df.columns:
                    dt = pd.to_datetime(f_df["order_timestamp"], errors="coerce")
                    f_df = f_df[("Q" + dt.dt.quarter.astype(str) + " " + dt.dt.year.astype(str)) == q_val]
                
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
    
    customers = dataframes.get("customers")
    orders = dataframes.get("orders")
    
    try:
        if customers is not None and not customers.empty and "city" in customers.columns and "churn_risk_profile" in customers.columns:
            high_churn_df = customers[pd.to_numeric(customers['churn_risk_profile'], errors='coerce') >= 7.0]
            if not high_churn_df.empty:
                top_churn_city = high_churn_df['city'].value_counts()
                if not top_churn_city.empty:
                    city_name, count = top_churn_city.index[0], top_churn_city.iloc[0]
                    briefing["needs_attention"] = f"Customer churn risk is elevated in {city_name} ({count:,} high-risk customers)."

        if orders is not None and not orders.empty and "city" in orders.columns:
            if "repeat_purchase_30d" in orders.columns:
                rep_by_city = orders.groupby("city")["repeat_purchase_30d"].mean().sort_values()
                if not rep_by_city.empty:
                    briefing["watch"] = f"Repeat purchase rates are underperforming in {rep_by_city.index[0]}."
                    
            if "basket_value" in orders.columns:
                aov_by_city = orders.groupby("city")["basket_value"].mean().sort_values(ascending=False)
                if not aov_by_city.empty:
                    briefing["positive"] = f"Average order value is strong in {aov_by_city.index[0]} at {format_currency(aov_by_city.iloc[0])}."
    except Exception:
        pass
        
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

def get_dashboard_queries(dataframes, section="executive"):
    """
    Runs ultra-fast in-memory vectorized aggregations for all dashboard charts.
    Formats data with clean categories and chronological sorting.
    """
    results = {}
    orders = dataframes.get("orders")
    customers = dataframes.get("customers")
    products = dataframes.get("products")
    order_items = dataframes.get("order_items")
    
    try:
        if orders is not None and not orders.empty:
            # 1. City Performance (Top 10 cities with revenue, order count, and AOV)
            if "city" in orders.columns and "basket_value" in orders.columns:
                city_agg = (
                    orders.groupby("city", as_index=False)
                    .agg(revenue=("basket_value", "sum"), orders=("order_id", "count"))
                )
                city_agg["aov"] = city_agg["revenue"] / city_agg["orders"].clip(lower=1)
                results["revenue_by_city"] = city_agg.sort_values("revenue", ascending=False).head(10)
                
            # 2. Revenue & Order Trends (Monthly aggregation for clean, readable executive trend)
            if "basket_value" in orders.columns and "order_timestamp" in orders.columns:
                ts = pd.to_datetime(orders["order_timestamp"], errors="coerce")
                
                # Check if filtered to a single month (<= 31 days): if so, group by day
                unique_months = orders["order_month"].dropna().unique() if "order_month" in orders.columns else []
                if len(unique_months) == 1:
                    trend_df = (
                        orders.assign(_day=ts.dt.strftime("%d %b"))
                        .groupby("_day", as_index=False)
                        .agg(orders=("order_id", "count"), revenue=("basket_value", "sum"))
                        .rename(columns={"_day": "dt"})
                    )
                else:
                    # Multi-month or full year: group by Year-Month and display clean 'Jan 2025'
                    trend_df = (
                        orders.assign(_period=ts.dt.to_period("M").astype(str), _label=ts.dt.strftime("%b %Y"))
                        .groupby(["_period", "_label"], as_index=False)
                        .agg(orders=("order_id", "count"), revenue=("basket_value", "sum"))
                        .sort_values("_period")
                        .rename(columns={"_label": "dt"})
                        [["dt", "orders", "revenue"]]
                    )
                results["orders_trend"] = trend_df
                
            # 3. Delivery Delay vs Customer Satisfaction (Clear delivery window buckets)
            if "delivery_time_minutes" in orders.columns and "customer_satisfaction_score" in orders.columns:
                del_mins = orders["delivery_time_minutes"]
                del_windows = pd.cut(
                    del_mins, 
                    bins=[-1, 15, 25, 35, 45, 200], 
                    labels=["Under 15 min", "15-25 min", "25-35 min", "35-45 min", "Over 45 min"]
                )
                sat_df = (
                    orders.assign(delivery_window=del_windows.astype(str))
                    .groupby("delivery_window", as_index=False)
                    .agg(avg_sat=("customer_satisfaction_score", "mean"), orders=("order_id", "count"))
                )
                # Keep fixed logical order
                order_map = {"Under 15 min": 1, "15-25 min": 2, "25-35 min": 3, "35-45 min": 4, "Over 45 min": 5}
                sat_df["_sort"] = sat_df["delivery_window"].map(order_map).fillna(99)
                sat_df = sat_df.sort_values("_sort").drop(columns=["_sort"])
                results["delivery_vs_sat"] = sat_df
                
        # 4. Customer Persona Distribution
        if customers is not None and not customers.empty:
            if "persona" in customers.columns:
                p_counts = customers["persona"].value_counts().reset_index()
                p_counts.columns = ["persona", "count"]
                results["persona_dist"] = p_counts
                
            # 5. Churn Risk by Persona
            if "persona" in customers.columns and "churn_risk_profile" in customers.columns:
                churn_df = (
                    customers.assign(churn_num=pd.to_numeric(customers["churn_risk_profile"], errors="coerce") * 10)
                    .groupby("persona", as_index=False)["churn_num"]
                    .mean()
                    .rename(columns={"churn_num": "avg_churn"})
                    .sort_values("avg_churn", ascending=False)
                )
                churn_df["avg_churn"] = churn_df["avg_churn"].round(1)
                results["churn_by_persona"] = churn_df
                
        # 6. Product Category Revenue
        if products is not None and order_items is not None and not products.empty and not order_items.empty:
            if "product_id" in products.columns and "product_id" in order_items.columns:
                p_map = dict(zip(products["product_id"], products["category"]))
                cat_col = order_items["product_id"].map(p_map)
                cat_rev = (
                    order_items.groupby(cat_col, observed=False)["final_price"]
                    .sum()
                    .reset_index()
                    .rename(columns={"product_id": "category", "final_price": "revenue"})
                    .sort_values("revenue", ascending=False)
                    .head(8)
                )
                results["cat_revenue"] = cat_rev
                
    except Exception as e:
        print(f"Error in get_dashboard_queries: {e}")
        
    return results
