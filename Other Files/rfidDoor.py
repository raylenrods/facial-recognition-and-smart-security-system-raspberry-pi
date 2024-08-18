import RPi.GPIO as GPIO #import the GPIO library
import time
from mfrc522 import SimpleMFRC522
import requests
import multiprocessing
from multiprocessing import Queue

GPIO.setmode(GPIO.BOARD)
GPIO.setup(31, GPIO.IN, pull_up_down=GPIO.PUD_UP)

state = multiprocessing.Value("i")


def rfid(state):
    reader = SimpleMFRC522()
    while True:
        try:
                id, text = reader.read()
                state.value=not state.value
                print(text)
                time.sleep(1)
        finally:
                print("Finally")
                
def doorSensor(state):
    flag=False
    while True:
        if state.value==1:
            if GPIO.input(31):
                print("Door is open")
                if flag == False:
                    requests.get('https://maker.ifttt.com/trigger/Door_open/with/key/FXZewkIElv6hx0xoyiXFS')
                flag=GPIO.input(31)
                time.sleep(2)
            if GPIO.input(31) == False:
                print("Door is closed")
                flag=GPIO.input(31)
                time.sleep(2)        
        else:
            continue    
    
    
state.value=1
p1 = multiprocessing.Process(target=rfid, args=(state,))
p2 = multiprocessing.Process(target=doorSensor, args=(state,))
p1.start()
p2.start()



 
        


