// URLs API
const API_URL = '/latest/';
const INCIDENT_STATUS_URL = '/incident-status/';
const UPDATE_INCIDENT_URL = '/update-incident/';
const MANUAL_ENTRY_URL = '/api/manual-entry/';

// Theme toggle
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

// Load saved theme
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

// Manual data entry
async function submitManualData() {
    const tempInput = document.getElementById('manual-temp');
    const humInput = document.getElementById('manual-hum');
    const messageEl = document.getElementById('manual-entry-message');

    const temperature = parseFloat(tempInput.value);
    const humidity = parseFloat(humInput.value);

    // Validation
    if (isNaN(temperature) || isNaN(humidity)) {
        messageEl.textContent = '⚠️ Veuillez entrer des valeurs valides';
        messageEl.className = 'manual-entry-message error';
        messageEl.style.display = 'block';
        return;
    }

    if (humidity < 0 || humidity > 100) {
        messageEl.textContent = '⚠️ L\'humidité doit être entre 0 et 100%';
        messageEl.className = 'manual-entry-message error';
        messageEl.style.display = 'block';
        return;
    }

    try {
        const response = await fetch(MANUAL_ENTRY_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                temperature: temperature,
                humidity: humidity
            })
        });

        const data = await response.json();

        if (data.success) {
            messageEl.textContent = '✅ Données enregistrées avec succès!';
            messageEl.className = 'manual-entry-message success';
            messageEl.style.display = 'block';

            // Clear inputs
            tempInput.value = '';
            humInput.value = '';

            // Refresh data immediately
            await getData();
            await getIncidentStatus();

            // Hide message after 3 seconds
            setTimeout(() => {
                messageEl.style.display = 'none';
            }, 3000);
        } else {
            messageEl.textContent = '❌ Erreur: ' + data.error;
            messageEl.className = 'manual-entry-message error';
            messageEl.style.display = 'block';
        }
    } catch (error) {
        messageEl.textContent = '❌ Erreur de connexion';
        messageEl.className = 'manual-entry-message error';
        messageEl.style.display = 'block';
        console.error('Error:', error);
    }
}

// Récupérer et afficher le statut de l'incident
async function getIncidentStatus() {
    try {
        const res = await fetch(INCIDENT_STATUS_URL);
        const data = await res.json();

        const statusEl = document.getElementById('incident-status');
        const detailsEl = document.getElementById('incident-details');
        const compteurEl = document.getElementById('incident-compteur');
        const dateDebutEl = document.getElementById('incident-date-debut');

        if (data.incident_actif) {
            // Incident actif - afficher en rouge
            statusEl.textContent = '⚠️ Incident détecté!';
            statusEl.className = 'incident-status-alert';
            detailsEl.classList.remove('incident-details-hidden');
            compteurEl.textContent = data.compteur;

            // Afficher la date de début
            const dateDebut = new Date(data.date_debut);
            dateDebutEl.textContent = dateDebut.toLocaleString('fr-FR');

            // Charger les états des opérations et leurs noms
            document.getElementById('op1-check').checked = data.op1_checked;
            document.getElementById('op1-comment').value = data.op1_comment || '';
            document.getElementById('op1-label').textContent = '✓ ' + (data.nom_op1 || 'Opération Corrective 1');

            document.getElementById('op2-check').checked = data.op2_checked;
            document.getElementById('op2-comment').value = data.op2_comment || '';
            document.getElementById('op2-label').textContent = '✓ ' + (data.nom_op2 || 'Opération Corrective 2');

            document.getElementById('op3-check').checked = data.op3_checked;
            document.getElementById('op3-comment').value = data.op3_comment || '';
            document.getElementById('op3-label').textContent = '✓ ' + (data.nom_op3 || 'Opération Corrective 3');

            // Afficher les opérations selon le compteur
            const op1Container = document.getElementById('op1-container');
            const op2Container = document.getElementById('op2-container');
            const op3Container = document.getElementById('op3-container');

            if (data.compteur >= 1) {
                op1Container.classList.remove('op1-hidden');
            } else {
                op1Container.classList.add('op1-hidden');
            }

            if (data.compteur >= 4) {
                op2Container.classList.remove('op2-hidden');
            } else {
                op2Container.classList.add('op2-hidden');
            }

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

// Sauvegarder une opération spécifique
async function saveOperation(opNumber) {
    const checkId = `op${opNumber}-check`;
    const commentId = `op${opNumber}-comment`;
    const btnId = `op${opNumber}-btn`;

    const isChecked = document.getElementById(checkId).checked;
    const comment = document.getElementById(commentId).value.trim();

    // Validation: checkbox doit être cochée (obligatoire)
    if (!isChecked) {
        alert('⚠️ Veuillez cocher la case avant de valider l\'opération!');
        return;
    }

    // Désactiver le bouton pendant la sauvegarde
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
            alert(`✅ Opération ${opNumber} enregistrée avec succès!`);
            // Rafraîchir le statut après sauvegarde
            await getIncidentStatus();
        } else {
            alert('❌ Erreur: ' + (data.error || 'Erreur inconnue'));
        }
    } catch (e) {
        alert('❌ Erreur lors de la sauvegarde: ' + e.message);
    } finally {
        // Réactiver le bouton
        btn.disabled = false;
        btn.textContent = originalText;
    }
}

// Get CSRF token from cookies
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

// Fetch latest data
async function getData() {
    try {
        const res = await fetch(API_URL);
        const data = await res.json();

        document.getElementById('current-temp').textContent = data.temperature.toFixed(1) + '°C';
        document.getElementById('current-hum').textContent = data.humidity.toFixed(1) + '%';
        document.getElementById('last-update').textContent = new Date(data.timestamp).toLocaleString('fr-FR');
        document.getElementById('hum-time').textContent = new Date(data.timestamp).toLocaleString('fr-FR');

        // Update status
        const statusEl = document.getElementById('status');
        statusEl.textContent = '● En ligne';
        statusEl.className = 'status-online';
    } catch (e) {
        console.error('Erreur getData:', e);
        const statusEl = document.getElementById('status');
        statusEl.textContent = '● Hors ligne';
        statusEl.className = 'status-offline';
    }
}

// Fetch all data for stats
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

// Initialisation au chargement de la page
getData();
getStats();
getIncidentStatus();

// Auto-refresh
setInterval(getData, 10000); // Every 10 seconds
setInterval(getStats, 30000); // Every 30 seconds
setInterval(getIncidentStatus, 5000); // Every 5 seconds