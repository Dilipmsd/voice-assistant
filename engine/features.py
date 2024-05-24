import os
from pipes import quote
import re
import sqlite3
import struct
import subprocess
import time
import webbrowser
from playsound import playsound
import eel
import pyaudio
import pyautogui
from engine.command import speak
from engine.config import ASSISTANT_NAME
# Playing assiatnt sound function
import pywhatkit as kit
import pvporcupine
import datefinder
import datetime

from engine.helper import extract_yt_term, remove_words
from hugchat import hugchat

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

con = sqlite3.connect("jarvis.db")
cursor = con.cursor()

@eel.expose
def playAssistantSound():
    music_dir = "www/assets/audio/start_sound.mp3"
    playsound(music_dir)

    
def openCommand(query):
    query = query.replace(ASSISTANT_NAME, "")
    query = query.replace("open", "")
    query.lower()

    app_name = query.strip()

    if app_name != "":

        try:
            cursor.execute(
                'SELECT path FROM sys_command WHERE name IN (?)', (app_name,))
            results = cursor.fetchall()

            if len(results) != 0:
                speak("Opening "+query)
                os.startfile(results[0][0])

            elif len(results) == 0: 
                cursor.execute(
                'SELECT url FROM web_command WHERE name IN (?)', (app_name,))
                results = cursor.fetchall()
                
                if len(results) != 0:
                    speak("Opening "+query)
                    webbrowser.open(results[0][0])

                else:
                    speak("Opening "+query)
                    try:
                        os.system('start '+query)
                    except:
                        speak("not found")
        except:
            speak("some thing went wrong")

       

def PlayYoutube(query):
    print("youtube selected")
    search_term = extract_yt_term(query)
    print("youtube selected2", search_term)
    os.system(f'say "Playing {search_term}  on YouTube"')
    kit.playonyt(search_term)  


def hotword():
    porcupine=None
    paud=None
    audio_stream=None
    try:
       
        # pre trained keywords    
        porcupine=pvporcupine.create(keywords=["jarvis","alexa"]) 
        paud=pyaudio.PyAudio()
        audio_stream=paud.open(rate=porcupine.sample_rate,channels=1,format=pyaudio.paInt16,input=True,frames_per_buffer=porcupine.frame_length)
        
        # loop for streaming
        while True:
            keyword=audio_stream.read(porcupine.frame_length)
            keyword=struct.unpack_from("h"*porcupine.frame_length,keyword)

            # processing keyword comes from mic 
            keyword_index=porcupine.process(keyword)

            # checking first keyword detetcted for not
            if keyword_index>=0:
                print("hotword detected")

                # pressing shorcut key win+j
                import pyautogui as autogui
                autogui.keyDown("win")
                autogui.press("j")
                time.sleep(2)
                autogui.keyUp("win")
                
    except:
        if porcupine is not None:
            porcupine.delete()
        if audio_stream is not None:
            audio_stream.close()
        if paud is not None:
            paud.terminate()



# find contacts
def findContact(query):
    
    words_to_remove = [ASSISTANT_NAME, 'make', 'a', 'to', 'phone', 'call', 'send', 'message', 'wahtsapp', 'video']
    query = remove_words(query, words_to_remove)

    try:
        query = query.strip().lower()
        cursor.execute("SELECT mobile_no FROM contacts WHERE LOWER(name) LIKE ? OR LOWER(name) LIKE ?", ('%' + query + '%', query + '%'))
        results = cursor.fetchall()
        print(results[0][0])
        mobile_number_str = str(results[0][0])

        if not mobile_number_str.startswith('+91'):
            mobile_number_str = '+91' + mobile_number_str

        return mobile_number_str, query
    except:
        speak('not exist in contacts')
        return 0, 0
    
def whatsApp(mobile_no, message, flag, name):
    

    if flag == 'message':
        target_tab = 12
        jarvis_message = "message send successfully to "+name

    elif flag == 'call':
        target_tab = 7
        message = ''
        jarvis_message = "calling to "+name

    else:
        target_tab = 6
        message = ''
        jarvis_message = "staring video call with "+name


    # Encode the message for URL
    encoded_message = quote(message)
    print(encoded_message)
    # Construct the URL
    whatsapp_url = f"whatsapp://send?phone={mobile_no}&text={encoded_message}"

    # Construct the full command
    full_command = f'start "" "{whatsapp_url}"'

    # Open WhatsApp with the constructed URL using cmd.exe
    subprocess.run(full_command, shell=True)
    time.sleep(5)
    subprocess.run(full_command, shell=True)
    
    pyautogui.hotkey('ctrl', 'f')

    for i in range(1, target_tab):
        pyautogui.hotkey('tab')

    pyautogui.hotkey('enter')
    speak(jarvis_message)


# chat bot 
def chatBot(query):
    user_input = query.lower()
    chatbot = hugchat.ChatBot(cookie_path="engine\cookies.json")
    id = chatbot.new_conversation()
    chatbot.change_conversation(id)
    response =  chatbot.chat(user_input)
    print(response)
    speak(response)
    return response


def play_first_song(query):
    print("coming here")
        # Initialize a WebDriver instance (make sure to have the appropriate browser driver installed)
    driver = webdriver.Chrome()  # Using Chrome WebDriver

        # Search YouTube for the query
    search_url = "https://www.youtube.com/results?search_query=" + query
    print("Navigating to:", search_url)
    driver.get(search_url)

        # Find the first video link
    video_link = driver.find_element(By.CSS_SELECTOR, "#contents ytd-video-renderer #video-title")
    print("Found video link:", video_link.get_attribute("href"))

        # Click on the video link
    video_link.click()

        # Optionally, you might need to handle age verification pop-ups or consent forms here

        # Add a delay to allow the video to start playing
    time.sleep(500000)  # Adjust the delay time as needed

        # Play the video (simulate pressing the 'k' key)
    webdriver.ActionChains(driver).send_keys(Keys.SPACE).perform()

        # Keep the program running for a while to allow the video to play
    time.sleep(30000)  # Adjust the time as needed

def search_google(query):
    url = f"https://www.google.com/search?q={query}"
    webbrowser.open_new_tab(url)

def alarm():
    from engine.command import takecommand
    query = takecommand()
    if query:
        # Find all date and time matches in the text
        dTimeA = list(datefinder.find_dates(query))

        # Iterate over each match
        for mat in dTimeA:
            print(mat)
            speak("your reminder is at"+mat)
            # Extract hour and minute from the match
            hourA = mat.hour
            minA = mat.minute

            # Check if the alarm time matches the current time
            while True:
                if hourA == datetime.datetime.now().hour and minA == datetime.datetime.now().minute:
                    print("Alarm is running")
                    speak("Alarm is running")
                    # Play the sound (replace the path with the correct one)
                    playsound("/Users/dilipbganesh/Downloads/funk-in-kingdom-200507.mp3", True)
                elif minA < datetime.datetime.now().minute:
                    break

# def select_language():
#     say("Which language would you like to translate to?")
#     say("You can say: 'Spanish', 'French', or 'German'")
    
#     recognizer = sr.Recognizer()
    
#     with sr.Microphone() as source:
#         say("Listening for language choice...")
#         audio = recognizer.listen(source)
    
#     try:
#         choice = recognizer.recognize_google(audio)
#         print("You chose:", choice)
        
#         language_map = {'spanish': 'es', 'french': 'fr', 'german': 'de'}
#         target_language = language_map.get(choice.lower())
        
#         if target_language:
#             return target_language
#         else:
#             print("Sorry, couldn't recognize the language. Defaulting to English.")
#             return 'en'
        
#     except sr.UnknownValueError:
#         print("Sorry, could not understand audio.")
#         return 'en'
#     except sr.RequestError as e:
#         print("Could not request results; {0}".format(e))
#         return 'en'
#     except Exception as e:
#         print("Error occurred; {0}".format(e))
#         return 'en'

# # def speak_text(text):
# #     subprocess.call(['say', '-v', 'Alex', text])  # Adjust 'Alex' to the desired voice
    
# def listen_and_translate():
#     recognizer = sr.Recognizer()
#     translator = Translator()
    
#     with sr.Microphone() as source:
#         print("Listening...")
#         audio = recognizer.listen(source)
#         print("Recognizing...")
    
#     try:
#         text = recognizer.recognize_google(audio)
#         print("You said:", text)
        
#         target_language = select_language()
#         translated_text = translator.translate(text, dest=target_language).text
#         print("Translated text:", translated_text)
        
#         say(translated_text)
        
#     except sr.UnknownValueError:
#         print("Sorry, could not understand audio.")
#     except sr.RequestError as e:
#         print("Could not request results; {0}".format(e))
#     except Exception as e:
#         print("Error occurred; {0}".format(e))

# listen_and_translate()