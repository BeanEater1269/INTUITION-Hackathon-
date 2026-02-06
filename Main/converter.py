import pyttsx3
import speech_recognition as sr

def textToSpeech(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def speechToText():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        audio = recognizer.listen(source)
    text = recognizer.recognize_google(audio)
    print("Recognized:", text)
    return text