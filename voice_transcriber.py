import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import whisper
import torchaudio

# Record audio from mic and save it
def record_audio(duration=5, filename="recorded_audio.wav"):
    print("Recording... Speak now!")
    samplerate = 16000  # Whisper expects 16kHz
    recording = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype="int16")
    sd.wait()
    wav.write(filename, samplerate, recording)
    print("Recording complete.")

# Transcribe using Whisper without FFmpeg
def transcribe_with_whisper(audio_path="recorded_audio.wav"):
    print("Transcribing using Whisper...")
    model = whisper.load_model("base")
    
    # Use torchaudio instead of ffmpeg
    waveform, sample_rate = torchaudio.load(audio_path)
    audio = whisper.pad_or_trim(waveform[0].numpy())
    
    mel = whisper.log_mel_spectrogram(audio).to(model.device)
    options = whisper.DecodingOptions()
    result = whisper.decode(model, mel, options)
    
    return result.text

# Main logic
if __name__ == "__main__":
    record_audio()
    transcription = transcribe_with_whisper()
    print("Transcription:")
    print(transcription)




