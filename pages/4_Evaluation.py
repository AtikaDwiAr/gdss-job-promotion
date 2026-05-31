import streamlit as st
import pandas as pd
from database.supabase_client import supabase

st.title("📝 Evaluation")

# ==========================
# LOAD USERS
# ==========================

try:
    users = (
        supabase
        .table("users")
        .select("*")
        .execute()
    ).data

except Exception as e:
    st.error(f"Gagal mengambil user: {e}")
    st.stop()

# ==========================
# LOAD ALTERNATIVES
# ==========================

try:
    alternatives = (
        supabase
        .table("alternatives")
        .select("*")
        .order("alternative_code")
        .execute()
    ).data

except Exception as e:
    st.error(f"Gagal mengambil alternatives: {e}")
    st.stop()

# ==========================
# LOAD SUBCRITERIA
# ==========================

try:
    subcriteria = (
        supabase
        .table("subcriteria")
        .select("*")
        .order("subcriteria_code")
        .execute()
    ).data

except Exception as e:
    st.error(f"Gagal mengambil subcriteria: {e}")
    st.stop()

# ==========================
# VALIDASI DATA MASTER
# ==========================

if len(users) == 0:
    st.warning("Belum ada data user")
    st.stop()

if len(alternatives) == 0:
    st.warning("Belum ada data alternatives")
    st.stop()

if len(subcriteria) == 0:
    st.warning("Belum ada data subcriteria")
    st.stop()

# ==========================
# DROPDOWN USER
# ==========================

user_options = {
    user["name"]: user["id"]
    for user in users
}

selected_user = st.selectbox(
    "Decision Maker",
    list(user_options.keys())
)

user_id = user_options[selected_user]

# ==========================
# DROPDOWN ALTERNATIVE
# ==========================

alternative_options = {
    f"{alt['alternative_code']} - {alt['alternative_name']}": alt["id"]
    for alt in alternatives
}

selected_alternative = st.selectbox(
    "Alternative",
    list(alternative_options.keys())
)

alternative_id = alternative_options[selected_alternative]

# ==========================
# FORM PENILAIAN
# ==========================

st.subheader("Input Nilai")

scores = {}

with st.form("evaluation_form"):

    for sub in subcriteria:

        score = st.number_input(
            label=f"{sub['subcriteria_code']} - {sub['subcriteria_name']}",
            min_value=1.0,
            max_value=5.0,
            step=1.0,
            key=sub["id"]
        )

        scores[sub["id"]] = score

    submit = st.form_submit_button("Simpan Penilaian")

    if submit:

        try:

            # simpan semua nilai

            for sub_id, score in scores.items():

                supabase.table("evaluations").insert({
                    "user_id": user_id,
                    "alternative_id": alternative_id,
                    "subcriteria_id": sub_id,
                    "score": score
                }).execute()

            st.success("Penilaian berhasil disimpan")

        except Exception as e:

            st.error(f"Error : {e}")

# ==========================
# TAMPILKAN DATA EVALUASI
# ==========================

st.divider()

st.subheader("Data Evaluasi")

try:

    evaluations = (
        supabase
        .table("evaluations")
        .select("*")
        .execute()
    ).data

    if len(evaluations) > 0:

        df = pd.DataFrame(evaluations)

        st.dataframe(
            df,
            use_container_width=True
        )

    else:

        st.info("Belum ada data evaluasi")

except Exception as e:

    st.error(e)