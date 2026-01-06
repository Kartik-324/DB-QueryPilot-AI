# 🤖 DB-QueryPilot-AI

DB-QueryPilot-AI is an intelligent AI-powered assistant that allows users to interact with databases using **natural language instead of writing SQL queries manually**.  
It bridges the gap between non-technical users and databases by converting plain English questions into accurate SQL queries and executing them safely.

The system helps developers, analysts, and beginners quickly explore data, understand schemas, and retrieve insights without deep SQL knowledge.

---

## ✨ Features

### 🧠 AI-Powered Query Generation
- Converts natural language questions into SQL queries  
- Understands user intent clearly  
- Generates optimized and readable SQL  

### 🗄️ Database Support
- Supports relational databases (MySQL / PostgreSQL / SQLite*)  
- Automatically understands table structure and schema  

### 💬 Conversational Interface
- Ask questions like chatting with an assistant  
- No need to remember SQL syntax  
- Easy for beginners and non-tech users  

### ⚡ Fast & Accurate
- Instant query generation  
- Executes queries in real time  
- Displays results in tabular format  

### 🔐 Secure by Design
- Read-only query execution (safe mode)  
- Environment-based credentials  
- No hardcoded secrets  

---

## 🧠 Example Queries

Show all users who registered last month
Get total sales grouped by product category
Find top 5 customers by purchase amount
Show average salary by department

yaml
Copy code

---

## 🏗️ How It Works

1. User enters a natural language query  
2. AI analyzes intent and database schema  
3. SQL query is generated automatically  
4. Query is executed on the database  
5. Results are returned in a readable format  

---

## 📋 Prerequisites

Before running the project, make sure you have:

- Python 3.9 or higher  
- OpenAI API Key  
- A running SQL database (MySQL / PostgreSQL / SQLite)  

---

## 🚀 Installation & Setup

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/Kartik-324/DB-QueryPilot-AI.git
cd DB-QueryPilot-AI

2️⃣ Create Virtual Environment
bash
Copy code
python -m venv venv
venv\Scripts\activate

3️⃣ Install Dependencies
bash
Copy code
pip install -r requirements.txt

4️⃣ Environment Variables
Create a .env file in the root directory:

env
Copy code
OPENAI_API_KEY=your_openai_api_key
DB_HOST=localhost
DB_PORT=3306
DB_NAME=your_database
DB_USER=your_username
DB_PASSWORD=your_password
⚠️ Do not push .env to GitHub

▶️ Run the Application
bash
Copy code
python main.py
OR (if using FastAPI / Streamlit):

bash
Copy code
uvicorn main:app --reload

📁 Project Structure
pgsql
Copy code

DB-QueryPilot-AI/
│
├── main.py               # Application entry point
├── database/
│   ├── connection.py     # DB connection logic
│   ├── schema_reader.py  # Schema extraction
│
├── ai/
│   ├── prompt.py         # Prompt templates
│   ├── sql_generator.py  # AI SQL generation
│
├── utils/
│   ├── validator.py      # Query validation
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
🎯 Usage Flow
Connect database using .env

Enter your question in plain English

AI generates SQL query

Review & execute query

Get results instantly


🛠️ Tech Stack
Python

OpenAI (LLM for query generation)

SQLAlchemy

MySQL / PostgreSQL / SQLite

FastAPI / Streamlit (if applicable)


🐛 Troubleshooting
Invalid SQL generated → Check schema & table names

DB connection error → Verify .env credentials

OpenAI error → Check API key & usage limits
