"""
Définition des formulaires WTForms utilisés dans l'application.
Ils gèrent la validation et la génération HTML.
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, Optional
from it_assistant.models import User

class LoginForm(FlaskForm):
    """Formulaire de connexion."""
    username = StringField('Nom d\'utilisateur', validators=[DataRequired()])
    password = PasswordField('Mot de passe', validators=[DataRequired()])
    remember = BooleanField('Se souvenir de moi')
    submit = SubmitField('Se connecter')

class RegistrationForm(FlaskForm):
    """Formulaire d'inscription avec validation d'unicité et choix du rôle."""
    username = StringField('Nom d\'utilisateur', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Mot de passe', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Confirmer le mot de passe', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Rôle', choices=[('user', 'Utilisateur'), ('technician', 'Technicien')], default='user')
    secret_code = PasswordField('Code secret (si technicien)', validators=[Optional()])
    submit = SubmitField('S\'inscrire')

    def validate_username(self, username):
        """Vérifie que le nom d'utilisateur n'est pas déjà pris."""
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Ce nom d\'utilisateur est déjà pris.')

    def validate_email(self, email):
        """Vérifie que l'email n'est pas déjà utilisé."""
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Cet email est déjà utilisé.')

class TicketForm(FlaskForm):
    """Formulaire de création de ticket."""
    title = StringField('Titre', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[DataRequired()])
    priority = SelectField('Priorité', choices=[('basse', 'Basse'), ('moyenne', 'Moyenne'), ('haute', 'Haute'), ('critique', 'Critique')], default='moyenne')
    submit = SubmitField('Créer le ticket')

class TicketUpdateForm(FlaskForm):
    """Formulaire de mise à jour d'un ticket (pour techniciens)."""
    status = SelectField('Statut', choices=[('ouvert', 'Ouvert'), ('en cours', 'En cours'), ('résolu', 'Résolu'), ('fermé', 'Fermé')])
    assigned_to = SelectField('Assigné à', coerce=int)  # Les choix seront ajoutés dynamiquement
    resolution = TextAreaField('Solution', validators=[Optional()])
    submit = SubmitField('Mettre à jour')

class KnowledgeForm(FlaskForm):
    """Formulaire pour ajouter/modifier une entrée dans la base de connaissances."""
    keywords = StringField('Mots-clés (séparés par des virgules)', validators=[DataRequired()])
    problem = StringField('Problème', validators=[DataRequired(), Length(max=200)])
    solution = TextAreaField('Solution', validators=[DataRequired()])
    category = SelectField('Catégorie', choices=[('général', 'Général'), ('réseau', 'Réseau'), ('système', 'Système'), ('logiciel', 'Logiciel'), ('matériel', 'Matériel')])
    submit = SubmitField('Enregistrer')

class UserEditForm(FlaskForm):
    """Formulaire d'édition d'un utilisateur (admin)."""
    username = StringField('Nom d\'utilisateur', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    role = SelectField('Rôle', choices=[('user', 'Utilisateur'), ('technician', 'Technicien'), ('admin', 'Administrateur')])
    password = PasswordField('Nouveau mot de passe (laisser vide pour ne pas changer)')
    submit = SubmitField('Mettre à jour')


class ProfileSettingsForm(FlaskForm):
    """
    Formulaire "Paramètres" : profil + préférences d'apparence.

    Note : on passe l'utilisateur courant au constructeur pour valider l'unicité de l'email.
    """
    full_name = StringField('Nom complet', validators=[Optional(), Length(max=120)])
    phone = StringField('Téléphone', validators=[Optional(), Length(max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    theme = SelectField('Thème', choices=[('light', 'Clair'), ('dark', 'Sombre')], default='light')
    save_profile = SubmitField('Enregistrer')

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._user = user

    def validate_email(self, email):
        """Empêche de prendre l'email d'un autre compte."""
        if not self._user:
            return
        if email.data != self._user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Cet email est déjà utilisé.')


class ChangePasswordForm(FlaskForm):
    """Formulaire pour permettre à un utilisateur de changer son propre mot de passe."""
    current_password = PasswordField('Mot de passe actuel', validators=[DataRequired()])
    new_password = PasswordField('Nouveau mot de passe', validators=[DataRequired(), Length(min=6)])
    new_password2 = PasswordField('Confirmer le nouveau mot de passe', validators=[DataRequired(), EqualTo('new_password')])
    change_password = SubmitField('Changer le mot de passe')
