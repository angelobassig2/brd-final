import os
import time
from json import JSONDecodeError
from flask import Flask, jsonify, request
from flask_cors import CORS
import boto3
import botocore.exceptions
import cv2
from ultralytics import YOLO
from utils import (
    classify_products,
    convert_to_iso,
    generate_graph,
    get_all_products,
    save_predictions_to_json,
    save_detected_objects_frame,
    save_product_counts_to_json,
    save_current_frame,
    update_status_and_upload_to_dynamodb,
    get_one_image,
    get_json,
    upload_data_to_s3,
)

app = Flask(__name__)
# CORS(app)
# cors = CORS(app, resources={r"/*": {"origins": "https://master.d3l3gz5dk0re4e.amplifyapp.com/"}})
cors = CORS(app, resources={r"/*": {"origins": "*", "allow_headers": "*", "expose_headers": "*"}})

# AWS Variables
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
TABLE_NAME = "BRD_final_proj_logs"
TABLE_NAME_2 = "BRD_final_proj_products"
BUCKET_NAME = "2023-aiml-bootcamp-final-project-brd"
PREFIX = "logs/"
BUCKET_NAME_AND_PREFIX = f"{BUCKET_NAME}/{PREFIX}"
s3 = boto3.client("s3")
dynamodb = boto3.client("dynamodb", region_name="us-west-2")

STOP_WEBCAM_FLAG = False


@app.route("/get_all_products", methods=["GET"])
def get_all_products_endpoint():
    """
    Get a list of all product codenames from DynamoDB.

    Returns:
        dict: A dictionary with a single key "all_products" containing the list of product codenames.
    """
    try:
        all_products = get_all_products(dynamodb, TABLE_NAME_2)
        return jsonify(all_products)
    except botocore.exceptions.ClientError as client_error:
        return jsonify({"error": str(client_error)}), 500


@app.route("/generate_graph", methods=["GET"])
def generate_graph_endpoint():
    """
    Generate a graph of product counts for a specific product codename.

    Returns:
        list: A list of dictionaries containing date and product count information.
    """
    try:
        product_codename = request.args.get("product_codename")
        dates_and_counts = generate_graph(dynamodb, TABLE_NAME, product_codename, 10)
        return jsonify(dates_and_counts)
    except botocore.exceptions.ClientError as client_error:
        return jsonify({"error": str(client_error)}), 500


@app.route("/get_one_image", methods=["GET"])
def get_one_image_endpoint():
    """
    Read and encode an image file as base64.

    Returns:
        dict: A dictionary containing the base64 encoded image data.
    """
    try:
        image_path = request.args.get("image_path")
        response_data = get_one_image(image_path)
        return jsonify(response_data)
    except FileNotFoundError as file_error:
        return jsonify({"error": str(file_error)}), 500


@app.route("/get_json", methods=["GET"])
def get_json_endpoint():
    """
    Read a JSON file and return its contents as a dictionary.

    Returns:
        dict: A dictionary containing the JSON data.
    """
    try:
        json_filename = request.args.get("json_filename")
        response_data = get_json(json_filename)
        return jsonify(response_data)
    except FileNotFoundError as file_error:
        return jsonify({"error": str(file_error)}), 500
    except JSONDecodeError as json_error:
        return jsonify({"error": str(json_error)}), 500


@app.route("/stop_webcam", methods=["POST"])
def stop_webcam():
    """
    Stop the webcam process.

    Returns:
        str: A message indicating the webcam is stopping.
    """
    global STOP_WEBCAM_FLAG
    STOP_WEBCAM_FLAG = True
    return "Stopping webcam..."


@app.route("/detect_objects", methods=["GET"])
def detect_objects_endpoint():
    """
    Perform object detection and capture images with a webcam.

    Returns:
        dict: A message indicating the AI process status.
    """
    global STOP_WEBCAM_FLAG
    STOP_WEBCAM_FLAG = False

    all_products_str = request.args.get("allProducts")
    all_products = all_products_str.split(",")
    interval = int(request.args.get("timeInterval"))
    threshold = int(request.args.get("threshold"))

    output_dir = "captured_images"
    os.makedirs(output_dir, exist_ok=True)

    # model = YOLO("best18.pt")
    model = YOLO("yolov8n.pt")
    classifier = YOLO("best_brd.pt")

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 640)
    start_time = time.time()

    initial_capture = True

    while not STOP_WEBCAM_FLAG:
        ret, frame = cap.read()

        if not ret:
            break

        current_time = time.time()

        if initial_capture or (current_time - start_time >= interval):

            unix_timestamp = int(current_time)
            timestamp = convert_to_iso(unix_timestamp)
            timestamp_replaced = timestamp.replace(":", "_")

            prediction = model.predict(source=frame, conf=0.7, iou=0.4, classes=[39])

            detected_objects_list, frame_plot = classify_products(prediction, frame, classifier)

            formatted_json = save_predictions_to_json(
                output_dir, timestamp_replaced, timestamp, detected_objects_list, all_products
            )
            detected_objects_frame = save_detected_objects_frame(
                output_dir, timestamp_replaced, frame_plot
            )
            all_products_count = save_product_counts_to_json(
                all_products, threshold, detected_objects_list
            )
            save_current_frame("current_image.jpg", frame_plot)
            update_status_and_upload_to_dynamodb(
                dynamodb,
                TABLE_NAME,
                all_products,
                all_products_count,
                timestamp,
                unix_timestamp,
                threshold,
            )
            upload_data_to_s3(
                s3,
                timestamp,
                formatted_json,
                detected_objects_frame,
                BUCKET_NAME_AND_PREFIX,
            )

            start_time = current_time
            initial_capture = False

        cv2.imshow("CCTV", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()

    return jsonify({"message": "AI terminated!"})


if __name__ == "__main__":
    # app.run(host="localhost", port=5000)
    app.run(debug=True, host='0.0.0.0')
