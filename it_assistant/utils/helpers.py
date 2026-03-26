"""
Fonctions utilitaires diverses.
"""

def format_bytes(size):
    """Convertit une taille en octets en une chaîne lisible (Ko, Mo, Go)."""
    for unit in ['o', 'Ko', 'Mo', 'Go', 'To']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} Po"