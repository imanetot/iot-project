"""
MQTT Client for DHT11 IoT System
Place this file in: DHT/mqtt_client.py

Install required package:
pip install paho-mqtt
"""

import paho.mqtt.client as mqtt
import json
import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

# Configuration MQTT
MQTT_BROKER = getattr(settings, 'MQTT_BROKER', 'broker.hivemq.com')
MQTT_PORT = getattr(settings, 'MQTT_PORT', 1883)
MQTT_TOPIC_SUBSCRIBE = getattr(settings, 'MQTT_TOPIC_SUBSCRIBE', 'dht11/sensors')
MQTT_TOPIC_PUBLISH = getattr(settings, 'MQTT_TOPIC_PUBLISH', 'dht11/alerts')
MQTT_CLIENT_ID = getattr(settings, 'MQTT_CLIENT_ID', 'django_dht11_client')

# URL de l'API Django pour enregistrer les données
API_POST_URL = 'http://localhost:8000/api/post/'


class DHT11MQTTClient:
    def __init__(self):
        self.client = mqtt.Client(client_id=MQTT_CLIENT_ID)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect

    def on_connect(self, client, userdata, flags, rc):
        """Callback quand le client se connecte au broker"""
        if rc == 0:
            logger.info(f"✅ Connecté au broker MQTT: {MQTT_BROKER}:{MQTT_PORT}")
            # S'abonner au topic des capteurs
            client.subscribe(MQTT_TOPIC_SUBSCRIBE)
            logger.info(f"📡 Abonné au topic: {MQTT_TOPIC_SUBSCRIBE}")
        else:
            logger.error(f"❌ Échec de connexion au broker MQTT, code: {rc}")

    def on_disconnect(self, client, userdata, rc):
        """Callback quand le client se déconnecte"""
        if rc != 0:
            logger.warning(f"⚠️ Déconnexion inattendue du broker MQTT, code: {rc}")
            logger.info("🔄 Tentative de reconnexion...")

    def on_message(self, client, userdata, msg):
        """Callback quand un message est reçu"""
        try:
            # Décoder le message JSON
            payload = msg.payload.decode('utf-8')
            data = json.loads(payload)

            logger.info(f"📥 Message reçu sur {msg.topic}: {data}")

            # Extraire température et humidité
            temperature = float(data.get('temperature', data.get('temp', 0)))
            humidity = float(data.get('humidity', data.get('hum', 0)))

            # Envoyer les données à l'API Django
            self.send_to_api(temperature, humidity)

        except json.JSONDecodeError as e:
            logger.error(f"❌ Erreur de décodage JSON: {e}")
        except Exception as e:
            logger.error(f"❌ Erreur lors du traitement du message: {e}")

    def send_to_api(self, temperature, humidity):
        """Envoie les données à l'API Django"""
        try:
            payload = {
                'temp': temperature,
                'hum': humidity
            }

            response = requests.post(
                API_POST_URL,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=5
            )

            if response.status_code == 201:
                logger.info(f"✅ Données envoyées à l'API: Temp={temperature}°C, Hum={humidity}%")
            else:
                logger.error(f"❌ Erreur API: {response.status_code} - {response.text}")

        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Erreur de connexion à l'API: {e}")

    def publish_alert(self, message):
        """Publie une alerte sur le topic MQTT"""
        try:
            alert_data = {
                'alert': message,
                'timestamp': str(datetime.now())
            }

            self.client.publish(
                MQTT_TOPIC_PUBLISH,
                json.dumps(alert_data),
                qos=1
            )

            logger.info(f"📤 Alerte publiée: {message}")

        except Exception as e:
            logger.error(f"❌ Erreur lors de la publication de l'alerte: {e}")

    def connect(self):
        """Connecte le client au broker MQTT"""
        try:
            self.client.connect(MQTT_BROKER, MQTT_PORT, 60)
            return True
        except Exception as e:
            logger.error(f"❌ Erreur de connexion au broker MQTT: {e}")
            return False

    def start(self):
        """Démarre la boucle du client MQTT"""
        if self.connect():
            logger.info("🚀 Démarrage du client MQTT...")
            self.client.loop_forever()

    def stop(self):
        """Arrête le client MQTT"""
        logger.info("⏹️ Arrêt du client MQTT...")
        self.client.disconnect()
        self.client.loop_stop()


# Instance globale du client MQTT
mqtt_client = DHT11MQTTClient()


def start_mqtt_client():
    """Fonction pour démarrer le client MQTT dans un thread séparé"""
    import threading

    def run_mqtt():
        mqtt_client.start()

    mqtt_thread = threading.Thread(target=run_mqtt, daemon=True)
    mqtt_thread.start()
    logger.info("🔄 Client MQTT démarré dans un thread séparé")

# Exemple de format de message MQTT attendu:
# {
#     "temperature": 25.5,
#     "humidity": 65.0
# }
# ou
# {
#     "temp": 25.5,
#     "hum": 65.0
# }