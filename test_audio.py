import speech_recognition as sr

r = sr.Recognizer()

with sr.AudioFile("test.mp3") as source:
    audio = r.record(source)

text = r.recognize_google(audio)

print("Detected speech:")
print(text)
