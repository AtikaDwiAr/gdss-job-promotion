import streamlit as st
import pandas as pd

from database.supabase_client import supabase
from methods.auth import (
    require_login,
    is_admin_role,
    is_dm_role
)
from methods.ui import apply_base_theme

st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_base_theme()
require_login()

is_admin = is_admin_role(
    st.session_state.get("role_name")
)

is_dm = is_dm_role(
    st.session_state.get("role_name")
)

st.title("Evaluation")

# ==================================
# HANYA DM YANG BOLEH MENILAI
# ==================================

if not is_dm:

    st.info(
        "Halaman ini hanya digunakan oleh Decision Maker."
    )

    st.stop()

user_id = st.session_state["user_id"]

st.write(
    f"Decision Maker : {st.session_state['user_name']}"
)

# ==================================
# SESSION ACTIVE
# ==================================

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

    st.error(f"Gagal mengambil session : {e}")
    st.stop()

if len(sessions) == 0:

    st.warning(
        "Belum ada session yang aktif."
    )

    st.stop()

selected_session = st.selectbox(
    "Session",
    sessions,
    format_func=lambda x:
        f"{x['session_code']} - {x['session_name']}"
)

session_id = selected_session["id"]

if selected_session["status"] in [
    "completed",
    "finalized"
]:

    st.warning(
        "Session sudah ditutup."
    )

    st.stop()

# ==================================
# LOAD ALTERNATIVES
# ==================================

try:

    alternatives = (
        supabase
        .table("alternatives")
        .select("*")
        .eq("session_id", session_id)
        .order("alternative_code")
        .execute()
    ).data

except Exception as e:

    st.error(f"Gagal mengambil alternatives : {e}")
    st.stop()

if len(alternatives) == 0:

    st.warning(
        "Belum ada alternative pada session ini."
    )

    st.stop()

# ==================================
# LOAD SUBCRITERIA
# ==================================

try:

    subcriteria = (
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

except Exception as e:

    st.error(f"Gagal mengambil subcriteria : {e}")
    st.stop()

if len(subcriteria) == 0:

    st.warning(
        "Belum ada subcriteria pada session ini."
    )

    st.stop()

# ==================================
# PILIH ALTERNATIVE
# ==================================

alternative_options = {
    f"{alt['alternative_code']} - {alt['alternative_name']}":
    alt["id"]
    for alt in alternatives
}

selected_alternative = st.selectbox(
    "Alternative",
    list(alternative_options.keys())
)

alternative_id = alternative_options[
    selected_alternative
]

# ==================================
# LOAD EXISTING EVALUATION
# ==================================

existing = (
    supabase
    .table("evaluations")
    .select("*")
    .eq("user_id", user_id)
    .eq("alternative_id", alternative_id)
    .eq("session_id", session_id)
    .execute()
).data

existing_scores = {
    row["subcriteria_id"]: float(row["score"])
    for row in existing
}

# ==================================
# FORM PENILAIAN
# ==================================

st.subheader("Input Nilai")

scores = {}

with st.form("evaluation_form"):

    current_criteria = None

    for sub in subcriteria:

        criteria_name = (
            sub["criteria"]["criteria_code"]
            + " - "
            + sub["criteria"]["criteria_name"]
        )

        if current_criteria != criteria_name:

            st.markdown(
                f"### {criteria_name}"
            )

            current_criteria = criteria_name

        score = st.number_input(
            label=(
                f"{sub['subcriteria_code']} - "
                f"{sub['subcriteria_name']}"
            ),
            min_value=1.0,
            max_value=5.0,
            value=float(
                existing_scores.get(
                    sub["id"],
                    1
                )
            ),
            step=1.0,
            key=sub["id"]
        )

        scores[sub["id"]] = score

    submit = st.form_submit_button(
        "Simpan Penilaian"
    )

if submit:

    try:

        for sub_id, score in scores.items():

            existing_record = (
                supabase
                .table("evaluations")
                .select("id")
                .eq("user_id", user_id)
                .eq("alternative_id", alternative_id)
                .eq("subcriteria_id", sub_id)
                .eq("session_id", session_id)
                .execute()
            )

            if len(existing_record.data) > 0:

                evaluation_id = (
                    existing_record
                    .data[0]["id"]
                )

                (
                    supabase
                    .table("evaluations")
                    .update(
                        {
                            "score": score
                        }
                    )
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
                    .insert(
                        {
                            "user_id": user_id,
                            "alternative_id": alternative_id,
                            "subcriteria_id": sub_id,
                            "score": score,
                            "session_id": session_id
                        }
                    )
                    .execute()
                )

        st.success(
            "Penilaian berhasil disimpan"
        )

        st.rerun()

    except Exception as e:

        st.error(
            f"Gagal menyimpan penilaian : {e}"
        )

# ==================================
# DATA EVALUASI SAYA
# ==================================

st.divider()

st.subheader(
    "Data Evaluasi Saya"
)

try:

    evaluations = (
        supabase
        .table("evaluations")
        .select("""
            score,
            alternatives(
                alternative_code,
                alternative_name
            ),
            subcriteria(
                subcriteria_code,
                subcriteria_name
            )
        """)
        .eq("user_id", user_id)
        .eq("session_id", session_id)
        .execute()
    ).data

    if len(evaluations) > 0:

        rows = []

        for item in evaluations:

            rows.append(
                {
                    "Alternative":
                        f"{item['alternatives']['alternative_code']} - "
                        f"{item['alternatives']['alternative_name']}",

                    "Subcriteria":
                        f"{item['subcriteria']['subcriteria_code']} - "
                        f"{item['subcriteria']['subcriteria_name']}",

                    "Score":
                        item["score"]
                }
            )

        df = pd.DataFrame(rows)

        st.dataframe(
            df,
            use_container_width=True
        )

    else:

        st.info(
            "Belum ada data evaluasi."
        )

except Exception as e:

    st.error(e)