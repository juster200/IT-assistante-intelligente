"""
Blueprint pour la gestion de la base de connaissances.
Inclut une route d'ajout rapide via AJAX.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, jsonify
from flask_login import login_required, current_user
from it_assistant import db
from it_assistant.models import KnowledgeBase
from it_assistant.forms import KnowledgeForm

knowledge_bp = Blueprint('knowledge', __name__)

@knowledge_bp.before_request
def restrict_to_admin():
    """
    Restreint l'accès à toutes les routes /knowledge aux administrateurs.

    Demande : retirer la base de connaissances pour les techniciens et les utilisateurs.
    On garde l'authentification Flask-Login (login_required) sur chaque route :
    - Non connecté : redirection vers /auth/login.
    - Connecté mais non admin : 403.
    """
    if current_user.is_authenticated and not current_user.is_admin():
        abort(403)

@knowledge_bp.route('/')
@login_required
def list_knowledge():
    """Liste toutes les entrées de la base de connaissances (admin uniquement)."""
    entries = KnowledgeBase.query.order_by(KnowledgeBase.category, KnowledgeBase.problem).all()
    return render_template('knowledge.html', entries=entries)

@knowledge_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new_entry():
    """Ajout d'une nouvelle entrée (admin uniquement)."""
    form = KnowledgeForm()
    if form.validate_on_submit():
        entry = KnowledgeBase(
            keywords=form.keywords.data,
            problem=form.problem.data,
            solution=form.solution.data,
            category=form.category.data,
            author_id=current_user.id
        )
        db.session.add(entry)
        db.session.commit()
        flash('Entrée ajoutée à la base de connaissances.', 'success')
        return redirect(url_for('knowledge.list_knowledge'))
    return render_template('knowledge_form.html', form=form, title='Nouvelle entrée')

@knowledge_bp.route('/<int:entry_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_entry(entry_id):
    """Modification d'une entrée existante (admin uniquement)."""
    entry = KnowledgeBase.query.get_or_404(entry_id)
    form = KnowledgeForm()
    if form.validate_on_submit():
        entry.keywords = form.keywords.data
        entry.problem = form.problem.data
        entry.solution = form.solution.data
        entry.category = form.category.data
        entry.updated_at = db.func.now()
        db.session.commit()
        flash('Entrée mise à jour.', 'success')
        return redirect(url_for('knowledge.list_knowledge'))
    # Pré-remplir
    form.keywords.data = entry.keywords
    form.problem.data = entry.problem
    form.solution.data = entry.solution
    form.category.data = entry.category
    return render_template('knowledge_form.html', form=form, title='Modifier l\'entrée', entry=entry)

@knowledge_bp.route('/<int:entry_id>/delete', methods=['POST'])
@login_required
def delete_entry(entry_id):
    """Suppression d'une entrée (admin uniquement)."""
    entry = KnowledgeBase.query.get_or_404(entry_id)
    db.session.delete(entry)
    db.session.commit()
    flash('Entrée supprimée.', 'info')
    return redirect(url_for('knowledge.list_knowledge'))

@knowledge_bp.route('/quick_add', methods=['POST'])
@login_required
def quick_add():
    """
    Endpoint AJAX pour ajout rapide d'une entrée (utilisé depuis le tableau de bord technicien).
    Reçoit un JSON avec problem, solution, keywords, category.
    """
    # Sécurité : réponse JSON explicite côté front (même si le before_request filtre déjà).
    if not current_user.is_admin():
        return jsonify({'success': False, 'message': 'Accès refusé'}), 403
    data = request.get_json()
    problem = data.get('problem', '').strip()
    solution = data.get('solution', '').strip()
    keywords = data.get('keywords', '').strip()
    category = data.get('category', 'général')

    if not problem or not solution:
        return jsonify({'success': False, 'message': 'Le problème et la solution sont requis.'})

    entry = KnowledgeBase(
        keywords=keywords,
        problem=problem,
        solution=solution,
        category=category,
        author_id=current_user.id
    )
    db.session.add(entry)
    db.session.commit()
    return jsonify({'success': True})
