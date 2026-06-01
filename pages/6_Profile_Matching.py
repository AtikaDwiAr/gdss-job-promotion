import streamlit as st
import pandas as pd

from database.supabase_client import supabase
from methods.profile_matching import calculate_profile_matching
from methods.auth import (
    require_login,
    is_admin_role,
    is_dm_role
)
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

is_dm = is_dm_role(
    st.session_state.get("role_name")
)

st.title("Profile Matching")

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

    st.warning("Belum ada session")
    st.stop()

selected_session = st.selectbox(
    "Session",
    sessions,
    format_func=lambda x:
        f"{x['session_code']} - {x['session_name']}"
)

session_id = selected_session["id"]

# =====================================
# USER
# =====================================

if is_admin:

    users = (
        supabase
        .table("users")
        .select("*")
        .execute()
    ).data

    user_options = {
        f"{u['name']} ({u['email']})":
        u["id"]
        for u in users
    }

    selected_user = st.selectbox(
        "Decision Maker",
        list(user_options.keys())
    )

    user_id = user_options[
        selected_user
    ]

elif is_dm:

    user_id = st.session_state[
        "user_id"
    ]

    st.info(
        f"Decision Maker : "
        f"{st.session_state['user_name']}"
    )

else:

    st.stop()

# =====================================
# HITUNG PM
# =====================================

if is_admin:

    if st.button(
        "Hitung Profile Matching"
    ):

        try:

            calculate_profile_matching(
                session_id,
                user_id
            )

            st.success(
                "Perhitungan berhasil"
            )

            st.rerun()

        except Exception as e:

            st.error(e)

# =====================================
# DETAIL
# =====================================

st.divider()

st.subheader(
    "Profile Matching Detail"
)

try:

    detail = (

        supabase
        .table(
            "profile_matching_detail"
        )
        .select("""
            *,
            alternatives(
                alternative_code,
                alternative_name
            ),
            subcriteria(
                subcriteria_code,
                subcriteria_name
            )
        """)
        .eq(
            "session_id",
            session_id
        )
        .eq(
            "user_id",
            user_id
        )
        .execute()

    ).data

    if len(detail) > 0:

        rows = []

        for d in detail:

            rows.append({

                "Alternative":

                    f"{d['alternatives']['alternative_code']} - "
                    f"{d['alternatives']['alternative_name']}",

                "Subcriteria":

                    f"{d['subcriteria']['subcriteria_code']} - "
                    f"{d['subcriteria']['subcriteria_name']}",

                "Gap":

                    d["gap_value"],

                "Weight":

                    d["weight_value"]

            })

        st.dataframe(
            pd.DataFrame(rows),
            use_container_width=True
        )

    else:

        st.info(
            "Belum ada hasil"
        )

except Exception as e:

    st.error(e)

# =====================================
# RESULT
# =====================================

st.divider()

st.subheader(
    "Nilai Per Criteria"
)

try:

    results = (

        supabase
        .table(
            "profile_matching_results"
        )
        .select("""
            *,
            alternatives(
                alternative_code,
                alternative_name
            ),
            criteria(
                criteria_code,
                criteria_name
            )
        """)
        .eq(
            "session_id",
            session_id
        )
        .eq(
            "user_id",
            user_id
        )
        .execute()

    ).data

    if len(results) > 0:

        rows = []

        for r in results:

            rows.append({

                "Alternative":

                    f"{r['alternatives']['alternative_code']} - "
                    f"{r['alternatives']['alternative_name']}",

                "Criteria":

                    f"{r['criteria']['criteria_code']} - "
                    f"{r['criteria']['criteria_name']}",

                "Score":

                    round(
                        float(
                            r["criteria_score"]
                        ),
                        4
                    )

            })

        st.dataframe(
            pd.DataFrame(rows),
            use_container_width=True
        )

except Exception as e:

    st.error(e)

# =====================================
# SUMMARY
# =====================================

st.divider()

st.subheader(
    "Ranking Profile Matching"
)

try:

    summary = (

        supabase
        .table(
            "profile_matching_summary"
        )
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
        .eq(
            "user_id",
            user_id
        )
        .order(
            "ranking"
        )
        .execute()

    ).data

    if len(summary) > 0:

        rows = []

        for s in summary:

            rows.append({

                "Ranking":
                    s["ranking"],

                "Alternative":

                    f"{s['alternatives']['alternative_code']} - "
                    f"{s['alternatives']['alternative_name']}",

                "Total Score":

                    round(
                        float(
                            s["total_score"]
                        ),
                        4
                    )

            })

        df = pd.DataFrame(rows)

        st.dataframe(
            df,
            use_container_width=True
        )

        st.success(
            f"Peringkat 1 : "
            f"{df.iloc[0]['Alternative']}"
        )

    else:

        st.info(
            "Belum ada hasil"
        )

except Exception as e:

    st.error(e)