"""
OpenAI API interaction module.
Handles HTTP requests to the Whisper and ChatGPT APIs using the provided configuration.
"""
import os
import requests
import certifi
import logging
from config import (
    OPENAI_API_KEY, WHISPER_MODEL, CHATGPT_MODEL, MATH_MODEL,
    API_TIMEOUT_SECONDS, CHATGPT_SYSTEM_PROMPT, MATH_SYSTEM_PROMPT, MODEL_SELECTION_PROMPT
)

def call_whisper(audio_filename):
    """Sends an audio file to the OpenAI Whisper API and returns the transcribed text."""
    logging.info(f'Sending to OpenAI Whisper API ({WHISPER_MODEL})...')
    url = 'https://api.openai.com/v1/audio/transcriptions'
    headers = {'Authorization': f'Bearer {OPENAI_API_KEY}'}
    try:
        with open(audio_filename, 'rb') as f:
            files = {'file': (os.path.basename(audio_filename), f, 'audio/wav')}
            data = {'model': WHISPER_MODEL}
            resp = requests.post(url, headers=headers, files=files, data=data, timeout=API_TIMEOUT_SECONDS, verify=certifi.where())
        resp.raise_for_status()
        return resp.json().get('text', '').strip()
    except Exception as e:
        logging.error(f'Whisper API error: {e}')
        return None

def call_chatgpt(prompt_text, clipboard_content=None):
    """Sends a text prompt and optional clipboard context to the OpenAI ChatGPT API.
    Determines if the prompt is a math problem to select the appropriate model."""
    logging.info('Sending prompt to OpenAI for model selection/response...')
    url = 'https://api.openai.com/v1/chat/completions'
    headers = {
        'Authorization': f'Bearer {OPENAI_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    full_prompt = prompt_text
    if clipboard_content:
        full_prompt = f"User Request: {prompt_text}\\n\\nContext from Clipboard:\\n{clipboard_content}"
        logging.info("Clipboard content added as context.")

    try:
        selection_payload = {
            'model': CHATGPT_MODEL,
            'messages': [
                {'role': 'system', 'content': MODEL_SELECTION_PROMPT},
                {'role': 'user', 'content': full_prompt}
            ]
        }
        selection_resp = requests.post(url, headers=headers, json=selection_payload, timeout=API_TIMEOUT_SECONDS, verify=certifi.where())
        selection_resp.raise_for_status()
        model_choice = selection_resp.json().get('choices', [{}])[0].get('message', {}).get('content', '').strip()
        logging.info(f'Model selection result: {model_choice}')
        
        if model_choice == 'MATH':
            logging.info('Mathematical task recognized, routing to o3-mini...')
            payload = {
                'model': MATH_MODEL,
                'messages': [
                    {'role': 'system', 'content': MATH_SYSTEM_PROMPT},
                    {'role': 'user', 'content': full_prompt}
                ]
            }
        else:
            logging.info('General task recognized, using GPT-4o...')
            payload = {
                'model': CHATGPT_MODEL,
                'messages': [
                    {'role': 'system', 'content': CHATGPT_SYSTEM_PROMPT},
                    {'role': 'user', 'content': full_prompt}
                ]
            }
        resp = requests.post(url, headers=headers, json=payload, timeout=API_TIMEOUT_SECONDS, verify=certifi.where())
        resp.raise_for_status()
        chat_response = resp.json().get('choices', [{}])[0].get('message', {}).get('content', '').strip()
        logging.info(f"ChatGPT response received: '{chat_response[:100]}...'")
        return chat_response
    except Exception as e:
        logging.error(f'ChatGPT API error: {e}')
        return None
