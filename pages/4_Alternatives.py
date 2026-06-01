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

st.title("Alternatives")

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
# FORM TAMBAH ALTERNATIVE
# ==================================

if is_admin:

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

        submit = st.form_submit_button(
            "Simpan"
        )

    if submit:

        if alternative_code == "" or alternative_name == "":

            st.warning(
                "Kode dan Nama wajib diisi"
            )

        else:

            try:

                supabase.table(
                    "alternatives"
                ).insert(
                    {
                        "alternative_code": alternative_code,
                        "alternative_name": alternative_name,
                        "description": description,
                        "session_id": session_id
                    }
                ).execute()

                st.success(
                    "Alternative berhasil disimpan"
                )

                st.rerun()

            except Exception as e:

                st.error(f"Error : {e}")

else:

    st.info(
        "ℹ️ Hanya Admin yang dapat menambah Alternative"
    )

# ==================================
# TAMPILKAN DATA
# ==================================

st.divider()

st.subheader("Daftar Alternatives")

try:

    response = (
        supabase
        .table("alternatives")
        .select("*")
        .eq("session_id", session_id)
        .order("alternative_code")
        .execute()
    )

    data = response.data

except Exception as e:

    st.error(e)
    st.stop()

if len(data) > 0:

    rows = []

    for item in data:

        rows.append(
            {
                "Kode": item["alternative_code"],
                "Nama": item["alternative_name"],
                "Deskripsi": item["description"]
            }
        )

    df = pd.DataFrame(rows)

    st.dataframe(
        df,
        use_container_width=True
    )

else:

    st.info(
        "Belum ada data alternative"
    )