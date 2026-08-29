# 📊 Data Analyst Agent

An interactive Streamlit app that lets you upload a CSV or Excel file and ask questions about it in plain English. An AI agent (powered by [Agno](https://github.com/agno-agi/agno)) translates your questions into SQL, runs them against the data using DuckDB, and returns a clear answer.

Two versions are included:
- **`data_analyst_agent_gemini.py`** — uses Google's Gemini models via Google AI Studio (free tier available)

## Features

- Upload CSV or Excel files
- Automatic data preprocessing (date parsing, numeric type inference)
- Natural language querying of your data
- View the underlying generated SQL / tool calls
- Interactive data preview table

## Setup

1. Clone this repository:
   ```bash
   git clone <>
   cd <Ai-data_analyst>
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Get an API key:
   - **Gemini version**: get a free key from [Google AI Studio](https://aistudio.google.com/apikey)
   

4. Run the app:
   ```bash
   streamlit run app.py
   ```
  

5. Paste your API key into the sidebar, upload a CSV/Excel file, and start asking questions.

## Example queries

- "Which company has the most expensive average car price?"
- "Show me the top 5 most expensive rows"
- "What is the average value grouped by category?"



## Tech stack

- [Streamlit](https://streamlit.io/) — web UI
- [Agno](https://github.com/agno-agi/agno) — agent framework
- [DuckDB](https://duckdb.org/) — in-memory SQL engine for querying uploaded data
- [Pandas](https://pandas.pydata.org/) — data preprocessing

## License

MIT (or update this to match your preferred license)

