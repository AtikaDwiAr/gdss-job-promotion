import streamlit as st
import pandas as pd

from database.supabase_client import supabase
from methods.auth import (
    require_login,
    is_admin_role
)
from methods.ui import apply_base_theme
from methods.navigation import render_navigation

# ==================================
# PAGE CONFIG
# ==================================

st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_base_theme()
require_login()

render_navigation()

is_admin = is_admin_role(
    st.session_state.get("role_name")
)

st.title("Alternatives")

# ==================================
# SESSION
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

    st.error(e)
    st.stop()

if len(session_data) == 0:

    st.warning(
        "Belum ada session."
    )

    st.stop()

selected_session = st.selectbox(
    "Pilih Session",
    session_data,
    format_func=lambda x:
    f"{x['session_code']} - {x['session_name']}"
)

session_id = selected_session["id"]
session_status = selected_session["status"]

is_editable = (
    is_admin
    and session_status == "draft"
)

if (
    not is_admin
    and session_status == "draft"
):

    st.warning(
        "Alternatives belum dapat dilihat "
        "karena session masih DRAFT."
    )

    st.stop()

# ==================================
# LOAD ALTERNATIVES
# ==================================

try:

    alternatives_data = (

        supabase
        .table("alternatives")
        .select("*")
        .eq(
            "session_id",
            session_id
        )
        .order(
            "alternative_code"
        )
        .execute()

    ).data

except Exception as e:

    st.error(e)
    st.stop()

# ==================================
# TABS
# ==================================

if is_admin:

    tab1, tab2, tab3, tab4 = st.tabs([
        "Daftar Alternative",
        "Tambah",
        "Edit",
        "Hapus"
    ])

else:

    tab1 = st.container()

# ==================================
# TAB DAFTAR
# ==================================

with tab1:

    st.subheader(
        "Daftar Alternative"
    )

    if len(alternatives_data) == 0:

        st.info(
            "Belum ada data alternative"
        )

    else:

        rows = []

        for item in alternatives_data:

            rows.append({

                "Kode":
                item["alternative_code"],

                "Nama":
                item["alternative_name"],

                "Deskripsi":
                item["description"]

            })

        st.dataframe(
            pd.DataFrame(rows),
            use_container_width=True
        )

# ==================================
# ADMIN ONLY
# ==================================

if is_admin:

    # ==================================
    # TAB TAMBAH
    # ==================================

    with tab2:

        st.subheader(
            "Tambah Alternative"
        )

        if not is_editable:
            st.info(
                "Alternative hanya dapat ditambah saat session DRAFT."
            )

        else:

            with st.form(
                "add_alternative"
            ):

                alternative_code = st.text_input(
                    "Kode Alternative",
                    placeholder="Kode"
                )

                alternative_name = st.text_input(
                    "Nama Alternative",
                    placeholder="Nama"
                )

                description = st.text_area(
                    "Deskripsi",
                    placeholder="Kandidat promosi jabatan"
                )

                submit = st.form_submit_button(
                    "Simpan"
                )

            if submit:

                if (
                    alternative_code == ""
                    or
                    alternative_name == ""
                ):

                    st.warning(
                        "Kode dan Nama wajib diisi"
                    )

                else:

                    try:

                        supabase.table(
                            "alternatives"
                        ).insert({

                            "alternative_code":
                            alternative_code,

                            "alternative_name":
                            alternative_name,

                            "description":
                            description,

                            "session_id":
                            session_id

                        }).execute()

                        st.success(
                            "Alternative berhasil ditambahkan"
                        )

                        st.rerun()

                    except Exception as e:

                        st.error(e)

    # ==================================
    # TAB EDIT
    # ==================================

    with tab3:

        st.subheader(
            "Edit Alternative"
        )

        if not is_editable:
            st.info(
                "Alternative hanya dapat diedit saat session DRAFT."
            )

        else:

            if len(alternatives_data) == 0:

                st.info(
                    "Belum ada data"
                )

            else:

                selected = st.selectbox(

                    "Pilih Alternative",

                    alternatives_data,

                    format_func=lambda x:
                    f"{x['alternative_code']} - "
                    f"{x['alternative_name']}"

                )

                with st.form(
                    "edit_alternative"
                ):

                    edit_code = st.text_input(
                        "Kode Alternative",
                        value=selected[
                            "alternative_code"
                        ]
                    )

                    edit_name = st.text_input(
                        "Nama Alternative",
                        value=selected[
                            "alternative_name"
                        ]
                    )

                    edit_description = st.text_area(
                        "Deskripsi",
                        value=selected[
                            "description"
                        ]
                        if selected[
                            "description"
                        ]
                        else ""
                    )

                    update_btn = (
                        st.form_submit_button(
                            "Update"
                        )
                    )

                if update_btn:

                    try:

                        supabase.table(
                            "alternatives"
                        ).update({

                            "alternative_code":
                            edit_code,

                            "alternative_name":
                            edit_name,

                            "description":
                            edit_description

                        }).eq(
                            "id",
                            selected["id"]
                        ).execute()

                        st.success(
                            "Alternative berhasil diupdate"
                        )

                        st.rerun()

                    except Exception as e:

                        st.error(e)

    # ==================================
    # TAB HAPUS
    # ==================================

    with tab4:

        st.subheader(
            "Hapus Alternative"
        )

        if not is_editable:
            st.info(
                "Alternative hanya dapat dihapus saat session DRAFT."
            )

        else:

            if len(alternatives_data) == 0:

                st.info(
                    "Belum ada data"
                )

            else:

                selected_delete = st.selectbox(

                    "Pilih Alternative",

                    alternatives_data,

                    format_func=lambda x:
                    f"{x['alternative_code']} - "
                    f"{x['alternative_name']}",

                    key="delete_alternative"

                )

                st.warning(
                    "Data yang dihapus tidak dapat dikembalikan."
                )

                if st.button(
                    "Hapus Alternative"
                ):

                    try:

                        supabase.table(
                            "alternatives"
                        ).delete().eq(
                            "id",
                            selected_delete["id"]
                        ).execute()

                        st.success(
                            "Alternative berhasil dihapus"
                        )

                        st.rerun()

                    except Exception as e:

                        st.error(e)