import cv2
import numpy as np
import requests
import json
import base64
# import threading
from concurrent.futures import ThreadPoolExecutor
import time
from skimage.metrics import structural_similarity as ssim

executor = ThreadPoolExecutor(max_workers=1000)
MAX_DURATION = .5  # seconds

def open_camera_display():
    # Initialize the camera
    # 0 represents the default camera (usually the built-in webcam)
    cap = cv2.VideoCapture(0)
    
    # Check if the camera opened successfully
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return
    
    print("Camera opened successfully. Press 'q' to quit.")
    
    last_frame = []
    last_time = time.time()
    while True:
        ret, frame = cap.read()
        
        # If frame is read correctly ret is True
        if not ret:
            print("Error: Can't receive frame. Exiting...")
            break
        
        #skip if frame is mostly similar to last frame
        if is_similar_frame(frame, last_frame):
            last_frame = frame
            continue
        
        #every ten frames perfrom calculation
        current_time = time.time()
        
        # If one second has passed since last processing
        if current_time - last_time > 0.3:
            # Do your processing here (e.g., process_frame)
            executor.submit(process_frame, frame.copy(), current_time)
            last_time = current_time
    
        # Display the resulting frame
        cv2.imshow('Camera Feed', frame)
        
        # Break the loop when 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        last_frame = frame
        
    # When everything is done, release the capture and close windows
    cap.release()
    cv2.destroyAllWindows()

def is_similar_frame(frame1, frame2, threshold=0.75):
    """
    Returns True if two frames are mostly similar.
    Uses SSIM (Structural Similarity Index) if available, 
    else falls back to simple pixel difference ratio.
    """

    if type(frame1) != "<class 'numpy.ndarray'>" or type(frame2) != "<class 'numpy.ndarray'>":
        return False
    # Resize for faster comparison
    small1 = cv2.resize(frame1, (64, 64))
    small2 = cv2.resize(frame2, (64, 64))

    # Convert to grayscale
    gray1 = cv2.cvtColor(small1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(small2, cv2.COLOR_BGR2GRAY)

    # Option 1: Use SSIM (structural similarity) if available
    try:
        score, _ = ssim(gray1, gray2, full=True)
        return score >= threshold
    except ImportError:
        # Option 2: Fallback to basic difference percentage
        diff = cv2.absdiff(gray1, gray2)
        non_zero_count = np.count_nonzero(diff)
        total_pixels = diff.size
        similarity = 1 - (non_zero_count / total_pixels)
        return similarity >= threshold

def process_frame(frame, start_time):
    while True:
        if time.time() - start_time > MAX_DURATION:
            return  # Exit the thread safely

        _, buffer = cv2.imencode('.jpg', frame)
        jpg_as_text = base64.b64encode(buffer).decode('utf-8')  # <-- correct way

        response = requests.post(
            url="https://api.llama.com/v1/chat/completions", 
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer LLM|1267609331619212|6_agNYgCUQ1-hXFdwccaolGwDFM"
            },
            json={
                "model": "Llama-4-Maverick-17B-128E-Instruct-FP8",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "What is going on in this picture frame in 30-40 words. Please make sure you are at least '99%' confident in your answer. Do not write the confidence score",
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": "data:image/jpeg;base64," + jpg_as_text
                                }
                            }
                        ],
                    },
                ]
            }
        )

        print(response.json()['completion_message']['content']['text'])


if __name__ == "__main__":
    open_camera_display()