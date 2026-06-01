import streamlit as st
import pandas as pd

from database.supabase_client import supabase
from methods.auth import require_login, is_admin_role
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

st.title("Criteria")

# ==================================
# PILIH SESSION
# ==================================

try:

    session_response = (
        supabase
        .table("gdss_sessions")
        .select("*")
        .order("session_code")
        .execute()
    )

    sessions = session_response.data

except Exception as e:

    st.error(e)
    st.stop()

if len(sessions) == 0:

    st.warning(
        "Belum ada session. Silakan buat session terlebih dahulu."
    )

    st.stop()

selected_session = st.selectbox(
    "Pilih Session",
    options=sessions,
    format_func=lambda x:
        f"{x['session_code']} - {x['session_name']}"
)

session_id = selected_session["id"]

# ==================================
# TOTAL BOBOT
# ==================================

criteria_response = (
    supabase
    .table("criteria")
    .select("*")
    .eq("session_id", session_id)
    .order("criteria_code")
    .execute()
)

criteria_data = criteria_response.data

total_weight = sum(
    float(row["weight"])
    for row in criteria_data
)

st.info(
    f"Total Bobot Saat Ini : {total_weight:.2f}"
)

# ==================================
# FORM TAMBAH CRITERIA
# ==================================

if is_admin:

    st.subheader("Tambah Criteria")

    with st.form("criteria_form"):

        criteria_code = st.text_input(
            "Kode Criteria",
            placeholder="KA1"
        )

        criteria_name = st.text_input(
            "Nama Criteria",
            placeholder="Kecerdasan"
        )

        weight = st.number_input(
            "Bobot",
            min_value=0.0,
            max_value=1.0,
            step=0.01
        )

        submit = st.form_submit_button(
            "Simpan"
        )

    if submit:

        if total_weight + weight > 1:

            st.error(
                "Total bobot tidak boleh melebihi 1.0"
            )

        else:

            try:

                supabase.table(
                    "criteria"
                ).insert(
                    {
                        "criteria_code": criteria_code,
                        "criteria_name": criteria_name,
                        "weight": weight,
                        "session_id": session_id
                    }
                ).execute()

                st.success(
                    "Criteria berhasil ditambahkan"
                )

                st.rerun()

            except Exception as e:

                st.error(e)

else:

    st.info(
        "Hanya Admin yang dapat menambah Criteria"
    )

# ==================================
# DAFTAR CRITERIA
# ==================================

st.divider()

st.subheader("Daftar Criteria")

if len(criteria_data) == 0:

    st.info(
        "Belum ada criteria."
    )

else:

    df = pd.DataFrame(criteria_data)

    st.dataframe(
        df[
            [
                "criteria_code",
                "criteria_name",
                "weight"
            ]
        ],
        use_container_width=True
    )