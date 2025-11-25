// Configuration du graphique
const ctx = document.getElementById('myChart').getContext('2d');

const chart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: [],
        datasets: [
            {
                label: 'Température (°C)',
                data: [],
                borderColor: '#4fc3f7',
                backgroundColor: 'rgba(79, 195, 247, 0.1)',
                borderWidth: 3,
                tension: 0.4,
                fill: true,
                pointRadius: 4,
                pointHoverRadius: 6
            },
            {
                label: 'Humidité (%)',
                data: [],
                borderColor: '#7b68ee',
                backgroundColor: 'rgba(123, 104, 238, 0.1)',
                borderWidth: 3,
                tension: 0.4,
                fill: true,
                pointRadius: 4,
                pointHoverRadius: 6
            }
        ]
    },
    options: {
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
            legend: {
                labels: {
                    color: '#e0e0e0',
                    font: {
                        size: 14,
                        weight: '600'
                    }
                }
            },
            tooltip: {
                backgroundColor: 'rgba(26, 26, 38, 0.9)',
                titleColor: '#fff',
                bodyColor: '#e0e0e0',
                borderColor: '#4fc3f7',
                borderWidth: 1
            }
        },
        scales: {
            x: {
                ticks: {
                    color: '#9e9eb0'
                },
                grid: {
                    color: 'rgba(255, 255, 255, 0.05)'
                }
            },
            y: {
                ticks: {
                    color: '#9e9eb0'
                },
                grid: {
                    color: 'rgba(255, 255, 255, 0.08)'
                }
            }
        }
    }
});

// Fonction pour ajouter des données au graphique
function addDataToChart(temp, hum) {
    const now = new Date().toLocaleTimeString('fr-FR');

    chart.data.labels.push(now);
    chart.data.datasets[0].data.push(temp);
    chart.data.datasets[1].data.push(hum);

    // Limite à 20 points pour la performance
    if (chart.data.labels.length > 20) {
        chart.data.labels.shift();
        chart.data.datasets[0].data.shift();
        chart.data.datasets[1].data.shift();
    }

    chart.update();
}

// Fonction pour mettre à jour l'heure en direct
function updateLiveTime() {
    const now = new Date();
    const timeStr = now.toLocaleTimeString('fr-FR');
    const timeElement = document.getElementById('live-time');
    if (timeElement) {
        timeElement.textContent = timeStr;
    }
}

// Fonction pour mettre à jour les valeurs depuis l'API
async function updateValues() {
    try {
        const response = await fetch('/latest/');
        const data = await response.json();

        const temp = parseFloat(data.temperature);
        const hum = parseFloat(data.humidity);

        // Mise à jour des valeurs en direct
        document.getElementById('current-temp').textContent = temp.toFixed(1);
        document.getElementById('current-hum').textContent = hum.toFixed(1);

        // Mise à jour des cartes principales
        document.getElementById('temp-value').textContent = temp.toFixed(1);
        document.getElementById('hum-value').textContent = hum.toFixed(1);

        const now = new Date().toLocaleString('fr-FR');
        document.getElementById('temp-time').textContent = `Dernière mise à jour: ${now}`;
        document.getElementById('hum-time').textContent = `Dernière mise à jour: ${now}`;

        // Mise à jour du graphique
        addDataToChart(temp, hum);

        // Retirer l'effet de chargement
        document.querySelectorAll('.loading').forEach(el => el.classList.remove('loading'));

        // Mise à jour du statut
        document.getElementById('status').textContent = '● Connecté - Système opérationnel';
        const statusIndicator = document.getElementById('status-indicator');
        if (statusIndicator) {
            statusIndicator.textContent = '🟢';
        }

    } catch (error) {
        console.error('Erreur lors de la récupération des données:', error);
        document.getElementById('status').textContent = '● Erreur de connexion';
        const statusIndicator = document.getElementById('status-indicator');
        if (statusIndicator) {
            statusIndicator.textContent = '🔴';
        }
    }
}

// Fonction pour récupérer les statistiques globales
async function updateStatistics() {
    try {
        const response = await fetch('/api/');
        const result = await response.json();
        const allData = result.data;

        if (allData && allData.length > 0) {
            const temperatures = allData.map(d => parseFloat(d.temp));
            const humidities = allData.map(d => parseFloat(d.hum));

            // Calcul des statistiques
            const maxTemp = Math.max(...temperatures);
            const minTemp = Math.min(...temperatures);
            const avgTemp = temperatures.reduce((a, b) => a + b, 0) / temperatures.length;

            const maxHum = Math.max(...humidities);
            const minHum = Math.min(...humidities);
            const avgHum = humidities.reduce((a, b) => a + b, 0) / humidities.length;

            // Mise à jour de l'interface
            document.getElementById('total-records').textContent = allData.length;
            document.getElementById('max-temp').textContent = maxTemp.toFixed(1) + '°C';
            document.getElementById('min-temp').textContent = minTemp.toFixed(1) + '°C';
            document.getElementById('avg-temp').textContent = avgTemp.toFixed(1) + '°C';
            document.getElementById('max-hum').textContent = maxHum.toFixed(1) + '%';
            document.getElementById('min-hum').textContent = minHum.toFixed(1) + '%';
            document.getElementById('avg-hum').textContent = avgHum.toFixed(1) + '%';

            // Retirer l'effet de chargement
            document.querySelectorAll('.loading').forEach(el => el.classList.remove('loading'));
        }
    } catch (error) {
        console.error('Erreur lors de la récupération des statistiques:', error);
        document.getElementById('total-records').textContent = '0';
    }
}

// Fonction pour mettre à jour les données en direct
async function updateLiveData() {
    try {
        const response = await fetch('/latest/');
        const data = await response.json();

        document.getElementById('current-temp').textContent = data.temperature.toFixed(1);
        document.getElementById('current-hum').textContent = data.humidity.toFixed(1);

        const updateTime = new Date(data.timestamp);
        const lastUpdateElement = document.getElementById('last-update');
        if (lastUpdateElement) {
            lastUpdateElement.textContent = 'Dernière mise à jour: ' + updateTime.toLocaleString('fr-FR');
        }

        const statusIndicator = document.getElementById('status-indicator');
        if (statusIndicator) {
            statusIndicator.textContent = '🟢';
        }
    } catch (error) {
        const lastUpdateElement = document.getElementById('last-update');
        if (lastUpdateElement) {
            lastUpdateElement.textContent = 'En attente de données...';
        }
        const statusIndicator = document.getElementById('status-indicator');
        if (statusIndicator) {
            statusIndicator.textContent = '🟠';
        }
    }
}

// Fonction pour mettre à jour l'horloge
function updateClock() {
    const now = new Date();
    const liveTimeElement = document.getElementById('live-time');
    if (liveTimeElement) {
        liveTimeElement.textContent = now.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' });
    }
}

// Initialisation au chargement de la page
document.addEventListener('DOMContentLoaded', function() {
    console.log('Dashboard initialisé');

    // Première mise à jour
    updateLiveTime();
    updateValues();
    updateStatistics();
    updateLiveData();
    updateClock();

    // Mises à jour automatiques
    setInterval(updateLiveTime, 1000);
    setInterval(updateClock, 1000);
    setInterval(updateValues, 5000);
    setInterval(updateStatistics, 30000);
    setInterval(updateLiveData, 5000);
});
