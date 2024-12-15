{\rtf1\ansi\deff0\nouicompat{\fonttbl{\f0\fnil\fcharset0 Calibri;}}
{\*\generator Riched20 10.0.22621}\viewkind4\uc1 
\pard\sa200\sl276\slmult1\f0\fs22\lang9 import cv2\par
import time\par
import threading\par
\par
classNames = []\par
classFile = "/home/User/Desktop/Object_Detection_Files/coco.names"\par
with open(classFile, "rt") as f:\par
    classNames = f.read().rstrip("\\n").split("\\n")\par
\par
configPath = "/home/User/Desktop/Object_Detection_Files/ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt"\par
weightsPath = "/home/User/Desktop/Object_Detection_Files/frozen_inference_graph.pb"\par
\par
net = cv2.dnn_DetectionModel(weightsPath, configPath)\par
net.setInputSize(320, 320)\par
net.setInputScale(1.0 / 127.5)\par
net.setInputMean((127.5, 127.5, 127.5))\par
net.setInputSwapRB(True)\par
\par
current_frame = None\par
frame_lock = threading.Lock()\par
\par
def capture_frames(cap):\par
    global current_frame\par
    while True:\par
        ret, frame = cap.read()\par
        if not ret:\par
            print("Error: Failed to capture image.")\par
            break\par
\par
        with frame_lock:\par
            current_frame = frame\par
            \par
def process_frame():\par
    global current_frame\par
    while True:\par
        if current_frame is not None:\par
            \par
            frame = current_frame.copy()\par
            \par
            result, objectInfo = getObjects(frame, 0.65, 0.5)\par
            \par
            cv2.imshow("Output", result)\par
            \par
            if cv2.waitKey(1) & 0xFF == ord('q'):\par
                break\par
            \par
def getObjects(img, thres, nms, draw=True, objects=[]):\par
    classIds, confs, bbox = net.detect(img, confThreshold=thres, nmsThreshold=nms)\par
    if len(objects) == 0:\par
        objects = classNames\par
    objectInfo = []\par
    if len(classIds) != 0:\par
        for classId, confidence, box in zip(classIds.flatten(), confs.flatten(), bbox):\par
            className = classNames[classId - 1]\par
            if className in objects:\par
                objectInfo.append([box, className])\par
                if draw:\par
                    cv2.rectangle(img, box, color=(0, 255, 0), thickness=2)\par
                    cv2.putText(img, classNames[classId - 1].upper(), (box[0] + 10, box[1] + 30),\par
                                cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)\par
                    cv2.putText(img, str(round(confidence * 100, 2)), (box[0] + 200, box[1] + 30),\par
                                cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)\par
    return img, objectInfo\par
\par
if _name_ == "_main_":\par
    \par
    cap = cv2.VideoCapture(2, cv2.CAP_V4L2) \par
    if not cap.isOpened():\par
        print("Error: Could not open the USB camera.")\par
        exit()\par
        \par
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)\par
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)\par
    \par
    capture_thread = threading.Thread(target=capture_frames, args=(cap,))\par
    capture_thread.daemon = True  \par
    capture_thread.start()\par
    \par
    process_thread = threading.Thread(target=process_frame)\par
    process_thread.daemon = True  \par
    process_thread.start()\par
    \par
    while True:\par
        time.sleep(0.1)\par
\par
    cap.release()\par
    cv2.destroyAllWindows()\par
}
 