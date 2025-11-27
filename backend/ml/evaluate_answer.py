from textblob import TextBlob
from groq import Groq
import os
from dotenv import load_dotenv

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

    Evaluate the candidate's answer with 3 dimensions:
    1. Technical correctness  
    2. Grammar & clarity  

    Question: {question}
    Candidate's Answer: {answer}

    Provide the output in the EXACT format below:

    Technical Score: X/5
    Grammar Score: X/5
    Feedback: <2–3 lines of technical feedback>
    Grammar Suggestions: <1–2 grammar improvement suggestions>
    """

    try:
        resonse = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )

        evaluation_text = resonse.choices[0].message.content

        sentiment = sentiment_analysis(answer)

        final_output = {
            "evaluation": evaluation_text,
            "sentiment": sentiment
        }

        print("Final Combined Output:", final_output)
        return final_output
    
    except Exception as e:
        print("ERROR:", e)
        return f"Error: {str(e)}"


if __name__ == "__main__":

    question = input("Enter the interview question: ")
    answer = input("Enter the candidate's answer: ")

    result = score_answer(question, answer)

    print("\nRESULT")
    print(result["evaluation"])
    print("\nSentiment:", result["sentiment"])