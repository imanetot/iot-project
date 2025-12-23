from django.core.management.base import BaseCommand
import time
from DHT.models import Incident

class Command(BaseCommand):
    help = 'Increment counter for active incidents every 10 seconds'

    def handle(self, *args, **options):
        self.stdout.write('Starting counter increment loop...')
        while True:
            incidents = Incident.objects.filter(actif=True)
            for incident in incidents:
                if incident.compteur < 9:
                    incident.compteur += 1
                    incident.save()
                    self.stdout.write(f'Incremented incident {incident.id} to {incident.compteur}')
            time.sleep(10)