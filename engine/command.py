import pyttsx3
import speech_recognition as sr
import eel
import time
import datetime
import wikipedia
import requests
from GoogleNews import GoogleNews

from engine.features import * 

chatStr = ""
googlenews = GoogleNews()
def speak(text):
    os.system(f'say "{text}"')

def takecommand():

    r = sr.Recognizer()

    with sr.Microphone() as source:
        print('listening....')
        eel.DisplayMessage('listening....')
        r.pause_threshold = 1
        r.adjust_for_ambient_noise(source)
        
        audio = r.listen(source, 10, 6)

    try:
        print('recognizing')
        eel.DisplayMessage('recognizing....')
        query = r.recognize_google(audio, language='en-in')
        print(f"user said: {query}")
        eel.DisplayMessage(query)
        time.sleep(2)
       
    except Exception as e:
        return ""
    
    return query.lower()

@eel.expose
def allCommands(message=1):

    if message == 1:
        query = takecommand()
        print(query)
        eel.senderText(query)
    else:
        query = message
        eel.senderText(query)
    try:

        if "play song" in query:
            print("playing song:", query)
            from engine.features import play_first_song
            play_first_song(query)

        elif "open music" in query:
            musicPath = "/Users/dilipbganesh/Downloads/funk-in-kingdom-200507.mp3"
            os.system(f"open {musicPath}")

        elif "the time" in query:
            musicPath = "/Users/harry/Downloads/downfall-21371.mp3"
            hour = datetime.datetime.now().strftime("%H")
            min = datetime.datetime.now().strftime("%M")
            speak(f"Sir time is {hour}  {min} minutes")

        elif "search" in query:
            from engine.features import search_google
            search_google(query)

        elif "tell me about" in query:
            topic = query.replace("tell me about", "").strip()
            try:
                summary = wikipedia.summary(topic, sentences=2)
                print("Here is some information about", topic, ":", summary)
                speak(summary)
            except wikipedia.exceptions.DisambiguationError as e:
                speak(f"There are multiple options for {topic}. Please be more specific.")
            except wikipedia.exceptions.PageError as e:
                speak(f"Sorry, I couldn't find information about {topic}.")

        elif 'tech' in query:
            speak("Getting news for you")
            googlenews.get_news('Tech')
            googlenews.result()
            a = googlenews.gettext()
            print(*a[1:5], sep=',')
            for line in a[:5]:
                speak(line)

        elif 'politics' in query:
            speak("Getting news for you")
            googlenews.get_news('Politics')
            googlenews.result()
            a = googlenews.gettext()
            print(*a[1:5], sep=',')
            for line in a[:5]:
                speak(line)

        elif 'sports' in query:
            os.system('say "Getting news for you"')
            googlenews.get_news('Sports')
            googlenews.result()
            a = googlenews.gettext()
            print(*a[1:5], sep=',')
            for line in a[:5]:
                speak(line)

        elif 'alarm' in query:
              alarm()

        elif 'open facetime' in query:
            os.system(f"open /System/Applications/FaceTime.app")

        elif 'open pass' in query:
            os.system(f"open /Applications/Passky.app")
            
        elif 'weather' in query:
            api_key = "bce789909c0d49c5aa0122318241404"  
            base_url = "http://api.weatherapi.com/v1/current.json"
            
            speak("Please tell me the city name.")
            city_name = takecommand()
            
            complete_url = f"{base_url}?key={api_key}&q={city_name}"
            response = requests.get(complete_url)
            
            if response.status_code == 200:
                data = response.json()
                temperature_celsius = data["current"]["temp_c"]
                weather_description = data["current"]["condition"]["text"]
                humidity = data["current"]["humidity"]
                wind_speed = data["current"]["wind_kph"]
                
                weather_info = f"The current weather in {city_name} is {temperature_celsius} degrees Celsius with {weather_description}. "
                weather_info += f"The humidity is {humidity} percent and the wind speed is {wind_speed} kilometers per hour."
                print(weather_info)
                speak(weather_info)
            else:
                print("Sorry, I couldn't fetch the weather information for that city.")
                speak("Sorry, I couldn't fetch the weather information for that city.")
        else:
            print("Chatting...")
            print(query)
            # chat(query)
    except:
        print("error")
    
    eel.ShowHood()
    
    
