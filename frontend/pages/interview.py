import requests
import streamlit as st

st.title("Interview")

API_BASE = "http://localhost:8000"

sess = st.session_state.get("interview_session")

if not sess:
    with st.form("start_interview"):
        job_title = st.text_input("Job title")
        num_questions = st.slider("Number of questions", 3, 10, 5)
        start = st.form_submit_button("Start Interview")
    if start:
        if not job_title.strip():
            st.warning("Please enter a job title before starting the interview.")
            st.stop()
        
        try:
            resp = requests.post(
                f"{API_BASE}/interview/start",
                json={
                    "job_title": job_title.strip() or None,
                    "num_questions": int(num_questions)
                },
                timeout=10,
            )
            data = resp.json()
            if resp.status_code == 200:
                st.session_state.interview_session = {
                    "session_id": data["session_id"],
                    "questions": data["questions"],
                    "answers": {},
                    "current_idx": 0
                }
                st.rerun()
            else:
                st.error(data.get("detail") or data.get("error") or "Could not start interview.")
        except Exception as e:
            st.error(f"Failed to contact backend: {e}")
    st.stop()

sess = st.session_state.get("interview_session")
# Add this near the top, after getting sess
if "transcription_status" not in st.session_state:
    st.session_state.transcription_status = None
questions = sess["questions"]
idx = int(sess.get("current_idx", 0))
idx = max(0, min(idx, len(questions) - 1))

st.metric("Progress", f"{idx + 1} / {len(questions)}")

q = questions[idx]
st.subheader(f"Question {idx + 1}")
st.write(q["text"])

ans_key = f"ans_{q['id']}"
default_ans = sess["answers"].get(q["id"], "")
# Clear widget state so it re-reads value=
# if ans_key in st.session_state:
#     del st.session_state[ans_key]

answer_text = st.text_area("Your answer", value=default_ans, key=ans_key, height=180)

st.write("🎤 Answer using voice")
audio = st.audio_input("Record your answer", key=f"audio_recorder_{q['id']}")

if audio is not None:
    if st.button("Transcribe Audio", key=f"transcribe_{q['id']}"):
        with st.spinner("Transcribing audio..."):
            try:
                files = {"file": ("answer.wav", audio.getvalue(), "audio/wav")}
                r = requests.post(f"{API_BASE}/stt/transcribe", files=files, timeout=30)

                if r.status_code == 200:
                    transcript = r.json().get("text", "").strip()
                    if transcript:
                        # Save transcript to session
                        st.session_state.interview_session["answers"][q["id"]] = transcript
                        # Set a temporary flag for success message
                        st.session_state.transcription_status = "success"
                        st.session_state.last_transcript = transcript
                    else:
                        st.session_state.transcription_status = "empty"
                else:
                    st.session_state.transcription_status = "error"
                    st.session_state.transcription_error = f"Status {r.status_code}: {r.text}"

            except Exception as e:
                st.session_state.transcription_status = "exception"
                st.session_state.transcription_error = str(e)

        # Trigger rerun AFTER processing
        st.rerun()

# --- Show feedback AFTER rerun ---
if st.session_state.transcription_status == "success":
    st.success(f"Copy the your answer to the text box: {st.session_state.last_transcript}")
# Clear the audio recorder for next use
    if f"audio_recorder_{q['id']}" in st.session_state:
        del st.session_state[f"audio_recorder_{q['id']}"]
    
    # Optional: clear status after showing once
    st.session_state.transcription_status = None

elif st.session_state.transcription_status == "empty":
    st.warning("Transcription completed but returned empty text.")

elif st.session_state.transcription_status == "error":
    st.error("Transcription failed")
    st.code(st.session_state.transcription_error)

elif st.session_state.transcription_status == "exception":
    st.error("Error during transcription")
    st.code(st.session_state.transcription_error)

col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("Save Answer"):
        try:
            payload = {
                "session_id": sess["session_id"],
                "question_id": q["id"],
                "answer": st.session_state.get(ans_key, ""),
            }
            r = requests.post(f"{API_BASE}/interview/answer", json=payload,timeout=10)
            if r.status_code == 200:
                st.session_state.interview_session["answers"][q["id"]] = payload["answer"]
                st.success("Saved")
            else:
                try:
                    er = r.json()
                    st.error(er.get("detail") or er.get("error") or "Save failed")
                except Exception:
                    st.error("Save failed")
        except Exception as e:
            st.error(f"Error: {e}")
with col2:
    if st.button("Previous", disabled=(idx == 0)):
        st.session_state.interview_session["current_idx"] = idx - 1
        st.rerun()
with col3:
    if st.button("Next", disabled=(idx >= len(questions) - 1)):
        st.session_state.interview_session["current_idx"] = idx + 1
        st.rerun()
with col4:
    finish_now = st.button("Finish Interview")

if finish_now:
    try:
        r = requests.post(
            f"{API_BASE}/interview/finish",
            json={"session_id": sess["session_id"]},
            timeout=20,
        )
        data = r.json()
        if r.status_code == 200:
            st.session_state.eval_results = data
            st.session_state.eval_session_id = sess["session_id"]
            st.switch_page("pages/evaluation.py")
        else:
            st.error(data.get("detail") or data.get("error") or "Finish failed")
    except Exception as e:
        st.error(f"Error finishing interview: {e}")


st.write("---")
if st.button("Cancel Interview"):
    for k in ("interview_session", "eval_results", "eval_session_id"):
        st.session_state.pop(k, None)
    st.switch_page("pages/interview.py")
