# QueryCraft AI

A local-first natural-language-to-SQL assistant. Ask questions in plain English, generate SQLite SELECT queries with a local Ollama model, review the SQL, execute it against a synthetic company database, and export results.

## Features

- Natural language to SQLite SQL using Ollama
- Schema-aware prompt generation
- Editable SQL preview before execution
- Read-only query validation plus SQLite authorizer
- Plain-language SQL explanation
- Tabular results, quick charts and CSV export
- Synthetic sample database; no external database credentials
- Windows one-click launcher

## Tech stack

Python, Streamlit, SQLite, Pandas, Ollama, Requests.

## Requirements

- Windows 10/11 (or macOS/Linux with manual commands)
- Python 3.10+
- Ollama installed: https://ollama.com/

## Run on Windows

1. Install and start Ollama.
2. Open PowerShell and download a model:

   ```powershell
   ollama pull qwen2.5-coder:7b
   ```

3. Extract this ZIP.
4. Double-click `run_windows.bat`.

The launcher creates a virtual environment, installs dependencies, builds the sample database, and opens the Streamlit app. Usually available at `http://localhost:8501`.

## Run manually

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python create_db.py
ollama pull qwen2.5-coder:7b
streamlit run app.py
```

If PowerShell blocks activation, run this once in the current terminal:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

## Example questions

- Show the 10 customers who spent the most money.
- What are the top 5 best-selling products by quantity?
- Show monthly revenue for 2025.
- List orders with customer names and order dates.
- Which product category has the highest revenue?

## Project structure

```text
QueryCraft-AI/
├── app.py
├── create_db.py
├── requirements.txt
├── run_windows.bat
├── .env.example
├── .gitignore
├── README.md
└── data/
    └── company.db   # generated locally
```

## Safety notes

This is a portfolio/demo project, not a production database agent. It uses synthetic data. Generated SQL should always be reviewed. The app blocks non-SELECT statements and also applies a SQLite authorizer as defense in depth. Do not connect it to a sensitive or production database.

## Future improvements

- Add PostgreSQL support with a read-only database account
- Add query history and saved prompts
- Add schema relationship visualization
- Add SQL test cases and automated evaluation
- Add authentication for multi-user deployment

## Resume bullet (use only after you have run and tested it)

Built a local-first natural-language-to-SQL assistant using Streamlit, Ollama and SQLite, featuring schema-aware SQL generation, read-only query safeguards, query explanations, data visualization and CSV export.
