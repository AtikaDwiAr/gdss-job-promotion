import streamlit as st

from database.supabase_client import supabase
from methods.auth import require_admin
from methods.session_status import get_dm_evaluation_status
from methods.navigation import render_navigation

require_admin()

render_navigation()

st.title("Session Management")

tab1, tab2 = st.tabs(
    [
        "Daftar Session",
        "Input Session"
    ]
)

# =====================================
# FORM TAMBAH SESSION
# =====================================

with tab2:

    st.subheader("Tambah Session")

    with st.form("add_session_form"):

        session_code = st.text_input(
            "Session Code",
            placeholder="GS001"
        )

        session_name = st.text_input(
            "Session Name",
            placeholder="Promosi Jabatan 2026"
        )

        description = st.text_area(
            "Description"
        )

        submit = st.form_submit_button(
            "Simpan Session"
        )

    if submit:

        if not session_code or not session_name:

            st.error(
                "Session Code dan Session Name wajib diisi"
            )

        else:

            try:

                (
                    supabase
                    .table("gdss_sessions")
                    .insert(
                        {
                            "session_code": session_code,
                            "session_name": session_name,
                            "description": description,
                            "status": "draft"
                        }
                    )
                    .execute()
                )

                st.success(
                    "Session berhasil ditambahkan"
                )

                st.rerun()

            except Exception as e:

                st.error(str(e))

# =====================================
# DAFTAR SESSION
# =====================================

with tab1:

    st.subheader("Daftar Session")

    try:

        sessions = (
            supabase
            .table("gdss_sessions")
            .select("*")
            .order("id")
            .execute()
        )

        session_data = sessions.data

    except Exception as e:

        st.error(str(e))
        st.stop()

    if len(session_data) == 0:

        st.info("Belum ada session.")

    else:

        for session in session_data:

            with st.expander(
                f"{session['session_code']} - {session['session_name']}"
            ):

                st.write(
                    f"**Status:** {session['status']}"
                )

                st.write(
                    f"**Description:** {session['description']}"
                )

                # =====================================
                # STATUS PENILAIAN DM
                # =====================================

                st.subheader("Status Penilaian DM")

                try:

                    statuses = get_dm_evaluation_status(
                        session["id"]
                    )

                    if len(statuses) == 0:

                        st.info(
                            "Belum ada decision maker atau penilaian."
                        )

                    else:

                        for item in statuses:

                            status_text = (
                                "Selesai"
                                if item["completed"]
                                else "Belum Selesai"
                            )

                            st.write(
                                f"{item['user_name']} : "
                                f"{item['total_input']}/"
                                f"{item['total_required']} "
                                f"({status_text})"
                            )

                except Exception as e:

                    st.error(
                        f"Gagal mengambil status penilaian: {str(e)}"
                    )

                col1, col2 = st.columns(2)

                # =====================================
                # FINALISASI HASIL
                # =====================================

                st.divider()

                if session["status"] == "completed":

                    if st.button(
                        "Finalisasi Hasil",
                        key=f"finalize_{session['id']}"
                    ):

                        try:

                            (
                                supabase
                                .table("gdss_sessions")
                                .update(
                                    {
                                        "status": "finalized"
                                    }
                                )
                                .eq(
                                    "id",
                                    session["id"]
                                )
                                .execute()
                            )

                            st.success(
                                "Session berhasil difinalisasi"
                            )

                            st.rerun()

                        except Exception as e:

                            st.error(str(e))

                elif session["status"] == "finalized":

                    st.success(
                        "Session sudah Finalized"
                    )

                # =====================================
                # UPDATE STATUS
                # =====================================

                with col1:

                    if session["status"] == "finalized":

                        st.success(
                            "Status sudah Finalized dan tidak dapat diubah lagi."
                        )

                    else:

                        status_options = [
                            "draft",
                            "active",
                            "completed"
                        ]

                        current_status = session["status"]

                        if current_status not in status_options:

                            current_status = "draft"

                        new_status = st.selectbox(
                            "Status",
                            options=status_options,
                            index=status_options.index(
                                current_status
                            ),
                            key=f"status_{session['id']}"
                        )

                        if st.button(
                            "Update Status",
                            key=f"update_{session['id']}"
                        ):

                            try:

                                (
                                    supabase
                                    .table("gdss_sessions")
                                    .update(
                                        {
                                            "status": new_status
                                        }
                                    )
                                    .eq(
                                        "id",
                                        session["id"]
                                    )
                                    .execute()
                                )

                                st.success(
                                    "Status berhasil diperbarui"
                                )

                                st.rerun()

                            except Exception as e:

                                st.error(str(e))

                # =====================================
                # HAPUS SESSION
                # =====================================

                with col2:

                    if st.button(
                        "Hapus Session",
                        key=f"delete_{session['id']}"
                    ):

                        try:

                            session_id = session["id"]

                            related_tables = [
                                "criteria",
                                "subcriteria",
                                "alternatives",
                                "evaluations",
                                "profile_matching_detail",
                                "profile_matching_results",
                                "profile_matching_summary",
                                "borda_results"
                            ]

                            has_relation = False

                            for table_name in related_tables:

                                result = (
                                    supabase
                                    .table(table_name)
                                    .select("id")
                                    .eq(
                                        "session_id",
                                        session_id
                                    )
                                    .limit(1)
                                    .execute()
                                )

                                if len(result.data) > 0:

                                    has_relation = True
                                    break

                            if has_relation:

                                st.error(
                                    "Session tidak dapat dihapus karena masih memiliki data terkait."
                                )

                            else:

                                (
                                    supabase
                                    .table("gdss_sessions")
                                    .delete()
                                    .eq(
                                        "id",
                                        session_id
                                    )
                                    .execute()
                                )

                                st.success(
                                    "Session berhasil dihapus."
                                )

                                st.rerun()

                        except Exception as e:

                            st.error(str(e))