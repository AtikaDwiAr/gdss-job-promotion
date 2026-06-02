import streamlit as st

def render_navigation():

    role = st.session_state.get(
        "role_name"
    )

    st.sidebar.page_link(
        "app.py",
        label="Beranda"
    )

    if role == "Admin":

        st.sidebar.page_link(
            "pages/1_Session.py",
            label="Session"
        )

    st.sidebar.page_link(
        "pages/2_Criteria.py",
        label="Criteria"
    )

    st.sidebar.page_link(
        "pages/3_Subcriteria.py",
        label="Subcriteria"
    )

    st.sidebar.page_link(
        "pages/4_Alternatives.py",
        label="Alternatives"
    )

    if role == "Decision Maker":

        st.sidebar.page_link(
            "pages/5_Evaluation.py",
            label="Evaluation"
        )

    st.sidebar.page_link(
        "pages/6_Profile_Matching.py",
        label="Profile Matching"
    )

    st.sidebar.page_link(
        "pages/7_Borda_Result.py",
        label="Borda Result"
    )