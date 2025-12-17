import streamlit as st
import requests

st.title("Create Account")

with st.form("registerForm"):
    username = st.text_input("Username", max_chars=20)
    email = st.text_input("Email")
    password = st.text_input("Password", type="password", max_chars=24)
    submit = st.form_submit_button("Register")

if submit:
    # Backend endpoint URL
    BACKEND_URL = "http://localhost:8000/auth/register"

    try:
        resp = requests.post(
            BACKEND_URL,
            json={
                "username": username,
                "email": email,
                "password": password
            },
            timeout=5
        )
        data = resp.json()
        if resp.status_code == 200:
            st.success("Registration sucessful! Please login below.")
        else:
            # Show error message from backend
            st.error(data.get("error", "Registration failed."))
    except Exception as e:
        st.error(f"Error connecting to backend:{e}")

if st.button("Already have an account? Login"):
    st.switch_page("pages/login.py")