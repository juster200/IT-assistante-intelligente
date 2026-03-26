"""
Module de configuration de l'application Flask.
Charge les variables d'environnement ou utilise des valeurs par défaut.
"""
import os

class Config:
    # Clé secrète pour les sessions (à changer absolument en production)
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'une-cle-secrete-tres-difficile-a-deviner'
    
    # URI de la base de données SQLite (fichier dans le dossier instance/)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance', 'database.db')
    
    # Désactiver le tracking des modifications pour économiser des ressources
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Code secret pour devenir technicien (à définir dans l'environnement de préférence)
    TECHNICIAN_SECRET_CODE = os.environ.get('TECHNICIAN_SECRET_CODE') or 'TECH123'