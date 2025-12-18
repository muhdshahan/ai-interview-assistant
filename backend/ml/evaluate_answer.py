from textblob import TextBlob
from groq import Groq
import os
from dotenv import load_dotenv
import json

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)


def sentiment_analysis(text):
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    print(polarity)
    if polarity > 0.2:
        return "Positive"
    elif polarity < -0.2:
        return "Negative"
    else:
        return "Neutral"


def score_answer(question, answer):

    prompt = f"""
    You are an expert AI interviewer.

    Evaluate the candidate answer STRICTLY in JSON.

    Question:
    {question}

    Candidate Answer:
    {answer}

    Return ONLY valid JSON in this exact format:

    {{
    "technical_score": number out of 5,
    "grammar_score": number out of 5,
    "technical_feedback": "2-3 lines explaining what is missing or correct",
    "grammar_suggestions": "1-2 grammar improvement suggestions"
    }}
    """

    try:
        resonse = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )
        evaluation_text = resonse.choices[0].message.content.strip()
        try:
            evaluation_json = json.loads(evaluation_text)
        except:
            evaluation_json = {
                "technical_score": 0.0,
                "grammar_score": 0.0,
                "technical_feedback": "Could not properly evaluate the answer.",
                "grammar_suggestions": "Please improve clarity and grammar."
            }

        return {
            "technical_score": float(evaluation_json.get("technical_score", 0)),
            "grammar_score": float(evaluation_json.get("grammar_score", 0)),
            "technical_feedback": evaluation_json.get("technical_feedback", ""),
            "grammar_suggestions": evaluation_json.get("grammar_suggestions", ""),
            "sentiment": sentiment_analysis(answer)
        }
    
    except Exception as e:
        print("ERROR:", e)
        return f"Error: {str(e)}"


if __name__ == "__main__":

    question = input("Enter the interview question: ")
    answer = input("Enter the candidate's answer: ")

    result = score_answer(question, answer)

    print("\nRESULT")
    print(result)
    print("\nSentiment:", result["sentiment"])