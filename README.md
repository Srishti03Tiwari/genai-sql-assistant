🤖 GenAI SQL Assistant

Ask questions about your database in plain English — no SQL knowledge needed.
AI understands your question, generates SQL, runs it, and returns downloadable results.

📸 What It Does
1️⃣You type a question in plain English
2️⃣RAG finds relevant database schema context
3️⃣LLaMA 3.3-70B generates the SQL query
4️⃣SQL runs on the database
5️⃣Results appear as a table
6️⃣Download as CSV, Excel, or PDF

⚙️ Setup & Installation
Prerequisites

Python 3.10 or higher
A free Groq API Key — sign up with Google

Step 1 — Clone the repository
git clone https://github.com/YOUR_USERNAME/genai-sql-assistant.git
cd genai-sql-assistant

Step 2 — Create a virtual environment
# Create
python -m venv venv

# Activate (Mac/Linux)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

Step 3 — Install dependencies
pip install -r requirements.txt

Step 4 — Set up your API key
Create a .env file in the root folder:

GROQ_API_KEY=gsk_your_key_here
DB_PATH=./database/company.db
FAISS_INDEX_PATH=./faiss_index/index.faiss
FAISS_CHUNKS_PATH=./faiss_index/chunks.pkl

Step 5 — Initialize the database
python -m database.seed_data

Step 6 — Build the FAISS index
python -c "from rag.faiss_store import build_index; build_index('./data/schema_docs.txt')"

Step 7 — Run the app
streamlit run app.py



