"""
Script pour ajouter des données de démonstration dans la base de connaissances.
À exécuter une fois après la création de la base.
"""
from it_assistant import create_app, db
from it_assistant.models import KnowledgeBase

app = create_app()
with app.app_context():
    # Liste d'exemples (vous pouvez en ajouter beaucoup plus)
    entries = [
        {
            "keywords": "mot de passe, oubli, réinitialisation",
            "problem": "J'ai oublié mon mot de passe",
            "solution": "Cliquez sur 'Mot de passe oublié' sur la page de connexion. Un email vous sera envoyé avec un lien de réinitialisation. Si vous n'avez pas accès à votre email, contactez votre administrateur.",
            "category": "compte"
        },
        {
            "keywords": "connexion, réseau, wifi, internet",
            "problem": "Impossible de se connecter au WiFi",
            "solution": "Vérifiez que le WiFi est activé sur votre appareil. Redémarrez votre routeur. Si le problème persiste, oubliez le réseau et reconnectez-vous en saisissant à nouveau le mot de passe.",
            "category": "réseau"
        },
        {
            "keywords": "lenteur, performance, ralentissement",
            "problem": "L'ordinateur est très lent",
            "solution": "Fermez les applications inutilisées. Vérifiez l'utilisation du CPU et de la mémoire dans le gestionnaire des tâches. Effectuez un scan antivirus. Pensez à redémarrer votre machine.",
            "category": "système"
        },
        {
            "keywords": "imprimante, impression, papier",
            "problem": "L'imprimante n'imprime pas",
            "solution": "Vérifiez qu'elle est allumée et connectée. Dans les paramètres d'impression, assurez-vous qu'elle est définie comme imprimante par défaut. Redémarrez la file d'attente d'impression.",
            "category": "matériel"
        },
        {
            "keywords": "email, messagerie, envoi, réception",
            "problem": "Je ne reçois pas mes emails",
            "solution": "Vérifiez votre dossier 'Spam' ou 'Indésirables'. Assurez-vous que votre boîte n'est pas pleine. Si vous utilisez un client de messagerie, vérifiez les paramètres du serveur.",
            "category": "logiciel"
        },
        # ... ajoutez autant d'entrées que souhaité
    ]

    for e in entries:
        # Éviter les doublons (optionnel)
        exists = KnowledgeBase.query.filter_by(problem=e["problem"]).first()
        if not exists:
            kb = KnowledgeBase(
                keywords=e["keywords"],
                problem=e["problem"],
                solution=e["solution"],
                category=e["category"],
                author_id=None  # ou un ID d'admin si vous voulez
            )
            db.session.add(kb)

    db.session.commit()
    print(f"{len(entries)} entrées ajoutées à la base de connaissances.")