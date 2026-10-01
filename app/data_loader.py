import pandas as pd
import streamlit as st
import os

@st.cache_resource
def load_data():
    """
    Loads all required CSV datasets into pandas DataFrames.
    Uses Streamlit caching to prevent reloading data on every interaction.
    """
    # Dynamically resolve data directory
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    possible_dirs = [
        "data",
        os.path.join(base_dir, "data"),
        os.path.join("Tanu Project", "data"),
        os.path.join(base_dir, "Tanu Project", "data"),
    ]
    
    data_dir = "data"
    for d in possible_dirs:
        if os.path.exists(os.path.join(d, "customers.csv")):
            data_dir = d
            break
    
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
            m_map = {
                1: "January", 2: "February", 3: "March", 4: "April",
                5: "May", 6: "June", 7: "July", 8: "August",
                9: "September", 10: "October", 11: "November", 12: "December"
            }
            years = ts.dt.year.astype(str)
            df_orders["order_month"] = ts.dt.month.map(m_map) + " " + years
            df_orders["order_quarter"] = "Q" + ts.dt.quarter.astype(str) + " " + years
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
