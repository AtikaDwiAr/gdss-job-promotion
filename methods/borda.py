from collections import defaultdict

from database.supabase_client import supabase


def calculate_borda(session_id):

    # =====================================
    # HAPUS HASIL BORDA SESSION INI
    # =====================================

    (
        supabase
        .table("borda_results")
        .delete()
        .eq("session_id", session_id)
        .execute()
    )

    # =====================================
    # LOAD PROFILE MATCHING SUMMARY
    # =====================================

    summary = (

        supabase
        .table("profile_matching_summary")
        .select("*")
        .eq(
            "session_id",
            session_id
        )
        .execute()

    ).data

    if len(summary) == 0:

        return False

    # =====================================
    # LOAD ALTERNATIVES
    # =====================================

    alternatives = (

        supabase
        .table("alternatives")
        .select("*")
        .eq(
            "session_id",
            session_id
        )
        .execute()

    ).data

    total_alternative = len(
        alternatives
    )

    if total_alternative == 0:

        return False

    # =====================================
    # HITUNG BORDA
    # =====================================

    borda_scores = defaultdict(float)

    voter_set = set()

    for row in summary:

        user_id = row["user_id"]

        alternative_id = row[
            "alternative_id"
        ]

        ranking = row["ranking"]

        voter_set.add(user_id)

        point = (

            total_alternative

            -

            ranking

            +

            1

        )

        borda_scores[
            alternative_id
        ] += point

    # =====================================
    # SORTING
    # =====================================

    sorted_result = sorted(

        borda_scores.items(),

        key=lambda x: x[1],

        reverse=True

    )

    # =====================================
    # SAVE RESULT
    # =====================================

    rank = 1

    for alternative_id, score in sorted_result:

        (
            supabase
            .table("borda_results")
            .insert(
                {
                    "session_id":
                        session_id,

                    "alternative_id":
                        alternative_id,

                    "borda_score":
                        score,

                    "voter_count":
                        len(voter_set),

                    "final_ranking":
                        rank
                }
            )
            .execute()
        )

        rank += 1

    return True