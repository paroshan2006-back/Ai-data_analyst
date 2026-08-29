import os
import tempfile
import csv
import streamlit as st
import pandas as pd
from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.duckdb import DuckDbTools
from agno.tools.pandas import PandasTools


# Function to preprocess and save the uploaded file
def preprocess_and_save(file):
    try:
        # Read the uploaded file into a DataFrame
        if file.name.endswith('.csv'):
            df = pd.read_csv(file, encoding='utf-8', na_values=['NA', 'N/A', 'missing'])
        elif file.name.endswith('.xlsx'):
            df = pd.read_excel(file, na_values=['NA', 'N/A', 'missing'])
        else:
            st.error("Unsupported file format. Please upload a CSV or Excel file.")
            return None, None, None

        # Parse dates and numeric columns
        for col in df.columns:
            if 'date' in col.lower():
                df[col] = pd.to_datetime(df[col], errors='coerce')
            elif df[col].dtype == 'object':
                try:
                    df[col] = pd.to_numeric(df[col])
                except (ValueError, TypeError):
                    # Keep as is if conversion fails
                    pass

        # Create a temporary file to save the preprocessed data
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as temp_file:
            temp_path = temp_file.name
            df.to_csv(temp_path, index=False, quoting=csv.QUOTE_ALL)

        return temp_path, df.columns.tolist(), df
    except Exception as e:
        st.error(f"Error processing file: {e}")
        return None, None, None


# Streamlit app
st.title("📊 Data Analyst Agent (Gemini 3.6 Flash)")

# Sidebar for API key
with st.sidebar:
    st.header("API Key")
    st.markdown(
        "Get a free key from [Google AI Studio](https://aistudio.google.com/apikey)."
    )
    google_key = st.text_input("Enter your Google AI Studio API key:", type="password")
    if google_key:
        st.session_state.google_key = google_key
        st.success("API key saved!")
    else:
        st.warning("Please enter your Google AI Studio API key to proceed.")

# Build the agent once we have a key, and cache it in session_state
# so it survives Streamlit reruns without being recreated every time.
if "google_key" in st.session_state and "data_analyst_agent" not in st.session_state:
    st.session_state.data_analyst_agent = Agent(
        model=Gemini(
            id="gemini-3.6-flash",
            api_key=st.session_state.google_key,
        ),
        tools=[DuckDbTools(), PandasTools()],
        instructions=(
            "You are an expert data analyst. Use the 'uploaded_data' table to answer "
            "user queries. Generate SQL queries using DuckDB tools to solve the user's "
            "query. Provide clear and concise answers with the results."
        ),
        markdown=True,
    )

# File upload widget
uploaded_file = st.file_uploader("Upload a CSV or Excel file", type=["csv", "xlsx"])

if uploaded_file is not None and "google_key" in st.session_state:
    temp_path, columns, df = preprocess_and_save(uploaded_file)

    if temp_path and columns and df is not None:
        st.write("Uploaded Data:")
        st.dataframe(df)

        st.write("Uploaded columns:", columns)

        # Load the CSV file into DuckDB as a table, with error handling
        try:
            st.session_state.data_analyst_agent.tools[0].load_local_csv_to_table(
                path=temp_path,
                table="uploaded_data",
            )
        except Exception as e:
            st.error(f"Error loading data into DuckDB: {e}")
            st.stop()

        # Clean up the temp file now that DuckDB has loaded it
        try:
            os.remove(temp_path)
        except OSError:
            pass

        user_query = st.text_area("Ask a query about the data:")

        show_sql = st.checkbox("Show generated SQL / tool calls", value=False)

        if st.button("Submit Query"):
            if user_query.strip() == "":
                st.warning("Please enter a query.")
            else:
                try:
                    with st.spinner("Processing your query..."):
                        response = st.session_state.data_analyst_agent.run(user_query)
                        response_content = getattr(response, "content", str(response))

                    st.markdown(response_content)

                    if show_sql:
                        tool_calls = getattr(response, "tools", None)
                        if tool_calls:
                            st.subheader("Tool calls")
                            st.json(tool_calls)

                except Exception as e:
                    st.error(f"Error generating response from the agent: {e}")
                    st.error("Please try rephrasing your query or check if the data format is correct.")
elif uploaded_file is not None and "google_key" not in st.session_state:
    st.warning("Please enter your Google AI Studio API key in the sidebar before uploading data.")