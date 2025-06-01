import cv2
import numpy as np
import requests
import json
import base64
# import threading
from concurrent.futures import ThreadPoolExecutor
import time
import csv

executor = ThreadPoolExecutor(max_workers=1000)
MAX_DURATION = .5


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
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

        
    # When everything is done, release the capture and close windows
    cap.release()
    cv2.destroyAllWindows()

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
                    {"role": "system", "content": "You are a precise video frame analyzer. You're job is to analyze all parts of the video frame, including the people, objects, items in the background, etc. Please answer a detailed response in 2 or more sentences. Please do not put a newline at the end of the response."},
                    {
                        "role": "user",
                        "content": [
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

        f =  open("responses.txt", "a", encoding="utf-8", buffering=1)

        response_text = response.json()['completion_message']['content']['text'];

        with open("responses.txt", "a", newline='', encoding="utf-8") as txtfile:
            writer = csv.writer(txtfile)
            writer.writerow([response_text])  # Optional tim

        


        

if __name__ == "__main__":
    open_camera_display()