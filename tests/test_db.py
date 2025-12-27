from database.connection import get_connection

conn = get_connection()

if conn:
    print("✅ Connexion réussie à la base de données")
    conn.close()
else:
    print("❌ Connexion échouée")
