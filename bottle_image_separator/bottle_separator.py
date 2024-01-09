import cv2 as cv
import os
from ultralytics import YOLO
import numpy


def detect_Object(frame):
    model = YOLO('yolov8n.pt')

    detected_obj = model.predict(frame, conf=0.7, save=False, classes = [39], iou = 1)
    names = model.names

    if len(detected_obj) != 0:
        for obj in detected_obj:
            for deets in obj.boxes.data.tolist():
                xmin, ymin, xmax, ymax = int(deets[0]), int(deets[1]), int(deets[2]), int(deets[3])
                roi = frame[ymin:ymax, xmin:xmax]
                # # TODO: CNN Classifier
                # cv.rectangle(frame, (xmin, ymin) , (xmax, ymax), (0,255,0), 2)
                # cv.putText(frame, str(names[deets[5]]), (xmin, ymin - 15), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                return roi

if __name__ == '__main__':
    new_ds = '../separated_bottles'
    os.makedirs(new_ds, exist_ok=True)
    path = '../bottles_imgs'
    folders = os.listdir(path)
    folders = [folder for folder in folders if not folder.endswith('.DS_Store')]


    for folder in folders:
        folder_path = os.path.join(path, folder)
        images = os.listdir(f'{path}/{folder}')
        new_folder = os.path.join(new_ds, folder)
        os.makedirs(new_folder, exist_ok=True)
        for image in images:
            image_path = os.path.join(folder_path, image)
            img_array = cv.imread(image)
            separated = detect_Object(img_array)
            obj_filename = f"{new_folder}/{os.path.basename(image_path)}.jpg"
            cv.imwrite(obj_filename, separated)    
