"""
Moteur du chatbot : traite les messages utilisateur et retourne une réponse.
Utilise la recherche floue pour interroger la base de connaissances.
"""

import re
from fuzzywuzzy import fuzz
from it_assistant.models import KnowledgeBase
from it_assistant.utils.diagnostics import system_diagnostic, network_diagnostic

def process_query(user_message, current_user):
    """
    Analyse le message utilisateur et détermine la réponse appropriée.
    Retourne un tuple (response, action, details) où action peut être utilisé
    pour déclencher des actions côté frontend.
    """
    message_lower = user_message.lower().strip()

    # 1. Commandes spécifiques (diagnostics)
    if message_lower in ['diagnostic système', 'diag système', 'etat système']:
        diag = system_diagnostic()
        response = "**Diagnostic système :**\n\n"
        response += f"- **CPU :** {diag['cpu_percent']}% utilisé\n"
        response += f"- **Mémoire :** {diag['memory_percent']}% utilisé\n"
        response += f"- **Disque :** {diag['disk_percent']}% utilisé\n"
        if diag['disk_percent'] > 90:
            response += "\n⚠️ **Alerte :** Le disque est presque plein. Pensez à libérer de l'espace.\n"
        return response, 'system_diagnostic', diag

    if message_lower.startswith('ping') or 'diagnostic réseau' in message_lower:
        # Extraire l'hôte si la commande est "ping <hôte>"
        match = re.search(r'ping\s+(\S+)', message_lower)
        host = match.group(1) if match else '8.8.8.8'
        diag = network_diagnostic(host)
        response = f"**Diagnostic réseau vers {host} :**\n\n"
        response += f"- **Ping :** {diag['ping']}\n"
        if 'port' in diag:
            response += f"- **Port :** {diag['port']}\n"
        return response, 'network_diagnostic', diag

    # 2. Recherche dans la base de connaissances
    all_entries = KnowledgeBase.query.all()
    best_match = None
    best_score = 0
    for entry in all_entries:
        # Comparer le message avec les mots-clés et le problème
        text_to_compare = entry.keywords + " " + entry.problem
        score = fuzz.partial_ratio(message_lower, text_to_compare.lower())
        if score > best_score and score > 60:  # Seuil de similarité
            best_score = score
            best_match = entry

    if best_match:
        response = f"**Problème :** {best_match.problem}\n\n**Solution :** {best_match.solution}"
        return response, 'knowledge_found', {'entry_id': best_match.id}

    # 3. Si rien trouvé, proposer de créer un ticket
    response = "Je n'ai pas trouvé de solution dans ma base de connaissances. Voulez-vous créer un ticket d'incident ?"
    return response, 'ask_ticket', None
