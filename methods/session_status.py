from database.supabase_client import supabase


from database.supabase_client import supabase


def get_dm_users():

    users = (
        supabase
        .table("users")
        .select("""
            id,
            name,
            email,
            roles(role_name)
        """)
        .execute()
    ).data

    dm_users = []

    for user in users:

        role = user.get("roles")

        role_name = None

        if isinstance(role, dict):

            role_name = role.get(
                "role_name"
            )

        elif isinstance(role, list):

            if len(role) > 0:

                role_name = role[0].get(
                    "role_name"
                )

        if role_name:

            normalized = (
                role_name
                .lower()
                .strip()
            )

            if normalized in [
                "decision maker",
                "dm",
                "decisionmaker",
                "decision_maker"
            ]:

                dm_users.append(
                    {
                        "id": user["id"],
                        "name": user["name"],
                        "email": user["email"]
                    }
                )

    return dm_users


def get_dm_evaluation_status(session_id):

    dm_users = get_dm_users()

    alternatives = (
        supabase
        .table("alternatives")
        .select("id")
        .eq("session_id", session_id)
        .execute()
    ).data

    subcriteria = (
        supabase
        .table("subcriteria")
        .select("id")
        .eq("session_id", session_id)
        .execute()
    ).data

    total_required = (
        len(alternatives)
        *
        len(subcriteria)
    )

    results = []

    for dm in dm_users:

        evaluations = (
            supabase
            .table("evaluations")
            .select("id")
            .eq("session_id", session_id)
            .eq("user_id", dm["id"])
            .execute()
        ).data

        total_input = len(evaluations)

        is_completed = (
            total_input >= total_required
            and total_required > 0
        )

        results.append({
            "user_id": dm["id"],
            "user_name": dm["name"],
            "total_input": total_input,
            "total_required": total_required,
            "completed": is_completed
        })

    return results