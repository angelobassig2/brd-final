import cv2
import os
import time
from ultralytics import YOLO
from ultralytics.yolo.v8.detect.predict import DetectionPredictor
import json
from utils import get_available_products, get_missing_products
import boto3

output_dir = 'captured_images'
os.makedirs(output_dir, exist_ok=True)

model = YOLO('yolov8n.pt')
cap = cv2.VideoCapture(0)
start_time = time.time()
all_products = ['person', 'bowl', 'bottle', 'cup', 'tissue', 'chair']
available_products = []
missing_products = []
# state_1 = []
state_2 = [1 if product in available_products else 0 for product in all_products]
table_name = 'BRD_final_proj_logs'
dynamodb = boto3.client('dynamodb', region_name='us-west-2')

while True:
    ret, frame = cap.read()

    # Check if the frame was captured successfully
    if not ret:
        break

    current_time = time.time()

    # Check if 5 seconds have passed
    if current_time - start_time >= 5:
        # model.predict(source="0", show=True, conf=0.5)

        # Save the captured image with a timestamp
        timestamp = int(current_time)

        state_1 = state_2
        print('State_1----------------------------------------------:', state_1)

        # Perform object detection and save predictions to a json
        prediction = model.predict(source=frame, conf=0.5)
        predictions_filename = os.path.join(output_dir, f'predictions_{timestamp}.json')
        with open(predictions_filename, 'w') as f:
            available_products = list(get_available_products(prediction))
            missing_products = list(get_missing_products(all_products, available_products))
            prediction_json = prediction[0].tojson()
            prediction_dict = json.loads(prediction_json)

            # Create the modified JSON structure
            modified_json = {
                "time_created": timestamp,
                "detected_objects": prediction_dict,
                "all_products": all_products,
                "available_products": available_products,
                "missing_products": missing_products
            }

            formatted_json = json.dumps(modified_json, indent=4) # Convert the modified JSON structure to a formatted JSON string
            # print(formatted_json)
            f.write(formatted_json + '\n')

        # print(f'Predictions saved: {predictions_filename}')

        # Draw bounding boxes and labels on the frame
        for detected_obj in prediction_dict:
            boxes = detected_obj["box"]
            # print(boxes)
            x1 = int(boxes['x1'])
            y1 = int(boxes['y1'])
            x2 = int(boxes['x2'])
            y2 = int(boxes['y2'])
            label = f'{detected_obj["name"]} {detected_obj["confidence"]}'
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        image_filename = os.path.join(output_dir, f'captured_{timestamp}.jpg')
        cv2.imwrite(image_filename, frame)

        # print(f'Image saved: {image_filename}')
    
        # --------------------------------------- DYNAMODB CODE ----------------------------------------------------------
        state_2 = [1 if product in available_products else 0 for product in all_products]
        print('State_2----------------------------------------------:', state_2)
        
        for i in range(len(state_1)):
            if state_1[i] != state_2[i]:
                if state_2[i] == 0:
                    status = 'offstock'
                else:
                    status = 'reshelf'

                item = {
                    'prod_timestamp': {'S': f'{all_products[i]}_{timestamp}'},
                    'Product': {'S': all_products[i]},
                    'Status': {'S': status},
                }

                response = dynamodb.put_item(
                    TableName=table_name,
                    Item=item
                )
                print(f'PutItem response: {response}')
                # print(f'Save: {all_products[i]}')

        start_time = current_time # Update the start time for the next capture

    # Display the frame
    cv2.imshow('CCTV', frame)

    # Exit the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close the OpenCV windows
cap.release()
cv2.destroyAllWindows()
