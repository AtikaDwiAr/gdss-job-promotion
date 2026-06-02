import streamlit as st

from database.supabase_client import supabase


def init_auth_state():
    if "is_authenticated" not in st.session_state:
        st.session_state["is_authenticated"] = False
        st.session_state["user_id"] = None
        st.session_state["user_name"] = None
        st.session_state["user_email"] = None
        st.session_state["role_id"] = None
        st.session_state["role_name"] = None


def authenticate_user(email, password):
    if email == "" or password == "":
        return None, "Email dan password wajib diisi"

    try:
        response = (
            supabase
            .table("users")
            .select("id, name, email, role_id, password, roles(role_name)")
            .eq("email", email)
            .limit(1)
            .execute()
        )
    except Exception as e:
        return None, f"Gagal memeriksa user: {e}"

    data = response.data

    if len(data) == 0:
        return None, "Email tidak ditemukan"

    user = data[0]

    if user.get("password") != password:
        return None, "Password salah"

    role_name = None
    role = user.get("roles")

    if isinstance(role, dict):
        role_name = role.get("role_name")
    elif isinstance(role, list) and len(role) > 0:
        role_name = role[0].get("role_name")

    if role_name is None and user.get("role_id") is not None:
        try:
            role_response = (
                supabase
                .table("roles")
                .select("role_name")
                .eq("id", user["role_id"])
                .limit(1)
                .execute()
            )
        except Exception as e:
            return None, f"Gagal mengambil role: {e}"

        role_data = role_response.data

        if len(role_data) > 0:
            role_name = role_data[0].get("role_name")

    user["role_name"] = role_name

    return user, None


def set_user_session(user):
    st.session_state["is_authenticated"] = True
    st.session_state["user_id"] = user["id"]
    st.session_state["user_name"] = user["name"]
    st.session_state["user_email"] = user["email"]
    st.session_state["role_id"] = user.get("role_id")
    st.session_state["role_name"] = user.get("role_name")


def is_admin_role(role_name):
    if role_name is None:
        return False

    normalized = str(role_name).strip().lower()
    return normalized in {"admin", "admin1", "admin 1"}


def is_dm_role(role_name):
    if role_name is None:
        return False
    
    normalized = str(role_name).strip().lower()
    return normalized in {"decision maker", "dm", "decision_maker", "decisionmaker"}


def require_login():

    init_auth_state()

    if not st.session_state["is_authenticated"]:

        st.warning(
            "Sesi login tidak ditemukan atau telah berakhir."
        )

        st.info(
            "Silakan login melalui halaman login."
        )

        if st.button(
            "Kembali ke Halaman Login",
            key="back_to_home"
        ):
            st.switch_page("app.py")

        st.stop()

def require_admin():
    require_login()
    
    if not is_admin_role(st.session_state.get("role_name")):
        # st.error("❌ Akses Ditolak: Hanya Admin yang dapat mengakses halaman ini.")
        st.stop()


def require_dm():
    require_login()
    
    if not is_dm_role(st.session_state.get("role_name")):
        # st.error("❌ Akses Ditolak: Hanya Decision Maker yang dapat mengakses halaman ini.")
        st.stop()

def logout():
    """
    Membersihkan seluruh session state
    """

    for key in list(st.session_state.keys()):
        del st.session_state[key]

    init_auth_state()