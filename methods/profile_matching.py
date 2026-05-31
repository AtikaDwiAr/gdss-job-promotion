from database.supabase_client import supabase


# =====================================
# KONVERSI GAP -> BOBOT GAP
# =====================================

def gap_weight(gap):

    mapping = {
        0: 5,
        1: 4.5,
        -1: 4,
        2: 3.5,
        -2: 3,
        3: 2.5,
        -3: 2,
        4: 1.5,
        -4: 1
    }

    return mapping.get(gap, 1)


# =====================================
# PROFILE MATCHING
# =====================================

def calculate_profile_matching(user_id):

    # =====================================
    # HAPUS HASIL LAMA
    # =====================================

    supabase.table(
        "profile_matching_detail"
    ).delete().eq(
        "user_id",
        user_id
    ).execute()

    supabase.table(
        "profile_matching_results"
    ).delete().eq(
        "user_id",
        user_id
    ).execute()

    supabase.table(
        "profile_matching_summary"
    ).delete().eq(
        "user_id",
        user_id
    ).execute()

    # =====================================
    # LOAD DATA
    # =====================================

    evaluations = (
        supabase
        .table("evaluations")
        .select("*")
        .eq("user_id", user_id)
        .execute()
    ).data

    criteria = (
        supabase
        .table("criteria")
        .select("*")
        .execute()
    ).data

    subcriteria = (
        supabase
        .table("subcriteria")
        .select("*")
        .execute()
    ).data

    alternatives = (
        supabase
        .table("alternatives")
        .select("*")
        .execute()
    ).data

    # =====================================
    # HITUNG GAP DAN SIMPAN DETAIL
    # =====================================

    for ev in evaluations:

        sub = next(
            (
                s for s in subcriteria
                if s["id"] == ev["subcriteria_id"]
            ),
            None
        )

        if not sub:
            continue

        gap = float(ev["score"]) - float(sub["target_value"])

        weight = gap_weight(gap)

        supabase.table(
            "profile_matching_detail"
        ).insert({

            "user_id":
                user_id,

            "alternative_id":
                ev["alternative_id"],

            "subcriteria_id":
                ev["subcriteria_id"],

            "gap_value":
                gap,

            "weight_value":
                weight

        }).execute()

    # =====================================
    # HITUNG NILAI PER KRITERIA
    # =====================================

    for alt in alternatives:

        for crt in criteria:

            related_subcriteria = [

                s for s in subcriteria

                if s["criteria_id"] == crt["id"]

            ]

            if len(related_subcriteria) == 0:
                continue

            core_values = []
            secondary_values = []

            for sub in related_subcriteria:

                detail = (

                    supabase
                    .table("profile_matching_detail")
                    .select("*")
                    .eq("user_id", user_id)
                    .eq("alternative_id", alt["id"])
                    .eq("subcriteria_id", sub["id"])
                    .execute()

                ).data

                if len(detail) == 0:
                    continue

                weight = float(
                    detail[0]["weight_value"]
                )

                if sub["factor_type"] == "core":

                    core_values.append(weight)

                else:

                    secondary_values.append(weight)

            # ==============================
            # NCF
            # ==============================

            if len(core_values) > 0:

                ncf = (
                    sum(core_values)
                    /
                    len(core_values)
                )

            else:

                ncf = 0

            # ==============================
            # NSF
            # ==============================

            if len(secondary_values) > 0:

                nsf = (
                    sum(secondary_values)
                    /
                    len(secondary_values)
                )

            else:

                nsf = 0

            # ==============================
            # NILAI KRITERIA
            # 60% NCF + 40% NSF
            # ==============================

            criteria_score = (

                (0.6 * ncf)

                +

                (0.4 * nsf)

            )

            supabase.table(
                "profile_matching_results"
            ).insert({

                "user_id":
                    user_id,

                "alternative_id":
                    alt["id"],

                "criteria_id":
                    crt["id"],

                "criteria_score":
                    criteria_score

            }).execute()

    # =====================================
    # HITUNG TOTAL SCORE
    # =====================================

    summary_data = []

    for alt in alternatives:

        pm_results = (

            supabase
            .table("profile_matching_results")
            .select("*")
            .eq("user_id", user_id)
            .eq("alternative_id", alt["id"])
            .execute()

        ).data

        total_score = 0

        for result in pm_results:

            crt = next(
                (
                    c for c in criteria
                    if c["id"] == result["criteria_id"]
                ),
                None
            )

            if not crt:
                continue

            total_score += (

                float(result["criteria_score"])

                *

                float(crt["weight"])

            )

        summary_data.append({

            "alternative_id":
                alt["id"],

            "total_score":
                total_score

        })

    # =====================================
    # RANKING
    # =====================================

    summary_data = sorted(

        summary_data,

        key=lambda x: x["total_score"],

        reverse=True

    )

    ranking = 1

    for row in summary_data:

        supabase.table(
            "profile_matching_summary"
        ).insert({

            "user_id":
                user_id,

            "alternative_id":
                row["alternative_id"],

            "total_score":
                row["total_score"],

            "ranking":
                ranking

        }).execute()

        ranking += 1

    return True