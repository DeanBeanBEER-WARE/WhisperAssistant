"""
Configuration module for the whisper voice-to-text project.
Loads environment variables and defines constant parameters for the application.
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables based on execution context (PyInstaller or script)
if getattr(sys, 'frozen', False):
    application_path = sys._MEIPASS
else:
    # Go up one level since config is in src/
    application_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

env_path = os.path.join(application_path, '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')

SAMPLE_RATE = 16000
CHANNELS = 1
AUDIO_TIMEOUT_SECONDS = 30
STREAM_STOP_TIMEOUT = 3
DELAY_MULTIPLIER = 0.005
API_TIMEOUT_SECONDS = 60

WHISPER_MODEL = 'whisper-1'
CHATGPT_MODEL = 'gpt-4o-mini'
MATH_MODEL = 'o3-mini'

CHATGPT_SYSTEM_PROMPT = 'You are a precise assistant. Answer directly and without unnecessary context or explanations.\nIf asked to translate something, provide only the translation.\nAlways answer in the target language requested, without additional comments.\nYou have access to the user\'s clipboard content, if it is relevant.'
MATH_SYSTEM_PROMPT = 'You are a precise assistant for mathematical tasks.\nReturn only the numerical result, without explanations or intermediate steps.'
MODEL_SELECTION_PROMPT = 'You are an assistant that decides whether a request is a mathematical task.\nAnswer only with "MATH" if it is a mathematical task, or "GENERAL" for all other requests.\nNote: A mathematical task contains numbers and mathematical operations (addition, subtraction, multiplication, division).\nAnswer only with one of the two words, without further explanations.'
