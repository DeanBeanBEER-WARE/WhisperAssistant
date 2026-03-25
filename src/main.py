"""
Main application module.
Initializes the application, listens for keyboard events to trigger recording,
and coordinates the audio processing, API calls, and text typing.
"""
import os
import tempfile
import threading
import logging
import numpy as np
import soundfile as sf
from pynput import keyboard

from config import SAMPLE_RATE
import audio_recorder
from openai_api import call_whisper, call_chatgpt
from system_utils import get_clipboard_content, type_text

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

pressed_keys = set()
active_mode = None

def check_whisper_keys_pressed(current_keys):
    """Checks if the keyboard combination for Whisper transcription (Ctrl + Alt) is pressed."""
    ctrl_pressed = any(k in current_keys for k in [keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r])
    alt_pressed = any(k in current_keys for k in [keyboard.Key.alt, keyboard.Key.alt_l, keyboard.Key.alt_r, keyboard.Key.alt_gr])
    return ctrl_pressed and alt_pressed

def check_chatgpt_keys_pressed(current_keys):
    """Checks if the keyboard combination for ChatGPT processing (Ctrl + Cmd) is pressed."""
    ctrl_pressed = any(k in current_keys for k in [keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r])
    cmd_pressed = any(k in current_keys for k in [keyboard.Key.cmd, keyboard.Key.cmd_l, keyboard.Key.cmd_r])
    return ctrl_pressed and cmd_pressed

def process_audio(mode_at_start):
    """Processes the recorded audio depending on the active mode (Whisper only or ChatGPT pipeline)."""
    logging.info(f'Processing audio for OpenAI (Mode: {mode_at_start})...')
    audio_blocks = []
    while not audio_recorder.openai_audio_queue.empty():
        audio_blocks.append(audio_recorder.openai_audio_queue.get_nowait())
    
    if not audio_blocks:
        logging.warning('No audio data recorded.')
        return
        
    temp_filename = ''
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_audio:
            temp_filename = temp_audio.name
            audio_np = np.concatenate(audio_blocks, axis=0)
            sf.write(temp_filename, audio_np, SAMPLE_RATE, subtype='PCM_16')
            
        transcribed_text = call_whisper(temp_filename)
        if not transcribed_text:
            logging.error('Transcription failed.')
            return
            
        if mode_at_start == 'chatgpt':
            clipboard_content = get_clipboard_content()
            if clipboard_content and len(clipboard_content) > 10000:
                clipboard_content = clipboard_content[:10000] + "... [Text truncated]"
                
            final_text = call_chatgpt(transcribed_text, clipboard_content)
        else:
            final_text = transcribed_text
            
        if final_text:
            type_text(final_text)
    finally:
        if temp_filename and os.path.exists(temp_filename):
            os.remove(temp_filename)

def on_press(key):
    """Handles keyboard press events to detect hotkey combinations and start recording."""
    global active_mode
    pressed_keys.add(key)
    if not audio_recorder.recording:
        if check_chatgpt_keys_pressed(pressed_keys):
            active_mode = 'chatgpt'
            audio_recorder.start_recording(active_mode)
        elif check_whisper_keys_pressed(pressed_keys):
            active_mode = 'whisper_only'
            audio_recorder.start_recording(active_mode)

def on_release(key):
    """Handles keyboard release events to stop recording and trigger processing."""
    global active_mode
    if key in pressed_keys:
        pressed_keys.remove(key)
        
    if audio_recorder.recording:
        mode_to_process = active_mode
        released_valid = False
        
        if mode_to_process == 'chatgpt':
            if not check_chatgpt_keys_pressed(pressed_keys):
                released_valid = True
        elif mode_to_process == 'whisper_only':
            if not check_whisper_keys_pressed(pressed_keys):
                released_valid = True
        
        if released_valid:
            audio_recorder.stop_recording()
            threading.Thread(target=process_audio, args=(mode_to_process,)).start()
            active_mode = None
            
    try:
        if hasattr(key, 'char') and key.char == '^':
            audio_recorder.emergency_reset()
        elif key == keyboard.Key.esc:
            if audio_recorder.recording:
                audio_recorder.emergency_reset()
    except Exception:
        pass

def main():
    """Main application entry point. Initializes keyboard listener and displays status messages."""
    logging.info('Speech processing started.')
    logging.info('Hold Ctrl + Alt (Option) for Whisper transcription.')
    logging.info('Hold Ctrl + Cmd for GPT-4o / o1 processing (Whisper -> GPT).')
    logging.info('The system automatically uses the clipboard content (Cmd+C) as context.')
    logging.info('Emergency reset key: ^ or ESC')
    logging.info('Default input device is used automatically.')
    logging.info('Release keys to process.')
    
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

if __name__ == '__main__':
    main()
