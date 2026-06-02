import streamlit as st
import pandas as pd

from database.supabase_client import supabase
from methods.auth import (
    authenticate_user,
    init_auth_state,
    set_user_session,
    logout
)
from methods.ui import apply_base_theme
from methods.navigation import render_navigation

st.set_page_config(
    page_title="Job Promotion Group Decision Support System",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_base_theme()
init_auth_state()

# =====================================
# LOGIN
# =====================================

if not st.session_state["is_authenticated"]:

    st.title("Job Promotion Group Decision Support System")

    with st.form("login_form"):

        email = st.text_input("Email")
        password = st.text_input(
            "Password",
            type="password"
        )

        submit = st.form_submit_button(
            "Login"
        )

    if submit:

        user, error = authenticate_user(
            email,
            password
        )

        if error:

            st.error(error)

        else:

            set_user_session(user)

            st.success(
                "Login berhasil"
            )

            st.rerun()

    st.stop()

# =====================================
# SIDEBAR
# =====================================

with st.sidebar:

    st.success(
        f"👤 {st.session_state['user_name']}"
    )

    st.caption(
        st.session_state["role_name"]
    )

    if st.button("Logout"):

        logout()
        st.rerun()

render_navigation()

# =====================================
# DASHBOARD
# =====================================

st.title("Beranda")

st.write(
    f"Selamat datang **{st.session_state['user_name']}**"
)

# =====================================
# AMBIL DATA
# =====================================

sessions = (
    supabase
    .table("gdss_sessions")
    .select("*")
    .execute()
).data

criteria = (
    supabase
    .table("criteria")
    .select("*")
    .execute()
).data

subcriteria = (
    supabase
    .table("subcriteria")
    .select("*")
    .execute()
).data

alternatives = (
    supabase
    .table("alternatives")
    .select("*")
    .execute()
).data

# =====================================
# CARD SUMMARY
# =====================================

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Session",
    len(sessions)
)

col2.metric(
    "Criteria",
    len(criteria)
)

col3.metric(
    "Subcriteria",
    len(subcriteria)
)

col4.metric(
    "Alternatives",
    len(alternatives)
)

st.divider()

# =====================================
# SESSION STATUS
# =====================================

st.subheader("Daftar Session")

if len(sessions) > 0:

    session_df = pd.DataFrame(
        [
            {
                "Kode":
                s["session_code"],

                "Nama":
                s["session_name"],

                "Status":
                s["status"]
            }
            for s in sessions
        ]
    )

    st.dataframe(
        session_df,
        use_container_width=True
    )

else:

    st.info(
        "Belum ada session"
    )

# =====================================
# SESSION AKTIF
# =====================================

active_session = [

    s for s in sessions

    if s["status"] == "active"
]

st.divider()

st.subheader("Session Aktif")

if len(active_session) > 0:

    for s in active_session:

        st.success(
            f"{s['session_code']} - "
            f"{s['session_name']}"
        )

else:

    st.warning(
        "Tidak ada session aktif"
    )

# =====================================
# INFO USER
# =====================================

st.divider()

st.subheader("Informasi Pengguna")

col1, col2 = st.columns(2)

with col1:

    st.metric(
        "Nama",
        st.session_state["user_name"]
    )

with col2:

    st.metric(
        "Role",
        st.session_state["role_name"]
    )