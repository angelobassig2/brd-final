import cv2 as cv
import os
from ultralytics import YOLO
import numpy
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.pyplot as plt
import numpy as np

from ann_visualizer.visualize import ann_viz
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, Flatten, Dense, MaxPooling2D, AveragePooling2D, Dropout
from tensorflow.keras.preprocessing import image_dataset_from_directory
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, accuracy_score
import seaborn as sns
sns.set(style="whitegrid")

def detect_Object():
    vid = cv.VideoCapture('../others_test.mp4')
    # vid.set(cv.CAP_PROP_FRAME_WIDTH, 640)
    # vid.set(cv.CAP_PROP_FRAME_HEIGHT, 640)

    class_model = tf.keras.models.load_model('my_model.h5')

    if not vid.isOpened():
        print("Failed to read video.")
        return []
    detect_model = YOLO('yolov8n.pt')

    img_size = (256,256)
    classes = ['coke', 'mountaindew', 'others', 'pocari']

    while True:
        ret, frame = vid.read()
        # frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)

        if not ret:
            print("Cannot receive feed from stream end. Exiting...")
            break
        
        detected_obj = detect_model.predict(frame, conf = 0.7, iou = 0.9, save=False, classes = [39])

        if len(detected_obj) != 0:
            for obj in detected_obj:
                for deets in obj.boxes.data.tolist():
                    xmin, ymin, xmax, ymax = int(deets[0]), int(deets[1]), int(deets[2]), int(deets[3])
                    # names = model.names

                    # print(xmin, ymin, xmax, ymax)
                    roi = frame[ymin:ymax, xmin:xmax]
                    roi = cv.cvtColor(roi, cv.COLOR_BGR2GRAY)
                    roi = cv.resize(roi, img_size)
                    roi = np.expand_dims(roi, axis=0)
                    print(roi.shape)
                    
                    predictions = class_model.predict(roi)
                    # print(predictions)
                    brand = np.argmax(predictions[0])
                    confidence = round(predictions[0][brand],4)

                    if confidence > 0.5:
                        cv.rectangle(frame, (xmin, ymin) , (xmax, ymax), (0,255,0), 2)
                        cv.putText(frame, str(classes[brand]), (xmin, ymin +15), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                        cv.putText(frame, str(confidence), (xmin, ymin +30), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)


        cv.imshow('Object Detection', frame)

        key = cv.waitKey(1)
        if key == ord('q'):
            break
    vid.release()
    cv.destroyAllWindows()



if __name__ == '__main__':
    detect_Object()
    
