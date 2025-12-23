from django.core.management.base import BaseCommand
from DHT.mqtt_client import mqtt_client
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class Command(BaseCommand):
    help = 'Démarre le client MQTT pour recevoir les données des capteurs DHT11'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Démarrage du client MQTT...'))

        try:
            mqtt_client.start()
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('\n Arrêt du client MQTT...'))
            mqtt_client.stop()
            self.stdout.write(self.style.SUCCESS(' Client MQTT arrêté'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f' Erreur: {e}'))