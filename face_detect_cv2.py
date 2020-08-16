import cv2
import numpy as np
import time
import paho.mqtt.client as paho

IMAGE_PATH = './mav.jpg'

# load the harrcascade for face detection
face_cascade = cv2.CascadeClassifier('/opencv/data/haarcascades/haarcascade_frontalface_default.xml')

img = cv2.imread(IMAGE_PATH)

img_number = 0

 # detect the faces
faces = face_cascade.detectMultiScale(img, 1.1, 4)
print("Detect {0} Faces".format(len(faces)))
# Draw the rectangle around each face and extract face images
for (x, y, w, h) in faces:
    cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
    roi_color = img[y:y + h, x:x + w]

    # convert face to gray
    roi_gray = cv2.cvtColor(roi_color, cv2.COLOR_BGR2GRAY)
    cv2.imwrite(str(w) + str(h) + '_faceCV2.png', roi_gray)
    # encode and publish image to TX2 broker

cv2.imwrite('cv2_results.png', img)