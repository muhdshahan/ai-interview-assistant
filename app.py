import streamlit as st
import os
from generate_questions import generate_interview_questions
from audio_to_text import record_audio_file, transcribe_audio_file
from evaluate_answer import grammar_check, sentiment_analysis, score_answer

st.set_page_config(page_title="AI Interview Assistant")
st.title("🎤 AI Interview Assistant")

# Session state setup
if "questions" not in st.session_state:
    st.session_state.questions = []
if "q_index" not in st.session_state:
    st.session_state.q_index = 0
if "transcribed_text" not in st.session_state:
    st.session_state.transcribed_text = ""

# Job role input
role = st.text_input("Enter Job Role (e.g., Data Scientist, Web Developer)")

# Generate interview questions
if st.button("🎯 Generate Questions") and role:
    st.session_state.questions = generate_interview_questions(role)
    st.session_state.q_index = 0
    st.session_state.transcribed_text = ""

# If questions are available
if st.session_state.q_index < len(st.session_state.questions):
    question = st.session_state.questions[st.session_state.q_index]
    st.subheader(f"Question {st.session_state.q_index + 1}")
    st.write(question)

    # Start recording
    if st.button("🎙️ Start Recording"):
        st.info("Recording for 15 seconds...")
        filename = record_audio_file(duration=15)
        st.session_state.transcribed_text = transcribe_audio_file(filename)
        os.remove(filename)

    # Show transcription
    if st.session_state.transcribed_text:
        st.text_area("📝 Transcribed Answer", st.session_state.transcribed_text, height=100)

        if st.button("✅ Analyze Answer"):
            answer = st.session_state.transcribed_text
            g_score, g_issues = grammar_check(answer)
            sentiment = sentiment_analysis(answer)
            feedback = score_answer(question, answer)

            st.markdown("### 📊 Evaluation")
            st.write(f" Sentiment: {sentiment}")
            st.write(f" Grammar Issues: {g_score}")
            st.markdown("####  Technical Feedback:")
            st.markdown(feedback)

            # Go to next question
            st.session_state.q_index += 1
            st.session_state.transcribed_text = ""
else:
    if st.session_state.questions:
        st.success("✅ Interview Completed.")
