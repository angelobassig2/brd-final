import os
import json
from json import JSONDecodeError
import base64
import datetime
import pandas as pd
import boto3
import cv2
import botocore.exceptions

def classify_products(prediction, frame, classifier):
    # Create a detected_objects list to recreate .tojson() method
            detected_objects_list = []

            if len(prediction) != 0:
                for obj in prediction:
                    for deets in obj.boxes.data.tolist():
                        xmin, ymin, xmax, ymax = int(deets[0]), int(deets[1]), int(deets[2]), int(deets[3])
                        roi = frame[ymin:ymax, xmin:xmax]

                        predicted_class = classifier.predict(source=roi)
                        
                        predicted_class[0].save_txt('pred.txt')
                        print('what is probz', predicted_class[0].probs)
                        print('nsaofnsofsfs', predicted_class[0].probs.top1)
                        print('Confidence of top 1', predicted_class[0].probs.top1conf)    
                        print('fsndfsdfdsfds', predicted_class[0].names)

                        predicted_class_number = predicted_class[0].probs.top1
                        predicted_class_name = predicted_class[0].names[predicted_class_number]
                        predicted_class_confidence = predicted_class[0].probs.top1conf

                        label = f'{predicted_class_name} {predicted_class_confidence}'

                        if predicted_class_confidence > 0.9:
                            if (predicted_class_name == 'coke'):
                                cv2.rectangle(frame, (xmin, ymin) , (xmax, ymax), (0, 0, 255), 2)
                                cv2.putText(frame, str(label), (xmin, ymin - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                            elif (predicted_class_name == 'mountain_dew'):
                                cv2.rectangle(frame, (xmin, ymin) , (xmax, ymax), (0, 255, 0), 2)
                                cv2.putText(frame, str(label), (xmin, ymin - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                            elif (predicted_class_name == 'pocari'):
                                cv2.rectangle(frame, (xmin, ymin) , (xmax, ymax), (255, 0, 0), 2)
                                cv2.putText(frame, str(label), (xmin, ymin - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
                            else:
                                cv2.rectangle(frame, (xmin, ymin) , (xmax, ymax), (0, 0, 0), 2)
                                cv2.putText(frame, str(label), (xmin, ymin - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
                            
                            detected_objects_list.append({
                                "name": str(predicted_class_name),
                                "class": int(predicted_class_number),
                                "confidence": float(predicted_class_confidence)
                            })        
                            
                return detected_objects_list, frame


# IMPORTANT: Change DOCSTRING
def get_available_products(detected_objects_list):
    """
    Get a list of available products from the model's result.

    Args:
        model_result (ultralytics.yolo.v8.utils.metrics.results.Result): Model's prediction result.

    Returns:
        list: A list of available product names.
    """
    # pred = model_result[0].tojson()
    # result_dict = json.loads(pred)
    # dataframe = pd.DataFrame(result_dict)
    dataframe = pd.DataFrame(detected_objects_list)
    try:
        available_products = dataframe["name"].unique()
        return available_products
    except KeyError:
        return []


def get_missing_products(all_products, available_products):
    """
    Get a list of missing products based on all products and available products.

    Args:
        all_products (list): List of all product names.
        available_products (list): List of available product names.

    Returns:
        set: A set of missing product names.
    """
    missing_products = set(all_products) - set(available_products)
    return missing_products

# IMPORTANT: Change DOCSTRING
def count_products(detected_objects_list):
    """
    Count the number of each product in the model's result.

    Args:
        model_result (ultralytics.yolo.v8.utils.metrics.results.Result): Model's prediction result.

    Returns:
        dict: A dictionary containing product names as keys and their counts as values.
    """
    # pred = model_result[0].tojson()
    # result_dict = json.loads(pred)
    # dataframe = pd.DataFrame(result_dict)
    dataframe = pd.DataFrame(detected_objects_list)
    try:
        products_count = dataframe["name"].value_counts().to_dict()
        return products_count
    except KeyError:
        return {}


def convert_to_iso(timestamp):
    """
    Convert a Unix timestamp to ISO 8601 format.

    Args:
        timestamp (float): Unix timestamp.

    Returns:
        str: ISO 8601 formatted timestamp.
    """
    datetime_obj = datetime.datetime.fromtimestamp(timestamp)
    iso_timestamp = datetime_obj.isoformat()
    return iso_timestamp

# IMPORTANT: Change DOCSTRING
def save_predictions_to_json(
    output_dir, timestamp_replaced, timestamp, detected_objects_list, all_products
):
    """
    Save prediction results to a JSON file.

    Args:
        output_dir (str): Output directory path.
        timestamp_replaced (str): Timestamp with underscores instead of colons.
        timestamp (str): ISO 8601 formatted timestamp.
        prediction (ultralytics.yolo.v8.utils.metrics.results.Result): Model's prediction result.
        all_products (list): List of all product names.

    Returns:
        str or None: The saved JSON filename on success, or None on failure.
    """
    predictions_filename = os.path.join(
        output_dir, f"predictions_{timestamp_replaced}.json"
    )
    try:
        available_products = list(get_available_products(detected_objects_list))
        missing_products = list(get_missing_products(all_products, available_products))
        # prediction_json = prediction[0].tojson()
        # prediction_dict = json.loads(prediction_json)
        modified_dict = {
            "time_created": timestamp,
            "detected_objects": detected_objects_list,
            "all_products": all_products,
            "available_products": available_products,
            "missing_products": missing_products,
        }
        formatted_json = json.dumps(modified_dict, indent=4)

        with open(predictions_filename, "w", encoding="utf-8") as file:
            file.write(formatted_json + "\n")

        # return predictions_filename
        return formatted_json
    except IOError as io_error:
        print(f"An error occurred while saving the JSON file: {str(io_error)}")
        return None


def save_detected_objects_frame(output_dir, timestamp_replaced, detected_objects_frame):
    """
    Save detected objects frame as an image.

    Args:
        output_dir (str): Output directory path.
        timestamp_replaced (str): Timestamp with underscores instead of colons.
        detected_objects_frame (numpy.ndarray): Detected objects frame.

    Returns:
        str or None: The saved image filename on success, or None on failure.
    """
    image_filename = os.path.join(output_dir, f"captured_{timestamp_replaced}.jpg")
    try:
        cv2.imwrite(image_filename, detected_objects_frame)
        return detected_objects_frame
    except cv2.error as cv2_error:
        print(f"An error occurred while saving the image: {str(cv2_error)}")
        return None


def save_product_counts_to_json(all_products, threshold, detected_objects_list):
    """
    Save product counts to a JSON file.

    Args:
        all_products (list): List of all product names.
        threshold (int): Product count threshold.
        prediction (ultralytics.yolo.v8.utils.metrics.results.Result): Model's prediction result.

    Returns:
        list or None: A list of product counts on success, or None on failure.
    """
    try:
        available_products_count = count_products(detected_objects_list)
        all_products_count = [
            available_products_count.get(product, 0) for product in all_products
        ]
        threshold_list = [threshold] * len(all_products)
        zip_to_json = [
            {"product": p, "count": c, "threshold": t}
            for p, c, t in zip(all_products, all_products_count, threshold_list)
        ]
        all_products_count_json = json.dumps(zip_to_json, indent=4)
        json_filename = "all_products_count.json"

        with open(json_filename, "w", encoding="utf-8") as json_file:
            json_file.write(all_products_count_json)

        print("JSON file saved successfully.")
        return all_products_count
    except JSONDecodeError as json_error:
        print(f"JSON decoding error: {str(json_error)}")
        return None
    except FileNotFoundError as file_error:
        print(f"File not found error: {str(file_error)}")
        return None


def save_current_frame(current_image_path, detected_objects_frame):
    """
    Save the current frame as an image.

    Args:
        current_image_path (str): Path to save the current frame image.
        detected_objects_frame (numpy.ndarray): Detected objects frame.

    Returns:
        None
    """
    try:
        detected_objects_frame_resized = cv2.resize(detected_objects_frame, (320, 320))
        cv2.imwrite(current_image_path, detected_objects_frame_resized)
        print(f"Current frame saved: {current_image_path}")
    except cv2.error as cv2_error:
        print(f"OpenCV error: {str(cv2_error)}")
    except FileNotFoundError as file_error:
        print(f"File not found error: {str(file_error)}")


def update_status_and_upload_to_dynamodb(
    dynamodb,
    table_name,
    all_products,
    all_products_count,
    timestamp,
    unix_timestamp,
    threshold,
):
    """
    Update product status and upload data to DynamoDB.

    Args:
        table_name (str): Name of the DynamoDB table.
        all_products (list): List of all product names.
        all_products_count (list): List of product counts.
        timestamp (str): ISO 8601 formatted timestamp.
        unix_timestamp (int): Unix timestamp.
        threshold (int): Product count threshold.

    Returns:
        None
    """
    try:
        for i, product_count in enumerate(all_products_count):
            if product_count > threshold:
                status = "onshelf"
            elif 0 < product_count <= threshold:
                status = "threshold"
                print("Warning: Product count below threshold. Please restock now!")
            else:
                status = "offshelf"
                print("Alert: No products available. Please restock now!")
            item = {
                "Prod_timestamp": {"S": f"{all_products[i]}_{unix_timestamp}"},
                "Date_created": {"S": timestamp},
                "Product_codename": {"S": all_products[i]},
                "Product_count": {"N": str(product_count)},
                "Status": {"S": status},
                "Threshold": {"N": str(threshold)},
            }
            response = dynamodb.put_item(TableName=table_name, Item=item)
            print(f"PutItem response: {response}")
    except boto3.exceptions.Boto3Error as boto3_error:
        print(f"Boto3 error: {str(boto3_error)}")


def get_all_products(dynamodb, table_name):
    """
    Get a list of all product codenames from DynamoDB.

    Returns:
        dict: A dictionary with a single key "all_products" containing the list of product codenames.
    """
    try:
        response = dynamodb.scan(TableName=table_name)
        product_codenames = [
            item["product_codename"]["S"] for item in response.get("Items", [])
        ]
        all_products = {"all_products": product_codenames}
        return all_products
    except botocore.exceptions.ClientError as client_error:
        print(f"An error occurred while retrieving all products: {str(client_error)}")
        return {"all_products": []}


def generate_graph(dynamodb, table_name, product_codename, num_items_to_retrieve):
    """
    Generate a graph of product counts for a specific product codename.

    Args:
        product_codename (str): Product codename.
        num_items_to_retrieve (int): Number of items to retrieve from DynamoDB.

    Returns:
        list: A list of dictionaries containing date and product count information.
    """
    try:
        response = dynamodb.query(
            TableName=table_name,
            Limit=num_items_to_retrieve,
            ScanIndexForward=False,
            KeyConditionExpression="Product_codename = :product",
            ExpressionAttributeValues={":product": {"S": product_codename}},
            ProjectionExpression="Date_created, Product_count",
        )
        queried_products = [
            {
                "Date_created": item["Date_created"]["S"],
                "Product_count": int(item["Product_count"]["N"]),
            }
            for item in response["Items"]
        ]
        queried_products = sorted(queried_products, key=lambda x: x["Date_created"])
        return queried_products
    except botocore.exceptions.ClientError as client_error:
        print(f"An error occurred while generating the graph: {str(client_error)}")
        return []


def get_one_image(image_path):
    """
    Read and encode an image file as base64.

    Args:
        image_path (str): Path to the image file.

    Returns:
        dict: A dictionary containing the base64 encoded image data.
    """
    try:
        if os.path.isfile(image_path):
            with open(image_path, "rb") as image_file:
                image_data = image_file.read()
                image_base64 = base64.b64encode(image_data).decode("utf-8")
                response_data = {"image_base64": image_base64}
                return response_data
    except FileNotFoundError as file_error:
        print(f"File not found error: {str(file_error)}")
    return None


def get_json(json_filename):
    """
    Read a JSON file and return its contents as a dictionary.

    Args:
        json_filename (str): Path to the JSON file.

    Returns:
        dict: A dictionary containing the JSON data.
    """
    try:
        with open(f"{json_filename}.json", "r", encoding="utf-8") as file:
            response_data = json.load(file)
            return response_data
    except FileNotFoundError as file_error:
        print(f"File not found error: {str(file_error)}")
        return None
    except JSONDecodeError as json_error:
        print(f"JSON decoding error: {str(json_error)}")
        return None


def generate_s3_key(s3, timestamp, file_type, prefix):
    """
    Generate an S3 key based on the timestamp, file type, and prefix.

    Args:
        s3 (boto3.client): An initialized Boto3 S3 client.
        timestamp (str): The timestamp to use for generating the key.
        file_type (str): The type of file (e.g., 'json' or 'images').
        prefix (str): The prefix for the S3 key.

    Returns:
        str: The generated S3 key.
    """
    try:
        timestamp_obj = datetime.datetime.fromisoformat(timestamp)
        year_month_day = timestamp_obj.strftime("%Y/%B/%d")
        file_extension = "jpg" if file_type == "images" else "json"
        return f"{prefix}{year_month_day}/{file_type}/{timestamp}.{file_extension}"
    except (ValueError, TypeError) as error:
        print(f"Error generating S3 key: {str(error)}")
        return None


def save_to_s3(s3, data, file_type, bucket_name, s3_key):
    """
    Save data to an S3 bucket.

    Args:
        s3 (boto3.client): An initialized Boto3 S3 client.
        data (str or bytes): The data to be saved to S3.
        file_type (str): The type of file (e.g., 'json' or 'images').
        bucket_name (str): The name of the S3 bucket.
        s3_key (str): The S3 key under which to save the data.

    Returns:
        bool: True if the upload was successful, False otherwise.
    """
    try:
        if file_type == "json":
            if not isinstance(data, (str, bytes)):
                raise ValueError("Invalid JSON data provided")

            json_bytes = data.encode("utf-8") if isinstance(data, str) else data
            s3.put_object(Bucket=bucket_name, Key=s3_key, Body=json_bytes)
            print(f"Uploaded JSON data to S3: {bucket_name}/{s3_key}")
            return True

        if file_type == "images":
            _, frame_bytes = cv2.imencode(".jpg", data)
            s3.put_object(Bucket=bucket_name, Key=s3_key, Body=frame_bytes.tobytes())
            print(f"Uploaded image to S3: {bucket_name}/{s3_key}")
            return True
        raise ValueError("Unsupported file type provided")
    except (ValueError, TypeError) as error:
        print(f"Error saving data to S3: {str(error)}")
        return False


def upload_data_to_s3(s3, timestamp, formatted_json, image_filename, bucket_and_prefix):
    """
    Upload formatted JSON data and an image to S3.

    Args:
        s3 (boto3.client): An initialized Boto3 S3 client.
        timestamp (str): The timestamp associated with the data.
        formatted_json (str): The formatted JSON data to be uploaded.
        image_filename (str): The filename of the image to be uploaded.
        bucket_and_prefix (str): The S3 bucket and prefix (e.g., 'my-bucket/logs/').

    Returns:
        bool: True if the upload was successful, False otherwise.
    """
    try:
        bucket_name, prefix, _ = bucket_and_prefix.split("/")
        prefix = f"{prefix}/"
        json_key = generate_s3_key(s3, timestamp, "json", prefix)
        timestamp_replaced = timestamp.replace(":", "-")  # Ensure a valid file name
        with open(f"{timestamp_replaced}.json", "w", encoding="utf-8") as json_file:
            json_file.write(formatted_json)

        save_to_s3(s3, formatted_json, "json", bucket_name, json_key)
        image_key = generate_s3_key(s3, timestamp, "images", prefix)
        save_to_s3(s3, image_filename, "images", bucket_name, image_key)

        os.remove(f"{timestamp_replaced}.json")
        return True
    except (FileNotFoundError, ValueError) as error:
        print(f"Error uploading data to S3: {str(error)}")
        return False
