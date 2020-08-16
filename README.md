# IoT-face-recognition-application
Build a lightweight IoT application pipeline with components running both on the edge and the cloud

## Project Goal

- Capture faces using OpenCV or Tensorflow in a video stream coming from the edge in real time (Jetson TX2 with external USB webcam)
- Publish face image through Jatson TX2 MQTT broker (Alpine)
- Transmit them to the cloud in real time (MQTT broker and forwarder on Jetson TX2, MQTT broker on IBM cloud VM)
- Subsribe face image through IBM cloud VM broker (Alpine)
- Write and store images on IBM cloud object storage

## Edge Device and Cloud VM

- Nvidia Jetson TX2
- External USB Camara
- IBM Cloud VM

## Systems, Programming Language, and Packages

- Ubuntu 18.04
- Alpine 3.9
- Python 3.6
- Docker
- OpenCV 
- Mosquitto (Mqtt)
- Tensorflow

-----

## Summary of architecture 
![Summary](Summary.png)

## ON Jetson TX2  

### 1. Build docker images for opencv and MQTT
    
- Opencv-python3: /TX2_files/Dockerfile.ocv-p3-mqtt
    ```
    sudo docker build --network=host -t opencv-python3-mqtt -f Dockerfile.ocv-p3-mqtt .
    ```
- Mosquitto MQTT: /TX2_files/Dockerfile.apk_mqtt
    ```
    sudo docker build --network=host -t mqtt_alpine -f Dockerfile.apk_mqtt .
    ```
### 2. Create network and linker for TX2 docker containiers

- link name: hw3; IP address: 172.18.0.0/16 
    ```
    sudo docker network create --subnet=172.18.0.0/16 hw3
    ```

### 3. Run docker containers
- MQTT broker, forwarder, and face detector container were linked by `hw3`

- MQTT broker containers: mqtt-jx2-broker; config file: /TX2_files/jx2_broker.conf
    ```
    sudo docker run --name mqtt-jx2-broker --network hw3 --rm -p 1883:1883 -v /home/MIDS-W251/HW3:/HW3 -d mqtt_alpine -c /TX2_files/jx2_broker.conf
    ```
- MQTT forwarder containers: mqtt-jx2-forwarder; config file: /TX2_files/jx2_forwarder.conf
    ```
    sudo docker run --name mqtt-jx2-forwarder --network hw3 --rm -v /home/MIDS-W251/HW3:/HW3 mqtt_alpine -c /TX2_files/jx2_forwarder.conf
    ```
- Opencv-python face detector container: face-detector
    
    **First enter X environment**
    ```
    xhost + local:root
    ```
    **Next, spin up docker face detector container** 
    ```
    sudo docker run -e DISPLAY=$DISPLAY --name face-detector --network hw3 --rm --privileged -v /tmp:/tmp -v /home/MIDS-W251/HW3:/home -ti opencv-python3-mqtt bash  
    ```
### 4. Run face detect python file: /TX2_files/face_detector.py 

- Inside opencv-python3-mqtt container bash, run
    
    ```
    python3 /TX2_files/face_detector.py
    ```
### 5. Once face detection start, you will see following log

![face_detect_log](face_detect_log.png)


## ON IBM cloud

### 1. Create a IBM cloud VM as instructed in week2/hw and week2/labs
- cloud name: cclinmqtt.cclin.cloud (IP address: 169.45.121.51)
    - SSH into the VM and edit `/etc/ssh/sshd_config` with following changes
    ```
    PermitRootLogin prohibit-password
    PasswordAuthentication no
    ```
- Restart the ssh daemon: `service sshd restart`

### 2. Install DockerCE with .sh file: /IBMcloud_files/Docker_install.sh

```
chmod + /IBMcloud_files/Docker_install.sh
/IBMcloud_files/Docker_install.sh
```

### 3. Create IBM S3 object storage as instructed in week02/lab2
- Object storage name: cclin-face-detect

### 4. Add cloud storage to server
- Provide credentials to VM for access object storage
```
echo "<Access_Key_ID>:<Secret_Access_Key>" > $HOME/.cos_creds
```
- Give authority
```
chmod 600 $HOME/.cos_creds
```

### 5. Mount a bucket of object storage to VM 
- Create a directory in VM for mounting
```
sudo mkdir -m 777 /mnt/cclin-HW3-images 
```
- Create a bucket in IBM object storage:
    - Bucket name: cclin-face-detect-cos-standard-xez

- Mount object storage bucket to VM
```
s3fs cclin-HW3-images /mnt/cclin-HW3-images -o passwd_file=$HOME/.cos_creds -o sigv2 -o use_path_request_style -o url=https://s3.us.cloud-object-storage.appdomain.cloud
```

### 6. Build docker images for opencv and MQTT
    
- Opencv-python3: /IBMcloud_files/Dockerfile.ocv-p3-mqtt
    ```
    docker build --network=host -t opencv-python3-mqtt -f /IBMcloud_files/Dockerfile.ocv-p3-mqtt .
    ```
- Mosquitto MQTT: /IBMcloud_files/Dockerfile.apk_mqtt
    ```
    docker build --network=host -t mqtt_alpine -f /IBMcloud_files/Dockerfile.apk_mqtt .

### 7. Run docker containers

- MQTT broker container: mqtt-ibm-broker
    
    ```
    docker run --name mqtt-ibm-broker -p 1883:1883 -v /home/MIDS-W251/HW3:/home mqtt-alpine mosquitto
    ```
    - can add flag `-d` to run container in background

- MQTT subcriber container: mqtt-ibm-sub

    ```
    docker run --name mqtt-ibm-sub -v /home/MIDS-W251/HW3:/home -v /mnt/cclin-HW3-images:/cclin-HW3-images -ti opencv-python3-mqtt bash
    ```

### 8. Run face image subscribe python file

- Inside mqtt-ibm-sub container bash, run 
    ```
    python3 /IBMcloud_files/face-subscriber.py
    ```


## 
## Implementation

-------------------------------------------------------
## Part I: Face detection with Tensorflow and send images to IBM cloud object storage

### 1. IBM cloud object storage:
- A new object storage and busket was created for HW7 (cclin-jumper-storage-cos-standard-x5t)

### 2. Face images 

- Example imags: http://s3.us-south.cloud-object-storage.appdomain.cloud/cclin-jumper-storage-cos-standard-x5t/TF-face_10.png

![TF-face_10](http://s3.us-south.cloud-object-storage.appdomain.cloud/cclin-jumper-storage-cos-standard-x5t/TF-face_10.png)


----------------------------------------------------
## Part II: Comparison of OpenCV and Tensorflow-based face detection 

### 1. OpenCV: 

- Classified images:

![CV2_results](cv2_results.png)

- Identified faces

![CV2_face1](5252_faceCV2.png)

![CV2_face2](5353_faceCV2.png)

![CV2_face3](5454_faceCV2.png)

![CV2_face4](6060_faceCV2.png)

![CV2_face5](6161_faceCV2.png)

![CV2_face6](6262_faceCV2.png)

### 2. Tensorflow: 

- Classified images:

![TF1_results](TF1_results.png)

- Identified faces

![TF1_face1](faceTF1_0.png)

![TF1_face2](faceTF1_1.png)

![TF1_face3](faceTF1_2.png)

![TF1_face4](faceTF1_3.png)

![TF1_face5](faceTF1_4.png)



