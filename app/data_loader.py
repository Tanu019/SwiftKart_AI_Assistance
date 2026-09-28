import pandas as pd
import streamlit as st
import os

@st.cache_resource
def load_data():
    """
    Loads all required CSV datasets into pandas DataFrames.
    Uses Streamlit caching to prevent reloading data on every interaction.
    """
    data_dir = "data"
    
    # Define file paths
    files = {
        "customers": os.path.join(data_dir, "customers.csv"),
        "products": os.path.join(data_dir, "products.csv"),
        "orders": os.path.join(data_dir, "orders.csv"),
        "order_items": os.path.join(data_dir, "order_items.csv")
    }
    
    dataframes = {}
    
    def _read_csv_fast(path):
        try:
            return pd.read_csv(path, engine="pyarrow")
        except Exception:
            return pd.read_csv(path)
            
    try:
        dataframes["customers"] = _read_csv_fast(files["customers"])
    except FileNotFoundError:
        st.warning("customers.csv not found.")
        dataframes["customers"] = pd.DataFrame()
        
    try:
        dataframes["products"] = _read_csv_fast(files["products"])
    except FileNotFoundError:
        st.warning("products.csv not found.")
        dataframes["products"] = pd.DataFrame()
        
    try:
        df_orders = _read_csv_fast(files["orders"])
        if not df_orders.empty and "order_timestamp" in df_orders.columns:
            ts = pd.to_datetime(df_orders["order_timestamp"], errors="coerce")
            df_orders["_dt"] = ts.dt.date
            df_orders["order_month"] = ts.dt.strftime("%B %Y")
            df_orders["order_quarter"] = "Q" + ts.dt.quarter.astype(str) + " " + ts.dt.year.astype(str)
        dataframes["orders"] = df_orders
    except FileNotFoundError:
        st.warning("orders.csv not found.")
        dataframes["orders"] = pd.DataFrame()
        
    try:
        dataframes["order_items"] = _read_csv_fast(files["order_items"])
    except FileNotFoundError:
        st.warning("order_items.csv not found.")
        dataframes["order_items"] = pd.DataFrame()
        
    return dataframes
