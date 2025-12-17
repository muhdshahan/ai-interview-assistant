import streamlit as st
import requests

st.title("Evaluation Results")

API_BASE = "http://localhost:8000"

results = st.session_state.get("eval_results")
if not results:
    sess_id = st.session_state.get("eval_session_id")
    if sess_id:
        try:
            r = requests.get(f"{API_BASE}/interview/results", params={"session_id": sess_id}, timeout=15)
            if r.status_code == 200:
                results = r.json()
                st.session_state.eval_results = results
            else:
                try:
                    er = r.json()
                except Exception:
                    er = {}
                st.error(er.get("detail") or er.get("error") or "Could not retrieve results")
        except Exception as e:
            st.error(f"Error fetching results: {e}")

if not results:
    st.info("No results available yet.")
    st.stop()

st.subheader("Overall Score")
st.metric(label="Score (0-10)", value=results.get("overall_score", 0))

st.write("---")
st.subheader("Details")
for item in results.get("details", []):
    with st.expander(item.get("question", "Question")):
        st.markdown("**Your answer**")
        st.write(item.get("answer", ""))
        st.markdown("**Score**")
        st.write(item.get("score", 0))
        st.markdown("**Feedback**")
        st.write(item.get("feedback", ""))

st.write("---")
col1, col2 = st.columns(2)
with col1:
    if st.button("Start New Interview"):
        for k in ("interview_session", "eval_results", "eval_session_id"):
            st.session_state.pop(k, None)
        st.switch_page("pages/interview.py")
with col2:
    if st.button("Logout"):
        for k in ("token", "user_id", "interview_session", "eval_results", "eval_session_id"):
            st.session_state.pop(k, None)
        st.switch_page("app.py")
