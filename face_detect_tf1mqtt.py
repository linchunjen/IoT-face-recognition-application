from PIL import Image
import cv2
import sys
import os
import paho.mqtt.client as paho
import urllib
import urllib.request
import tensorflow.contrib.tensorrt as trt
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import tensorflow as tf
import numpy as np
import time
from tf_trt_models.detection import download_detection_model, build_detection_graph

FROZEN_GRAPH_NAME = 'frozen_inference_graph_face.pb'

url = 'https://github.com/yeephycho/tensorflow-face-detection/blob/master/model/frozen_inference_graph_face.pb?raw=true'
urllib.request.urlretrieve(url, FROZEN_GRAPH_NAME)
output_dir=''
frozen_graph = tf.GraphDef()
with open(os.path.join(output_dir, FROZEN_GRAPH_NAME), 'rb') as f:
  frozen_graph.ParseFromString(f.read())

INPUT_NAME='image_tensor'
BOXES_NAME='detection_boxes'
CLASSES_NAME='detection_classes'
SCORES_NAME='detection_scores'
MASKS_NAME='detection_masks'
NUM_DETECTIONS_NAME='num_detections'

input_names = [INPUT_NAME]
output_names = [BOXES_NAME, CLASSES_NAME, SCORES_NAME, NUM_DETECTIONS_NAME]

trt_graph = trt.create_inference_graph(
    input_graph_def=frozen_graph,
    outputs=output_names,
    max_batch_size=1,
    max_workspace_size_bytes=1 << 25,
    precision_mode='FP16',
    minimum_segment_size=50
)


tf_config = tf.ConfigProto()
tf_config.gpu_options.allow_growth = True

tf_sess = tf.Session(config=tf_config)
tf.import_graph_def(frozen_graph, name='')

tf_input = tf_sess.graph.get_tensor_by_name(input_names[0] + ':0')
tf_scores = tf_sess.graph.get_tensor_by_name('detection_scores:0')
tf_boxes = tf_sess.graph.get_tensor_by_name('detection_boxes:0')
tf_classes = tf_sess.graph.get_tensor_by_name('detection_classes:0')
tf_num_detections = tf_sess.graph.get_tensor_by_name('num_detections:0')

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

# capture images
cap = cv2.VideoCapture(1)

# OpenCV uses BGR but matplotlib uses RGB
# convert BGR to RGB

while True:
    # read images
    _, image = cap.read()
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image_resized = cv2.resize(image, (300, 300))

    scores, boxes, classes, num_detections = tf_sess.run([tf_scores, tf_boxes, tf_classes, tf_num_detections], feed_dict={
        tf_input: image_resized[None, ...]
    })

    boxes = boxes[0] # index by 0 to remove batch dimension
    scores = scores[0]
    classes = classes[0]
    num_detections = num_detections[0]

# suppress boxes that are below the threshold.. 
    DETECTION_THRESHOLD = 0.5

    # count detected faces
    img_number = 0
    
    # Detect faces and publish
    for i in range(int(num_detections)):
        # img = image
        if scores[i] < DETECTION_THRESHOLD:
            continue
        # scale box to image coordinates
        box = boxes[i] * np.array([image.shape[0], image.shape[1], image.shape[0], image.shape[1]])
    
        # crop faces and save faces
        roi = image[int(box[0]):int(box[2]), int(box[1]):int(box[3]), 0]
        img_label = "faceTF1_" + str(img_number) + ".png"
        cv2.imwrite(img_label, roi)

        # encode and publish image to TX2 broker
        roi_gray_encode = cv2.imencode('.png', roi)[1]
        client.publish("face_detect/test", bytearray(roi_gray_encode), qos=1)

        # detect multiple faces
        img_number += 1
    print("Detect %s faces with Tensorflow" %img_number)
    

# release capture images and stop connect to broker
client.loop_stop()
client.disconnect()
