import os
import eel

from engine.features import *
from engine.command import *

def start():
    
    eel.init("www")

    playAssistantSound()


    os.system('open -a "Google Chrome" "http://localhost:8000/index.html"')

    eel.start('index.html', mode=None, host='localhost', block=True)