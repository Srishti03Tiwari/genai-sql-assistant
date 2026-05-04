# llm/query_generator.py
from groq import Groq
import os
from dotenv import load_dotenv
from rag.context_builder import build_context
from database.db_connection import get_schema_as_text

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """You are an expert SQL assistant.
Your job is to convert natural language questions into valid SQLite SQL queries.

Rules:
1. Return ONLY the raw SQL query — no explanation, no markdown, no backticks.
2. Use only tables and columns that exist in the schema provided.
3. Always use table aliases for clarity in JOINs.
4. For aggregations always use proper GROUP BY.
5. Limit results to 500 rows max unless user asks for all.
6. Never use DROP, DELETE, INSERT, UPDATE — read-only SELECT queries only.
7. If the question cannot be answered with the schema, return: ERROR: <reason>
"""

def generate_sql(user_query: str) -> str:
    rag_context = build_context(user_query)
    live_schema = get_schema_as_text()

    user_message = f"""
Database Schema (live):
{live_schema}

Relevant Documentation (from knowledge base):
{rag_context}

User Question:
{user_query}

Generate the SQL query:
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": user_message},
        ],
        temperature=0,
        max_tokens=500,
    )

    sql = response.choices[0].message.content.strip()

    # Clean markdown backticks if model adds them
    if "```" in sql:
        lines = sql.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        sql = "\n".join(lines).strip()

    return sql