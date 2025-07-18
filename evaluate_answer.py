import requests
import language_tool_python
from textblob import TextBlob

TOGETHER_API_KEY = "tgp_v1_cxQWpIUae78O1gpIWQPoEllw3M4Zn3P2wthFunCO74A" 

tool = language_tool_python.LanguageTool('en-US')

def grammar_check(text):
    issues = tool.check(text)
    return len(issues), issues

def sentiment_analysis(text):
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    if polarity > 0.2:
        return "Positive"
    elif polarity < -0.2:
        return "Negative"
    else:
        return "Neutral"

def score_answer(question, answer):
    prompt = f"""
You are an expert AI interviewer.

Question: {question}
Candidate's Answer: {answer}

Give:
1. Technical Score out of 5
2. Brief Feedback (technical only)
"""

    response = requests.post(
        "https://api.together.xyz/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {TOGETHER_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "mistralai/Mistral-7B-Instruct-v0.1",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7
        }
    )

    output = response.json()
    print("🔍 Evaluation Raw Response:", output)

    if "choices" not in output:
        return f"Error: {output.get('error', {}).get('message', 'Unknown error')}"
    
    return output["choices"][0]["message"]["content"]






# | Module                 | Purpose                                                   |
# | ---------------------- | --------------------------------------------------------- |
# | `requests`             | Send API requests to Together AI (for scoring answers)    |
# | `language_tool_python` | Checks grammar issues in the answer                       |
# | `textblob`             | Used for sentiment analysis (positive, neutral, negative) |
