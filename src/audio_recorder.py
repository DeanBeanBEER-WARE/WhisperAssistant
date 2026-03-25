"""
Audio recording module.
Manages the recording state, captures audio from the microphone, and stores it in a queue.
"""
import logging
import queue
import sounddevice as sd
from config import SAMPLE_RATE, CHANNELS

openai_audio_queue = queue.Queue()
recording = False
stream = None

def audio_callback(indata, frames, time_info, status):
    """Callback function for the sounddevice input stream to capture audio chunks."""
    global recording
    if status:
        logging.warning(f'Sounddevice Status: {status}')
    if recording:
        openai_audio_queue.put(indata.copy())

def start_recording(active_mode):
    """Starts the audio recording stream using the default system input device."""
    global recording, stream
    if recording:
        logging.warning('Attempted to start recording while already recording.')
        return
    
    while not openai_audio_queue.empty():
        openai_audio_queue.get_nowait()
        
    recording = True
    logging.info(f'Starting audio stream for mode: {active_mode} (Default Input Device)...')
    try:
        stream = sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS, callback=audio_callback, blocksize=int(SAMPLE_RATE / 5), device=None, latency=None)
        stream.start()
        logging.info('Recording started...')
    except Exception as e:
        logging.error(f'Error starting recording: {e}')
        recording = False

def stop_recording():
    """Stops the audio recording stream."""
    global recording, stream
    if not recording:
        return
    recording = False
    logging.info('Stopping audio stream...')
    if stream:
        stream.stop()
        stream.close()
        stream = None

def emergency_reset():
    """Stops recording and clears the audio queue."""
    global recording
    logging.warning('Performing emergency reset of the audio system!')
    stop_recording()
    while not openai_audio_queue.empty():
        openai_audio_queue.get_nowait()
