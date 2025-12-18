import streamlit as st
import requests
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

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
    with st.expander(item["question"]):
        st.markdown("**Your Answer**")
        st.write(item["answer"])

        st.markdown("**Scores**")
        st.write(f"Technical: {item['technical_score']} / 5")
        st.write(f"Grammar: {item['grammar_score']} / 5")

        st.markdown("**Technical Feedback**")
        st.write(item["technical_feedback"])

        st.markdown("**Grammar Suggestions**")
        st.write(item["grammar_suggestions"])

# PDF generation
def generate_evaluation_pdf(results: dict) -> BytesIO:
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()
    story = []

    # Title
    story.append(Paragraph("<b>Interview Evaluation Report</b>", styles["Title"]))
    story.append(Spacer(1, 12))

    story.append(
        Paragraph(
            f"<b>Overall Score:</b> {results.get('overall_score', 0)} / 10",
            styles["Normal"],
        )
    )
    story.append(Spacer(1, 20))

    for i, item in enumerate(results.get("details", []), start=1):
        story.append(Paragraph(f"<b>Question {i}</b>", styles["Heading2"]))
        story.append(Spacer(1, 8))

        story.append(Paragraph("<b>Question:</b>", styles["Normal"]))
        story.append(Paragraph(item["question"], styles["Normal"]))
        story.append(Spacer(1, 6))

        story.append(Paragraph("<b>Your Answer:</b>", styles["Normal"]))
        story.append(Paragraph(item["answer"], styles["Normal"]))
        story.append(Spacer(1, 6))

        story.append(
            Paragraph(
                f"<b>Score:</b> {item['score']}<br/>"
                f"<b>Technical Score:</b> {item['technical_score']} / 5<br/>"
                f"<b>Grammar Score:</b> {item['grammar_score']} / 5",
                styles["Normal"],
            )
        )
        story.append(Spacer(1, 6))

        story.append(Paragraph("<b>Technical Feedback:</b>", styles["Normal"]))
        story.append(Paragraph(item["technical_feedback"], styles["Normal"]))
        story.append(Spacer(1, 6))

        story.append(Paragraph("<b>Grammar Suggestions:</b>", styles["Normal"]))
        story.append(Paragraph(item["grammar_suggestions"], styles["Normal"]))
        story.append(Spacer(1, 14))

    doc.build(story)
    buffer.seek(0)
    return buffer


st.write("---")

pdf_buffer = generate_evaluation_pdf(results)

st.download_button(
    label="📄 Download Evaluation as PDF",
    data=pdf_buffer,
    file_name="interview_evaluation_report.pdf",
    mime="application/pdf",
)


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


