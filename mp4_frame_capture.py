import cv2 as cv
import os

# Open the video file
video = "../performance_test_2.mp4"
cap = cv.VideoCapture(video)

if not cap.isOpened():
    print("Error: Could not open video.")
    exit()

output_dir = "../performance_test_2"
os.makedirs(output_dir, exist_ok=True)

frame_count = 0
image_count = 50

while True:
    ret, frame = cap.read()

    if not ret:
        break
    if frame_count % 45 == 0:
        image_count += 1
        image_filename = os.path.join(output_dir, f"frame_{image_count:04d}.jpg")
        cv.imwrite(image_filename, frame)
        print(f"Saved {image_filename}")

    frame_count += 1

cap.release()
cv.destroyAllWindows()
