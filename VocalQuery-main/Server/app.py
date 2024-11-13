from flask import Flask, request, jsonify
import psycopg2
import os
import sounddevice as sd
import numpy as np
from google.cloud import speech
import google.generativeai as genai
from dotenv import load_dotenv

from flask_cors import CORS

app = Flask(__name__)
CORS(app)  #

# Load environment variables
load_dotenv()
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'Google-SpeechToText-API-Credentials.json'

# Initialize Flask app

# Configure Google Generative AI Key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Google Speech-to-Text Client
client = speech.SpeechClient()

# Function to clean the generated SQL query
def clean_sql_query(query):
    return query.replace('```', '').strip()

# Function to get SQL query from Google Gemini API based on input text
def get_gemini_response(question, prompt):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content([prompt[0], question])
    return response.text

# Transcribe the recorded audio using Google Speech-to-Text
# Transcribe the recorded audio using Google Speech-to-Text
def transcribe_audio(audio_data, sample_rate):
    # Convert the audio to bytes directly (no need to call .read())
    audio_content = speech.RecognitionAudio(content=audio_data)

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,  # Specify the correct encoding
        sample_rate_hertz=48000,  # Match the actual sample rate
        language_code="en-US",
    )

    # Send the request to Google Speech-to-Text API
    response = client.recognize(request={"config": config, "audio": audio_content})

    # Extract the transcript from the response
    for result in response.results:
        transcript = result.alternatives[0].transcript
        print(transcript)
        return transcript



@app.route('/transcribe_audio', methods=['POST'])
def transcribe():
    # Get the audio data from the request
    audio_data = request.files['audio'].read()
    sample_rate = int(request.form['sample_rate'])

    # Transcribe the audio
    transcript = transcribe_audio(audio_data, sample_rate)

    # Generate the SQL query using the transcribed text
    if transcript:
        prompt = """
        give only query dont mention sql word
        You are an expert in converting English questions to Postgresql SQL queries!
        Also, the SQL code should not have ``` in the beginning or end, and no 'sql' word in the output.
        We need a single query even if there are multiple inputs from the user.
        Always the query will end with a semicolon.
        ex:
        sql -- no nede of this sql word
            CREATE TABLE human ();
        """
        response = get_gemini_response(transcript, prompt)
        cleaned_response = clean_sql_query(response)

        return jsonify({
            "transcription": transcript,
            "sql_query": cleaned_response
        })
    else:
        return jsonify({"error": "Transcription failed"}), 400

@app.route('/execute_query', methods=['POST'])
def execute_query():
    data = request.json
    sql_query = data.get('sql_query')

    if sql_query:
        # Establish database connection
        conn = psycopg2.connect(
            dbname="VocalQuery",
            user="postgres",
            password="YOUR-PASSWORD",
            host="localhost",
            port="5432"
        )

        cur = conn.cursor()
        try:
            cur.execute(sql_query)
            conn.commit()
            return jsonify({"status": "success"})
        except Exception as e:
            conn.rollback()
            return jsonify({"status": "error", "message": str(e)}), 500
        finally:
            cur.close()
            conn.close()
    else:
        return jsonify({"error": "No query provided"}), 400

if __name__ == "__main__":
    app.run(debug=True)
