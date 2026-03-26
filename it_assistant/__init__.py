"""
Initialisation de l'application Flask et de ses extensions.
Ce fichier est exécuté lorsque le package est importé.
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

# Initialisation des extensions (sans application pour le moment)
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'  # Route de redirection si non connecté
login_manager.login_message = "Veuillez vous connecter pour accéder à cette page."

def create_app(config_class=Config):
    """
    Fonction factory de l'application Flask.
    Configure l'application, initialise les extensions et enregistre les blueprints.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialisation des extensions avec l'application
    db.init_app(app)
    login_manager.init_app(app)

    # Enregistrement des blueprints (sous-modules de routes)
    from it_assistant.views.auth import auth_bp
    from it_assistant.views.main import main_bp
    from it_assistant.views.tickets import tickets_bp
    from it_assistant.views.knowledge import knowledge_bp
    from it_assistant.views.admin import admin_bp
    from it_assistant.views.settings import settings_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)
    app.register_blueprint(tickets_bp, url_prefix='/tickets')
    app.register_blueprint(knowledge_bp, url_prefix='/knowledge')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(settings_bp, url_prefix='/settings')

    # Création des tables dans la base de données (si elles n'existent pas)
    with app.app_context():
        db.create_all()
        # Créer un administrateur par défaut si aucun utilisateur n'existe
        from it_assistant.models import User, UserSettings
        if not User.query.filter_by(role='admin').first():
            admin = User(username='admin', email='admin@example.com', role='admin')
            admin.set_password('admin123')  # À changer en production
            db.session.add(admin)
            db.session.commit()
            print("Compte administrateur créé par défaut : admin / admin123")

        # Backfill : s'assurer que chaque utilisateur a une ligne de préférences.
        # Important car la page Paramètres et le thème lisent current_user.settings.
        created_settings = False
        for user in User.query.all():
            if user.settings is None:
                db.session.add(UserSettings(user_id=user.id))
                created_settings = True
        if created_settings:
            db.session.commit()

    return app
