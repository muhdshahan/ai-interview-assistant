from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)

def generate_interview_questions(role: str):
    prompt = f"""
    You are an expert technical interviewer. 
    Generate exactly 5 relevant technical interview questions for the job role: {role}.
    Return ONLY the questions, each numbered from 1 to 5.
    """

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )

        message = response.choices[0].message.content
        cleaned_message = message.strip().split("\n")
        print(cleaned_message)
        return cleaned_message
    
    except Exception as e:
        print("ERROR:", e)
        return [f"Error: {str(e)}"]
    

if __name__ == "__main__":
    generate_interview_questions("Data Scientist")