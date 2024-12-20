import cv2
import time
import threading

classNames = []
classFile = "/home/KG/Desktop/Object_Detection_Files/coco.names"
with open(classFile, "rt") as f:
    classNames = f.read().rstrip("\n").split("\n")

configPath = "/home/KG/Desktop/Object_Detection_Files/ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt"
weightsPath = "/home/KG/Desktop/Object_Detection_Files/frozen_inference_graph.pb"

net = cv2.dnn_DetectionModel(weightsPath, configPath)
net.setInputSize(320, 320)
net.setInputScale(1.0 / 127.5)
net.setInputMean((127.5, 127.5, 127.5))
net.setInputSwapRB(True)

current_frame = None
frame_lock = threading.Lock()

def capture_frames(cap):
    global current_frame
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to capture image.")
            break

        with frame_lock:
            current_frame = frame
            
def process_frame():
    global current_frame
    while True:
        if current_frame is not None:
            
            frame = current_frame.copy()
            
            result, objectInfo = getObjects(frame, 0.65, 0.5)
            
            cv2.imshow("Output", result)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            
def getObjects(img, thres, nms, draw=True, objects=[]):
    classIds, confs, bbox = net.detect(img, confThreshold=thres, nmsThreshold=nms)
    if len(objects) == 0:
        objects = classNames
    objectInfo = []
    if len(classIds) != 0:
        for classId, confidence, box in zip(classIds.flatten(), confs.flatten(), bbox):
            className = classNames[classId - 1]
            if className in objects:
                objectInfo.append([box, className])
                if draw:
                    cv2.rectangle(img, box, color=(0, 255, 0), thickness=2)
                    cv2.putText(img, classNames[classId - 1].upper(), (box[0] + 10, box[1] + 30),
                                cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)
                    cv2.putText(img, str(round(confidence * 100, 2)), (box[0] + 200, box[1] + 30),
                                cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)
    return img, objectInfo

if _name_ == "_main_":
    
    cap = cv2.VideoCapture(2, cv2.CAP_V4L2) 
    if not cap.isOpened():
        print("Error: Could not open the USB camera.")
        exit()
        
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    capture_thread = threading.Thread(target=capture_frames, args=(cap,))
    capture_thread.daemon = True  
    capture_thread.start()
    
    process_thread = threading.Thread(target=process_frame)
    process_thread.daemon = True  
    process_thread.start()
    
    while True:
        time.sleep(0.1)

    cap.release()
    cv2.destroyAllWindows()
