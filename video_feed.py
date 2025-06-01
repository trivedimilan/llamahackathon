import cv2
import requests
import base64
from concurrent.futures import ThreadPoolExecutor
import time
import csv
from dotenv import load_dotenv
import os

load_dotenv()  

API_KEY = os.getenv("API_KEY")
executor = ThreadPoolExecutor(max_workers=1000)
MAX_DURATION = .5

def open_camera_display():
    # Initialize the camera
    cap = cv2.VideoCapture(0)
    
    # Check if the camera opened successfully
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return
    
    print("Camera opened successfully. Press 'Cntrl C' to quit.")
    
    last_time = time.time()
    try:
        while True:
            ret, frame = cap.read()
            
            # If frame is read correctly ret is True
            if not ret:
                print("Error: Can't receive frame. Exiting...")
                break
            
            current_time = time.time()
            # If .3 second has passed since last processing
            if current_time - last_time > 0.3:
                executor.submit(process_frame, frame.copy(), current_time)
                last_time = current_time
        
            # Display the resulting frame
            cv2.imshow('Camera Feed', frame)
            
    except KeyboardInterrupt:
        print("\nExiting. Goodbye!")
        
    # When everything is done, release the capture and close windows
    cap.release()
    cv2.destroyAllWindows()

def process_frame(frame, start_time):
    while True:
        if time.time() - start_time > MAX_DURATION:
            return  # Exit the thread safely

        _, buffer = cv2.imencode('.jpg', frame)
        jpg_as_text = base64.b64encode(buffer).decode('utf-8')

        response = requests.post(
            url="https://api.llama.com/v1/chat/completions", 
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {API_KEY}"
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
            writer.writerow([f"{start_time} {response_text}"])


if __name__ == "__main__":
    open_camera_display()