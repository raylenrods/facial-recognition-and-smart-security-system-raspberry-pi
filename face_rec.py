#! /usr/bin/python

# import the necessary packages
from imutils.video import VideoStream
from imutils.video import FPS
import face_recognition
import imutils
import pickle
import time
import cv2
import requests


import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders


import RPi.GPIO as GPIO #import the GPIO library
from mfrc522 import SimpleMFRC522
import multiprocessing
from multiprocessing import Queue

GPIO.setmode(GPIO.BOARD)
LED=32
DOOR=31
GPIO.setup(DOOR, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(LED, GPIO.OUT)
GPIO.setup(11, GPIO.IN)

           
state = multiprocessing.Value("i")


def rfid(state):
    reader = SimpleMFRC522()
    while True:
        try: 
                id, text = reader.read()
                state.value=not state.value
                print("Toggled")
                time.sleep(1)
        finally:
                print("")
                
def doorSensor(state):
    flag=False
    while True:
        if state.value==1:
            GPIO.output(LED,GPIO.HIGH)
            requests.get("http://blynk-cloud.com/Z7mMUrhdRn0-cj6n5RzO_Q01NIgYposl/update/V3?value=255")
            if GPIO.input(DOOR):
                print("Door is open")
                if flag == False:
                    requests.get('https://maker.ifttt.com/trigger/Door_open/with/key/FXZewkIElv6hx0xoyiXFS')
                flag=GPIO.input(DOOR)
                time.sleep(2)
            if GPIO.input(DOOR) == False:
                print("Door is closed")
                flag=GPIO.input(DOOR)
                time.sleep(2)
        else:
            GPIO.output(LED,GPIO.LOW)
            requests.get("http://blynk-cloud.com/Z7mMUrhdRn0-cj6n5RzO_Q01NIgYposl/update/V3?value=0")
            continue 

def blynk(state):
    flag=False
    while True:
        if GPIO.input(11) == True:
            while GPIO.input(11) == True:
                continue
            state.value=not state.value
        else:
            while GPIO.input(11) == False:
                continue
            state.value=not state.value


def snapshot(frame):

    img_counter=0
    img_name = "alert/alert_{}.jpg".format(img_counter)
    cv2.imwrite(img_name, frame)
   # print("{} written!".format(img_name))
    

def email():
    fromaddr = "rrs017@chowgules.ac.in"
    toaddr = "raylenrods@gmail.com"

    # instance of MIMEMultipart
    msg = MIMEMultipart()

    # storing the senders email address
    msg['From'] = fromaddr
    # storing the receivers email address
    msg['To'] = toaddr
    # storing the subject
    msg['Subject'] = "Intruder Alert!!"
    # string to store the body of the mail
    body = "An unknown person has been detected. Please check the attatched image."

    # attach the body with the msg instance
    msg.attach(MIMEText(body, 'plain'))

    # open the file to be sent
    filename = "alert_0.jpg"
    attachment = open("/home/pi/Face Recognition/alert/"+filename, "rb")

    # instance of MIMEBase and named as p
    p = MIMEBase('application', 'octet-stream')

    # To change the payload into encoded form
    p.set_payload((attachment).read())
    # encode into base64
    encoders.encode_base64(p)

    p.add_header('Content-Disposition', "attachment; filename= %s" % filename)

    # attach the instance 'p' to instance 'msg'
    msg.attach(p)

    # creates SMTP session
    s = smtplib.SMTP('smtp.gmail.com', 587)

    # start TLS for security
    s.starttls()

    # Authentication
    s.login(fromaddr,"raylen1503")

    # Converts the Multipart msg into a string
    text = msg.as_string()

    # sending the mail
    s.sendmail(fromaddr, toaddr, text)
    print("Email sent")
    # terminating the session
    s.quit()
        


state.value=1
p1 = multiprocessing.Process(target=rfid, args=(state,))
p2 = multiprocessing.Process(target=doorSensor, args=(state,))
p3 = multiprocessing.Process(target=blynk, args=(state,))

p1.start()
p2.start()
p3.start()    


#Initialize 'currentname' to trigger only when a new person is identified.
currentname = "unknown"
encodingsP = "encodings.pickle"
cascade = "haarcascade_frontalface_default.xml"

# load the known faces and embeddings along with OpenCV's Haar cascade for face detection
print("[INFO] loading encodings + face detector…")
data = pickle.loads(open(encodingsP, "rb").read())
detector = cv2.CascadeClassifier(cascade)

# initialize the video stream and allow the camera sensor to warm up
print("[INFO] starting video stream…")
vs = VideoStream(src=0).start()
time.sleep(2.0)

fps = FPS().start()

# loop over frames from the video file stream
while True:
	frame = vs.read()
	frame = imutils.resize(frame, width=500)
	
	# convert the input frame from BGR to grayscale
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

	# detect faces in the grayscale frame
	rects = detector.detectMultiScale(gray, scaleFactor=1.1, 
		minNeighbors=5, minSize=(30, 30),
		flags=cv2.CASCADE_SCALE_IMAGE)

	
	boxes = [(y, x + w, y + h, x) for (x, y, w, h) in rects]

	# compute the facial embeddings for each face bounding box
	encodings = face_recognition.face_encodings(rgb, boxes)
	names = []

	# loop over the facial embeddings
	for encoding in encodings:
		# attempt to match each face in the input image to our known
		# encodings
		matches = face_recognition.compare_faces(data["encodings"],
			encoding)
		name = "Unknown" #if face is not recognized, then print Unknown
		
		#snapshot()


		# check to see if we have found a match
		
		if True in matches:
			# find the indexes of all matched faces then initialize a
			
			# dictionary to count the total number of times each face
			# was matched
			matchedIdxs = [i for (i, b) in enumerate(matches) if b]
			counts = {}

			# loop over the matched indexes and maintain a count for
			# each recognized face face
			for i in matchedIdxs:
				name = data["names"][i]
				counts[name] = counts.get(name, 0) + 1

			# determine the recognized face with the largest number of votes
			name = max(counts, key=counts.get)
			
			#If someone in your dataset is identified, print their name
			if currentname != name:
				currentname = name
				print(currentname)
				

		else:
			print("Unknown")
			if state.value==1:
				requests.get('https://maker.ifttt.com/trigger/Intruder/with/key/FXZewkIElv6hx0xoyiXFS')
				time.sleep(2)
				snapshot(frame)
				email()
			else:
				continue                
			
		# update the list of names
		names.append(name)
		

	# loop over the recognized faces
	for ((top, right, bottom, left), name) in zip(boxes, names):
		# draw the predicted face name on the image – color is in BGR
		cv2.rectangle(frame, (left, top), (right, bottom),
			(0, 255, 0), 2)
		y = top - 15 if top - 15 > 15 else top + 15
		cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX,
			.8, (255, 0, 0), 2)

	# display the image to our screen
	cv2.imshow("Facial Recognition is Running", frame)
	key = cv2.waitKey(1) & 0xFF

	# quit when 'q' key is pressed
	if key == ord("q"):
		break

	# update the FPS counter
	fps.update()

# stop the timer and display FPS information
fps.stop()

print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

# do a bit of cleanup
cv2.destroyAllWindows()
vs.stop()





