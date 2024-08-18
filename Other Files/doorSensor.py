import RPi.GPIO as GPIO #import the GPIO library
import time
import requests 

GPIO.setmode(GPIO.BOARD)
GPIO.setup(31, GPIO.IN, pull_up_down=GPIO.PUD_UP)

name = "Raylen"
print("Hello " + name)
flag=False

while True:
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