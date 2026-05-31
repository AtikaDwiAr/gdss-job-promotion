import streamlit as st
import pandas as pd

from database.supabase_client import supabase
from methods.profile_matching import calculate_profile_matching
from methods.auth import require_login, is_admin_role
from methods.ui import apply_base_theme

st.set_page_config(layout="wide", initial_sidebar_state="expanded")

apply_base_theme()
require_login()

st.title("Profile Matching")

# =====================================
# LOAD USERS
# =====================================

try:

    users = (
        supabase
        .table("users")
        .select("*")
        .execute()
    ).data

except Exception as e:

    st.error(e)
    st.stop()

if len(users) == 0:

    st.warning("Belum ada data user")
    st.stop()

# =====================================
# PILIH DECISION MAKER
# =====================================

is_admin = is_admin_role(st.session_state.get("role_name"))

if is_admin:
    user_options = {

        f"{u['name']} ({u['email']})":
            u["id"]

        for u in users

    }

    selected_user = st.selectbox(
        "Decision Maker",
        list(user_options.keys())
    )

    user_id = user_options[selected_user]
else:
    user_id = st.session_state["user_id"]
    st.text(f"Decision Maker: {st.session_state['user_name']}")

# =====================================
# HITUNG PROFILE MATCHING
# =====================================

if st.button("Hitung Profile Matching"):

    try:

        calculate_profile_matching(user_id)

        st.success(
            "Perhitungan Profile Matching berhasil"
        )

    except Exception as e:

        st.error(e)

# =====================================
# DETAIL GAP
# =====================================

st.divider()

st.subheader("Profile Matching Detail")

try:

    detail = (

        supabase
        .table("profile_matching_detail")
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
        .eq("user_id", user_id)
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

        st.info("Belum ada hasil")

except Exception as e:

    st.error(e)

# =====================================
# HASIL PER KRITERIA
# =====================================

st.divider()

st.subheader("Nilai Per Kriteria")

try:

    results = (

        supabase
        .table("profile_matching_results")
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
        .eq("user_id", user_id)
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

                "Criteria Score":

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

    else:

        st.info("Belum ada hasil")

except Exception as e:

    st.error(e)

# =====================================
# SUMMARY
# =====================================

st.divider()

st.subheader("Ranking Profile Matching")

try:

    summary = (

        supabase
        .table("profile_matching_summary")
        .select("""
            *,
            alternatives(
                alternative_code,
                alternative_name
            )
        """)
        .eq("user_id", user_id)
        .order(
            "ranking",
            desc=False
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

        st.info("Belum ada hasil")

except Exception as e:

    st.error(e)
