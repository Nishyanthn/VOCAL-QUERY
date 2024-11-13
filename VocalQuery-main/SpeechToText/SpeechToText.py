import os
import io
import numpy as np
import sounddevice as sd
from google.cloud import speech

# Setting Google credentials
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'Google-SpeechToText-API-Credentials.json'

# Create a client instance
client = speech.SpeechClient()

# Audio recording parameters
duration = 10  # seconds
sample_rate = 16000  # sample rate of the audio

def record_audio(duration, sample_rate):
    print("Recording...")
    audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='int16')
    sd.wait()  # Wait until recording is finished
    print("Recording complete.")
    return audio

def transcribe_audio(audio):
    # Convert the audio to bytes
    audio_bytes = audio.tobytes()
    audio_content = speech.RecognitionAudio(content=audio_bytes)

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=sample_rate,
        language_code="en-US",
    )

    # Send the request to Google to transcribe the audio
    response = client.recognize(request={"config": config, "audio": audio_content})

    # Read the response
    for result in response.results:
        print("Transcript: {}".format(result.alternatives[0].transcript))

# Record audio from the microphone
audio_data = record_audio(duration, sample_rate)

# Transcribe the recorded audio
transcribe_audio(audio_data)
