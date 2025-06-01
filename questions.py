import csv
import requests
def get_last_30_rows(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        rows = list(reader)
        return rows[-30:]  # Return last 30 rows
    
def summarize_rows(rows_str):
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
            "Authorization": f"Bearer LLM|1267609331619212|6_agNYgCUQ1-hXFdwccaolGwDFM"
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
    rows = get_last_30_rows('/Users/milantrivedi/llamahackathon/responses.txt')
    rows_str = " ".join(row[0] for row in rows)
    summary = summarize_rows(rows_str)
    answer = ask_question(summary, 'What kind of architecture is the background inspired by?')
    print(answer)
    



