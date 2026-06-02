import streamlit as st
import pandas as pd

from database.supabase_client import supabase
from methods.auth import (
    require_login,
    is_dm_role
)
from methods.ui import apply_base_theme
from methods.navigation import render_navigation

st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_base_theme()
require_login()
render_navigation()

# =====================================
# ROLE CHECK
# =====================================

if not is_dm_role(
    st.session_state.get("role_name")
):

    st.info(
        "Halaman ini hanya digunakan oleh Decision Maker."
    )

    st.stop()

user_id = st.session_state["user_id"]

st.title("Evaluation")

st.info(
    f"Decision Maker : {st.session_state['user_name']}"
)

# =====================================
# SESSION
# =====================================

try:

    sessions = (
        supabase
        .table("gdss_sessions")
        .select("*")
        .eq("status", "active")
        .order("session_code")
        .execute()
    ).data

except Exception as e:

    st.error(e)
    st.stop()

if len(sessions) == 0:

    st.warning(
        "Penilaian hanya dapat dilakukan pada session ACTIVE."
    )

    st.stop()

selected_session = st.selectbox(
    "Session",
    sessions,
    format_func=lambda x:
    f"{x['session_code']} - {x['session_name']}"
)

session_id = selected_session["id"]

# =====================================
# ALTERNATIVES
# =====================================

alternatives = (
    supabase
    .table("alternatives")
    .select("*")
    .eq("session_id", session_id)
    .order("alternative_code")
    .execute()
).data

if len(alternatives) == 0:

    st.warning(
        "Belum ada alternative"
    )

    st.stop()

# =====================================
# CRITERIA
# =====================================

criteria_data = (
    supabase
    .table("criteria")
    .select("*")
    .eq("session_id", session_id)
    .order("criteria_code")
    .execute()
).data

if len(criteria_data) == 0:

    st.warning(
        "Belum ada criteria"
    )

    st.stop()

# =====================================
# SUBCRITERIA
# =====================================

subcriteria_data = (
    supabase
    .table("subcriteria")
    .select("""
        *,
        criteria(
            criteria_code,
            criteria_name
        )
    """)
    .eq("session_id", session_id)
    .order("subcriteria_code")
    .execute()
).data

if len(subcriteria_data) == 0:

    st.warning(
        "Belum ada subcriteria"
    )

    st.stop()

# =====================================
# TABS
# =====================================

tab1, tab2 = st.tabs([
    "Data Evaluasi Saya",
    "Input Penilaian"
])

# =====================================
# TAB DATA
# =====================================

with tab1:

    st.subheader(
        "Data Evaluasi Saya"
    )

    try:

        evaluations = (

            supabase
            .table("evaluations")
            .select("""
                *,
                alternatives(
                    alternative_code,
                    alternative_name
                ),
                subcriteria(
                    subcriteria_code,
                    subcriteria_name
                )
            """)
            .eq(
                "user_id",
                user_id
            )
            .eq(
                "session_id",
                session_id
            )
            .execute()

        ).data

        if len(evaluations) > 0:

            rows = []

            for item in evaluations:

                rows.append({

                    "Alternative":

                    f"{item['alternatives']['alternative_code']} - "
                    f"{item['alternatives']['alternative_name']}",

                    "Subcriteria":

                    f"{item['subcriteria']['subcriteria_code']} - "
                    f"{item['subcriteria']['subcriteria_name']}",

                    "Score":
                    item["score"]

                })

            st.dataframe(
                pd.DataFrame(rows),
                use_container_width=True
            )

        else:

            st.info(
                "Belum ada data evaluasi"
            )

    except Exception as e:

        st.error(e)

# =====================================
# TAB INPUT / EDIT
# =====================================

with tab2:

    st.subheader(
        "Input Penilaian"
    )

    alternative_options = {

        f"{a['alternative_code']} - "
        f"{a['alternative_name']}":

        a["id"]

        for a in alternatives

    }

    selected_alternative = st.selectbox(
        "Alternative",
        list(
            alternative_options.keys()
        )
    )

    alternative_id = (
        alternative_options[
            selected_alternative
        ]
    )

    criteria_options = {

        f"{c['criteria_code']} - "
        f"{c['criteria_name']}":

        c["id"]

        for c in criteria_data

    }

    selected_criteria = st.selectbox(
        "Criteria",
        list(
            criteria_options.keys()
        )
    )

    criteria_id = (
        criteria_options[
            selected_criteria
        ]
    )

    selected_subcriteria = [

        s

        for s in subcriteria_data

        if s["criteria_id"]
        == criteria_id

    ]

    existing = (

        supabase
        .table("evaluations")
        .select("*")
        .eq(
            "user_id",
            user_id
        )
        .eq(
            "alternative_id",
            alternative_id
        )
        .eq(
            "session_id",
            session_id
        )
        .execute()

    ).data

    existing_scores = {

        row["subcriteria_id"]:
        float(
            row["score"]
        )

        for row in existing

    }

    scores = {}

    with st.form(
        "evaluation_form"
    ):

        for sub in selected_subcriteria:

            scores[sub["id"]] = st.number_input(

                label=
                f"{sub['subcriteria_code']} - "
                f"{sub['subcriteria_name']}",

                min_value=1.0,
                max_value=5.0,

                value=float(
                    existing_scores.get(
                        sub["id"],
                        1
                    )
                ),

                step=1.0,

                key=f"sub_{sub['id']}"

            )

        submit = st.form_submit_button(
            "Simpan"
        )

    if submit:

        try:

            for sub_id, score in scores.items():

                existing_record = (

                    supabase
                    .table("evaluations")
                    .select("id")
                    .eq(
                        "user_id",
                        user_id
                    )
                    .eq(
                        "alternative_id",
                        alternative_id
                    )
                    .eq(
                        "subcriteria_id",
                        sub_id
                    )
                    .eq(
                        "session_id",
                        session_id
                    )
                    .execute()

                )

                if len(
                    existing_record.data
                ) > 0:

                    evaluation_id = (
                        existing_record
                        .data[0]["id"]
                    )

                    (
                        supabase
                        .table("evaluations")
                        .update({
                            "score": score
                        })
                        .eq(
                            "id",
                            evaluation_id
                        )
                        .execute()
                    )

                else:

                    (
                        supabase
                        .table("evaluations")
                        .insert({

                            "user_id":
                            user_id,

                            "alternative_id":
                            alternative_id,

                            "subcriteria_id":
                            sub_id,

                            "score":
                            score,

                            "session_id":
                            session_id

                        })
                        .execute()
                    )

            st.success(
                "Penilaian berhasil disimpan"
            )

            st.rerun()

        except Exception as e:

            st.error(e)
