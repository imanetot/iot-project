// Variables globales
let chart = null;
let currentPeriod = 'all';

// Fonction pour obtenir l'URL selon la période
function getApiUrl(period) {
    const urls = {
        'all': '/chart-data/',
        'jour': '/chart-data-jour/',
        'semaine': '/chart-data-semaine/',
        'mois': '/chart-data-mois/'
    };
    return urls[period] || urls['all'];
}

// Fonction pour calculer les statistiques
function calculateStats(humidity) {
    if (humidity.length === 0) return null;

    const current = humidity[humidity.length - 1];
    const sum = humidity.reduce((a, b) => a + b, 0);
    const avg = sum / humidity.length;
    const min = Math.min(...humidity);
    const max = Math.max(...humidity);

    return { current, avg, min, max };
}

// Fonction pour mettre à jour les statistiques
function updateStats(stats) {
    if (!stats) return;

    document.getElementById('current-hum').textContent = `${stats.current.toFixed(1)}%`;
    document.getElementById('avg-hum').textContent = `${stats.avg.toFixed(1)}%`;
    document.getElementById('min-hum').textContent = `${stats.min.toFixed(1)}%`;
    document.getElementById('max-hum').textContent = `${stats.max.toFixed(1)}%`;
}

// Fonction pour créer/mettre à jour le graphique
function createChart(data) {
    const ctx = document.getElementById('humChart').getContext('2d');

    // Formater les labels de date
    const labels = data.temps.map(t => {
        const date = new Date(t);
        return date.toLocaleDateString('fr-FR', {
            day: '2-digit',
            month: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        });
    });

    // Détruire l'ancien graphique s'il existe
    if (chart) {
        chart.destroy();
    }

    // Créer le nouveau graphique
    chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Humidité (%)',
                data: data.humidity,
                borderColor: '#ffffff',
                backgroundColor: 'rgba(255, 255, 255, 0.1)',
                borderWidth: 2,
                tension: 0.4,
                fill: true,
                pointRadius: 3,
                pointHoverRadius: 6,
                pointBackgroundColor: '#ffffff',
                pointBorderColor: '#1a1a1a',
                pointBorderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        color: '#ffffff',
                        font: {
                            size: 14,
                            weight: 'bold'
                        }
                    }
                },
                title: {
                    display: true,
                    text: 'Évolution de l\'humidité',
                    color: '#ffffff',
                    font: {
                        size: 18,
                        weight: 'bold'
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        color: '#b0b0b0',
                        callback: function(value) {
                            return value + '%';
                        }
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    title: {
                        display: true,
                        text: 'Humidité (%)',
                        color: '#ffffff',
                        font: {
                            weight: 'bold'
                        }
                    }
                },
                x: {
                    ticks: {
                        color: '#b0b0b0',
                        maxRotation: 45,
                        minRotation: 45
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.05)'
                    },
                    title: {
                        display: true,
                        text: 'Date et heure',
                        color: '#ffffff',
                        font: {
                            weight: 'bold'
                        }
                    }
                }
            }
        }
    });

    // Mettre à jour les statistiques
    const stats = calculateStats(data.humidity);
    updateStats(stats);

    // Mettre à jour le compteur
    document.getElementById('data-count').textContent =
        `${data.humidity.length} mesure${data.humidity.length > 1 ? 's' : ''} affichée${data.humidity.length > 1 ? 's' : ''}`;
}

// Fonction pour charger les données
async function loadData(period = 'all') {
    try {
        currentPeriod = period;
        const url = getApiUrl(period);

        const response = await fetch(url);
        if (!response.ok) {
            throw new Error('Erreur de chargement');
        }

        const data = await response.json();
        createChart(data);

    } catch (error) {
        console.error('Erreur:', error);
        document.getElementById('data-count').textContent = 'Erreur de chargement des données';
    }
}

// Gestionnaires d'événements pour les filtres
document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        // Retirer la classe active de tous les boutons
        document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));

        // Ajouter la classe active au bouton cliqué
        this.classList.add('active');

        // Charger les données pour la période sélectionnée
        const period = this.dataset.period;
        loadData(period);
    });
});

// Charger les données au démarrage
loadData('all');

// Log pour debug
console.log('Graphique humidité initialisé');