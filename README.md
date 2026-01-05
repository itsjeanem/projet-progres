# 📊 Système de Gestion Commerciale – Application Desktop PyQt6

## 🎯 Description

Une **application desktop modulaire** dédiée à la gestion commerciale. Développée en **Python avec PyQt6**, elle offre une interface pour la gestion d'une petite ou moyenne entreprise, avec support des rôles utilisateur, génération de rapports PDF/Excel.

**Technologie** : PyQt6 + MySQL + Python 3  
**Architecture** : MVC (Model-View-Controller) avec séparation claire des responsabilités  
**Base de données** : MySQL 8.0+ avec modèle relationnel normalisé

---

## 🏗️ Architecture du Projet

```
.
├── config.py                    # Configuration (DB, env)
├── main.py                      # Point d'entrée principal
├── requirements.txt             # Dépendances Python
├── .env                         # Variables d'environnement (DB credentials)
│
├── models/                      # Couche métier (logique applicative)
│   ├── user.py                  # Gestion utilisateurs & authentification
│   ├── client.py                # CRUD clients + recherche
│   ├── product.py               # Catalogue produits + stock
│   ├── category.py              # Catégories produits
│   ├── sale.py                  # Gestion ventes & factures
│   ├── statistics.py            # Agrégations & KPI
│   └── settings.py              # Configuration app
│
├── controllers/                 # Couche présentation (liaison Vue-Modèle)
│   ├── user_controller.py       # Login, changement rôle
│   ├── client_controller.py     # CRUD interface clients
│   ├── product_controller.py    # CRUD interface produits
│   ├── sale_controller.py       # CRUD interface ventes
│   ├── statistics_controller.py # Agrégation données pour dashboard
│   └── settings_controller.py   # Gestion préférences
│
├── views/                       # Couche présentation (UI PyQt6)
│   ├── main_window.py           # Fenêtre principale + navigation
│   ├── login_view.py            # Interface d'authentification
│   ├── splash_screen.py         # Écran de démarrage
│   ├── dashboard_view.py        # Tableau de bord (KPI, graphiques)
│   ├── clients_view.py          # Gestion des clients
│   ├── products_view.py         # Catalogue produits
│   ├── sales_view.py            # Gestion ventes & factures
│   ├── settings_view.py         # Paramètres utilisateur
│   └── ui/                      # Fichiers Designer (.ui) Qt
│       ├── login.ui
│       ├── main_window.ui
│       ├── clients.ui
│       ├── products.ui
│       └── sales.ui
│
├── database/                    # Couche données
│   ├── connection.py            # Pool de connexion MySQL
│   ├── schema.sql               # DDL (création tables + indexes)
│   └── seed_data.sql            # Données initiales (admin, démo)
│
├── utils/                       # Utilitaires & helpers
│   ├── session.py               # Gestion session utilisateur
│   ├── permissions.py           # Système de rôles (admin/manager/vendeur)
│   ├── validators.py            # Validation données (email, phone…)
│   ├── helpers.py               # Fonctions communes
│   ├── excel_exporter.py        # Export Excel (openpyxl)
│   └── pdf_generator.py         # Génération PDF factures (reportlab)
│
├── resources/                   # Assets
│   ├── styles/
│   │   └── main.qss             # Stylesheet QSS (thème application)
│   ├── icons/                   # Icônes UI
│   └── images/                  # Images branding
│
└── tests/                       # Tests & utilitaires
    ├── test_models.py           # Unit tests modèles
    ├── test_controllers.py      # Tests contrôleurs
    ├── test_db.py               # Tests base de données
    ├── test_login.py            # Tests authentification
    └── create_admin.py          # Script création utilisateur admin
```

---

## 🔐 Sécurité & Permissions

### Système de rôles

| Rôle        | Clients    | Produits | Ventes     | Rapport   | Stats | Admin      |
| ----------- | ---------- | -------- | ---------- | --------- | ----- | ---------- |
| **vendeur** | Lire/Créer | Lire     | Créer/Lire | PDF/Excel | Oui   | ❌         |
| **manager** | CRUD       | CRUD     | CRUD       | PDF/Excel | Oui   | ❌         |
| **admin**   | CRUD       | CRUD     | CRUD       | PDF/Excel | Oui   | Paramètres |

---

## 📦 Dépendances

```
PyQt6==6.6.1                      # GUI desktop
mysql-connector-python==8.2.0     # Driver MySQL
python-dotenv==1.0.0              # Env variables
bcrypt==4.1.1                     # Hachage sécurisé
openpyxl==3.11.0                  # Export Excel
matplotlib==3.10.8                # Graphiques
Pillow==12.0.0                    # Images
reportlab==4.0.9                  # Génération PDF
```

---

## 🚀 Installation & Démarrage

### Prérequis

- **Python 3.9+**
- **MySQL 8.0+** (serveur local ou distant)
- **pip** et **venv** (optionnel mais recommandé)

### 1️⃣ Cloner et installer

```bash
git clone <repository>
cd projet-progres
python -m venv venv

# Activer l'environnement
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

pip install -r requirements.txt
```

### 2️⃣ Configurer la base de données

Créer un fichier `.env` à la racine :

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=gestion_commerciale
```

Initialiser la BD :

```bash
mysql -u root -p < database/schema.sql
```

> Cela crée la base de données et les differentes tables.

### 3️⃣ Lancer l'application

```bash
python main.py
```

L'application affiche un splash screen, puis la fenêtre de login.

---

## 🧪 Tests

Exécuter la suite de tests :

```bash
# Tests BD
python -m pytest tests/test_db.py -v

# Tests login
python -m pytest tests/test_login.py -v
```

Créer un utilisateur admin supplémentaire :

```bash
python tests/create_admin.py
```

---

## 🛠️ Développement

### Ajouter une nouvelle vue

1. Créer `views/ma_vue.py` (héritation `QWidget`)
2. Créer `controllers/ma_controller.py` (logique présentation)
3. Enregistrer dans `MainWindow.build_ui()`
4. Ajouter route navigation

### Exemple contrôleur simple

```python
from models.client import Client
from utils.validators import validate_email

class ClientController:
    @staticmethod
    def add_client(nom, prenom, email):
        if not validate_email(email):
            return False, "Email invalide"
        return Client.create(nom, prenom, email=email)
```
