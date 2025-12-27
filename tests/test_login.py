from controllers.user_controller import UserController

username = input("Username: ")
password = input("Password: ")

user, error = UserController.login(username, password)

if error:
    print("❌", error)
else:
    print("✅ Connexion réussie")
    print("Utilisateur :", user["username"])
    print("Rôle :", user["role"])
