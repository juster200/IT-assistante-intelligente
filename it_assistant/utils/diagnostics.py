"""
Fonctions de diagnostic système et réseau.
Utilise psutil pour le système, ping3 et socket pour le réseau.
"""

import psutil
import socket
from ping3 import ping
import platform

def system_diagnostic():
    """
    Récupère les informations système :
    - CPU : pourcentage d'utilisation, nombre de cœurs
    - Mémoire : totale, disponible, pourcentage utilisé
    - Disque : total, utilisé, libre, pourcentage
    - Plateforme : système, version, nom d'hôte
    """
    diag = {}
    # CPU
    diag['cpu_percent'] = psutil.cpu_percent(interval=1)
    diag['cpu_count'] = psutil.cpu_count()
    # Mémoire
    mem = psutil.virtual_memory()
    diag['memory_total'] = mem.total
    diag['memory_available'] = mem.available
    diag['memory_percent'] = mem.percent
    # Disque (partition racine)
    disk = psutil.disk_usage('/')
    diag['disk_total'] = disk.total
    diag['disk_used'] = disk.used
    diag['disk_free'] = disk.free
    diag['disk_percent'] = disk.percent
    # Informations système
    diag['platform'] = platform.system()
    diag['platform_version'] = platform.version()
    diag['hostname'] = platform.node()
    return diag

def network_diagnostic(host='8.8.8.8', port=None):
    """
    Effectue un diagnostic réseau :
    - Ping vers l'hôte donné
    - Test de port (si spécifié) avec connexion TCP
    """
    result = {}
    # Ping
    try:
        response_time = ping(host, timeout=2)
        if response_time is None:
            result['ping'] = 'Échec (timeout)'
        else:
            # Conversion en millisecondes
            result['ping'] = f'{response_time*1000:.2f} ms'
    except Exception as e:
        result['ping'] = f'Erreur: {str(e)}'

    # Test de port
    if port:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result_code = sock.connect_ex((host, port))
            if result_code == 0:
                result['port'] = f'Le port {port} est ouvert'
            else:
                result['port'] = f'Le port {port} est fermé ou filtré'
            sock.close()
        except Exception as e:
            result['port'] = f'Erreur: {str(e)}'
    return result

def free_disk_space(threshold=90):
    """
    Vérifie si l'espace disque dépasse un seuil et propose des actions.
    Retourne une liste de suggestions.
    """
    disk_percent = psutil.disk_usage('/').percent
    if disk_percent > threshold:
        suggestions = []
        if platform.system() == 'Windows':
            suggestions.append("Exécuter 'cleanmgr' pour nettoyer les fichiers temporaires.")
        else:
            suggestions.append("Utiliser 'sudo apt-get clean' ou 'sudo journalctl --vacuum-size=100M' selon la distribution.")
        return suggestions
    return []

def top_memory_processes(limit=5):
    """Retourne les processus les plus gourmands en mémoire."""
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'memory_percent']):
        try:
            processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    processes.sort(key=lambda x: x['memory_percent'], reverse=True)
    return processes[:limit]
