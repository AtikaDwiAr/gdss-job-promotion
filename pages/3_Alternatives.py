import streamlit as st
import pandas as pd
from database.supabase_client import supabase
from methods.auth import require_login

require_login()
st.title("Alternatives")

# ==========================
# FORM TAMBAH ALTERNATIVE
# ==========================

st.subheader("Tambah Alternative")

with st.form("alternative_form"):

    alternative_code = st.text_input(
        "Kode Alternative",
        placeholder="A001"
    )

    alternative_name = st.text_input(
        "Nama Alternative",
        placeholder="Andi"
    )

    description = st.text_area(
        "Deskripsi",
        placeholder="Kandidat untuk promosi jabatan"
    )

    submit = st.form_submit_button("Simpan")

    if submit:

        if alternative_code == "" or alternative_name == "":

            st.warning("Kode dan Nama wajib diisi")

        else:

            try:

                supabase.table("alternatives").insert({
                    "alternative_code": alternative_code,
                    "alternative_name": alternative_name,
                    "description": description
                }).execute()

                st.success("Alternative berhasil disimpan")

            except Exception as e:

                st.error(f"Error : {e}")

# ==========================
# TAMPILKAN DATA
# ==========================

st.divider()

st.subheader("Daftar Alternatives")

try:

    response = (
        supabase
        .table("alternatives")
        .select("*")
        .order("alternative_code")
        .execute()
    )

    data = response.data

    if len(data) > 0:

        df = pd.DataFrame(data)

        st.dataframe(
            df,
            use_container_width=True
        )

    else:

        st.info("Belum ada data alternative")

except Exception as e:

    st.error(e)