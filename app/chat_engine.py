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
    """Initialise the Groq LLM via the OpenAI-compatible endpoint."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        st.error("❌ Please set a valid GROQ_API_KEY in your .env file.")
        return None

    return OpenAILike(
        model="qwen/qwen3.8-27b",
        api_base="https://api.groq.com/openai/v1",
        api_key=api_key,
        is_chat_model=True,
        context_window=8192,
        max_tokens=2048,
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

    def _generate_sql(self, question: str, history: str = "", error_msg: str = "", role: str = "Business Head") -> str:
        prompt = f"""You are an expert SQL Data Analyst acting as a {role}.
Given the following database schema:
{self.schema_context}

Write a SQL query (DuckDB dialect) to answer the user's question.
Rules:
- Return ONLY the raw SQL query. Do not include markdown formatting (like ```sql), do not explain your answer, and DO NOT output any <think> reasoning process. Just output the final SQL.
- Ensure column names match exactly.

Recent Chat History (for context):
{history}

{f"WARNING: Your previous SQL failed with this error: {error_msg}. Please fix the syntax or column names and try again." if error_msg else ""}

Question: {question}
"""
        response = self.llm.complete(prompt)
        raw_sql = str(response).strip()
        
        # Extract SQL from markdown if present
        match = re.search(r"```(?:sql)?\n(.*?)\n```", raw_sql, flags=re.DOTALL | re.IGNORECASE)
        if match:
            sql = match.group(1)
        else:
            sql = raw_sql
            # Remove properly closed <think> blocks
            sql = re.sub(r"<think>.*?</think>", "", sql, flags=re.DOTALL).strip()
            # If there's an unclosed <think> block, find the first SELECT
            if "<think>" in sql.lower():
                idx = sql.upper().find("SELECT ")
                if idx != -1:
                    sql = sql[idx:]
                else:
                    raise ValueError("The AI generated a thought process but got cut off before writing the SELECT statement. Please try again.")
            # Clean up backticks
            sql = re.sub(r"^```(?:sql)?\n?", "", sql)
            sql = re.sub(r"\n?```$", "", sql)
            
        # Ensure it actually looks like a query
        if not sql.upper().startswith("SELECT") and not sql.upper().startswith("WITH"):
            # try to find SELECT one more time
            idx = sql.upper().find("SELECT ")
            if idx != -1:
                sql = sql[idx:]
            else:
                raise ValueError(f"No valid SELECT statement found in output:\n{raw_sql[:200]}...")
            
        return sql.strip()

    def _run_sql(self, sql: str) -> pd.DataFrame:
        """Execute the SQL query and return a Pandas DataFrame."""
        try:
            # DuckDB returns a pandas dataframe easily
            return self.con.execute(sql).df()
        except Exception as e:
            raise ValueError(f"SQL Execution Error: {e}\nQuery was: {sql}")

    def _determine_route(self, question: str, df: pd.DataFrame) -> str:
        """Determines if the output should be TEXT, TABLE, or CHART instantly with zero latency."""
        if df.empty or df.shape == (1, 1):
            return "TEXT"
            
        q_lower = question.lower()
        chart_keywords = ["chart", "graph", "plot", "trend", "visualize", "distribution", "histogram", "bar chart", "line chart", "pie chart"]
        table_keywords = ["table", "raw data", "list all", "list of", "show records", "show data", "tabular", "dataframe", "all rows", "csv"]
        
        if any(k in q_lower for k in chart_keywords):
            return "CHART"
        if any(k in q_lower for k in table_keywords):
            return "TABLE"
        return "TEXT"

    def _synthesize_text(self, question: str, df: pd.DataFrame, status=None, role="Business Head"):
        data_str = df.head(20).to_string(index=False)
        
        if status: status.update(label="Synthesizing management insight...", state="running")
        
        prompt = f"""{SYSTEM_PROMPT}

You are analyzing this data for a {role}.
A data query was run to answer the following question:
"{question}"

The raw output from the query was:
{data_str}

Now write a highly structured management response based ONLY on this data.
DO NOT output any <think> tags. Just output the final polished text formatted with the requested sections (📌 Key Insight, 📊 Supporting Data, 🔎 Why It Matters, 🎯 Recommended Action).
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
                    # Strip newlines right after </think> if they leaked
                    if buffer.startswith("\n\n"):
                        buffer = buffer[2:]
                    elif buffer.startswith("\n"):
                        buffer = buffer[1:]
                    yield buffer
                    buffer = ""
                    
        if not in_think_block and buffer:
            yield buffer
    def _generate_chart(self, question: str, df: pd.DataFrame) -> go.Figure | str:
        """Generates Plotly Python code to visualize the DataFrame."""
        sample = df.head(5).to_dict(orient="records")
        prompt = f"""You are an expert Data Visualizer using Plotly.
The user asked: "{question}"
We have a pandas DataFrame named `df` with columns: {list(df.columns)}.
Sample data: {sample}

Write Python code using `plotly.graph_objects` as `go` to create a beautiful, modern chart.
Rules:
- Store the final figure in a variable named `fig`.
- Use a sleek dark theme for the layout (e.g., paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#f8fafc')).
- Do NOT use `fig.show()`.
- Do NOT import pandas or plotly (they are already imported).
- Return ONLY the raw Python code, no markdown, no explanations.
"""
        response = self.llm.complete(prompt)
        raw_code = str(response).strip()
        
        # Extract code from markdown if present
        match = re.search(r"```(?:python)?\n(.*?)\n```", raw_code, flags=re.DOTALL | re.IGNORECASE)
        if match:
            code = match.group(1)
        else:
            code = raw_code
            # Remove properly closed <think> blocks
            code = re.sub(r"<think>.*?</think>", "", code, flags=re.DOTALL).strip()
            # If there's an unclosed <think> block, find the first 'import ' or 'fig ='
            if "<think>" in code.lower():
                idx = code.find("import ")
                if idx == -1:
                    idx = code.find("fig =")
                if idx != -1:
                    code = code[idx:]
            
            # Clean up backticks
            code = re.sub(r"^```(?:python)?\n?", "", code)
            code = re.sub(r"\n?```$", "", code)
        
        # Execute chart code safely
        local_ns = {"df": df, "go": go, "fig": None}
        try:
            exec(code.strip(), local_ns) # noqa: S102
            fig = local_ns.get("fig")
            if isinstance(fig, go.Figure):
                return fig
            return "⚠️ Failed to generate chart object."
        except Exception as e:
            return f"⚠️ Chart generation failed: {e}"

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

    def query(self, question: str, history_list: list | None = None, status=None, role: str = "Business Head"):
        """Main routing execution with caching, memory, and self-healing."""
        # 1. Check Cache
        if status: status.update(label="Checking memory...", state="running")
        if question in self.cache:
            if status: status.update(label="Serving from cache...", state="complete")
            return self.cache[question]
            
        # 2. Format History
        history_str = ""
        if history_list:
            # Take last 4 messages to avoid blowing up context
            for msg in history_list[-4:]:
                if msg["type"] == "text":
                    role = "User" if msg["role"] == "user" else "Assistant"
                    history_str += f"{role}: {msg['content']}\n"
                    
        # 3. Self-Healing SQL Loop
        sql = ""
        df = None
        error_msg = ""
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                if status: status.update(label=f"Generating SQL (Attempt {attempt+1})...", state="running")
                sql = self._generate_sql(question, history_str, error_msg, role)
                if status: status.update(label="Executing query in DuckDB...", state="running")
                df = self._run_sql(sql)
                break # Success!
            except Exception as e:
                error_msg = str(e)
                if attempt == max_retries - 1:
                    if status: status.update(label="Failed to generate correct SQL.", state="error")
                    return f"⚠️ I encountered a data error I couldn't fix: {e}"
        
        if df is None:
            if status: status.update(label="Failed to retrieve data.", state="error")
            return "⚠️ No data could be retrieved for this query."

        # 4. Route Output
        try:
            if status: status.update(label="Routing data...", state="running")
            route = self._determine_route(question, df)
            
            if route == "TABLE":
                self.cache[question] = df
                if status: status.update(label="Complete!", state="complete")
                return df
            elif route == "CHART":
                if status: status.update(label="Generating interactive chart...", state="running")
                result = self._generate_chart(question, df)
                if isinstance(result, str) and result.startswith("⚠️"):
                    # Fallback to streaming text
                    return self._synthesize_text(question, df, status)
                self.cache[question] = result
                if status: status.update(label="Complete!", state="complete")
                return result
            else:
                return self._synthesize_text(question, df, status, role)
                
        except Exception as e:
            if status: status.update(label="Routing failed.", state="error")
            return f"⚠️ An error occurred during routing: {e}"


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
        st.error("No valid datasets loaded. Cannot initialise chat engine.")
        return None

    return DuckDBEngine(dataframes=valid, llm=llm)


def ask_assistant(engine: DuckDBEngine | None, query: str, history: list | None = None, status=None, role: str = "Business Head"):
    """Send a question to the engine with optional history and status."""
    if engine is None:
        return "⚠️ AI Assistant Engine is offline. Please check your GROQ_API_KEY in the .env file."
    return engine.query(query, history, status, role)

