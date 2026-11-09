import json
import re
import sqlite3
from pathlib import Path

import pandas as pd
import requests
import streamlit as st

ROOT = Path(__file__).parent
DB_PATH = ROOT / "data" / "company.db"
OLLAMA_URL = st.sidebar.text_input("Ollama URL", "http://localhost:11434")
MODEL = st.sidebar.text_input("Ollama model", "qwen2.5-coder:7b")

st.set_page_config(page_title="QueryCraft AI", page_icon="🧠", layout="wide")
st.title("🧠 QueryCraft AI")
st.caption("Turn plain-English questions into read-only SQL queries against a sample company database.")

def get_schema():
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute("""
            SELECT name, sql FROM sqlite_master
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """).fetchall()
    return "\n\n".join(f"Table: {name}\n{sql}" for name, sql in rows)

def clean_sql(text):
    text = text.strip()
    text = re.sub(r"^```(?:sql)?\s*", "", text, flags=re.I)
    text = re.sub(r"\s*```$", "", text)
    text = re.sub(r"^\s*SQL\s*:\s*", "", text, flags=re.I)
    return text.strip().rstrip(";") + ";"

def validate_sql(sql):
    normalized = sql.strip().lower()
    if not normalized.startswith("select"):
        return False, "Only SELECT queries are allowed."
    blocked = r"\b(insert|update|delete|drop|alter|create|replace|attach|detach|pragma|vacuum|reindex|begin|commit|rollback)\b"
    if re.search(blocked, normalized):
        return False, "The query contains a blocked SQL operation."
    if ";" in normalized[:-1]:
        return False, "Multiple SQL statements are not allowed."
    if "--" in normalized or "/*" in normalized:
        return False, "SQL comments are not allowed."
    return True, ""

def ask_ollama(question, schema):
    prompt = f"""You are a careful SQLite SQL assistant.
Return ONLY one SQLite SELECT statement. No markdown, no explanation.
Use only tables and columns in this schema. Never modify data.
Add a reasonable LIMIT 100 unless the query is an aggregate.
Schema:
{schema}

User question: {question}
SQL:"""
    response = requests.post(
        f"{OLLAMA_URL.rstrip('/')}/api/generate",
        json={"model": MODEL, "prompt": prompt, "stream": False},
        timeout=120,
    )
    response.raise_for_status()
    return clean_sql(response.json().get("response", ""))

def explain_sql(sql):
    prompt = f"Explain this SQLite SELECT query in simple language in 3-5 bullet points. Do not invent schema details.\n\n{sql}"
    response = requests.post(
        f"{OLLAMA_URL.rstrip('/')}/api/generate",
        json={"model": MODEL, "prompt": prompt, "stream": False},
        timeout=120,
    )
    response.raise_for_status()
    return response.json().get("response", "").strip()

def run_query(sql):
    ok, message = validate_sql(sql)
    if not ok:
        raise ValueError(message)
    with sqlite3.connect(DB_PATH) as conn:
        conn.set_authorizer(authorizer)
        return pd.read_sql_query(sql, conn)

def authorizer(action, arg1, arg2, dbname, source):
    # SQLite-level defense in depth: allow reads and SELECT-related functions only.
    allowed = {
        sqlite3.SQLITE_SELECT, sqlite3.SQLITE_READ, sqlite3.SQLITE_FUNCTION,
    }
    return sqlite3.SQLITE_OK if action in allowed else sqlite3.SQLITE_DENY

with st.sidebar:
    st.subheader("About the database")
    st.write("Sample company data with customers, products, orders and order_items.")
    if st.button("Show database schema", use_container_width=True):
        st.code(get_schema(), language="sql")
    st.divider()
    st.caption("Local-first: prompts are sent to your local Ollama server, not a paid API.")

examples = [
    "Show the 10 customers who spent the most money.",
    "What are the top 5 best-selling products by quantity?",
    "Show monthly revenue for 2025.",
    "List orders with customer names and order dates.",
    "Which product category has the highest revenue?",
]

left, right = st.columns([1.15, 1])
with left:
    st.subheader("Ask your database")
    question = st.text_area("Your question", placeholder="e.g. Show monthly revenue by month", height=110)
    chosen = st.selectbox("Or try an example", ["Choose an example..."] + examples)
    if chosen != "Choose an example..." and not question:
        question = chosen
    generate = st.button("✨ Generate SQL", type="primary", use_container_width=True)

with right:
    st.subheader("Connection")
    try:
        ping = requests.get(f"{OLLAMA_URL.rstrip('/')}/api/tags", timeout=3)
        models = [m.get("name") for m in ping.json().get("models", [])]
        st.success("Ollama is reachable")
        if models:
            st.caption("Available models: " + ", ".join(models[:6]))
        else:
            st.info("Ollama is running. Check that your selected model is installed.")
    except Exception:
        st.warning("Ollama not detected. Start Ollama to generate SQL.")

if "sql" not in st.session_state:
    st.session_state.sql = ""
if "last_question" not in st.session_state:
    st.session_state.last_question = ""

if generate:
    if not question.strip():
        st.error("Enter a question first.")
    else:
        with st.spinner("Asking your local model to generate SQL..."):
            try:
                st.session_state.sql = ask_ollama(question, get_schema())
                st.session_state.last_question = question
            except requests.exceptions.ConnectionError:
                st.error("Cannot connect to Ollama. Start Ollama and try again.")
            except requests.exceptions.Timeout:
                st.error("Ollama took too long. Try again or use a smaller model.")
            except Exception as exc:
                st.error(f"Could not generate SQL: {exc}")

if st.session_state.sql:
    st.divider()
    st.subheader("Generated SQL")
    edited_sql = st.text_area("Review or edit SQL before running", st.session_state.sql, height=130)
    c1, c2 = st.columns([1, 1])
    with c1:
        run = st.button("▶ Run read-only query", type="primary", use_container_width=True)
    with c2:
        explain = st.button("💡 Explain this SQL", use_container_width=True)
    if run:
        try:
            result = run_query(edited_sql)
            st.success(f"Query completed — {len(result)} row(s) returned.")
            st.dataframe(result, use_container_width=True)
            if len(result.columns) >= 2 and len(result) > 0:
                numeric_cols = result.select_dtypes(include="number").columns.tolist()
                if numeric_cols:
                    st.subheader("Quick chart")
                    chart_col = st.selectbox("Numeric column", numeric_cols)
                    st.bar_chart(result.set_index(result.columns[0])[chart_col])
            st.download_button(
                "⬇ Download results as CSV",
                result.to_csv(index=False).encode("utf-8"),
                file_name="querycraft-results.csv",
                mime="text/csv",
            )
        except Exception as exc:
            st.error(f"Query blocked or failed: {exc}")
    if explain:
        with st.spinner("Explaining query..."):
            try:
                st.info(explain_sql(edited_sql))
            except Exception as exc:
                st.error(f"Could not explain SQL: {exc}")

st.divider()
st.caption("⚠️ This is a portfolio/demo project. Review generated SQL before execution. It uses a synthetic SQLite database and local Ollama model.")
