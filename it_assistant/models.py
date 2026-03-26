"""
Définition des modèles de données avec SQLAlchemy.
Gère les utilisateurs, tickets, base de connaissances et logs.
"""

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from it_assistant import db, login_manager
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    """Charge un utilisateur à partir de son ID (utilisé par Flask-Login)."""
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    """
    Modèle représentant un utilisateur de l'application.
    Attributs :
        - username : nom d'utilisateur unique
        - email : adresse email unique
        - password_hash : mot de passe haché
        - role : rôle (user, technician, admin)
        - created_at : date de création
    Relations :
        - tickets_created : tickets créés par l'utilisateur
        - tickets_assigned : tickets assignés à l'utilisateur (technicien)
        - knowledge_entries : entrées de la base de connaissances créées
        - settings : préférences/profil utilisateur (thème, infos, etc.)
        - logs : actions journalisées
    """
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), default='user')  # 'user', 'technician', 'admin'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relations
    tickets_created = db.relationship('Ticket', foreign_keys='Ticket.user_id', backref='author', lazy='dynamic')
    tickets_assigned = db.relationship('Ticket', foreign_keys='Ticket.assigned_to', backref='technician', lazy='dynamic')
    knowledge_entries = db.relationship('KnowledgeBase', backref='author', lazy='dynamic')
    # One-to-one : un seul enregistrement de préférences par utilisateur.
    settings = db.relationship('UserSettings', backref='user', uselist=False, cascade='all, delete-orphan')
    logs = db.relationship('Log', backref='user', lazy='dynamic')

    def set_password(self, password):
        """Hache et stocke le mot de passe."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Vérifie si le mot de passe fourni correspond au haché."""
        return check_password_hash(self.password_hash, password)

    def is_technician(self):
        """Retourne True si l'utilisateur a un rôle de technicien ou admin."""
        return self.role in ['technician', 'admin']

    def is_admin(self):
        """Retourne True si l'utilisateur est administrateur."""
        return self.role == 'admin'

class UserSettings(db.Model):
    """
    Préférences et informations "profil" rattachées à un utilisateur.

    Pourquoi une table dédiée (plutôt que des colonnes sur users) :
    - Évite de casser une base SQLite déjà existante (db.create_all ne migre pas les colonnes).
    - Permet d'ajouter des champs de profil plus facilement.
    """
    __tablename__ = 'user_settings'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)

    # Profil (facultatif)
    full_name = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(50), nullable=True)

    # Apparence : "light" | "dark"
    theme = db.Column(db.String(20), default='light', nullable=False)

    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Ticket(db.Model):
    """
    Modèle représentant un ticket d'incident.
    Attributs :
        - title : titre du ticket
        - description : description détaillée
        - status : statut (ouvert, en cours, résolu, fermé)
        - priority : priorité (basse, moyenne, haute, critique)
        - created_at : date de création
        - updated_at : date de dernière mise à jour
        - user_id : ID de l'utilisateur ayant créé le ticket
        - assigned_to : ID du technicien assigné (peut être nul)
        - resolution : solution apportée (texte)
    """
    __tablename__ = 'tickets'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='ouvert')  # ouvert, en cours, résolu, fermé
    priority = db.Column(db.String(20), default='moyenne')  # basse, moyenne, haute, critique
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    resolution = db.Column(db.Text, nullable=True)  # Solution apportée

class KnowledgeBase(db.Model):
    """
    Modèle représentant une entrée de la base de connaissances.
    Attributs :
        - keywords : mots-clés (séparés par des virgules)
        - problem : description courte du problème
        - solution : solution détaillée
        - category : catégorie (réseau, système, etc.)
        - created_at : date de création
        - updated_at : date de mise à jour
        - author_id : ID de l'auteur (technicien)
    """
    __tablename__ = 'knowledge_base'
    id = db.Column(db.Integer, primary_key=True)
    keywords = db.Column(db.String(200), nullable=False)
    problem = db.Column(db.String(200), nullable=False)
    solution = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), default='général')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

class Log(db.Model):
    """
    Modèle pour journaliser les actions importantes.
    Attributs :
        - user_id : ID de l'utilisateur (peut être nul pour les actions anonymes)
        - action : type d'action (chat, diagnostic, etc.)
        - details : détails supplémentaires (format JSON ou texte)
        - timestamp : date et heure de l'action
    """
    __tablename__ = 'logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    action = db.Column(db.String(100), nullable=False)
    details = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
