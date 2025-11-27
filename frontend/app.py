import streamlit as st
import os
import requests
from backend.ml.generate_questions import generate_interview_questions
from backend.ml.audio_to_text import record_audio_file
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = "http://127.0.0.1:8080" 

st.set_page_config(page_title="AI Interview Assistant")
st.title("🎤 AI Interview Assistant")

# Session state setup
if "questions" not in st.session_state:
    st.session_state.questions = []
if "q_index" not in st.session_state:
    st.session_state.q_index = 0
if "transcribed_text" not in st.session_state:
    st.session_state.transcribed_text = ""
if "evaluation" not in st.session_state:
    st.session_state.evaluation = ""


# Job role input
role = st.text_input("Enter Job Role (e.g., Data Scientist, Web Developer)")


# Generate interview questions
if st.button("🎯 Generate Questions") and role:
    st.session_state.questions = generate_interview_questions(role)
    st.session_state.q_index = 0
    st.session_state.transcribed_text = ""
    st.session_state.evaluation = ""


# If questions are available
# If questions are available
if st.session_state.q_index < len(st.session_state.questions):

    question = st.session_state.questions[st.session_state.q_index]

    st.subheader(f"Question {st.session_state.q_index + 1}")
    st.write(question)

    # 🔴 Start local recording
    if st.button("🎙️ Start Recording"):
        st.info("Recording for 15 seconds...")
        
        filename = record_audio_file(duration=15)
        st.success("Recording finished! Uploading to server...")

        try:
            with open(filename, "rb") as audio_file:
                resp = requests.post(
                    f"{BACKEND_URL}/transcribe-audio",
                    files={"file": ("audio.wav", audio_file, "audio/wav")}
                )

            os.remove(filename)

            if resp.status_code == 200:
                result = resp.json()
                st.session_state.transcribed_text = result["transcription"]
                st.session_state.sentiment = result["sentiment"]
            else:
                st.error("Transcription failed.")

        except Exception as e:
            st.error(f"Error sending audio: {e}")

    # 📝 Display transcription
    if st.session_state.transcribed_text:
        st.text_area("📝 Transcribed Answer", st.session_state.transcribed_text, height=100)

        if st.button("✅ Analyze Answer"):
            answer = st.session_state.transcribed_text

            # ------------------------------
            # 🔵 Call FastAPI evaluation
            # ------------------------------
            try:
                eval_resp = requests.post(
                    f"{BACKEND_URL}/evaluate-answer",
                    json={
                        "question": question,
                        "answer": answer
                    }
                )

                if eval_resp.status_code == 200:
                    data = eval_resp.json()
                    st.session_state.evaluation = data["evaluation"]
                    st.session_state.sentiment = data["sentiment"]

                else:
                    st.error("Evaluation failed.")

            except Exception as e:
                st.error(f"Error: {e}")

    # Show results
    if st.session_state.evaluation:
        st.markdown("### 📊 Evaluation")
        st.write(f"**Sentiment:** {st.session_state.sentiment}")
        st.markdown("#### 🧠 Technical + Grammar Feedback")
        st.markdown(st.session_state.evaluation)

        # Go to next question
        if st.button("➡️ Next Question"):
            st.session_state.q_index += 1
            st.session_state.transcribed_text = ""
            st.session_state.evaluation = ""

else:
    if st.session_state.questions:
        st.success("Interview Completed!")