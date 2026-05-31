import streamlit as st

from methods.auth import authenticate_user, init_auth_state, set_user_session
from methods.ui import apply_base_theme

st.set_page_config(
    page_title="GDSS Recruitment System",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_base_theme()

init_auth_state()

st.title("GDSS Recruitment System")

if not st.session_state["is_authenticated"]:
    st.subheader("Login")

    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")

    if submit:
        user, error = authenticate_user(email, password)

        if error:
            st.error(error)
        else:
            set_user_session(user)
            st.success("Login berhasil")
            st.rerun()

    st.stop()

st.write(f"Selamat datang, {st.session_state['user_name']}")