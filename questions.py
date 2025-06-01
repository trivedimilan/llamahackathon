import csv
import requests
from dotenv import load_dotenv
import os
import sys

load_dotenv()  

API_KEY = os.getenv("API_KEY")

MAX_WINDOW = 6000 #set max window to 30 min of footage

def get_context(filepath, time_frame):
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        rows = list(reader)
        window = min(len(rows), MAX_WINDOW, time_frame)
        return rows[-window:]
    
def summarize_rows(rows_str):
    response = requests.post(
            url="https://api.llama.com/v1/chat/completions", 
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {API_KEY}"
            },
            json={
                "model": "Llama-4-Maverick-17B-128E-Instruct-FP8",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Can you summarize what is happening here?",
                            },
                                                        {
                                "type": "text",
                                "text": rows_str
                            },
                        ],
                    },
                ]
            }
        )

    return response.json()['completion_message']['content']['text']

def ask_question(summary, question):
    response = requests.post(
        url="https://api.llama.com/v1/chat/completions", 
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}"
        },
        json={
            "model": "Llama-4-Maverick-17B-128E-Instruct-FP8",
            "messages": [
                {"role": "system", "content": "You are a semi-precise question-answering assistant. When answering questions, please use the context as the basis. Please dont say 'According to the Context'. Please answer in 1 -2 sentences"},
                {"role": "user", "content": f"Context:\n{summary}\n\nQuestion: {question}"}
            ]
        }
    )

    return response.json()['completion_message']['content']['text'];


if __name__ == "__main__":
    time_frame = 30
    if len(sys.argv) > 1:
        timesframe = sys.argv[1] * 3

    rows = get_context('/Users/milantrivedi/llamahackathon/responses.txt', time_frame)
    rows_str = " ".join(row[0] for row in rows)
    summary = summarize_rows(rows_str)

    print("Ask a question (press Ctrl+C to exit):")
    try:
        while True:
            question = input("> ")
            answer = ask_question(summary, question)
            print(answer)
    except KeyboardInterrupt:
        print("\nExiting. Goodbye!")
    



