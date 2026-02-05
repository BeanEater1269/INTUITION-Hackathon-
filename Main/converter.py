import pyttsx3
import speech_recognition as sr

def textToSpeech(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def speechToText():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        audio = recognizer.listen(source)
    text = recognizer.recognize_google(audio)
    return text