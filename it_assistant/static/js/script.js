/**
 * script.js - Fonctions JavaScript globales
 *
 * Notes (maintenance) :
 * - Ce fichier est chargé sur toutes les pages via base.html.
 * - Chaque bloc doit donc vérifier l'existence des éléments DOM avant d'agir
 *   (sinon une page sans chat/diagnostic peut casser tout le script).
 */

// Attendre que le DOM soit chargé
document.addEventListener('DOMContentLoaded', function() {
    // Initialisation des tooltips Bootstrap (si utilisés).
    // Protection : si le CDN Bootstrap ne charge pas, on évite de casser le reste du script.
    if (window.bootstrap && bootstrap.Tooltip) {
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    // Gestion du chat si présent sur la page
    const chatSend = document.getElementById('chat-send');
    if (chatSend) {
        chatSend.addEventListener('click', sendChatMessage);
        // Permettre l'envoi avec la touche Entrée
        const chatInput = document.getElementById('chat-input');
        if (chatInput) {
            chatInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    sendChatMessage();
                }
            });
        }
    }

    // Gestion des boutons de suggestion
    document.querySelectorAll('.suggestion-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const input = document.getElementById('chat-input');
            if (!input) return; // Page sans chat : ignorer.
            // Récupérer le texte du bouton en supprimant l'emoji (premier caractère)
            let text = this.textContent.trim();
            // Enlever l'emoji s'il est présent (souvent au début)
            text = text.replace(/^[^\w\s]+/, '').trim();
            input.value = text;
            sendChatMessage();
        });
    });

    // Page Diagnostics : brancher les boutons vers les endpoints Flask.
    // Les IDs existent dans templates/diagnostic.html.
    const btnSystem = document.getElementById('btn-system');
    if (btnSystem) {
        btnSystem.addEventListener('click', runSystemDiagnostic);
    }
    const btnNetwork = document.getElementById('btn-network');
    if (btnNetwork) {
        btnNetwork.addEventListener('click', runNetworkDiagnostic);
    }

    // Gestion du formulaire d'ajout rapide (si présent)
    const quickForm = document.getElementById('quick-knowledge-form');
    if (quickForm) {
        quickForm.addEventListener('submit', quickAddKnowledge);
    }
});

/**
 * Envoie un message au chatbot via AJAX
 */
function sendChatMessage() {
    const input = document.getElementById('chat-input');
    if (!input) return;
    const message = input.value.trim();
    if (message === '') return;

    // Afficher le message de l'utilisateur
    addChatMessage('Vous', message, 'user');
    input.value = '';

    // Appel à l'API
    fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: message })
    })
    .then(response => response.json())
    .then(data => {
        addChatMessage('Assistant', data.response, 'bot');
        // Ticket auto-créé (ou déjà existant) côté serveur quand le chatbot ne trouve pas de réponse.
        if (data.action === 'ticket_created' || data.action === 'ticket_existing') {
            const ticketId = data.details && data.details.ticket_id ? data.details.ticket_id : null;
            if (ticketId) {
                addChatButton('Voir le ticket', function() {
                    window.location.href = '/tickets/' + ticketId;
                });
            }
        } else if (data.action === 'ask_ticket') {
            // Fallback si l'auto-création est désactivée/casse : garder l'ancien comportement.
            addChatButton('Créer un ticket', function() {
                window.location.href = '/tickets/new?description=' + encodeURIComponent(message);
            });
        }
        // Autres actions possibles (ex: knowledge_found)
    })
    .catch(error => {
        console.error('Erreur chat:', error);
        addChatMessage('Assistant', 'Désolé, une erreur est survenue.', 'bot');
    });
}

/**
 * Ajoute un message dans la zone de chat
 */
function addChatMessage(sender, text, type) {
    const chat = document.getElementById('chat-messages');
    if (!chat) return;
    const div = document.createElement('div');
    div.className = 'message ' + type;
    // Remplacer les retours à la ligne par des <br>
    div.innerHTML = '<strong>' + sender + ' :</strong> ' + text.replace(/\n/g, '<br>');
    chat.appendChild(div);
    chat.scrollTop = chat.scrollHeight; // Défiler vers le bas
}

/**
 * Ajoute un bouton dans le chat
 */
function addChatButton(text, callback) {
    const chat = document.getElementById('chat-messages');
    if (!chat) return;
    const btn = document.createElement('button');
    btn.className = 'btn btn-sm btn-success mt-2';
    btn.textContent = text;
    btn.onclick = callback;
    chat.appendChild(btn);
    chat.scrollTop = chat.scrollHeight;
}

/**
 * Ajout rapide à la base de connaissances (AJAX)
 */
function quickAddKnowledge(e) {
    e.preventDefault();
    const problem = document.getElementById('quick-problem').value.trim();
    const solution = document.getElementById('quick-solution').value.trim();
    const keywords = document.getElementById('quick-keywords').value.trim();
    const category = document.getElementById('quick-category').value;
    const feedback = document.getElementById('quick-feedback');

    if (!problem || !solution) {
        if (feedback) {
            feedback.innerHTML = '<div class="alert alert-danger">Le problème et la solution sont requis.</div>';
        }
        return;
    }

    fetch('/knowledge/quick_add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ problem, solution, keywords, category })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            if (feedback) {
                feedback.innerHTML = '<div class="alert alert-success">Entrée ajoutée avec succès !</div>';
            }
            // Réinitialiser le formulaire
            document.getElementById('quick-problem').value = '';
            document.getElementById('quick-solution').value = '';
            document.getElementById('quick-keywords').value = '';
            // Optionnel : recharger la page après un délai
            setTimeout(() => { window.location.reload(); }, 1500);
        } else {
            if (feedback) {
                feedback.innerHTML = '<div class="alert alert-danger">Erreur : ' + data.message + '</div>';
            }
        }
    })
    .catch(error => {
        if (feedback) {
            feedback.innerHTML = '<div class="alert alert-danger">Erreur de communication.</div>';
        }
    });
}

/**
 * Convertit des octets en chaîne lisible (o, Ko, Mo, Go...).
 * Utilisé pour rendre le diagnostic système plus compréhensible.
 */
function formatBytes(bytes) {
    if (typeof bytes !== 'number' || !Number.isFinite(bytes)) return 'N/A';
    const units = ['o', 'Ko', 'Mo', 'Go', 'To', 'Po'];
    let value = bytes;
    let unitIndex = 0;
    while (value >= 1024 && unitIndex < units.length - 1) {
        value /= 1024;
        unitIndex += 1;
    }
    return value.toFixed(2) + ' ' + units[unitIndex];
}

/**
 * Appelle /diagnostic/system et affiche les résultats dans #system-result.
 * Les résultats viennent de it_assistant/utils/diagnostics.py.
 */
function runSystemDiagnostic() {
    const output = document.getElementById('system-result');
    if (!output) return;

    output.innerHTML = '<div class="text-muted">Chargement du diagnostic système...</div>';

    fetch('/diagnostic/system')
        .then(response => response.json())
        .then(diag => {
            const cpu = `${diag.cpu_percent}% (${diag.cpu_count} cœurs)`;
            const mem = `${diag.memory_percent}% (${formatBytes(diag.memory_available)} libres / ${formatBytes(diag.memory_total)})`;
            const disk = `${diag.disk_percent}% (${formatBytes(diag.disk_free)} libres / ${formatBytes(diag.disk_total)})`;

            output.innerHTML =
                '<ul class="mb-0">' +
                `<li><strong>CPU :</strong> ${cpu}</li>` +
                `<li><strong>Mémoire :</strong> ${mem}</li>` +
                `<li><strong>Disque :</strong> ${disk}</li>` +
                `<li><strong>Plateforme :</strong> ${diag.platform} (${diag.platform_version})</li>` +
                `<li><strong>Hôte :</strong> ${diag.hostname}</li>` +
                '</ul>';
        })
        .catch(error => {
            console.error('Erreur diagnostic système:', error);
            output.innerHTML = '<div class="alert alert-danger mb-0">Impossible de récupérer le diagnostic système.</div>';
        });
}

/**
 * Appelle /diagnostic/network et affiche les résultats dans #network-result.
 * Le port est optionnel ; si fourni, le backend teste l'ouverture TCP.
 */
function runNetworkDiagnostic() {
    const output = document.getElementById('network-result');
    if (!output) return;

    const hostInput = document.getElementById('network-host');
    const portInput = document.getElementById('network-port');

    const host = (hostInput ? hostInput.value : '').trim() || '8.8.8.8';
    const port = (portInput ? portInput.value : '').trim();

    const params = new URLSearchParams({ host });
    if (port !== '') params.set('port', port);

    output.innerHTML = '<div class="text-muted">Chargement du diagnostic réseau...</div>';

    fetch('/diagnostic/network?' + params.toString())
        .then(response => response.json())
        .then(diag => {
            output.innerHTML =
                '<ul class="mb-0">' +
                `<li><strong>Hôte :</strong> ${host}</li>` +
                `<li><strong>Ping :</strong> ${diag.ping}</li>` +
                (diag.port ? `<li><strong>Port :</strong> ${diag.port}</li>` : '') +
                '</ul>';
        })
        .catch(error => {
            console.error('Erreur diagnostic réseau:', error);
            output.innerHTML = '<div class="alert alert-danger mb-0">Impossible de récupérer le diagnostic réseau.</div>';
        });
}

/**
 * Fonction utilitaire pour formater les dates (si nécessaire)
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('fr-FR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}
