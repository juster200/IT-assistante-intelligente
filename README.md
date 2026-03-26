
# 🤖 Assistant Intelligent pour le Support IT

Application web développée avec Flask dans le cadre d’un projet de licence. Elle offre une interface de chat, des diagnostics système et réseau, une base de connaissances évolutive et une gestion complète de tickets d’incident. L’application intègre différents rôles (utilisateur, technicien, administrateur) avec des tableaux de bord personnalisés.

---

## 📋 Table des matières

1. [Fonctionnalités](#-fonctionnalités)
2. [Technologies utilisées](#-technologies-utilisées)
3. [Installation](#-installation)
4. [Utilisation](#-utilisation)
5. [Structure du projet](#-structure-du-projet)
6. [API interne](#-api-interne)
7. [Captures d’écran](#-captures-décran)
8. [Auteurs](#-auteurs)
9. [Licence](#-licence)

---

## 🚀 Fonctionnalités

- **Authentification et gestion des utilisateurs**  
  Inscription, connexion, déconnexion. Trois rôles : **utilisateur**, **technicien**, **administrateur**.  
  L’inscription en tant que technicien nécessite un **code secret** (configurable) pour garantir la véracité du rôle.

- **Chatbot intelligent**  
  Interface de chat permettant de poser des questions en langage naturel.  
  - Compréhension par mots-clés et recherche floue dans la base de connaissances.  
  - Commandes spéciales : `diagnostic système`, `ping <hôte>`, etc.  
  - Suggestions de questions sous forme de boutons.  
  - Proposition de création de ticket si aucune solution n’est trouvée.

- **Diagnostics système et réseau**  
  - **Système** : pourcentage CPU, mémoire utilisée, espace disque, informations plateforme.  
  - **Réseau** : ping vers un hôte, test d’ouverture de port TCP.  
  - Page dédiée avec affichage dynamique des résultats.

- **Base de connaissances**  
  Consultation et gestion (ajout/modification/suppression) d’entrées classées par catégorie.  
  Recherche par mots-clés avec tolérance aux fautes.  
  Ajout rapide possible depuis le tableau de bord des techniciens.

- **Gestion de tickets d’incident**  
  Création, visualisation, mise à jour (statut, assignation, solution) et suppression.  
  Les techniciens peuvent prendre en charge les tickets et leur attribuer une résolution.

- **Tableaux de bord personnalisés**  
  - **Utilisateur** : vue de ses propres tickets, assistant virtuel.  
  - **Technicien** : statistiques globales (tickets ouverts, en cours, résolus), tickets récents, ajout rapide à la base de connaissances, chat.  
  - **Administrateur** : gestion des utilisateurs (CRUD), statistiques avancées avec graphiques, consultation des logs.

- **Journalisation**  
  Enregistrement des interactions (chat, diagnostics, actions) pour traçabilité et analyse.

---

## 🛠 Technologies utilisées

- **Backend** : Python 3.10+, Flask 2.3.3
- **Base de données** : SQLite avec SQLAlchemy ORM
- **Authentification** : Flask-Login, Werkzeug (hachage des mots de passe)
- **Formulaires** : Flask-WTF, WTForms
- **Diagnostics** : psutil, ping3, socket
- **Traitement du langage** : fuzzywuzzy (recherche approximative)
- **Frontend** : HTML5, CSS3, Bootstrap 5, JavaScript (vanilla), Chart.js pour les graphiques
- **Autres** : python-Levenshtein (optimisation de fuzzywuzzy), email-validator

---

## ⚙️ Installation

### Prérequis
- Python 3.10 ou supérieur
- pip (gestionnaire de paquets)
- Git (optionnel)

### Étapes

1. **Cloner le dépôt** (ou télécharger les sources)  

   ```bash
   git clone https://github.com/votre-repo/it-assistant.git
   cd it-assistant
   ```

2. **Créer un environnement virtuel** (recommandé)  
   ```bash
   python -m venv venv
   # Sous Windows
   venv\Scripts\activate
   # Sous Linux/Mac
   source venv/bin/activate
   ```

3. **Installer les dépendances**  
   ```bash
   pip install -r requirements.txt
   ```

4. **Lancer l’application**  
   ```bash
   python run.py
   ```

5. **Accéder à l’application**  
   Ouvrez un navigateur à l’adresse : [http://127.0.0.1:5000](http://127.0.0.1:5000)

### Compte administrateur par défaut
- **Nom d’utilisateur** : `admin`
- **Mot de passe** : `admin123`  
  (À changer après la première connexion)

### Peuplement de la base de connaissances (optionnel)
Pour ajouter des données de démonstration, exécutez le script :
```bash
python seed_knowledge.py
```

---

## 🖥 Utilisation

### Rôles et permissions

| Rôle        | Droits                                                                 |
|-------------|------------------------------------------------------------------------|
| Utilisateur | Créer et consulter ses propres tickets, utiliser le chat, consulter la base de connaissances. |
| Technicien  | Accès à tous les tickets, modification (statut, assignation, solution), ajout/modification dans la base de connaissances. |
| Administrateur | Gestion complète des utilisateurs (ajout, modification, suppression), accès aux statistiques globales. |

### Exemples d’utilisation

1. **Se connecter** avec le compte admin ou créer un nouvel utilisateur.
2. **Depuis le tableau de bord**, discuter avec l’assistant :  
   - Tapez *"diagnostic système"* pour obtenir l’état de la machine.  
   - Tapez *"ping google.com"* pour tester la connectivité.  
   - Posez une question comme *"comment réinitialiser mon mot de passe"* – si une entrée correspond dans la base, la solution s’affiche.
3. **Créer un ticket** manuellement ou via le chat (lorsque l’assistant ne trouve pas de solution).
4. **En tant que technicien**, accéder à la liste des tickets, les modifier, leur attribuer une solution.
5. **En tant qu’admin**, gérer les utilisateurs et consulter les statistiques.

---

## 📁 Structure du projet

```
it_assistant/
├── run.py                         # Point d'entrée
├── config.py                      # Configuration
├── requirements.txt               # Dépendances
├── seed_knowledge.py              # Script de peuplement de la base de connaissances
├── README.md
├── instance/
│   └── database.db                # Base de données SQLite (créée à la première exécution)
├── it_assistant/                   # Package principal
│   ├── __init__.py                # Initialisation de l'app, extensions, blueprints
│   ├── models.py                  # Modèles SQLAlchemy
│   ├── forms.py                    # Formulaires WTForms
│   ├── views/                       # Blueprints (routes)
│   │   ├── __init__.py
│   │   ├── auth.py                  # Authentification
│   │   ├── main.py                   # Pages principales, chat, diagnostics
│   │   ├── tickets.py                # Gestion des tickets
│   │   ├── knowledge.py              # Base de connaissances
│   │   └── admin.py                  # Administration
│   ├── utils/                        # Utilitaires
│   │   ├── __init__.py
│   │   ├── diagnostics.py             # Diagnostics système/réseau
│   │   ├── chatbot.py                 # Moteur du chatbot
│   │   └── helpers.py                 # Fonctions auxiliaires
│   ├── templates/                     # Templates HTML
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── dashboard_user.html
│   │   ├── dashboard_tech.html
│   │   ├── diagnostic.html
│   │   ├── tickets.html
│   │   ├── ticket_detail.html
│   │   ├── ticket_form.html
│   │   ├── knowledge.html
│   │   ├── knowledge_form.html
│   │   ├── admin_users.html
│   │   ├── admin_user_edit.html
│   │   └── admin_stats.html
│   └── static/                         # Fichiers statiques
│       ├── css/
│       │   └── style.css
│       └── js/
│           └── script.js
```

---

## 🔌 API interne

L’application expose quelques endpoints JSON utilisés par le frontend :

- `POST /chat` – Envoie un message au chatbot.  
  **Corps** : `{"message": "texte"}`  
  **Réponse** : `{"response": "...", "action": "...", "details": ...}`

- `GET /diagnostic/system` – Retourne les informations système (CPU, RAM, disque) au format JSON.

- `GET /diagnostic/network?host=...&port=...` – Effectue un diagnostic réseau (ping, test de port).  
  Paramètres optionnels : `host` (défaut 8.8.8.8), `port`.

- `POST /knowledge/quick_add` – Ajout rapide d’une entrée dans la base de connaissances (réservé aux techniciens).  
  **Corps** : `{"problem": "...", "solution": "...", "keywords": "...", "category": "..."}`

Ces endpoints sont réservés aux utilisateurs authentifiés.

---

## 📸 Captures d’écran

*Page de connexion*  
![Login](https://via.placeholder.com/800x400?text=Login)

*Tableau de bord utilisateur avec chat*  
![Dashboard User](https://via.placeholder.com/800x400?text=Dashboard+User)

*Page de diagnostic*  
![Diagnostic](https://via.placeholder.com/800x400?text=Diagnostic)

*Gestion des tickets (vue technicien)*  
![Tickets](https://via.placeholder.com/800x400?text=Tickets)

*Statistiques administrateur*  
![Stats](https://via.placeholder.com/800x400?text=Statistics)

---

## 👥 Auteurs

- **Votre Nom** – Étudiant en Licence Systèmes et Réseaux  
  Email : votre.email@example.com

Projet réalisé dans le cadre de la soutenance de fin d’année.

---

## 📄 Licence

Ce projet est distribué sous licence MIT. Voir le fichier `LICENSE` pour plus d’informations.

---

**Remarque** : Pour la production, pensez à modifier la clé secrète dans `config.py`, à changer le code secret des techniciens, et à utiliser un serveur WSGI (Gunicorn, Waitress) plutôt que le serveur de développement Flask.
```