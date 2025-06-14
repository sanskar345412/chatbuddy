import sounddevice as sd
import numpy as np

def callback(indata, frames, time, status):
    if status:
        print("Status:", status)
    volume_norm = np.linalg.norm(indata) * 10
    print("Mic input level:", volume_norm)

try:
    print("Listening for 5 seconds... Speak now.")
    with sd.InputStream(callback=callback):
        sd.sleep(5000)  # record for 5 seconds
    print("Test complete.")
except Exception as e:
    print("Error accessing microphone:", e)
