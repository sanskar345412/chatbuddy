import speech_recognition as sr

print("🔍 Scanning for available microphones...\n")

mic_list = sr.Microphone.list_microphone_names()
if not mic_list:
    print("❌ No microphones found. Make sure your mic is connected and not muted.")
else:
    for index, name in enumerate(mic_list):
        print(f"{index}: {name}")
