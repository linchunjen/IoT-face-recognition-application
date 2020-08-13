# Reference https://github.com/MIDS-scaling-up/v2/tree/master/week03/hw
# Reference from W251 OH
# Reference from https://answers.opencv.org/question/202145/how-to-decode-by-imdecode/

# Packages import
import numpy as np
import cv2
import time
import paho.mqtt.client as paho

# IBM cloud VM broker IP and mount directory
broker_ip = "169.45.121.51"
    
# Create methods for connections and subscription of messages
def on_connect(client, userdata, flags, rc):
    print("Connection estabilshed successfully with rc:" + str(rc))
    client.subscribe("face_detect/test")

# set counter to check the number of receive image
img_number = 0

def on_message(client, userdata, msg):
    global img_number
    print("Face image received")	

    # decode message
    buffer_img = np.frombuffer(msg.payload, dtype='uint8')
    img = cv2.imdecode(buffer_img, flags=1)
    img_label = "/cclin-HW3-images/face_" + str(img_number) + ".png"
    print("Image label: %s and image dimension: %s" %(img_label, str(img.shape)))
    img_number = img_number + 1
       
    # write and store image in IBM object storage
    cv2.imwrite(img_label, img)
    
# connect to MQTT client
client= paho.Client()
client.connect(broker_ip, 1883, 60)
client.on_connect = on_connect
client.on_message = on_message

# go into a loop
client.loop_forever()