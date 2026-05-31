from collections import defaultdict

from database.supabase_client import supabase


def calculate_borda():

    # ==========================
    # HAPUS HASIL LAMA
    # ==========================

    supabase.table(
        "borda_results"
    ).delete().neq(
        "id",
        0
    ).execute()

    # ==========================
    # LOAD DATA
    # ==========================

    summary = (

        supabase
        .table("profile_matching_summary")
        .select("*")
        .execute()

    ).data

    if len(summary) == 0:

        return False

    # ==========================
    # JUMLAH ALTERNATIF
    # ==========================

    alternatives = (

        supabase
        .table("alternatives")
        .select("*")
        .execute()

    ).data

    total_alternative = len(alternatives)

    # ==========================
    # BORDA POINT
    # ==========================

    borda_scores = defaultdict(float)

    voter_set = set()

    for row in summary:

        user_id = row["user_id"]

        voter_set.add(user_id)

        ranking = row["ranking"]

        alternative_id = row["alternative_id"]

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

    # ==========================
    # SORTING
    # ==========================

    sorted_result = sorted(

        borda_scores.items(),

        key=lambda x: x[1],

        reverse=True

    )

    # ==========================
    # SAVE
    # ==========================

    rank = 1

    for alternative_id, score in sorted_result:

        supabase.table(
            "borda_results"
        ).insert({

            "alternative_id":
                alternative_id,

            "borda_score":
                score,

            "voter_count":
                len(voter_set),

            "final_ranking":
                rank

        }).execute()

        rank += 1

    return True