import streamlit as st
import pandas as pd

from database.supabase_client import supabase
from methods.borda import calculate_borda
from methods.auth import require_login

require_login()

st.title("Borda Result")

# ==========================
# BUTTON
# ==========================

if st.button("Hitung Borda"):

    try:

        calculate_borda()

        st.success(
            "Perhitungan Borda berhasil"
        )

    except Exception as e:

        st.error(e)

# ==========================
# HASIL
# ==========================

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

                    r["borda_score"],

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