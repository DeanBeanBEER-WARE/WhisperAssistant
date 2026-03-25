"""
System utilities module.
Provides functions for interacting with macOS APIs such as reading the clipboard and simulating keystrokes via AppleScript.
"""
import time
import string
import logging
import subprocess

def get_clipboard_content():
    """Reads the current content of the system clipboard natively via macOS terminal tools."""
    try:
        result = subprocess.run(['pbpaste'], capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except Exception as e:
        logging.error(f"Error reading clipboard: {e}")
        return None

def type_text(text_to_type, is_live=False):
    """Types the given text automatically at the current cursor position using macOS system events. 
    It supports a hybrid approach: fast character-by-character typing for short text and clipboard pasting for long text."""
    if not text_to_type:
        if not is_live:
            logging.warning('No text to type.')
        return
    
    logging.info(f"Typing text ({'Live' if is_live else 'Batch'}): '{text_to_type[:100]}...'")
    simulate_enter = False
    
    final_text = text_to_type.rstrip()
    
    if not is_live:
        words = final_text.split()
        if words:
            last_word_clean = words[-1].strip(string.punctuation)
            if last_word_clean.lower() == 'enter':
                logging.info("Trigger word 'Enter' detected at the end.")
                final_text = ' '.join(words[:-1]).rstrip(string.punctuation).rstrip()
                simulate_enter = True
            else:
                final_text = final_text + ' '
                logging.info("Space appended at the end for fluent typing.")
    
    if final_text:
        if len(final_text) <= 50:
            logging.info(f"Short text ({len(final_text)} characters), using character-by-character method.")
            for char in final_text:
                escaped_char = char.replace('\\', '\\\\').replace('"', '\\"')
                osascript_command = f'tell application "System Events" to keystroke "{escaped_char}"'
                subprocess.run(['osascript', '-e', osascript_command], capture_output=True, text=True)
                time.sleep(0.003)
        else:
            logging.info(f"Long text ({len(final_text)} characters), using clipboard method.")
            try:
                old_clipboard = subprocess.run(['pbpaste'], capture_output=True, text=True, check=False).stdout
                
                process = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE, text=True)
                process.communicate(input=final_text)
                
                subprocess.run(['osascript', '-e', 'tell application "System Events" to keystroke "v" using command down'], capture_output=True, text=True)
                
                time.sleep(0.05)
                
                process = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE, text=True)
                process.communicate(input=old_clipboard)
                
                logging.info("Clipboard method successful, original clipboard restored.")
            except Exception as e:
                logging.error(f"Error with clipboard method: {e}, falling back to keystroke")
                escaped_text = final_text.replace('\\', '\\\\').replace('"', '\\"')
                osascript_command = f'tell application "System Events" to keystroke "{escaped_text}"'
                subprocess.run(['osascript', '-e', osascript_command], capture_output=True, text=True)
        
        if not is_live:
            time.sleep(0.05)
            
    if simulate_enter:
        subprocess.run(['osascript', '-e', 'tell application "System Events" to key code 36'], capture_output=True, text=True)
        logging.info('Enter successfully simulated.')
