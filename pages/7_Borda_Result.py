import streamlit as st
import pandas as pd

from database.supabase_client import supabase
from methods.borda import calculate_borda
from methods.auth import (
    require_login,
    is_admin_role
)
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

st.title("Borda Result")

# =====================================
# SESSION
# =====================================

try:

    sessions = (
        supabase
        .table("gdss_sessions")
        .select("*")
        .order("session_code")
        .execute()
    ).data

except Exception as e:

    st.error(e)
    st.stop()

if len(sessions) == 0:

    st.warning(
        "Belum ada session"
    )

    st.stop()

selected_session = st.selectbox(
    "Session",
    sessions,
    format_func=lambda x:
        f"{x['session_code']} - {x['session_name']}"
)

session_id = selected_session["id"]

# =====================================
# VALIDASI SESSION
# =====================================

if selected_session["status"] != "completed":

    st.warning(
        "Borda hanya dapat dihitung pada session COMPLETED."
    )

    st.stop()

# =====================================
# HITUNG BORDA
# =====================================

if is_admin:

    if st.button(
        "Hitung Borda"
    ):

        try:

            calculate_borda(
                session_id
            )

            # =====================================
            # FINALISASI SESSION
            # =====================================

            (
                supabase
                .table("gdss_sessions")
                .update({
                    "status": "finalized"
                })
                .eq("id", session_id)
                .execute()
            )

            st.success(
                "Perhitungan Borda berhasil"
            )

            st.rerun()

        except Exception as e:

            st.error(e)

else:

    st.info(
        "Hanya Admin yang dapat menjalankan perhitungan Borda"
    )

# =====================================
# HASIL
# =====================================

st.divider()

st.subheader(
    "Final Ranking GDSS"
)

try:

    results = (

        supabase
        .table("borda_results")
        .select("""
            *,
            alternatives(
                alternative_code,
                alternative_name
            )
        """)
        .eq(
            "session_id",
            session_id
        )
        .order(
            "final_ranking",
            desc=False
        )
        .execute()

    ).data

    if len(results) > 0:

        rows = []

        for r in results:

            rows.append({

                "Ranking":
                    r["final_ranking"],

                "Alternative":

                    f"{r['alternatives']['alternative_code']} - "
                    f"{r['alternatives']['alternative_name']}",

                "Borda Score":
                    round(
                        float(
                            r["borda_score"]
                        ),
                        4
                    ),

                "Jumlah DM":
                    r["voter_count"]

            })

        df = pd.DataFrame(rows)

        st.dataframe(
            df,
            use_container_width=True
        )

        st.success(
            f"Peringkat Akhir GDSS : "
            f"{df.iloc[0]['Alternative']}"
        )

    else:

        st.info(
            "Belum ada hasil Borda"
        )

except Exception as e:

    st.error(e)