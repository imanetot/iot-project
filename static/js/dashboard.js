// URLs API
const API_URL = '/latest/';
const API_POST_URL = '/api/post/';
const INCIDENT_STATUS_URL = '/incident-status/';
const UPDATE_INCIDENT_URL = '/update-incident/';

// ==================== DARK MODE FUNCTIONALITY ====================
function toggleTheme() {
    const body = document.body;
    const themeBtn = document.getElementById('theme-toggle');

    body.classList.toggle('light-mode');

    if (body.classList.contains('light-mode')) {
        themeBtn.textContent = '🌙 Mode Sombre';
        localStorage.setItem('theme', 'light');
    } else {
        themeBtn.textContent = '☀️ Mode Clair';
        localStorage.setItem('theme', 'dark');
    }
}

// Load saved theme on page load
document.addEventListener('DOMContentLoaded', function() {
    const savedTheme = localStorage.getItem('theme');
    const themeBtn = document.getElementById('theme-toggle');

    if (savedTheme === 'light') {
        document.body.classList.add('light-mode');
        themeBtn.textContent = '🌙 Mode Sombre';
    } else {
        themeBtn.textContent = '☀️ Mode Clair';
    }
});

// ==================== MANUAL DATA SUBMISSION ====================
async function submitManualData() {
    const tempInput = document.getElementById('manual-temp');
    const humInput = document.getElementById('manual-hum');
    const btn = document.querySelector('.btn-submit-manual');

    const temp = parseFloat(tempInput.value);
    const hum = parseFloat(humInput.value);

    // Validation
    if (isNaN(temp) || isNaN(hum)) {
        showNotification('⚠️ Veuillez entrer des valeurs valides', 'warning');
        return;
    }

    if (hum < 0 || hum > 100) {
        showNotification('⚠️ L\'humidité doit être entre 0 et 100%', 'warning');
        return;
    }

    // Disable button during submission
    const originalText = btn.textContent;
    btn.disabled = true;
    btn.textContent = '⏳ Envoi...';

    try {
        const response = await fetch(API_POST_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                temp: temp,
                hum: hum
            })
        });

        if (response.ok) {
            showNotification('✅ Données enregistrées', 'success');
            tempInput.value = '';
            humInput.value = '';

            // Refresh data
            await getData();
            await getIncidentStatus();
        } else {
            showNotification('❌ Erreur d\'enregistrement', 'error');
        }
    } catch (error) {
        console.error('Erreur:', error);
        showNotification('❌ Erreur de connexion', 'error');
    } finally {
        btn.disabled = false;
        btn.textContent = originalText;
    }
}

// ==================== INCIDENT STATUS ====================
async function getIncidentStatus() {
    try {
        const res = await fetch(INCIDENT_STATUS_URL);
        const data = await res.json();

        const statusEl = document.getElementById('incident-status');
        const detailsEl = document.getElementById('incident-details');
        const compteurEl = document.getElementById('incident-compteur');
        const dateDebutEl = document.getElementById('incident-date-debut');

        if (data.incident_actif) {
            // Incident détecté - afficher en rouge
            statusEl.textContent = '⚠️ Incident détecté!';
            statusEl.className = 'incident-status-alert';
            detailsEl.classList.remove('incident-details-hidden');
            compteurEl.textContent = data.compteur;

            // Afficher la date de début
            const dateDebut = new Date(data.date_debut);
            dateDebutEl.textContent = dateDebut.toLocaleString('fr-FR');

            // Charger les états des opérations SANS RÉINITIALISER
            const op1Check = document.getElementById('op1-check');
            const op2Check = document.getElementById('op2-check');
            const op3Check = document.getElementById('op3-check');

            // Ne mettre à jour que si la valeur a changé pour éviter de réinitialiser l'input utilisateur
            if (op1Check.checked !== data.op1_checked) {
                op1Check.checked = data.op1_checked || false;
            }
            if (op2Check.checked !== data.op2_checked) {
                op2Check.checked = data.op2_checked || false;
            }
            if (op3Check.checked !== data.op3_checked) {
                op3Check.checked = data.op3_checked || false;
            }

            // Charger les commentaires seulement s'ils sont vides
            const op1Comment = document.getElementById('op1-comment');
            const op2Comment = document.getElementById('op2-comment');
            const op3Comment = document.getElementById('op3-comment');

            if (!op1Comment.value && data.op1_comment) {
                op1Comment.value = data.op1_comment;
            }
            if (!op2Comment.value && data.op2_comment) {
                op2Comment.value = data.op2_comment;
            }
            if (!op3Comment.value && data.op3_comment) {
                op3Comment.value = data.op3_comment;
            }

            // Afficher les opérations selon le compteur
            const op1Container = document.getElementById('op1-container');
            const op2Container = document.getElementById('op2-container');
            const op3Container = document.getElementById('op3-container');

            // Opération 1: compteur >= 1
            if (data.compteur >= 1) {
                op1Container.classList.remove('op1-hidden');
            } else {
                op1Container.classList.add('op1-hidden');
            }

            // Opération 2: compteur >= 4
            if (data.compteur >= 4) {
                op2Container.classList.remove('op2-hidden');
            } else {
                op2Container.classList.add('op2-hidden');
            }

            // Opération 3: compteur >= 7
            if (data.compteur >= 7) {
                op3Container.classList.remove('op3-hidden');
            } else {
                op3Container.classList.add('op3-hidden');
            }
        } else {
            // Pas d'incident - afficher en vert
            statusEl.textContent = '✅ Pas d\'incidents';
            statusEl.className = 'incident-status-ok';
            detailsEl.classList.add('incident-details-hidden');
            compteurEl.textContent = '0';

            // Masquer toutes les opérations
            document.getElementById('op1-container').classList.add('op1-hidden');
            document.getElementById('op2-container').classList.add('op2-hidden');
            document.getElementById('op3-container').classList.add('op3-hidden');
        }
    } catch (e) {
        console.error('Erreur lors de la récupération du statut d\'incident:', e);
    }
}

// ==================== SAVE OPERATION (COMMENTAIRES OPTIONNELS) ====================
async function saveOperation(opNumber) {
    const checkId = `op${opNumber}-check`;
    const commentId = `op${opNumber}-comment`;
    const btnId = `op${opNumber}-btn`;

    const isChecked = document.getElementById(checkId).checked;
    const comment = document.getElementById(commentId).value.trim();

    // PAS DE VALIDATION - commentaires optionnels
    const btn = document.getElementById(btnId);
    const originalText = btn.textContent;
    btn.disabled = true;
    btn.textContent = '⏳ Enregistrement...';

    try {
        const payload = {
            [`op${opNumber}_checked`]: isChecked,
            [`op${opNumber}_comment`]: comment
        };

        const response = await fetch(UPDATE_INCIDENT_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (data.success) {
            showNotification(`✅ Opération ${opNumber} enregistrée`, 'success');
            // Ne pas recharger pour éviter de perdre les inputs
        } else {
            showNotification('❌ Erreur: ' + (data.error || 'Erreur inconnue'), 'error');
        }
    } catch (e) {
        showNotification('❌ Erreur de sauvegarde', 'error');
    } finally {
        btn.disabled = false;
        btn.textContent = originalText;
    }
}

// ==================== UTILITY FUNCTIONS ====================
function getTimeAgo(date) {
    const now = new Date();
    const diffMs = now - date;
    const diffSec = Math.floor(diffMs / 1000);
    const diffMin = Math.floor(diffSec / 60);
    const diffHour = Math.floor(diffMin / 60);

    const hours = diffHour;
    const minutes = diffMin % 60;
    const seconds = diffSec % 60;

    let result = 'il y a ';
    if (hours > 0) {
        result += hours + ' heure' + (hours > 1 ? 's' : '') + ' ';
    }
    if (minutes > 0) {
        result += minutes + ' minute' + (minutes > 1 ? 's' : '') + ' ';
    }
    if (seconds > 0 || (hours === 0 && minutes === 0)) {
        result += seconds + ' seconde' + (seconds > 1 ? 's' : '');
    }
    return result.trim();
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// ==================== FETCH LATEST DATA ====================
async function getData() {
    try {
        const res = await fetch(API_URL);
        const data = await res.json();

        document.getElementById('current-temp').textContent = data.temperature.toFixed(1) + '°C';
        document.getElementById('current-hum').textContent = data.humidity.toFixed(1) + '%';

        const timeAgo = getTimeAgo(new Date(data.timestamp));
        document.getElementById('last-update').textContent = 'Mis à jour ' + timeAgo;
        document.getElementById('last-update-hum').textContent = 'Mis à jour ' + timeAgo;

        document.getElementById('status').className = 'stat-value status-online';
        document.getElementById('status').textContent = '● En ligne';

        // Check for incidents based on current temperature
        await checkForIncidents(data.temperature);
    } catch (e) {
        console.error('Erreur getData:', e);
        document.getElementById('status').className = 'stat-value status-offline';
        document.getElementById('status').textContent = '● Hors ligne';
    }
}

// ==================== CHECK FOR INCIDENTS ====================
async function checkForIncidents(temperature) {
    try {
        const res = await fetch('/api/check-create-incident/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ temperature: temperature })
        });

        const data = await res.json();
        if (data.success) {
            console.log('Incident check:', data.message);
            // Refresh incident status after checking
            await getIncidentStatus();
        }
    } catch (e) {
        console.error('Erreur checkForIncidents:', e);
    }
}

// ==================== FETCH STATISTICS ====================
async function getStats() {
    try {
        const res = await fetch('/api/');
        const result = await res.json();
        const data = result.data;

        document.getElementById('total-records').textContent = data.length;

        if (data.length > 0) {
            const temps = data.map(d => d.temp);
            const hums = data.map(d => d.hum);

            const avgTemp = (temps.reduce((a, b) => a + b, 0) / temps.length).toFixed(1);
            const avgHum = (hums.reduce((a, b) => a + b, 0) / hums.length).toFixed(1);

            document.getElementById('avg-temp').textContent = avgTemp + '°C';
            document.getElementById('avg-hum').textContent = avgHum + '%';
        }
    } catch (e) {
        console.error('Erreur stats:', e);
    }
}

// ==================== INITIALIZATION ====================
getData();
getStats();
getIncidentStatus();

// Auto-refresh (réduit pour éviter de perdre les inputs)
setInterval(getData, 10000); // Every 10 seconds
setInterval(getStats, 30000); // Every 30 seconds
setInterval(getIncidentStatus, 10000); // Every 10 seconds (augmenté de 5s à 10s)

// ==================== NOTIFICATION SYSTEM ====================
function showNotification(message, type = 'info') {
    // Remove existing notification if any
    const existing = document.querySelector('.toast-notification');
    if (existing) {
        existing.remove();
    }

    // Create notification element
    const notification = document.createElement('div');
    notification.className = `toast-notification toast-${type}`;
    notification.textContent = message;

    // Add to body
    document.body.appendChild(notification);

    // Trigger animation
    setTimeout(() => {
        notification.classList.add('show');
    }, 10);

    // Auto remove after 3 seconds
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 3000);
}