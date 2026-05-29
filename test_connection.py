from database.supabase_client import supabase

try:
    response = supabase.table("test").select("*").execute()

    print("Koneksi Supabase berhasil!")
    print(response.data)

except Exception as e:
    print("Terjadi error:")
    print(e)