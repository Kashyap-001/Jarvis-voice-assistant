import speech_recognition as sr
import webbrowser
from gtts import gTTS
import os
import time
import pygame
from groq import Groq
from musicLibrary import music
import requests

# Initialize recognizer and pygame mixer once globally
recognizer = sr.Recognizer()
pygame.mixer.init()

# Initialize Groq client with your Groq API key (replace with your valid key)
client = Groq(api_key="gsk_your_actual_api_key_here")

# Optional: Your NewsAPI key (replace or remove news commands if not used)
newsapi = "<Your NewsAPI Key>"

def speak(text):
    print(f"Speaking: {text}")  # Debug output
    tts = gTTS(text=text, lang='en')
    filename = "temp_audio.mp3"
    tts.save(filename)

    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()

    # Wait until playback finishes
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)

    # Additional delay to release file lock on Windows
    time.sleep(0.7)

    os.remove(filename)
    time.sleep(0.3)

def aiProcess(command):
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a virtual assistant named Jarvis, skilled in general tasks. "
                        "Please keep answers short and clear, like Alexa and Google Assistant."
                    ),
                },
                {
                    "role": "user",
                    "content": command,
                }
            ],
            model="llama-3.3-70b-versatile",
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        print(f"Groq API error: {e}")
        return "Sorry, I am having trouble processing your request right now."

def processCommand(command):
    lower_c = command.lower()

    if "open google" in lower_c:
        webbrowser.open("https://www.google.com/")
        speak("Opening Google")
    elif "open youtube" in lower_c:
        webbrowser.open("https://www.youtube.com/")
        speak("Opening YouTube")
    elif "open insta" in lower_c:
        webbrowser.open("https://www.instagram.com/")
        speak("Opening Instagram")
    elif "open linkedin" in lower_c:
        webbrowser.open("https://www.linkedin.com/feed/")
        speak("Opening LinkedIn")
    elif lower_c.startswith("play "):
        song = lower_c[5:].strip()
        if song in music:
            link = music[song]
            webbrowser.open(link)
            speak(f"Playing {song}")
        else:
            speak(f"Sorry, I don't have the song {song} in the library.")
    elif "news" in lower_c and newsapi:
        try:
            r = requests.get(f"https://newsapi.org/v2/top-headlines?country=in&apiKey={newsapi}")
            if r.status_code == 200:
                data = r.json()
                articles = data.get('articles', [])
                if not articles:
                    speak("Sorry, no news articles found.")
                    return
                speak("Here are the top news headlines.")
                for article in articles[:5]:  # limit to first 5 headlines
                    speak(article.get('title', 'No title available'))
                    time.sleep(0.5)
            else:
                speak("Sorry, I could not get the news right now.")
        except Exception as e:
            print(f"News API error: {e}")
            speak("Error occurred while fetching news.")
    else:
        # Use Groq AI for all other commands
        output = aiProcess(command)
        speak(output)

if __name__ == "__main__":

    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)  # Calibrate ambient noise once
        speak("Initializing Jarvis...")

        while True:
            try:
                print("Listening for wake word 'Jarvis'...")
                audio = recognizer.listen(source, timeout=7, phrase_time_limit=7)

                try:
                    word = recognizer.recognize_google(audio)
                except sr.UnknownValueError:
                    print("Could not understand audio")
                    continue
                except sr.RequestError as e:
                    print(f"Could not request results; {e}")
                    continue

                print(f"Heard: {word}")

                if "jarvis" in word.lower():
                    speak("Yes sir.")
                    print("Jarvis Activated. Listening for command...")
                    audio = recognizer.listen(source, timeout=7, phrase_time_limit=7)

                    try:
                        command = recognizer.recognize_google(audio)
                    except sr.UnknownValueError:
                        speak("Sorry, I could not understand the command.")
                        continue
                    except sr.RequestError as e:
                        speak("Sorry, speech service is not available right now.")
                        continue

                    print(f"Command: {command}")
                    processCommand(command)

            except sr.WaitTimeoutError:
                print("Listening timed out while waiting for phrase to start")
                continue
            except Exception as e:
                print(f"Error: {e}")
                continue
