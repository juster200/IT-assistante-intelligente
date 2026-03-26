"""
Blueprint "Paramètres" : profil, apparence (thème), sécurité (mot de passe).

Objectifs :
- Permettre à l'utilisateur de gérer ses informations personnelles.
- Permettre le changement de mot de passe (self-service).
- Enregistrer le thème clair/sombre en base (UserSettings.theme).
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from it_assistant import db
from it_assistant.forms import ProfileSettingsForm, ChangePasswordForm
from it_assistant.models import UserSettings

settings_bp = Blueprint('settings', __name__)


@settings_bp.route('', methods=['GET', 'POST'])
@login_required
def index():
    """
    Page Paramètres.

    Note :
    - On utilise deux formulaires sur la même page (profil/theme et mot de passe).
    - On traite celui dont le bouton submit est présent dans la requête POST.
    """
    # Sécurité : en principe créé au démarrage et à l'inscription, mais on garde un filet.
    if current_user.settings is None:
        db.session.add(UserSettings(user_id=current_user.id))
        db.session.commit()

    profile_form = ProfileSettingsForm(user=current_user)
    password_form = ChangePasswordForm()

    if request.method == 'GET':
        profile_form.full_name.data = current_user.settings.full_name
        profile_form.phone.data = current_user.settings.phone
        profile_form.email.data = current_user.email
        profile_form.theme.data = current_user.settings.theme or 'light'

    # Enregistrer profil + theme
    if profile_form.save_profile.data and profile_form.validate_on_submit():
        current_user.email = profile_form.email.data
        current_user.settings.full_name = profile_form.full_name.data
        current_user.settings.phone = profile_form.phone.data
        current_user.settings.theme = profile_form.theme.data
        db.session.commit()
        flash('Paramètres mis à jour.', 'success')
        return redirect(url_for('settings.index'))

    # Changer mot de passe
    if password_form.change_password.data and password_form.validate_on_submit():
        if not current_user.check_password(password_form.current_password.data):
            password_form.current_password.errors.append('Mot de passe actuel incorrect.')
        else:
            current_user.set_password(password_form.new_password.data)
            db.session.commit()
            flash('Mot de passe mis à jour.', 'success')
            return redirect(url_for('settings.index'))

    return render_template(
        'settings.html',
        profile_form=profile_form,
        password_form=password_form,
    )

