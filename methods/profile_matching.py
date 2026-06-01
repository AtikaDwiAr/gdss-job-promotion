from database.supabase_client import supabase


# =====================================
# GAP → BOBOT
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

def calculate_profile_matching(
    session_id,
    user_id
):

    # =====================================
    # HAPUS HASIL LAMA
    # =====================================

    (
        supabase
        .table("profile_matching_detail")
        .delete()
        .eq("session_id", session_id)
        .eq("user_id", user_id)
        .execute()
    )

    (
        supabase
        .table("profile_matching_results")
        .delete()
        .eq("session_id", session_id)
        .eq("user_id", user_id)
        .execute()
    )

    (
        supabase
        .table("profile_matching_summary")
        .delete()
        .eq("session_id", session_id)
        .eq("user_id", user_id)
        .execute()
    )

    # =====================================
    # LOAD DATA
    # =====================================

    evaluations = (
        supabase
        .table("evaluations")
        .select("*")
        .eq("session_id", session_id)
        .eq("user_id", user_id)
        .execute()
    ).data

    criteria = (
        supabase
        .table("criteria")
        .select("*")
        .eq("session_id", session_id)
        .order("criteria_code")
        .execute()
    ).data

    subcriteria = (
        supabase
        .table("subcriteria")
        .select("*")
        .eq("session_id", session_id)
        .execute()
    ).data

    alternatives = (
        supabase
        .table("alternatives")
        .select("*")
        .eq("session_id", session_id)
        .execute()
    ).data

    # =====================================
    # DETAIL GAP
    # =====================================

    for ev in evaluations:

        sub = next(
            (
                s for s in subcriteria
                if s["id"] == ev["subcriteria_id"]
            ),
            None
        )

        if sub is None:
            continue

        gap = ( float(ev["score"]) - float(sub["target_value"]))

        weight = gap_weight(gap)

        (
            supabase
            .table("profile_matching_detail")
            .insert(
                {
                    "session_id": session_id,
                    "user_id": user_id,
                    "alternative_id": ev["alternative_id"],
                    "subcriteria_id": ev["subcriteria_id"],
                    "gap_value": gap,
                    "weight_value": weight
                }
            )
            .execute()
        )

    # =====================================
    # NILAI PER KRITERIA
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
                    .table(
                        "profile_matching_detail"
                    )
                    .select("*")
                    .eq(
                        "session_id",
                        session_id
                    )
                    .eq(
                        "user_id",
                        user_id
                    )
                    .eq(
                        "alternative_id",
                        alt["id"]
                    )
                    .eq(
                        "subcriteria_id",
                        sub["id"]
                    )
                    .execute()

                ).data

                if len(detail) == 0:
                    continue

                weight = float( detail[0]["weight_value"])

                if (sub["factor_type"] == "core"):

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

                nsf = (sum(secondary_values) /len(secondary_values))

            else:

                nsf = 0

            # ==============================
            # KRITERIA SCORE
            # 60% CORE
            # 40% SECONDARY
            # ==============================

            criteria_score = (

                (0.6 * ncf)

                +

                (0.4 * nsf)

            )

            (
                supabase
                .table(
                    "profile_matching_results"
                )
                .insert(
                    {
                        "session_id": session_id,
                        "user_id": user_id,
                        "alternative_id": alt["id"],
                        "criteria_id": crt["id"],
                        "criteria_score": criteria_score
                    }
                )
                .execute()
            )

    # =====================================
    # TOTAL SCORE
    # =====================================

    summary_data = []

    for alt in alternatives:

        pm_results = (

            supabase
            .table(
                "profile_matching_results"
            )
            .select("*")
            .eq(
                "session_id",
                session_id
            )
            .eq(
                "user_id",
                user_id
            )
            .eq(
                "alternative_id",
                alt["id"]
            )
            .execute()

        ).data

        total_score = 0

        for result in pm_results:

            crt = next(

                (
                    c for c in criteria
                    if c["id"] ==  result["criteria_id"]
                ),

                None

            )

            if crt is None:
                continue

            total_score += (

                float(
                    result[
                        "criteria_score"
                    ]
                )

                *

                float(
                    crt["weight"]
                )

            )

        summary_data.append(

            {
                "alternative_id":
                    alt["id"],

                "total_score":
                    total_score
            }

        )

    # =====================================
    # SORTING RANK
    # =====================================

    summary_data = sorted(

        summary_data,

        key=lambda x:
        x["total_score"],

        reverse=True

    )

    ranking = 1

    for row in summary_data:

        (
            supabase
            .table(
                "profile_matching_summary"
            )
            .insert(
                {
                    "session_id": session_id,
                    "user_id": user_id,
                    "alternative_id":
                        row[
                            "alternative_id"
                        ],
                    "total_score":
                        row[
                            "total_score"
                        ],
                    "ranking":
                        ranking
                }
            )
            .execute()
        )

        ranking += 1

    return True