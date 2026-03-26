# it_assistant/views/tickets.py
"""
Blueprint pour la gestion des tickets.
Permissions :
- Les techniciens et admins peuvent tout voir et modifier.
- Les utilisateurs normaux ne voient que leurs propres tickets (via la route view_ticket).

Fonctionnalités ajoutées :
- Page de résolution dédiée (technicien/admin) : /tickets/<id>/resolve
- Page de consultation de la solution (utilisateur concerné) : /tickets/<id>/solution
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from it_assistant import db
from it_assistant.models import Ticket, User
from it_assistant.forms import TicketForm, TicketUpdateForm

tickets_bp = Blueprint('tickets', __name__)

def _configure_assignment_choices(form):
    """
    Remplit la liste des techniciens pour l'assignation.

    Centralisé ici pour éviter de dupliquer la même logique entre plusieurs pages
    (édition/résolution).
    """
    technicians = User.query.filter(User.role.in_(['technician', 'admin'])).all()
    form.assigned_to.choices = [(0, 'Non assigné')] + [(t.id, t.username) for t in technicians]

@tickets_bp.route('/')
@login_required
def list_tickets():
    """Liste des tickets - réservée aux techniciens et admins."""
    if not current_user.is_technician():
        flash('Accès non autorisé.', 'danger')
        return redirect(url_for('main.dashboard'))
    tickets = Ticket.query.order_by(Ticket.created_at.desc()).all()
    return render_template('tickets.html', tickets=tickets)

@tickets_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new_ticket():
    """Création d'un nouveau ticket (accessible à tous)."""
    form = TicketForm()
    if request.method == 'GET':
        # Pré-remplir la description si fournie (ex: depuis le chat)
        desc = request.args.get('description')
        if desc:
            form.description.data = desc
    if form.validate_on_submit():
        ticket = Ticket(
            title=form.title.data,
            description=form.description.data,
            priority=form.priority.data,
            user_id=current_user.id
        )
        db.session.add(ticket)
        db.session.commit()
        flash('Ticket créé avec succès.', 'success')
        return redirect(url_for('tickets.list_tickets' if current_user.is_technician() else 'main.dashboard'))
    return render_template('ticket_form.html', form=form, title='Nouveau ticket')

@tickets_bp.route('/<int:ticket_id>')
@login_required
def view_ticket(ticket_id):
    """Affiche le détail d'un ticket. Accessible au propriétaire ou aux techniciens."""
    ticket = Ticket.query.get_or_404(ticket_id)
    # Vérification : propriétaire ou technicien
    if not (current_user.id == ticket.user_id or current_user.is_technician()):
        abort(403)
    return render_template('ticket_detail.html', ticket=ticket)

@tickets_bp.route('/<int:ticket_id>/solution')
@login_required
def ticket_solution(ticket_id):
    """
    Page dédiée à la consultation de la solution d'un ticket.

    Demande : permettre à l'utilisateur concerné (et aux techniciens/admin)
    de consulter la solution quand elle existe.
    """
    ticket = Ticket.query.get_or_404(ticket_id)
    if not (current_user.id == ticket.user_id or current_user.is_technician()):
        abort(403)
    return render_template('ticket_solution.html', ticket=ticket)

@tickets_bp.route('/<int:ticket_id>/resolve', methods=['GET', 'POST'])
@login_required
def resolve_ticket(ticket_id):
    """
    Page de résolution d'un ticket (technicien/admin).

    Remarque :
    - On réutilise TicketUpdateForm (statut, assignation, solution).
    - Si le statut est "résolu", une solution est exigée pour éviter les résolutions "vides".
    """
    ticket = Ticket.query.get_or_404(ticket_id)
    if not current_user.is_technician():
        abort(403)

    form = TicketUpdateForm()
    _configure_assignment_choices(form)

    if request.method == 'GET':
        # Pré-remplir le formulaire ; par défaut, on propose "résolu" pour une page de résolution.
        form.status.data = 'résolu' if ticket.status in ['ouvert', 'en cours'] else ticket.status
        form.assigned_to.data = ticket.assigned_to if ticket.assigned_to else 0
        form.resolution.data = ticket.resolution

    if form.validate_on_submit():
        if form.status.data == 'résolu' and not (form.resolution.data or '').strip():
            form.resolution.errors.append("La solution est requise pour marquer le ticket comme résolu.")
        else:
            ticket.status = form.status.data
            ticket.assigned_to = form.assigned_to.data if form.assigned_to.data != 0 else None
            ticket.resolution = (form.resolution.data or '').strip() or None
            ticket.updated_at = db.func.now()
            db.session.commit()
            flash('Ticket mis à jour.', 'success')
            return redirect(url_for('tickets.view_ticket', ticket_id=ticket.id))

    return render_template('ticket_form.html', form=form, title='Résolution du ticket', ticket=ticket)

@tickets_bp.route('/<int:ticket_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_ticket(ticket_id):
    """
    Ancienne route "edit" conservée pour compatibilité.

    On redirige vers la page de résolution, qui couvre le même besoin (statut/assignation/solution).
    """
    return resolve_ticket(ticket_id)

@tickets_bp.route('/<int:ticket_id>/delete', methods=['POST'])
@login_required
def delete_ticket(ticket_id):
    """Suppression d'un ticket (admin ou propriétaire)."""
    ticket = Ticket.query.get_or_404(ticket_id)
    if not (current_user.is_admin() or current_user.id == ticket.user_id):
        abort(403)
    db.session.delete(ticket)
    db.session.commit()
    flash('Ticket supprimé.', 'info')
    return redirect(url_for('tickets.list_tickets' if current_user.is_technician() else 'main.dashboard'))
