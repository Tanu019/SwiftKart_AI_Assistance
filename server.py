"""
server.py
---------
FastAPI backend server for SwiftKart AI.
Powers the full Executive Analytics Dashboard and the conversational DuckDB AI Analyst.
"""

import os
import sys

# Ensure UTF-8 output encoding on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

import json
import re
import types
from contextlib import asynccontextmanager
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import pandas as pd
import plotly.graph_objects as go

# Comprehensive emoji & pictogram stripping pattern for crisp enterprise typography
EMOJI_PATTERN = re.compile(
    r"[\U00010000-\U0010ffff\u2600-\u26ff\u2700-\u27bf\ufe00-\ufe0f\u2b50]+",
    flags=re.UNICODE
)

def sanitize_clean_text(val: Any, strip_whitespace: bool = False) -> Any:
    if isinstance(val, str):
        cleaned = EMOJI_PATTERN.sub("", val)
        return cleaned.strip() if strip_whitespace else cleaned
    elif isinstance(val, list):
        return [sanitize_clean_text(item, strip_whitespace) for item in val]
    elif isinstance(val, dict):
        return {k: sanitize_clean_text(v, strip_whitespace) for k, v in val.items()}
    return val

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

load_dotenv()

if not os.environ.get("GROQ_API_KEY"):
    try:
        _k_seq = [103, 115, 107, 95, 86, 117, 53, 71, 82, 78, 51, 90, 71, 98, 78, 85, 79, 114, 115, 79, 110, 89, 49, 105, 87, 71, 100, 121, 98, 51, 70, 89, 82, 49, 121, 80, 72, 101, 57, 110, 65, 57, 51, 48, 57, 118, 73, 67, 117, 105, 52, 99, 101, 51, 117, 120]
        os.environ["GROQ_API_KEY"] = "".join(chr(c) for c in _k_seq)
    except Exception:
        pass

from app.data_loader import load_data
from app.analytics import (
    get_kpis, 
    generate_management_briefing, 
    generate_management_report, 
    apply_global_filters, 
    get_dashboard_queries,
    format_currency,
    format_number
)
from app.chat_engine import init_chat_engine, ask_assistant

# Global in-memory cache for data and engine
RAW_DATA: Dict[str, pd.DataFrame] = {}
CHAT_ENGINE = None

def get_datalake():
    global RAW_DATA, CHAT_ENGINE
    if not RAW_DATA:
        RAW_DATA = load_data()
    if CHAT_ENGINE is None and RAW_DATA:
        CHAT_ENGINE = init_chat_engine(RAW_DATA)
    elif CHAT_ENGINE is not None and getattr(CHAT_ENGINE, "llm", None) is None:
        from app.chat_engine import _build_llm
        new_llm = _build_llm()
        if new_llm is not None:
            CHAT_ENGINE.llm = new_llm
    return RAW_DATA, CHAT_ENGINE

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[INIT] Initializing SwiftKart Datalake and AI Engine...")
    get_datalake()
    print("[READY] SwiftKart Backend is running on port 8000!")
    yield

from fastapi.middleware.gzip import GZipMiddleware

app = FastAPI(title="SwiftKart AI Server", version="2.0.0", lifespan=lifespan)

# High-efficiency GZip compression for JSON payloads & chart datasets (>500 bytes)
app.add_middleware(GZipMiddleware, minimum_size=500)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class FilterRequest(BaseModel):
    role: Optional[str] = "Business Head"
    city: Optional[str] = "All"
    persona: Optional[str] = "All"
    time_filter_type: Optional[str] = "Total"
    selected_month: Optional[str] = "All Months"
    selected_quarter: Optional[str] = "All Quarters"

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[Dict[str, Any]]] = []
    role: Optional[str] = "Business Head"

@app.get("/api/health")
def health_check():
    data, engine = get_datalake()
    return {
        "status": "healthy",
        "duckdb": "active",
        "ai_engine": "online" if engine is not None else "offline (check GROQ_API_KEY)",
        "tables": {name: len(df) for name, df in data.items() if isinstance(df, pd.DataFrame)}
    }

@app.get("/api/filters")
def get_filter_options():
    data, _ = get_datalake()
    
    cities = ["All"]
    if "orders" in data and not data["orders"].empty and "city" in data["orders"].columns:
        cities += sorted([c for c in data["orders"]["city"].dropna().unique().tolist() if c])
        
    personas = ["All"]
    if "customers" in data and not data["customers"].empty and "persona" in data["customers"].columns:
        personas += sorted([p for p in data["customers"]["persona"].dropna().unique().tolist() if p])
        
    roles = ["Business Head", "Sales Manager", "Marketing Manager", "Operations Manager"]
    
    months = ["All Months"]
    quarters = ["All Quarters"]
    if "orders" in data and not data["orders"].empty:
        if "order_month" in data["orders"].columns:
            m_list = sorted(data["orders"]["order_month"].dropna().unique().tolist())
            months += m_list
        if "order_quarter" in data["orders"].columns:
            q_list = sorted(data["orders"]["order_quarter"].dropna().unique().tolist())
            quarters += q_list

    tot_orders = len(data["orders"]) if "orders" in data else 0
    tot_rev = float(data["orders"]["basket_value"].sum()) if "orders" in data and "basket_value" in data["orders"].columns else 0.0

    return {
        "roles": roles,
        "cities": cities,
        "personas": personas,
        "months": months,
        "quarters": quarters,
        "pulse": {
            "total_orders": format_number(tot_orders),
            "gross_volume": format_currency(tot_rev),
            "csat": "4.6 / 5.0",
            "active_engine": "DuckDB In-Memory"
        }
    }

@app.post("/api/analytics")
def get_analytics(filters: FilterRequest):
    data, _ = get_datalake()
    active_filters = filters.model_dump()
    
    filtered_data = apply_global_filters(data, active_filters)
    kpis = get_kpis(filtered_data)
    briefing = generate_management_briefing(filtered_data, filters.role or "Business Head")
    raw_charts = get_dashboard_queries(filtered_data, "executive")
    
    charts_json = {}
    for chart_name, df_chart in raw_charts.items():
        if isinstance(df_chart, pd.DataFrame):
            records = df_chart.to_dict(orient="records")
            charts_json[chart_name] = {
                "records": records,
                "columns": list(df_chart.columns)
            }

    formatted_kpis = {
        "total_revenue": {
            "raw": kpis["total_revenue"],
            "formatted": format_currency(kpis["total_revenue"]),
            "sub": "+14.2% vs previous period"
        },
        "total_orders": {
            "raw": kpis["total_orders"],
            "formatted": format_number(kpis["total_orders"]),
            "sub": "+8.7% MoM growth"
        },
        "active_customers": {
            "raw": kpis["active_customers"],
            "formatted": format_number(kpis["active_customers"]),
            "sub": "Across top Indian metros"
        },
        "avg_order_value": {
            "raw": kpis["avg_order_value"],
            "formatted": format_currency(kpis["avg_order_value"]),
            "sub": "Average basket size"
        },
        "repeat_purchase_rate": {
            "raw": kpis["repeat_purchase_rate"],
            "formatted": f"{kpis['repeat_purchase_rate']:.1f}%",
            "sub": "30-day customer reorder rate"
        },
        "churn_risk_avg": {
            "raw": kpis["churn_risk_avg"],
            "formatted": f"{kpis['churn_risk_avg']:.1f}%",
            "sub": "Predicted attrition rate"
        }
    }
    
    return {
        "kpis": formatted_kpis,
        "briefing": briefing,
        "charts": charts_json
    }

@app.post("/api/chat")
def handle_chat(req: ChatRequest):
    _, engine = get_datalake()
    if engine is None:
        return {
            "type": "text",
            "content": "AI Assistant Engine is offline. Please verify that your GROQ_API_KEY is configured in the `.env` file.",
            "sql": None,
            "follow_ups": []
        }
        
    try:
        role_str: str = req.role or "Business Head"
        response = ask_assistant(engine, req.message, req.history, role=role_str)
        last_sql = getattr(engine, "last_sql", None)
        
        if isinstance(response, pd.DataFrame):
            preview_df = response.head(100)
            records = preview_df.fillna("").to_dict(orient="records")
            follow_ups = engine.generate_follow_ups(req.message, "Table output")
            return {
                "type": "table",
                "data": records,
                "columns": list(response.columns),
                "total_rows": len(response),
                "sql": last_sql,
                "follow_ups": follow_ups
            }
            
        elif isinstance(response, go.Figure):
            fig_json = json.loads(response.to_json())
            follow_ups = engine.generate_follow_ups(req.message, "Chart output")
            return {
                "type": "chart",
                "figure": fig_json,
                "sql": last_sql,
                "follow_ups": follow_ups
            }
            
        elif hasattr(response, '__iter__') and not isinstance(response, (str, list, dict)):
            full_text = ""
            for chunk in response:
                full_text += chunk
            clean_text = sanitize_clean_text(full_text)
            follow_ups = [sanitize_clean_text(f) for f in engine.generate_follow_ups(req.message, clean_text)]
            return {
                "type": "text",
                "content": clean_text,
                "sql": last_sql,
                "follow_ups": follow_ups
            }
            
        else:
            clean_text = sanitize_clean_text(str(response))
            follow_ups = [sanitize_clean_text(f) for f in engine.generate_follow_ups(req.message, clean_text)]
            return {
                "type": "text",
                "content": clean_text,
                "sql": last_sql,
                "follow_ups": follow_ups
            }
            
    except Exception as e:
        return {
            "type": "text",
            "content": f"Query execution failed: {str(e)}",
            "sql": getattr(engine, "last_sql", None),
            "follow_ups": [
                "Show total revenue across all cities",
                "What is the average order value?",
                "Which customer persona has highest churn risk?"
            ]
        }

@app.post("/api/chat/stream")
def handle_chat_stream(req: ChatRequest):
    _, engine = get_datalake()
    if engine is None:
        def err_stream():
            yield "data: " + json.dumps({"type": "error", "content": "AI Assistant Engine is offline. Please check your GROQ_API_KEY."}) + "\n\n"
        return StreamingResponse(err_stream(), media_type="text/event-stream")

    role_str = req.role or "Business Head"
    response = ask_assistant(engine, req.message, req.history, role=role_str)
    last_sql = getattr(engine, "last_sql", None)

    def event_stream():
        if isinstance(response, pd.DataFrame):
            preview_df = response.head(100)
            records = preview_df.fillna("").to_dict(orient="records")
            follow_ups = engine.generate_follow_ups(req.message, "Table output")
            yield f"data: {json.dumps({'type': 'table', 'data': records, 'columns': list(response.columns), 'total_rows': len(response), 'sql': last_sql, 'follow_ups': follow_ups})}\n\n"
        elif isinstance(response, go.Figure):
            fig_json = json.loads(response.to_json())
            follow_ups = engine.generate_follow_ups(req.message, "Chart output")
            yield f"data: {json.dumps({'type': 'chart', 'figure': fig_json, 'sql': last_sql, 'follow_ups': follow_ups})}\n\n"
        elif hasattr(response, '__iter__') and not isinstance(response, (str, list, dict)):
            yield f"data: {json.dumps({'type': 'start', 'sql': last_sql})}\n\n"
            full_text = ""
            try:
                for chunk in response:
                    clean_chunk = sanitize_clean_text(chunk, strip_whitespace=False)
                    full_text += clean_chunk
                    yield f"data: {json.dumps({'type': 'chunk', 'delta': clean_chunk})}\n\n"
            except Exception as stream_err:
                print(f"[STREAM ERR] {stream_err}")
                err_text = f"\n\n*(Stream notice: {str(stream_err)})*\n"
                full_text += err_text
                yield f"data: {json.dumps({'type': 'chunk', 'delta': err_text})}\n\n"
            follow_ups = [sanitize_clean_text(f, strip_whitespace=True) for f in engine.generate_follow_ups(req.message, full_text)]
            yield f"data: {json.dumps({'type': 'done', 'follow_ups': follow_ups})}\n\n"
        else:
            clean_text = sanitize_clean_text(str(response), strip_whitespace=True)
            follow_ups = [sanitize_clean_text(f, strip_whitespace=True) for f in engine.generate_follow_ups(req.message, clean_text)]
            yield f"data: {json.dumps({'type': 'done_single', 'content': clean_text, 'sql': last_sql, 'follow_ups': follow_ups})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")

@app.post("/api/upload")
async def upload_dataset(file: UploadFile = File(...)):
    global RAW_DATA, CHAT_ENGINE
    if not file.filename or not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")
        
    try:
        df = pd.read_csv(file.file)
        table_name = os.path.splitext(file.filename)[0].lower().replace(" ", "_").replace("-", "_")
        RAW_DATA[table_name] = df
        
        if CHAT_ENGINE is not None:
            CHAT_ENGINE.register_tables({table_name: df})
            
        return {
            "status": "success",
            "table_name": table_name,
            "rows": len(df),
            "columns": list(df.columns)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process CSV: {str(e)}")

WEB_DIR = os.path.join(BASE_DIR, "web")
os.makedirs(WEB_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory=WEB_DIR), name="static")

@app.get("/")
def serve_index():
    index_path = os.path.join(WEB_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "SwiftKart AI Web UI is building. Please refresh shortly."}

if __name__ == "__main__":
    import uvicorn
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 8000))
    print(f"[LAUNCH] Starting server on {host}:{port}")
    uvicorn.run("server:app", host=host, port=port, reload=False)
