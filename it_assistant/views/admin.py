"""
Blueprint pour l'administration : gestion des utilisateurs, statistiques.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from it_assistant import db
from it_assistant.models import User, Ticket, Log
from it_assistant.forms import UserEditForm

admin_bp = Blueprint('admin', __name__)

@admin_bp.before_request
def restrict_to_admin():
    """Vérifie que l'utilisateur est admin avant toute requête."""
    if not current_user.is_authenticated or not current_user.is_admin():
        abort(403)

@admin_bp.route('/users')
def list_users():
    """Liste tous les utilisateurs."""
    users = User.query.all()
    return render_template('admin_users.html', users=users)

@admin_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
def edit_user(user_id):
    """Modification d'un utilisateur."""
    user = User.query.get_or_404(user_id)
    form = UserEditForm()
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.role = form.role.data
        if form.password.data:
            user.set_password(form.password.data)
        db.session.commit()
        flash('Utilisateur mis à jour.', 'success')
        return redirect(url_for('admin.list_users'))
    # Pré-remplir
    form.username.data = user.username
    form.email.data = user.email
    form.role.data = user.role
    return render_template('admin_user_edit.html', form=form, user=user)

@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
def delete_user(user_id):
    """Suppression d'un utilisateur (sauf soi-même)."""
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('Vous ne pouvez pas vous supprimer vous-même.', 'danger')
        return redirect(url_for('admin.list_users'))
    db.session.delete(user)
    db.session.commit()
    flash('Utilisateur supprimé.', 'info')
    return redirect(url_for('admin.list_users'))

@admin_bp.route('/stats')
def stats():
    """Page de statistiques (nombre de tickets par statut/priorité, logs récents)."""
    total_tickets = Ticket.query.count()
    tickets_by_status = db.session.query(Ticket.status, db.func.count(Ticket.id)).group_by(Ticket.status).all()
    tickets_by_priority = db.session.query(Ticket.priority, db.func.count(Ticket.id)).group_by(Ticket.priority).all()
    users_count = User.query.count()
    recent_logs = Log.query.order_by(Log.timestamp.desc()).limit(10).all()
    return render_template('admin_stats.html',
                           total_tickets=total_tickets,
                           tickets_by_status=tickets_by_status,
                           tickets_by_priority=tickets_by_priority,
                           users_count=users_count,
                           recent_logs=recent_logs)