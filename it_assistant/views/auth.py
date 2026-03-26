"""
Blueprint pour l'authentification (connexion, déconnexion, inscription).
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from it_assistant import db
from it_assistant.models import User, UserSettings
from it_assistant.forms import LoginForm, RegistrationForm

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Route de connexion."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            flash('Connexion réussie.', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.index'))
        else:
            flash('Nom d\'utilisateur ou mot de passe incorrect.', 'danger')
    return render_template('login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    """Route de déconnexion."""
    logout_user()
    flash('Vous avez été déconnecté.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    Route d'inscription avec validation du code secret pour devenir technicien.
    Si le code est incorrect, l'utilisateur est enregistré avec le rôle 'user'.
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        # Déterminer le rôle en fonction du code secret
        role = form.role.data
        if role == 'technician':
            secret_code = form.secret_code.data
            # Vérification du code secret (depuis la config)
            if not secret_code or secret_code != current_app.config['TECHNICIAN_SECRET_CODE']:
                flash('Code secret incorrect. Vous serez enregistré en tant qu\'utilisateur standard.', 'warning')
                role = 'user'  # Forcer le rôle utilisateur
        else:
            role = 'user'

        user = User(username=form.username.data, email=form.email.data, role=role)
        user.set_password(form.password.data)
        db.session.add(user)
        # Créer immédiatement les préférences utilisateur (thème/profil) pour la page Paramètres.
        db.session.flush()  # Assigne user.id sans faire de commit
        db.session.add(UserSettings(user_id=user.id))
        db.session.commit()
        flash('Votre compte a été créé ! Vous pouvez maintenant vous connecter.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html', form=form)
