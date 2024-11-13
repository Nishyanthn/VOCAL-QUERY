import os
from dotenv import load_dotenv
load_dotenv() ## load all the environemnt variables

import streamlit as st

import sqlite3

import google.generativeai as genai
## Configure Genai Key

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


def execute_sql_query(sql, db):
    conn = sqlite3.connect(db)
    cur = conn.cursor()

    try:
        # Execute the SQL command
        cur.execute(sql)
        conn.commit()

        # Handle SELECT queries
        if sql.strip().upper().startswith("SELECT") or sql.strip().upper().startswith("PRAGMA"):
            rows = cur.fetchall()
            return rows

        # Handle INSERT, UPDATE, DELETE queries
        elif sql.strip().upper().startswith(("INSERT", "UPDATE", "DELETE")):
            return "Query executed successfully!"

        # If the query is unknown, return a message
        else:
            return "Query not recognized."

    except sqlite3.Error as e:
        return f"An error occurred: {e}"
    finally:
        conn.close()


## Define Your Prompt
prompt=[
    """
    You are an expert in converting English questions to SQL query!
    also the sql code should not have ``` in beginning or end and sql word in output
    We need a single query even if they are multiple inputs from the user
    Always the query will end with a ;
    """


]

## Streamlit App

def clean_sql_query(query):
    # Remove backticks and any leading/trailing whitespace
    return query.replace('```', '').strip()

def get_gemini_response(question, prompt):
    if "schema" in question.lower() and "STUDENT" in question.upper():
        return "PRAGMA table_info(STUDENT);"

    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content([prompt[0], question])
    return response.text

# Streamlit App
# Streamlit App
st.set_page_config(page_title="I can Retrieve Any SQL query")
st.header("Gemini App To Retrieve SQL Data")

question = st.text_input("Input: ", key="input")

submit = st.button("Ask the question")

# If submit is clicked
if submit:
    response = get_gemini_response(question, prompt)
    cleaned_response = clean_sql_query(response)  # Clean the SQL query
    st.subheader("Generated SQL Query:")
    st.code(cleaned_response)

    # Execute the cleaned SQL query and display the result
    execution_result = execute_sql_query(cleaned_response, "employee.db")

    if isinstance(execution_result, list):
        st.subheader("The Results are:")
        # Display the results in a user-friendly format
        if len(execution_result) > 0:
            for row in execution_result:
                st.write(row)  # Display each row of the result
        else:
            st.write("No records found.")
    else:
        st.subheader("Execution Status:")
        st.write(execution_result)

    # Handle specific case for schema request
    if "schema" in question.lower() and "employee" in question.lower():
        schema_query = "PRAGMA table_info(employee);"
        schema_result = execute_sql_query(schema_query, "employee.db")
        st.subheader("Employee Table Schema:")
        for column in schema_result:
            st.write(f"Column: {column[1]}, Type: {column[2]}, Not Null: {column[3]}, Default Value: {column[4]}, Primary Key: {column[5]}")
