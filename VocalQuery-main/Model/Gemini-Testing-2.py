import os
from dotenv import load_dotenv
load_dotenv()  # Load all environment variables

import google.generativeai as genai

# Configure GenAI Key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Define Your Prompt
prompt = [
    """
    You are an expert in converting English questions to SQL queries!
    Also, the SQL code should not have ``` in the beginning or end, and no 'sql' word in the output.
    We need a single query even if they are multiple inputs from the user.
    Always the query will end with a semicolon.
    """
]

def clean_sql_query(query):
    # Remove backticks and any leading/trailing whitespace
    return query.replace('```', '').strip()

def get_gemini_response(question, prompt):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content([prompt[0], question])
    return response.text

# Main execution flow for terminal-based interaction
if __name__ == "__main__":
    while True:
        question = input("Input your question (or type 'exit' to quit): ")

        if question.lower() == "exit":
            break

        # Get the AI-generated SQL query
        response = get_gemini_response(question, prompt)
        cleaned_response = clean_sql_query(response)  # Clean the SQL query

        # Display the generated SQL query
        print("\nGenerated SQL Query:")
        print(cleaned_response)
