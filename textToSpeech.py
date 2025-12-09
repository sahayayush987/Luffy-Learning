import streamlit as st
from io import BytesIO
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

client = OpenAI()

class TextToSpeech:

    @staticmethod
    def text_to_speech(text: str) -> BytesIO:
        try:
            speech_file = BytesIO()

            response = client.audio.speech.create(
                model="gpt-4o-mini-tts", 
                voice="alloy",            
                input=text
            )

            audio_bytes = response.read()
            speech_file.write(audio_bytes)
            speech_file.seek(0)
            return speech_file
        except Exception as e:
            st.error(f"Audio generation failed: {e}")
            return None
