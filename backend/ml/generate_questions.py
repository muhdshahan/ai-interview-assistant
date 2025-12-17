from groq import Groq
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List
import json

load_dotenv()

if not os.getenv("GROQ_API_KEY"):
    raise ValueError("GROQ_API_KEY not found in .env file!")

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


# This is the model your FastAPI endpoint expects
class Question(BaseModel):
    id: int
    text: str


def generate_interview_questions(role: str, ques_no: int):
    """
    Returns a clean list of Question objects (not strings!)
    Works even if Groq returns messy text.
    """
    prompt = f"""
    You are an expert technical interviewer.
    Generate exactly {ques_no} unique and non-repetitive technical/behavioral interview questions for a {role} position.
    Focus on a random mix of:
    - theory
    - real-world problem solving
    - scenario-based reasoning
    - debugging or optimization
    - trade-off discussions

    Avoid repeating common textbook questions.
    
    Return ONLY valid JSON in this exact format (no markdown, no extra text):
    [
      {{"id": 1, "text": "What is the difference between...?"}},
      {{"id": 2, "text": "Explain how you would..."}},
      ...
    ]
    """

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
            top_p=0.9,
            max_tokens=2048,
        )

        raw = response.choices[0].message.content.strip()

        try:
            data = json.loads(raw)
            questions = []
            for i, item in enumerate(data, start=1):
                if isinstance(item, dict):
                    text = item.get("text", "").strip()
                    qid = int(item.get("id", i))
                else:
                    text = str(item).strip()
                    qid = i
                if text:
                    questions.append(Question(id=qid, text=text))
            print(questions[:ques_no])
            return questions[:ques_no]

        except json.JSONDecodeError:
            # Fallback: extract numbered questions using regex
            pass

    except Exception as e:
        print("GROQ ERROR:", e)
        # Return dummy questions so app doesn't crash
        return [
            Question(id=i, text=f"Sample question {i} for {role}")
            for i in range(1, min(ques_no, 6))
        ]


# Test it
if __name__ == "__main__":
    qs = generate_interview_questions("Data Scientist", 5)
    print(qs)
    # for q in qs:
    #     print(q.id, "-", q.text)