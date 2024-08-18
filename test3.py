import RPi.GPIO as GPIO #import the GPIO library
GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.IN)


while True:
    if GPIO.input(11) == True:
        print("on")
    else:
        print("off")