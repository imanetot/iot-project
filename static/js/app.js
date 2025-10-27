const API_URL = "/latest/";

const tempEl = document.getElementById('temp');
const humEl  = document.getElementById('hum');
const timeEl = document.getElementById('time');
const statusEl = document.getElementById('status');

async function getData() {
  statusEl.textContent = "Chargement...";
  try {
    const res = await fetch(API_URL);
    const data = await res.json();
    tempEl.textContent = data.temperature;
    humEl.textContent  = data.humidity;
    timeEl.textContent = new Date(data.timestamp).toLocaleString();
    statusEl.textContent = "OK";
  } catch (e) {
    statusEl.textContent = "Erreur: " + e.message;
  }
}

setInterval(() => {
  window.location.reload();
}, 20000);


function updateData() {
  fetch('/data') // ton endpoint Flask/Django qui renvoie {temperature, humidity}
    .then(response => response.json())
    .then(data => {
      const temp = data.temperature;
      const hum = data.humidity;

      // Mise à jour des valeurs affichées
      document.getElementById('temperature').textContent = temp + " °C";
      document.getElementById('humidity').textContent = hum + " %";

      // --- 🔥 Changement de couleur de fond ---
      if (temp > 30) {
        document.body.style.backgroundColor = "red";
      } else if (hum < 30) {
        document.body.style.backgroundColor = "blue";
      } else {
        document.body.style.backgroundColor = "white"; // couleur normale
      }
    })
    .catch(error => console.error('Erreur de récupération des données :', error));
}

updateData();
setInterval(updateData, 20000);

document.getElementById('refresh').addEventListener('click', getData);
getData();