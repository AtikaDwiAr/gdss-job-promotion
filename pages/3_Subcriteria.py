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

st.title("Subcriteria")

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

    session_data = session_response.data

except Exception as e:

    st.error(f"Gagal mengambil session: {e}")
    st.stop()

if len(session_data) == 0:

    st.warning(
        "Belum ada session. Silakan buat session terlebih dahulu."
    )

    st.stop()

selected_session = st.selectbox(
    "Pilih Session",
    options=session_data,
    format_func=lambda x:
        f"{x['session_code']} - {x['session_name']}"
)

session_id = selected_session["id"]

# ==================================
# AMBIL CRITERIA BERDASARKAN SESSION
# ==================================

try:

    criteria_response = (
        supabase
        .table("criteria")
        .select("*")
        .eq("session_id", session_id)
        .order("criteria_code")
        .execute()
    )

    criteria_data = criteria_response.data

except Exception as e:

    st.error(f"Gagal mengambil criteria: {e}")
    st.stop()

if len(criteria_data) == 0:

    st.warning(
        "Session ini belum memiliki criteria."
    )

    st.stop()

# ==================================
# FORM TAMBAH SUBCRITERIA
# ==================================

if is_admin:

    st.divider()

    st.subheader("Tambah Subcriteria")

    criteria_options = {
        f"{c['criteria_code']} - {c['criteria_name']}": c["id"]
        for c in criteria_data
    }

    with st.form("subcriteria_form"):

        selected_criteria = st.selectbox(
            "Criteria",
            options=list(criteria_options.keys())
        )

        subcriteria_code = st.text_input(
            "Kode Subcriteria",
            placeholder="K1"
        )

        subcriteria_name = st.text_input(
            "Nama Subcriteria",
            placeholder="IQ Test"
        )

        target_value = st.number_input(
            "Target Value",
            min_value=1.0,
            max_value=5.0,
            value=3.0,
            step=1.0
        )

        factor_type = st.selectbox(
            "Factor Type",
            ["core", "secondary"]
        )

        weight = st.number_input(
            "Weight",
            min_value=0.0,
            max_value=1.0,
            value=0.0,
            step=0.01
        )

        submit = st.form_submit_button(
            "Simpan"
        )

    if submit:

        try:

            criteria_id = criteria_options[
                selected_criteria
            ]

            supabase.table(
                "subcriteria"
            ).insert(
                {
                    "subcriteria_code": subcriteria_code,
                    "criteria_id": criteria_id,
                    "subcriteria_name": subcriteria_name,
                    "target_value": target_value,
                    "factor_type": factor_type,
                    "weight": weight,
                    "session_id": session_id
                }
            ).execute()

            st.success(
                "Subcriteria berhasil disimpan"
            )

            st.rerun()

        except Exception as e:

            st.error(f"Error: {e}")

else:

    st.info(
        "ℹ️ Hanya Admin yang dapat menambah Subcriteria"
    )

# ==================================
# DAFTAR SUBCRITERIA
# ==================================

st.divider()

st.subheader("Daftar Subcriteria")

try:

    response = (
        supabase
        .table("subcriteria")
        .select(
            """
            id,
            subcriteria_code,
            subcriteria_name,
            target_value,
            factor_type,
            weight,
            criteria(
                criteria_code,
                criteria_name
            )
            """
        )
        .eq("session_id", session_id)
        .order("subcriteria_code")
        .execute()
    )

    data = response.data

    if len(data) > 0:

        rows = []

        for item in data:

            rows.append(
                {
                    "Kode": item["subcriteria_code"],
                    "Nama": item["subcriteria_name"],
                    "Criteria": (
                        f"{item['criteria']['criteria_code']} - "
                        f"{item['criteria']['criteria_name']}"
                    ),
                    "Target": item["target_value"],
                    "Factor": item["factor_type"],
                    "Weight": item["weight"]
                }
            )

        df = pd.DataFrame(rows)

        st.dataframe(
            df,
            use_container_width=True
        )

    else:

        st.info(
            "Belum ada data subcriteria"
        )

except Exception as e:

    st.error(e)