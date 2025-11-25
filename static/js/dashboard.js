// Fonction pour mettre à jour l'heure
function updateLiveTime() {
    const now = new Date();
    document.getElementById('live-time').textContent = now.toLocaleTimeString('fr-FR');
}

// Fonction pour charger les dernières données
async function loadLatest() {
    try {
        const res = await fetch("/latest/");
        const data = await res.json();

        document.getElementById("tempValue").textContent = data.temperature + " °C";
        document.getElementById("humValue").textContent = data.humidity + " %";

        const date = new Date(data.timestamp);
        const diffMs = Date.now() - date;
        const diffSec = Math.round(diffMs / 1000);
        const days = Math.floor(diffSec / 86400);
        const hours = Math.floor((diffSec % 86400) / 3600);
        const minutes = Math.floor((diffSec % 3600) / 60);
        const seconds = diffSec % 60;

        let timeText = "il y a : ";
        if (days > 0) timeText += days + "j ";
        if (hours > 0) timeText += hours + "h ";
        if (minutes > 0) timeText += minutes + "min ";
        timeText += seconds + "s (" + date.toLocaleTimeString() + ")";

        document.getElementById("tempTime").textContent = timeText;
        document.getElementById("humTime").textContent = timeText;

        // Mise à jour du statut
        document.getElementById("status").textContent = "● Connecté - Système opérationnel";
        document.getElementById("status").className = "status-online";
        document.getElementById("status-indicator").textContent = "🟢";
    } catch (e) {
        console.log("Erreur API :", e);
        document.getElementById("status").textContent = "● En attente de données...";
        document.getElementById("status").className = "status-offline";
        document.getElementById("status-indicator").textContent = "🟡";
    }
}

// Fonction pour charger les données du graphique
async function loadChartData(period) {
    // Mettre à jour les boutons actifs
    document.querySelectorAll('.btn').forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');

    // Définir l'URL selon la période
    let url = '/chart-data/';
    if (period === 'jour') url = '/chart-data-jour/';
    if (period === 'semaine') url = '/chart-data-semaine/';
    if (period === 'mois') url = '/chart-data-mois/';

    try {
        const response = await fetch(url);
        const data = await response.json();
        console.log('Données chargées:', data);
    } catch (error) {
        console.error('Erreur:', error);
    }
}

// Fonction pour charger les statistiques
async function updateStatistics() {
    try {
        const response = await fetch('/api/');
        const result = await response.json();
        const allData = result.data;

        if (allData && allData.length > 0) {
            const temperatures = allData.map(d => parseFloat(d.temp));
            const humidities = allData.map(d => parseFloat(d.hum));

            const avgTemp = temperatures.reduce((a, b) => a + b, 0) / temperatures.length;
            const avgHum = humidities.reduce((a, b) => a + b, 0) / humidities.length;

            document.getElementById('total-records').textContent = allData.length;
            document.getElementById('avg-temp').textContent = avgTemp.toFixed(1) + '°C';
            document.getElementById('avg-hum').textContent = avgHum.toFixed(1) + '%';
        }
    } catch (error) {
        console.error('Erreur statistiques:', error);
    }
}

// Gestion des incidents
async function updateIncidentStatus() {
    try {
        const response = await fetch('/incident-status/');
        const data = await response.json();

        const statusDiv = document.getElementById('incident-status');
        const detailsDiv = document.getElementById('incident-details');
        const compteurSpan = document.getElementById('incident-compteur');

        if (data.incident_actif) {
            statusDiv.className = 'incident-status-alert';
            statusDiv.innerHTML = '⚠️ INCIDENT EN COURS';
            detailsDiv.className = 'incident-details-visible';
            compteurSpan.textContent = data.compteur;

            // Afficher opérations selon compteur
            const op1 = document.getElementById('op1-container');
            const op2 = document.getElementById('op2-container');
            const op3 = document.getElementById('op3-container');

            op1.className = data.compteur >= 1 ? 'operation-container op1-container op1-visible' : 'operation-container op1-container op1-hidden';
            op2.className = data.compteur >= 4 ? 'operation-container op2-container op2-visible' : 'operation-container op2-container op2-hidden';
            op3.className = data.compteur >= 7 ? 'operation-container op3-container op3-visible' : 'operation-container op3-container op3-hidden';

            // Charger états sauvegardés
            document.getElementById('op1-check').checked = data.op1_checked;
            document.getElementById('op1-comment').value = data.op1_comment || '';
            document.getElementById('op2-check').checked = data.op2_checked;
            document.getElementById('op2-comment').value = data.op2_comment || '';
            document.getElementById('op3-check').checked = data.op3_checked;
            document.getElementById('op3-comment').value = data.op3_comment || '';
        } else {
            statusDiv.className = 'incident-status-ok';
            statusDiv.innerHTML = '✅ Pas d\'incidents';
            detailsDiv.className = 'incident-details-hidden';
        }
    } catch (error) {
        console.error('Erreur mise à jour incidents:', error);
    }
}

async function saveIncident() {
    try {
        const data = {
            op1_checked: document.getElementById('op1-check').checked,
            op1_comment: document.getElementById('op1-comment').value,
            op2_checked: document.getElementById('op2-check').checked,
            op2_comment: document.getElementById('op2-comment').value,
            op3_checked: document.getElementById('op3-check').checked,
            op3_comment: document.getElementById('op3-comment').value,
        };

        const response = await fetch('/update-incident/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(data)
        });

        if (response.ok) {
            alert('✅ Opérations enregistrées avec succès!');
        } else {
            alert('❌ Erreur lors de l\'enregistrement');
        }
    } catch (error) {
        console.error('Erreur sauvegarde incident:', error);
        alert('❌ Erreur de connexion');
    }
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

// Initialisation
updateLiveTime();
loadLatest();
updateStatistics();
updateIncidentStatus();

// Mises à jour automatiques
setInterval(updateLiveTime, 1000);
setInterval(loadLatest, 5000);
setInterval(updateStatistics, 30000);
setInterval(updateIncidentStatus, 5000);