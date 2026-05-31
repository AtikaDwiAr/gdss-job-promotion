import streamlit as st
import pandas as pd
from database.supabase_client import supabase
from methods.auth import require_login

require_login()

st.title("Criteria")

# ==========================
# FORM TAMBAH DATA
# ==========================

st.subheader("Tambah Criteria")

with st.form("criteria_form"):

    criteria_code = st.text_input("Kode Criteria", placeholder="KA1")

    criteria_name = st.text_input(
        "Nama Criteria",
        placeholder="Kecerdasan"
    )

    weight = st.number_input(
        "Bobot",
        min_value=0.0,
        max_value=1.0,
        step=0.1
    )

    submit = st.form_submit_button("Simpan")

    if submit:

        try:

            supabase.table("criteria").insert({
                "criteria_code": criteria_code,
                "criteria_name": criteria_name,
                "weight": weight
            }).execute()

            st.success("Data berhasil disimpan")

        except Exception as e:

            st.error(f"Error : {e}")

# ==========================
# TAMPILKAN DATA
# ==========================

st.divider()

st.subheader("Daftar Criteria")

try:

    response = (
        supabase
        .table("criteria")
        .select("*")
        .order("id")
        .execute()
    )

    data = response.data

    if data:

        df = pd.DataFrame(data)

        st.dataframe(
            df,
            use_container_width=True
        )

    else:

        st.info("Belum ada data criteria")

except Exception as e:

    st.error(e)