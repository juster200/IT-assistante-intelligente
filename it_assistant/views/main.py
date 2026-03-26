"""
Blueprint principal : pages d'accueil, tableau de bord, chat, diagnostics.
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from it_assistant import db
from it_assistant.models import Ticket, KnowledgeBase, Log
from it_assistant.utils.diagnostics import system_diagnostic, network_diagnostic
from it_assistant.utils.chatbot import process_query

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Page d'accueil publique."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Tableau de bord personnalisé selon le rôle."""
    if current_user.is_technician():
        # Statistiques pour les techniciens
        tickets_open = Ticket.query.filter_by(status='ouvert').count()
        tickets_in_progress = Ticket.query.filter_by(status='en cours').count()
        tickets_resolved = Ticket.query.filter_by(status='résolu').count()
        recent_tickets = Ticket.query.order_by(Ticket.created_at.desc()).limit(5).all()
        return render_template('dashboard_tech.html',
                               tickets_open=tickets_open,
                               tickets_in_progress=tickets_in_progress,
                               tickets_resolved=tickets_resolved,
                               recent_tickets=recent_tickets)
    else:
        # Utilisateur normal : ses tickets
        user_tickets = Ticket.query.filter_by(user_id=current_user.id).order_by(Ticket.created_at.desc()).all()
        return render_template('dashboard_user.html', tickets=user_tickets)

@main_bp.route('/diagnostic')
@login_required
def diagnostic():
    """Page dédiée aux diagnostics système et réseau."""
    return render_template('diagnostic.html')

@main_bp.route('/chat', methods=['POST'])
@login_required
def chat():
    """
    Endpoint AJAX pour le chatbot.
    Reçoit un message JSON, le traite et retourne une réponse.
    """
    data = request.get_json()
    user_message = (data.get('message', '') or '').strip()
    if not user_message:
        return jsonify({'response': "Veuillez entrer un message."})

    # Traiter la requête via le module chatbot
    response, action, details = process_query(user_message, current_user)

    # Si le chatbot ne trouve pas de réponse : création automatique d'un ticket.
    # Demande : éviter d'obliger l'utilisateur à cliquer sur "Créer un ticket".
    log_action = 'chat_query'
    if action == 'ask_ticket':
        log_action = 'chat_ticket_auto'

        # Anti-duplication : si l'utilisateur vient d'envoyer exactement le même message,
        # on réutilise le ticket le plus récent au lieu d'en créer un nouveau.
        window_start = datetime.utcnow() - timedelta(minutes=10)
        existing = (
            Ticket.query
            .filter_by(user_id=current_user.id, description=user_message)
            .filter(Ticket.created_at >= window_start)
            .order_by(Ticket.created_at.desc())
            .first()
        )

        if existing:
            action = 'ticket_existing'
            details = {'ticket_id': existing.id}
            response = (
                f"Je n'ai pas trouvé de solution. Un ticket récent existe déjà (#{existing.id}). "
                "Vous pouvez l'ouvrir pour suivre le traitement."
            )
        else:
            # Génère un titre court à partir du message.
            first_line = user_message.splitlines()[0].strip()
            title = first_line[:80] + ('...' if len(first_line) > 80 else '')
            if not title:
                title = "Demande via chatbot"

            ticket = Ticket(
                title=title,
                description=user_message,
                priority='moyenne',
                user_id=current_user.id,
            )
            db.session.add(ticket)
            db.session.flush()  # Assigne ticket.id avant de construire la réponse

            action = 'ticket_created'
            details = {'ticket_id': ticket.id}
            response = (
                "Je n'ai pas trouvé de solution dans ma base de connaissances. "
                f"J'ai créé automatiquement un ticket (#{ticket.id}). "
                "Un technicien va le traiter."
            )

    # Journaliser l'interaction (ou la création automatique)
    log = Log(
        user_id=current_user.id,
        action=log_action,
        details=f"Message: {user_message} | Réponse: {response[:100]}",
    )
    db.session.add(log)
    db.session.commit()

    return jsonify({'response': response, 'action': action, 'details': details})

@main_bp.route('/diagnostic/system')
@login_required
def diagnostic_system():
    """Lance un diagnostic système et retourne les résultats en JSON."""
    diag = system_diagnostic()
    log = Log(user_id=current_user.id, action='diagnostic_system', details=str(diag))
    db.session.add(log)
    db.session.commit()
    return jsonify(diag)

@main_bp.route('/diagnostic/network')
@login_required
def diagnostic_network():
    """
    Lance un diagnostic réseau.
    Paramètres GET : host (défaut: 8.8.8.8), port (optionnel)
    """
    host = request.args.get('host', '8.8.8.8')
    port = request.args.get('port', None, type=int)
    diag = network_diagnostic(host, port)
    log = Log(user_id=current_user.id, action='diagnostic_network', details=f"host={host}, port={port}")
    db.session.add(log)
    db.session.commit()
    return jsonify(diag)
