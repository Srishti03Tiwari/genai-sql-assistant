# app.py
import streamlit as st
import os
from database.db_connection import run_query, get_schema_as_text
from database.seed_data import init_db
from rag.faiss_store import build_index, load_index
from llm.query_generator import generate_sql
from output.exporter import to_csv, to_excel, to_pdf

# ── Page Config ────────────────────────────────────────
st.set_page_config(
    page_title="GenAI SQL Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────
st.markdown("""
<style>
    /* Main background */
    .stApp { background-color: #0f0f0f; }

    /* SQL output box */
    .sql-box {
        background: #1a1a1a;
        border: 1px solid #2a2a2a;
        border-left: 3px solid #00ff88;
        border-radius: 6px;
        padding: 14px 18px;
        font-family: 'Courier New', monospace;
        font-size: 13px;
        color: #00ff88;
        white-space: pre-wrap;
        margin: 8px 0 16px 0;
    }

    /* Step labels */
    .step-label {
        font-size: 12px;
        color: #888;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 4px;
    }

    /* Success banner */
    .success-banner {
        background: #0a2a1a;
        border: 1px solid #00ff88;
        border-radius: 8px;
        padding: 10px 16px;
        color: #00ff88;
        font-size: 14px;
        margin: 8px 0;
    }
</style>
""", unsafe_allow_html=True)


# ── One-time Setup ─────────────────────────────────────
@st.cache_resource(show_spinner="🔧 Setting up database...")
def setup():
    # Init DB if not exists
    init_db()
    # Build FAISS index if not exists
    if not os.path.exists("./faiss_index/index.faiss"):
        build_index("./data/schema_docs.txt")
    return True

setup()


# ── Sidebar ────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Settings")
    st.divider()

    # Export format selector
    export_format = st.selectbox(
        "📤 Export Format",
        options=["CSV", "Excel", "PDF"],
        index=0,
    )

    st.divider()

    # Live schema viewer
    st.markdown("### 🗄️ Database Schema")
    with st.expander("View Schema"):
        st.code(get_schema_as_text(), language="sql")

    st.divider()

    # Example queries — click to auto-fill
    st.markdown("### 💡 Example Queries")
    examples = [
        "Show all customers",
        "Show all products in Electronics",
        "Show delivered orders with customer and product names",
        "Top 3 customers by total spending",
        "Total revenue by product category",
        "Products with stock less than 100",
        "How many orders per customer",
        "All pending orders",
        "Most expensive product",
        "Orders placed in February 2024",
    ]
    for example in examples:
        if st.button(f"▶  {example}", use_container_width=True, key=example):
            st.session_state["prefill_query"] = example
            st.rerun()

    st.divider()

    # Rebuild FAISS index button
    if st.button("🔄 Rebuild FAISS Index", use_container_width=True):
        with st.spinner("Rebuilding index..."):
            build_index("./data/schema_docs.txt")
        st.success("✅ Index rebuilt!")


# ── Header ─────────────────────────────────────────────
st.markdown("# 🤖 GenAI SQL Assistant")
st.markdown("Ask anything about your database in **plain English**. The AI generates SQL, runs it, and returns results you can download.")
st.divider()


# ── Query Input ────────────────────────────────────────
prefill = st.session_state.get("prefill_query", "")

user_query = st.text_area(
    "💬 Ask a question about your data",
    value=prefill,
    placeholder="e.g.  Show me top 5 customers by total spending",
    height=90,
)

# Clear prefill after use
if prefill:
    st.session_state["prefill_query"] = ""

col1, col2 = st.columns([1, 5])
with col1:
    run_btn = st.button("🚀 Run", type="primary", use_container_width=True)
with col2:
    clear_btn = st.button("🗑️ Clear", use_container_width=True)

if clear_btn:
    st.session_state["prefill_query"] = ""
    st.rerun()


# ── Main Logic ─────────────────────────────────────────
if run_btn:

    if not user_query.strip():
        st.warning("⚠️ Please type a question first.")
        st.stop()

    st.divider()

    # ── Step 1: Generate SQL ───────────────────────────
    st.markdown('<p class="step-label">Step 1 — Generating SQL</p>',
                unsafe_allow_html=True)

    with st.spinner("🧠 Thinking with LLM + RAG context..."):
        try:
            sql = generate_sql(user_query)
        except Exception as e:
            st.error(f"❌ LLM Error: {e}")
            st.stop()

    st.markdown("**Generated SQL:**")
    st.markdown(f'<div class="sql-box">{sql}</div>', unsafe_allow_html=True)

    # Block if LLM returned an error
    if sql.strip().upper().startswith("ERROR"):
        st.warning(f"⚠️ LLM could not generate SQL: {sql}")
        st.stop()

    # Safety — block write operations
    forbidden = ["DROP", "DELETE", "INSERT", "UPDATE", "ALTER", "CREATE"]
    if any(kw in sql.upper() for kw in forbidden):
        st.error("🚫 Only SELECT queries are allowed for safety.")
        st.stop()

    # ── Step 2: Run SQL ────────────────────────────────
    st.markdown('<p class="step-label">Step 2 — Running query on database</p>',
                unsafe_allow_html=True)

    with st.spinner("⚡ Executing query..."):
        try:
            df = run_query(sql)
        except Exception as e:
            st.error(f"❌ SQL Error: {e}")
            st.error("The LLM generated invalid SQL. Try rephrasing your question.")
            st.stop()

    # ── Step 3: Show Results ───────────────────────────
    st.markdown('<p class="step-label">Step 3 — Results</p>',
                unsafe_allow_html=True)

    if df.empty:
        st.info("ℹ️ Query ran successfully but returned no results.")
        st.stop()

    # Metrics row
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("📊 Rows returned", len(df))
    col_b.metric("📋 Columns", len(df.columns))
    col_c.metric("✅ Status", "Success")

    # Results table
    st.dataframe(df, use_container_width=True, height=380)

    # ── Step 4: Export ─────────────────────────────────
    st.divider()
    st.markdown('<p class="step-label">Step 4 — Download Results</p>',
                unsafe_allow_html=True)

    st.markdown(f"**Selected format: `{export_format}`** — change in sidebar")

    if export_format == "CSV":
        data     = to_csv(df)
        filename = "results.csv"
        mime     = "text/csv"

    elif export_format == "Excel":
        data     = to_excel(df)
        filename = "results.xlsx"
        mime     = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    elif export_format == "PDF":
        with st.spinner("📝 Generating PDF..."):
            data = to_pdf(df, title=user_query)
        filename = "results.pdf"
        mime     = "application/pdf"

    st.download_button(
        label=f"⬇️ Download {export_format}",
        data=data,
        file_name=filename,
        mime=mime,
        type="primary",
        use_container_width=False,
    )

    st.markdown(
        f'<div class="success-banner">✅ {len(df)} rows ready to download as {export_format}</div>',
        unsafe_allow_html=True
    )