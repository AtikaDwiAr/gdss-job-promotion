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

st.title("Criteria")

# ==================================
# LOAD SESSION
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
        "Belum ada session."
    )

    st.stop()

selected_session = st.selectbox(
    "Pilih Session",
    sessions,
    format_func=lambda x:
        f"{x['session_code']} - {x['session_name']}"
)

session_id = selected_session["id"]
session_status = selected_session["status"]

is_editable = (
    is_admin
    and session_status == "draft"
)

# ==================================
# AKSES DM
# ==================================

if (
    not is_admin
    and session_status == "draft"
):

    st.warning(
        "Criteria belum dapat dilihat "
        "karena session masih DRAFT."
    )

    st.stop()

# ==================================
# LOAD CRITERIA
# ==================================

try:

    criteria_data = (
        supabase
        .table("criteria")
        .select("*")
        .eq(
            "session_id",
            session_id
        )
        .order("criteria_code")
        .execute()
    ).data

except Exception as e:

    st.error(e)
    st.stop()

total_weight = sum(
    float(row["weight"])
    for row in criteria_data
)

st.info(
    f"Total Bobot Saat Ini : {total_weight:.2f}"
)

# ==================================
# TABS
# ==================================

if is_admin:

    tab1, tab2, tab3, tab4 = st.tabs([
        "Daftar Criteria",
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
        "Daftar Criteria"
    )

    if len(criteria_data) == 0:

        st.info(
            "Belum ada criteria"
        )

    else:

        df = pd.DataFrame(
            criteria_data
        )

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

# ==================================
# ADMIN ONLY
# ==================================

if is_admin:

    # =============================
    # TAB TAMBAH
    # =============================

    with tab2:

        st.subheader(
            "Tambah Criteria"
        )

        if not is_editable:

            st.info(
                "Criteria hanya dapat ditambah saat session DRAFT."
            )

        else:

            with st.form(
                "add_criteria_form"
            ):

                criteria_code = st.text_input(
                    "Kode Criteria",
                    placeholder="Kode"
                )

                criteria_name = st.text_input(
                    "Nama Criteria",
                    placeholder="Kriteria"
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
                        "Total bobot tidak boleh melebihi 1"
                    )

                else:

                    try:

                        supabase.table(
                            "criteria"
                        ).insert({

                            "criteria_code":
                            criteria_code,

                            "criteria_name":
                            criteria_name,

                            "weight":
                            weight,

                            "session_id":
                            session_id

                        }).execute()

                        st.success(
                            "Criteria berhasil ditambahkan"
                        )

                        st.rerun()

                    except Exception as e:

                        st.error(e)
    # =============================
    # TAB EDIT
    # =============================

    with tab3:

        st.subheader(
            "Edit Criteria"
        )

        if not is_editable:
            st.info(
                "Criteria hanya dapat diedit saat session DRAFT."
            )

        else:

            if len(criteria_data) == 0:

                st.info(
                    "Belum ada data"
                )

            else:

                selected = st.selectbox(
                    "Pilih Criteria",
                    criteria_data,
                    format_func=lambda x:
                        f"{x['criteria_code']} - {x['criteria_name']}"
                )

                with st.form(
                    "edit_criteria_form"
                ):

                    edit_code = st.text_input(
                        "Kode Criteria",
                        value=selected[
                            "criteria_code"
                        ]
                    )

                    edit_name = st.text_input(
                        "Nama Criteria",
                        value=selected[
                            "criteria_name"
                        ]
                    )

                    edit_weight = st.number_input(
                        "Bobot",
                        min_value=0.0,
                        max_value=1.0,
                        value=float(
                            selected[
                                "weight"
                            ]
                        ),
                        step=0.01
                    )

                    update_btn = (
                        st.form_submit_button(
                            "Update"
                        )
                    )

                if update_btn:

                    try:

                        other_weight = sum(
                            float(
                                row["weight"]
                            )
                            for row in criteria_data
                            if row["id"]
                            != selected["id"]
                        )

                        if (
                            other_weight
                            + edit_weight
                            > 1
                        ):

                            st.error(
                                "Total bobot tidak boleh melebihi 1"
                            )

                        else:

                            supabase.table(
                                "criteria"
                            ).update({

                                "criteria_code":
                                edit_code,

                                "criteria_name":
                                edit_name,

                                "weight":
                                edit_weight

                            }).eq(
                                "id",
                                selected["id"]
                            ).execute()

                            st.success(
                                "Criteria berhasil diupdate"
                            )

                            st.rerun()

                    except Exception as e:

                        st.error(e)

    # =============================
    # TAB HAPUS
    # =============================

    with tab4:

        st.subheader(
            "Hapus Criteria"
        )

        if not is_editable:
            st.info(
                "Criteria hanya dapat dihapus saat session DRAFT."
            )

        else:

            if len(criteria_data) == 0:

                st.info(
                    "Belum ada data"
                )

            else:

                selected_delete = st.selectbox(
                    "Pilih Criteria",
                    criteria_data,
                    format_func=lambda x:
                        f"{x['criteria_code']} - {x['criteria_name']}",
                    key="delete_criteria"
                )

                st.warning(
                    "Data yang dihapus tidak dapat dikembalikan."
                )

                if st.button(
                    "Hapus Criteria"
                ):

                    try:

                        supabase.table(
                            "criteria"
                        ).delete().eq(
                            "id",
                            selected_delete["id"]
                        ).execute()

                        st.success(
                            "Criteria berhasil dihapus"
                        )

                        st.rerun()

                    except Exception as e:

                        st.error(e)