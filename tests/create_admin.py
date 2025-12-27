from models.user import User

ok = User.create(
    username="admin",
    password="admin123",
    email="admin@test.com",
    role="admin"
)

if ok:
    print("✅ Administrateur créé")
else:
    print("❌ Échec création admin")
