import streamlit as st
import pandas as pd
from database.supabase_client import supabase
from methods.auth import require_login

require_login()

st.title("Subcriteria")

# ==========================
# AMBIL DATA CRITERIA
# ==========================

try:

    criteria_response = (
        supabase
        .table("criteria")
        .select("*")
        .order("criteria_code")
        .execute()
    )

    criteria_data = criteria_response.data

except Exception as e:

    st.error(f"Gagal mengambil data criteria: {e}")
    st.stop()

# ==========================
# FORM TAMBAH SUBCRITERIA
# ==========================

st.subheader("Tambah Subcriteria")

if len(criteria_data) == 0:

    st.warning("Belum ada data criteria")
    st.stop()

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
        placeholder="IQ"
    )

    target_value = st.number_input(
        "Target Value",
        min_value=1.0,
        max_value=5.0,
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
        step=0.1
    )

    submit = st.form_submit_button("Simpan")

    if submit:

        try:

            criteria_id = criteria_options[selected_criteria]

            supabase.table("subcriteria").insert({
                "subcriteria_code": subcriteria_code,
                "criteria_id": criteria_id,
                "subcriteria_name": subcriteria_name,
                "target_value": target_value,
                "factor_type": factor_type,
                "weight": weight
            }).execute()

            st.success("Subcriteria berhasil disimpan")

        except Exception as e:

            st.error(f"Error : {e}")

# ==========================
# TAMPILKAN DATA
# ==========================

st.divider()

st.subheader("Daftar Subcriteria")

try:

    response = (
        supabase
        .table("subcriteria")
        .select("""
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
        """)
        .order("subcriteria_code")
        .execute()
    )

    data = response.data

    if len(data) > 0:

        rows = []

        for item in data:

            rows.append({
                "Kode": item["subcriteria_code"],
                "Nama": item["subcriteria_name"],
                "Criteria": f"{item['criteria']['criteria_code']} - {item['criteria']['criteria_name']}",
                "Target": item["target_value"],
                "Factor": item["factor_type"],
                "Weight": item["weight"]
            })

        df = pd.DataFrame(rows)

        st.dataframe(
            df,
            use_container_width=True
        )

    else:

        st.info("Belum ada data subcriteria")

except Exception as e:

    st.error(e)