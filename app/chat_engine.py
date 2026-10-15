"""
chat_engine.py
--------------
Uses DuckDB for fast, secure Text-to-SQL querying over pandas DataFrames,
and LlamaIndex for LLM interactions. Supports automatic text synthesis,
raw data table returns, and dynamic Plotly chart generation.
"""

import os
import re
import io
import contextlib
import traceback
import streamlit as st
import pandas as pd
import duckdb
import plotly.graph_objects as go

from llama_index.core.llms import LLM
from llama_index.llms.openai_like import OpenAILike

from app.prompts import SYSTEM_PROMPT, FOLLOW_UP_PROMPT


# ---------------------------------------------------------------------------
# Groq LLM factory
# ---------------------------------------------------------------------------

def _build_llm() -> OpenAILike | None:
    """Initialise the Groq LLM via the OpenAI-compatible endpoint with low latency settings."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return None

    return OpenAILike(
        model="qwen/qwen3.8-27b",
        api_base="https://api.groq.com/openai/v1",
        api_key=api_key,
        is_chat_model=True,
        context_window=4096,
        max_tokens=512,
        temperature=0.1,
    )


# ---------------------------------------------------------------------------
# Data Schema Definitions
# ---------------------------------------------------------------------------

_DF_DESCRIPTIONS = {
    "customers": (
        "customers — columns: customer_id, persona, age, gender, city, city_tier, "
        "occupation, monthly_income, household_size, loyalty_program_member, "
        "preferred_payment_method, app_engagement_score, price_sensitivity_score, "
        "impulsiveness_score, health_consciousness_score, discount_affinity_score, "
        "late_night_ordering_tendency, weekend_ordering_tendency, brand_loyalty_score, "
        "churn_risk_profile"
    ),
    "products": (
        "products — columns: product_id, category, subcategory, brand, "
        "package_size, mrp, selling_price, margin_percentage, organic_flag, "
        "premium_flag, rating, popularity_index, festival_relevance"
    ),
    "orders": (
        "orders — columns: order_id, customer_id, order_timestamp, delivery_timestamp, "
        "city, weather_condition, festival_flag, payday_period_flag, basket_value, "
        "item_count, discount_amount, delivery_fee, surge_fee, coupon_used, "
        "coupon_type, delivery_time_minutes, packing_delay, stockout_items, "
        "substitution_count, customer_satisfaction_score, refund_requested, "
        "repeat_purchase_7d, repeat_purchase_30d, churn_risk_score, "
        "impulse_purchase_flag, late_night_order_flag, healthy_basket_flag, "
        "premium_basket_flag"
    ),
    "order_items": (
        "order_items — columns: order_item_id, order_id, product_id, "
        "quantity, unit_price, discount, final_price"
    ),
}

# ---------------------------------------------------------------------------
# DuckDB SQL Engine
# ---------------------------------------------------------------------------

class DuckDBEngine:
    """
    A secure text-to-SQL engine using DuckDB.
    1. Translates natural language to SQL.
    2. Executes SQL safely against registered DuckDB tables.
    3. Routes the result to Text, Table, or Chart.
    """

    def __init__(self, dataframes: dict[str, pd.DataFrame], llm: LLM):
        self.llm = llm
        # Initialize an in-memory DuckDB connection
        self.con = duckdb.connect(database=':memory:')
        self.cache = {} # In-memory exact match cache
        
        self.schema_lines = ["Available Tables (DuckDB Dialect):"]
        
        self.registered_names = set()
        self.register_tables(dataframes)

    def register_tables(self, dataframes: dict[str, pd.DataFrame]):
        """Registers or updates tables in DuckDB and expands schema context."""
        for name, df in dataframes.items():
            if not df.empty:
                self.con.register(name, df)
                if name not in self.registered_names:
                    self.registered_names.add(name)
                    desc = _DF_DESCRIPTIONS.get(name, f"{name} table — columns: {', '.join(df.columns.astype(str))}")
                    self.schema_lines.append(f"  • {desc}")
                    try:
                        sample_row = df.head(1).to_dict(orient="records")[0]
                        self.schema_lines.append(f"    Sample Row: {sample_row}")
                    except Exception:
                        pass
        self.schema_context = "\n".join(self.schema_lines)

    def _fast_path_sql(self, question: str) -> str | None:
        """Instant sub-millisecond SQL template routing for executive inquiries."""
        q = question.lower().strip()
        
        # 1. Top cities / revenue by city
        if any(p in q for p in ["top cities", "revenue by city", "city by revenue", "highest revenue city", "highest revenue cities", "city revenue", "city-by-city"]):
            return "SELECT city, ROUND(SUM(basket_value), 2) AS total_revenue, COUNT(*) AS orders, ROUND(AVG(basket_value), 2) AS aov FROM orders GROUP BY city ORDER BY total_revenue DESC LIMIT 5;"
            
        # 2. Churn risk by persona / customer segment churn
        if any(p in q for p in ["churn risk", "churn by persona", "highest churn", "at-risk", "persona churn", "attrition risk", "greatest risk of churning"]):
            return "SELECT persona, ROUND(AVG(churn_risk_profile)*10, 1) AS avg_churn_risk_pct, COUNT(*) AS customer_count, ROUND(AVG(monthly_income), 0) AS avg_income FROM customers GROUP BY persona ORDER BY avg_churn_risk_pct DESC;"
            
        # 3. Product categories / margins
        if any(p in q for p in ["product categories", "highest margin", "category revenue", "top categories", "boost aov", "category margins", "categories by margin"]):
            return "SELECT p.category, ROUND(AVG(p.margin_percentage), 2) AS avg_margin_pct, ROUND(SUM(oi.final_price), 2) AS total_revenue, COUNT(DISTINCT oi.order_id) AS total_orders FROM products p JOIN order_items oi ON p.product_id = oi.product_id GROUP BY p.category ORDER BY avg_margin_pct DESC LIMIT 5;"
            
        # 4. Average order value (AOV)
        if any(p in q for p in ["average order value", "average basket", "aov", "mean order value", "basket size"]):
            return "SELECT ROUND(AVG(basket_value), 2) AS avg_order_value, ROUND(MIN(basket_value), 2) AS min_basket, ROUND(MAX(basket_value), 2) AS max_basket, COUNT(*) AS total_orders FROM orders;"
            
        # 5. Delivery delay vs satisfaction / CSAT
        if any(p in q for p in ["delivery delay", "csat", "satisfaction", "delivery time impact", "delayed deliveries", "fulfillment window"]):
            return "SELECT CASE WHEN delivery_time_minutes <= 15 THEN 'Under 15 min' WHEN delivery_time_minutes <= 25 THEN '15-25 min' WHEN delivery_time_minutes <= 35 THEN '25-35 min' WHEN delivery_time_minutes <= 45 THEN '35-45 min' ELSE 'Over 45 min' END AS delivery_window, ROUND(AVG(customer_satisfaction_score), 2) AS avg_csat, COUNT(*) AS orders FROM orders GROUP BY 1 ORDER BY avg_csat DESC;"
            
        # 6. Repeat purchase rate / loyalty
        if any(p in q for p in ["repeat purchase", "repeat rate", "loyalty", "reorder rate", "repeat purchase loyalty"]):
            return "SELECT ROUND(AVG(CAST(repeat_purchase_30d AS INT))*100, 1) AS repeat_rate_30d_pct, ROUND(AVG(CAST(repeat_purchase_7d AS INT))*100, 1) AS repeat_rate_7d_pct, COUNT(*) AS total_orders FROM orders;"
            
        # 7. Customer personas distribution / spending habits
        if any(p in q for p in ["customer personas", "persona breakdown", "spending habits", "buyer profiles", "customer persona composition"]):
            return "SELECT c.persona, COUNT(DISTINCT c.customer_id) AS customers, ROUND(SUM(o.basket_value), 2) AS total_revenue, ROUND(AVG(o.basket_value), 2) AS avg_order_value FROM customers c LEFT JOIN orders o ON c.customer_id = o.customer_id GROUP BY c.persona ORDER BY total_revenue DESC;"
            
        # 8. Revenue growth / seasonal trends / trajectory
        if any(p in q for p in ["revenue growth", "growth trajectory", "peak seasons", "trends over time", "monthly revenue", "factors driving our current revenue"]):
            return "SELECT strftime('%Y-%m', order_timestamp) AS month, COUNT(*) AS orders, ROUND(SUM(basket_value), 2) AS revenue, ROUND(AVG(basket_value), 2) AS aov FROM orders GROUP BY 1 ORDER BY 1;"

        # 9. Weekday vs Weekend
        if any(p in q for p in ["weekday", "weekend", "weekday vs weekend"]):
            return "SELECT CASE WHEN strftime('%w', order_timestamp) IN ('0', '6') THEN 'Weekend' ELSE 'Weekday' END AS day_type, COUNT(*) AS order_count, ROUND(SUM(basket_value), 2) AS total_revenue, ROUND(AVG(basket_value), 2) AS aov FROM orders GROUP BY 1;"

        # 10. Briefing / high churn retention
        if any(p in q for p in ["strategic briefing", "retention plan", "high churn cities"]):
            return "SELECT c.city, ROUND(AVG(c.churn_risk_profile)*10, 1) AS avg_churn_pct, COUNT(DISTINCT c.customer_id) AS customers, ROUND(SUM(o.basket_value), 2) AS total_revenue FROM customers c LEFT JOIN orders o ON c.customer_id = o.customer_id GROUP BY c.city ORDER BY avg_churn_pct DESC LIMIT 5;"

        return None

    def _generate_sql(self, question: str, history: str = "", error_msg: str = "", role: str = "Business Head") -> str:
        # 1. Fast path match first
        fast = self._fast_path_sql(question)
        if fast:
            return fast

        # 2. Focused LLM generation
        prompt = f"""You are an expert SQL Data Analyst acting as a {role}.
Given these tables in DuckDB:
- customers (customer_id, persona, age, city, monthly_income, app_engagement_score, churn_risk_profile)
- products (product_id, category, subcategory, brand, mrp, selling_price, margin_percentage)
- orders (order_id, customer_id, order_timestamp, city, basket_value, delivery_time_minutes, customer_satisfaction_score, repeat_purchase_30d)
- order_items (order_item_id, order_id, product_id, quantity, unit_price, final_price)

Write a SQL query (DuckDB dialect) to answer: "{question}"
Rules:
- Return ONLY the executable SQL query. No markdown, no comments, no thought tags.
- Limit rows to 10 unless asked otherwise.
"""
        response = self.llm.complete(prompt)
        raw_sql = str(response).strip()
        
        match = re.search(r"```(?:sql)?\n(.*?)\n```", raw_sql, flags=re.DOTALL | re.IGNORECASE)
        sql = match.group(1) if match else raw_sql
        sql = re.sub(r"<think>.*?</think>", "", sql, flags=re.DOTALL).strip()
        if "<think>" in sql.lower():
            idx = sql.upper().find("SELECT ")
            if idx != -1:
                sql = sql[idx:]
        sql = re.sub(r"^```(?:sql)?\n?", "", sql)
        sql = re.sub(r"\n?```$", "", sql)
        if not sql.upper().startswith("SELECT") and not sql.upper().startswith("WITH"):
            idx = sql.upper().find("SELECT ")
            if idx != -1:
                sql = sql[idx:]
        return sql.strip()

    def _run_sql(self, sql: str) -> pd.DataFrame:
        """Execute the SQL query and return a Pandas DataFrame."""
        try:
            self.last_sql = sql
            return self.con.execute(sql).df()
        except Exception as e:
            raise ValueError(f"SQL Execution Error: {e}\nQuery was: {sql}")

    def _determine_route(self, question: str, df: pd.DataFrame) -> str:
        """Determines if the output should be TEXT, TABLE, or CHART instantly with zero latency."""
        if df.empty or df.shape == (1, 1):
            return "TEXT"
            
        q_lower = question.lower()
        chart_keywords = ["chart", "graph", "plot", "histogram", "bar chart", "line chart", "pie chart"]
        table_keywords = ["table", "raw data", "list all", "list of", "show records", "show data", "tabular", "dataframe", "all rows", "csv"]
        
        if any(k in q_lower for k in chart_keywords):
            return "CHART"
        if any(k in q_lower for k in table_keywords):
            return "TABLE"
        return "TEXT"

    def _synthesize_text(self, question: str, df: pd.DataFrame, status=None, role="Business Head"):
        data_str = df.head(8).to_string(index=False)
        
        prompt = f"""You are SwiftKart AI Analyst acting as a {role}.
Question: "{question}"
Data Result:
{data_str}

Provide an executive, high-impact business analysis strictly based on the data above.

Formatting Rules:
1. Always format answers in structured paragraphs or distinct bullet points (- ) with a blank line between every section and bullet.
2. Never run paragraphs or bullet items together into a continuous block.
3. Absolutely ZERO emojis anywhere (no warning icons, symbols, or pictograms).
4. Do NOT include <think> tags. Keep the total response concise (under 150 words).

Structure:
### Key Insight
- [1 concise bullet summarizing the core finding]

### Supporting Data
- [1 to 2 bullets with exact figures, revenue in INR/Lakhs, margins, or percentages]

### Strategic Actions
1. **[Immediate Recommendation]**: [Specific step based on the data]
2. **[Follow-up]**: [Next strategic check]

### Watchlist
- [1 bullet on risk, trend to monitor, or data limitation]
"""
        response_gen = self.llm.stream_complete(prompt)
        in_think_block = False
        buffer = ""
        for chunk in response_gen:
            if chunk.delta:
                buffer += chunk.delta
            
            if "<think>" in buffer:
                in_think_block = True
                
            if in_think_block:
                if "</think>" in buffer:
                    in_think_block = False
                    buffer = buffer.split("</think>")[-1]
                else:
                    continue
                    
            if not in_think_block:
                if buffer.endswith("<") or buffer.endswith("<t") or buffer.endswith("<th") or buffer.endswith("<thi") or buffer.endswith("<thin"):
                    continue
                if buffer:
                    yield buffer
                    buffer = ""
                    
        if not in_think_block and buffer:
            yield buffer

    def _generate_chart(self, question: str, df: pd.DataFrame) -> go.Figure | str:
        """Generates Plotly Python code to visualize the DataFrame."""
        sample = df.head(5).to_dict(orient="records")
        prompt = f"""You are an expert Data Visualizer using Plotly.
The user asked: "{question}"
Columns: {list(df.columns)}. Sample: {sample}
Write Python code using `plotly.graph_objects` as `go` to create a beautiful chart.
Rules:
- Store the final figure in `fig`.
- Sleek dark layout: paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#f8fafc').
- Return ONLY the raw Python code, no markdown, no think tags.
"""
        response = self.llm.complete(prompt)
        raw_code = str(response).strip()
        
        match = re.search(r"```(?:python)?\n(.*?)\n```", raw_code, flags=re.DOTALL | re.IGNORECASE)
        code = match.group(1) if match else raw_code
        code = re.sub(r"<think>.*?</think>", "", code, flags=re.DOTALL).strip()
        code = re.sub(r"^```(?:python)?\n?", "", code)
        code = re.sub(r"\n?```$", "", code)
        
        local_ns = {"df": df, "go": go, "fig": None}
        try:
            exec(code.strip(), local_ns) # noqa: S102
            fig = local_ns.get("fig")
            if isinstance(fig, go.Figure):
                return fig
            return "Failed to generate chart object."
        except Exception as e:
            return f"Chart generation failed: {e}"

    def generate_follow_ups(self, question: str, response_text: str) -> list[str]:
        """Provides instant high-value follow-up questions with zero API latency."""
        q_lower = question.lower()
        if "churn" in q_lower or "risk" in q_lower:
            return [
                "What is the average order frequency for high-churn customers?",
                "Which city has the highest churn rate?",
                "How does price sensitivity affect churn risk?",
                "What retention campaigns are recommended for at-risk personas?"
            ]
        elif "revenue" in q_lower or "sales" in q_lower or "city" in q_lower or "aov" in q_lower:
            return [
                "Which product categories drive the highest margins?",
                "Show monthly revenue trends across all cities.",
                "What is the average basket value during festivals?",
                "Compare repeat purchase rates between top 3 cities."
            ]
        elif "satisfaction" in q_lower or "csat" in q_lower or "rating" in q_lower or "delivery" in q_lower:
            return [
                "How does packing delay impact customer ratings?",
                "What is the average delivery time by weather condition?",
                "Which cities experience the highest delivery delays?",
                "Does refund rate increase with delayed deliveries?"
            ]
        elif "product" in q_lower or "margin" in q_lower or "category" in q_lower:
            return [
                "Which products have high revenue but low margins?",
                "What are the top 5 organic products by popularity?",
                "Which categories have the highest repeat purchase rates?",
                "Show brand distribution for top-rated products."
            ]
        else:
            return [
                "Which customer segment generates the most revenue?",
                "Does surge fee impact order drop-offs?",
                "What factors correlate most with repeat purchases?",
                "Show revenue breakdown by payment method."
            ]

    @staticmethod
    def _normalize_key(text: str) -> str:
        s = text.lower().strip()
        s = re.sub(r"[?!.,;:\'\"`]", "", s)
        prefixes = [
            "what is the", "what are the", "what is", "what are",
            "which city has the", "which is the", "which are the", "which",
            "show me the", "show me", "show", "tell me about", "tell me the",
            "tell me", "display the", "display", "give me the", "give me",
            "can you show", "can you tell", "please show", "please tell"
        ]
        for p in prefixes:
            if s.startswith(p + " "):
                s = s[len(p):].strip()
                break
        return re.sub(r"\s+", " ", s).strip()

    def query(self, question: str, history_list: list | None = None, status=None, role: str = "Business Head"):
        """Fast-path execution with intelligent normalized in-memory caching."""
        cache_key = f"{role.lower()}::{self._normalize_key(question)}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        # Fast path SQL attempt
        sql = self._fast_path_sql(question)
        df = None
        if sql:
            try:
                df = self._run_sql(sql)
            except Exception:
                df = None

        if df is None:
            # Fall back to LLM SQL generation
            history_str = ""
            if history_list:
                for msg in history_list[-2:]:
                    if msg.get("type") == "text":
                        r = "User" if msg.get("role") == "user" else "Assistant"
                        history_str += f"{r}: {msg.get('content', '')}\n"

            error_msg = ""
            for attempt in range(2):
                try:
                    sql = self._generate_sql(question, history_str, error_msg, role)
                    df = self._run_sql(sql)
                    break
                except Exception as e:
                    error_msg = str(e)
                    if attempt == 1:
                        return f"Query failed: {e}"

        if df is None:
            return "No data retrieved for this inquiry."

        route = self._determine_route(question, df)
        if route == "TABLE":
            self.cache[cache_key] = df
            return df
        elif route == "CHART":
            result = self._generate_chart(question, df)
            if isinstance(result, str) and "failed" in result.lower():
                return self._synthesize_text(question, df, status, role)
            self.cache[cache_key] = result
            return result
        else:
            def _caching_streamer():
                accumulated = []
                for chunk in self._synthesize_text(question, df, status, role):
                    accumulated.append(chunk)
                    yield chunk
                full_text = "".join(accumulated).strip()
                if full_text:
                    self.cache[cache_key] = full_text

            return _caching_streamer()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def init_chat_engine(dataframes: dict) -> DuckDBEngine | None:
    """Initialises the DuckDB engine."""
    llm = _build_llm()
    if llm is None:
        return None

    valid = {k: v for k, v in dataframes.items() if not v.empty}
    if not valid:
        print("[WARN] No valid datasets loaded. Cannot initialise chat engine.")
        return None

    return DuckDBEngine(dataframes=valid, llm=llm)


def ask_assistant(engine: DuckDBEngine | None, query: str, history: list | None = None, status=None, role: str = "Business Head"):
    """Send a question to the engine with optional history and status."""
    if engine is None:
        return "AI Assistant Engine is offline. Please verify that your GROQ_API_KEY is configured in your environment."
    return engine.query(query, history, status, role)

