import streamlit as st
import pandas as pd

from database.supabase_client import supabase
from methods.auth import require_login, is_admin_role
from methods.ui import apply_base_theme
from methods.navigation import render_navigation

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
# LOAD SUBCRITERIA
# ==================================

try:

    response = (
        supabase
        .table("subcriteria")
        .select("""
            *,
            criteria(
                criteria_code,
                criteria_name
            )
        """)
        .eq(
            "session_id",
            session_id
        )
        .order(
            "subcriteria_code"
        )
        .execute()
    )

    subcriteria_data = response.data

except Exception as e:

    st.error(e)
    st.stop()

# ==================================
# TABS
# ==================================

if is_admin:

    tab1, tab2, tab3, tab4 = st.tabs([
        "Daftar Subcriteria",
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
        "Daftar Subcriteria"
    )

    if len(subcriteria_data) == 0:

        st.info(
            "Belum ada data subcriteria"
        )

    else:

        rows = []

        for item in subcriteria_data:

            rows.append({

                "Kode":
                item["subcriteria_code"],

                "Nama":
                item["subcriteria_name"],

                "Criteria":
                f"{item['criteria']['criteria_code']} - "
                f"{item['criteria']['criteria_name']}",

                "Target":
                item["target_value"],

                "Factor":
                item["factor_type"]

            })

        st.dataframe(
            pd.DataFrame(rows),
            use_container_width=True
        )

# ==================================
# ADMIN ONLY
# ==================================

if is_admin:

    criteria_options = {

        f"{c['criteria_code']} - {c['criteria_name']}":
        c["id"]

        for c in criteria_data

    }

    # ==================================
    # TAB TAMBAH
    # ==================================

    with tab2:

        st.subheader(
            "Tambah Subcriteria"
        )

        with st.form(
            "add_subcriteria"
        ):

            selected_criteria = st.selectbox(
                "Criteria",
                list(
                    criteria_options.keys()
                )
            )

            subcriteria_code = st.text_input(
                "Kode Subcriteria",
                placeholder="Kode"
            )

            subcriteria_name = st.text_input(
                "Nama Subcriteria",
                placeholder="Subcriteria"
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
                [
                    "core",
                    "secondary"
                ]
            )

            submit = st.form_submit_button(
                "Simpan"
            )

        if submit:

            try:

                supabase.table(
                    "subcriteria"
                ).insert({

                    "subcriteria_code":
                    subcriteria_code,

                    "criteria_id":
                    criteria_options[
                        selected_criteria
                    ],

                    "subcriteria_name":
                    subcriteria_name,

                    "target_value":
                    target_value,

                    "factor_type":
                    factor_type,

                    "session_id":
                    session_id

                }).execute()

                st.success(
                    "Subcriteria berhasil ditambahkan"
                )

                st.rerun()

            except Exception as e:

                st.error(e)

    # ==================================
    # TAB EDIT
    # ==================================

    with tab3:

        st.subheader(
            "Edit Subcriteria"
        )

        if len(subcriteria_data) == 0:

            st.info(
                "Belum ada data"
            )

        else:

            selected = st.selectbox(
                "Pilih Subcriteria",
                subcriteria_data,
                format_func=lambda x:
                f"{x['subcriteria_code']} - "
                f"{x['subcriteria_name']}"
            )

            current_criteria = None

            for key, value in criteria_options.items():

                if value == selected["criteria_id"]:

                    current_criteria = key

                    break

            with st.form(
                "edit_subcriteria"
            ):

                edit_criteria = st.selectbox(
                    "Criteria",
                    list(
                        criteria_options.keys()
                    ),
                    index=list(
                        criteria_options.keys()
                    ).index(
                        current_criteria
                    )
                )

                edit_code = st.text_input(
                    "Kode Subcriteria",
                    value=selected[
                        "subcriteria_code"
                    ]
                )

                edit_name = st.text_input(
                    "Nama Subcriteria",
                    value=selected[
                        "subcriteria_name"
                    ]
                )

                edit_target = st.number_input(
                    "Target Value",
                    min_value=1.0,
                    max_value=5.0,
                    value=float(
                        selected[
                            "target_value"
                        ]
                    ),
                    step=1.0
                )

                edit_factor = st.selectbox(
                    "Factor Type",
                    [
                        "core",
                        "secondary"
                    ],
                    index=0
                    if selected[
                        "factor_type"
                    ] == "core"
                    else 1
                )

                update_btn = (
                    st.form_submit_button(
                        "Update"
                    )
                )

            if update_btn:

                try:

                    supabase.table(
                        "subcriteria"
                    ).update({

                        "criteria_id":
                        criteria_options[
                            edit_criteria
                        ],

                        "subcriteria_code":
                        edit_code,

                        "subcriteria_name":
                        edit_name,

                        "target_value":
                        edit_target,

                        "factor_type":
                        edit_factor

                    }).eq(
                        "id",
                        selected["id"]
                    ).execute()

                    st.success(
                        "Subcriteria berhasil diupdate"
                    )

                    st.rerun()

                except Exception as e:

                    st.error(e)

    # ==================================
    # TAB HAPUS
    # ==================================

    with tab4:

        st.subheader(
            "Hapus Subcriteria"
        )

        if len(subcriteria_data) == 0:

            st.info(
                "Belum ada data"
            )

        else:

            selected_delete = st.selectbox(

                "Pilih Subcriteria",

                subcriteria_data,

                format_func=lambda x:
                f"{x['subcriteria_code']} - "
                f"{x['subcriteria_name']}",

                key="delete_subcriteria"

            )

            st.warning(
                "Data yang dihapus tidak dapat dikembalikan."
            )

            if st.button(
                "Hapus Subcriteria"
            ):

                try:

                    supabase.table(
                        "subcriteria"
                    ).delete().eq(
                        "id",
                        selected_delete["id"]
                    ).execute()

                    st.success(
                        "Subcriteria berhasil dihapus"
                    )

                    st.rerun()

                except Exception as e:

                    st.error(e)