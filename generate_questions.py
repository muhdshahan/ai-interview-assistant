
import requests
import os
from dotenv import load_dotenv
load_dotenv()

TOGETHER_API_KEY =os.getenv("TOGETHER_API_KEY")


def generate_interview_questions(role: str): # promt
    prompt = f"""
You are an expert interviewer. Generate 5 relevant technical interview questions for the job role: {role}.
Only return the questions numbered.
"""

    response = requests.post(  #Send API request to Together AI
        "https://api.together.xyz/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {TOGETHER_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "mistralai/Mistral-7B-Instruct-v0.1",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7
        }
    )

    try:
        output = response.json()
        print("🔍 Full Response JSON:", output)  # DEBUG PRINT

        
        if "error" in output:                   # Check for error
            raise Exception(output["error"]["message"])

        message = output["choices"][0]["message"]["content"]
        return message.strip().split('\n')

    except Exception as e:
        print("❌ ERROR:", e)
        return [f"Error: {str(e)}"]
    

# output["choices"][0]["message"]["content"] → This is the actual answer from the AI.
# .strip() → Removes blank spaces at the beginning and end.
# .split('\n') → Splits the text into a list of 5 separate questions, one per line.