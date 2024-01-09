import cv2 as cv
import os
import json
from ultralytics import YOLO
import numpy

def detect_Object():
    vid = cv.VideoCapture(0)
    vid.set(cv.CAP_PROP_FRAME_WIDTH, 640)
    vid.set(cv.CAP_PROP_FRAME_HEIGHT, 640)

    if not vid.isOpened():
        print("Failed to open camera")
        return []
    
    model = YOLO('yolov8n.pt')
    classifier = YOLO('best_brd.pt')

    # print(detection_output[0].np())
    while True:
        ret, frame = vid.read()
        
        if not ret:
            print("Cannot receive feed from stream end. Exiting...")
            break

        detected_obj = model.predict(frame, conf=0.7, save=False, iou=0.4, classes=39)
        names = model.names

        # annotated_frame = results[0].plot()
        # print(results)

        # array = detected_obj[0].numpy()
        # print(array)

        if len(detected_obj) != 0:
            for obj in detected_obj:
                for deets in obj.boxes.data.tolist():
                    xmin, ymin, xmax, ymax = int(deets[0]), int(deets[1]), int(deets[2]), int(deets[3])
                    roi = frame[ymin:ymax, xmin:xmax]

                    predicted_class = classifier.predict(source=roi)
                    
                    predicted_class[0].save_txt('pred.txt')
                    print('Probabilities:', predicted_class[0].probs)
                    print('Highest Probability:', predicted_class[0].probs.top1)
                    print('Confidence of Top 1', predicted_class[0].probs.top1conf)    
                    print('Class Names:', predicted_class[0].names)

                    predicted_class_number = predicted_class[0].probs.top1
                    predicted_class_name = predicted_class[0].names[predicted_class_number]

                    label = f'{predicted_class_name} {predicted_class[0].probs.top1conf}'

                    if predicted_class[0].probs.top1conf > 0.9:
                        cv.rectangle(frame, (xmin, ymin) , (xmax, ymax), (255, 0, 0), 2)
                        cv.putText(frame, str(label), (xmin, ymin - 15), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)


        cv.imshow('Object Detection', frame)

        key = cv.waitKey(1)
        if key == ord('q'):
            break
    vid.release()
    cv.destroyAllWindows()

if __name__ == '__main__':
    detect_Object()
    
