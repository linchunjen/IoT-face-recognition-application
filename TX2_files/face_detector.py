# Reference from https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_objdetect/py_face_detection/py_face_detection.html
# Reference from W251 OH
# Reference from https://answers.opencv.org/question/202145/how-to-decode-by-imdecode/

import cv2
import numpy as np
import time
import paho.mqtt.client as paho

# connect internal TX2 broker
broker_ip = "172.18.0.2"

# check connection between face detector and broker
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connection estabilshed successfully with rc:" + str(rc))


# connect to MQTT broker  
client = paho.Client()
client.on_connect = on_connect
client.connect(broker_ip, 1883, 60)

# load the harrcascade for face detection
face_cascade = cv2.CascadeClassifier('/opencv/data/haarcascades/haarcascade_frontalface_default.xml')

# capture video from TX2 USB webcam. 
cap = cv2.VideoCapture(1)

# start loop
client.loop_start()

while True:
    # read images
    _, img = cap.read()

    # detect the faces
    faces = face_cascade.detectMultiScale(img, 1.1, 4)
    print("Detect {0} Faces".format(len(faces)))
    # Draw the rectangle around each face and extract face images
    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
        roi_color = img[y:y + h, x:x + w]

        # convert face to gray
        roi_gray = cv2.cvtColor(roi_color, cv2.COLOR_BGR2GRAY)

        # encode and publish image to TX2 broker
        roi_gray_encode = cv2.imencode('.png', roi_gray)[1]
        client.publish("face_detect/test", bytearray(roi_gray_encode), qos=1)

    # display the frame with detected faces
    cv2.imshow('img', img)

    # stop if escape key is pressed
    k = cv2.waitKey(30) & 0xff
    if k==27:
        break

# release capture images and stop connect to broker
client.loop_stop()
client.disconnect()
cap.release()

