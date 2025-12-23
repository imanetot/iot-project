from django.core.mail import send_mail
from DHT.utils import send_telegram, send_whatsapp
from .models import Dht11, Incident
from .serializers import DHT11serialize
from rest_framework.decorators import api_view
from rest_framework import status, generics
from rest_framework.response import Response
from django.conf import settings
from django.utils import timezone


@api_view(['GET'])
def Dlist(request):
    """
    Récupérer toutes les données DHT11
    """
    all_data = Dht11.objects.all()
    data = DHT11serialize(all_data, many=True).data
    return Response({'data': data})


class Dhtviews(generics.CreateAPIView):
    """
    Créer une nouvelle entrée DHT11 avec alertes automatiques
    """
    queryset = Dht11.objects.all()
    serializer_class = DHT11serialize

    def perform_create(self, serializer):
        # Sauvegarder l'instance
        instance = serializer.save()
        temp = instance.temp
        hum = instance.hum

        # Chercher incident actif
        incident_actif = Incident.objects.filter(actif=True).first()
        now = timezone.now()

        # Si la température est anormale (< 2 ou > 8)
        if temp < 2 or temp > 8:
            if not incident_actif:
                # Créer nouvel incident et initialiser last_increment
                incident_actif = Incident.objects.create(compteur=1, last_increment=now)
            else:
                # Incrémenter compteur (max 9) mais seulement si 10s se sont écoulées
                if incident_actif.compteur < 9:
                    if (not incident_actif.last_increment) or ((now - incident_actif.last_increment).total_seconds() >= 10):
                        incident_actif.compteur += 1
                        incident_actif.last_increment = now
                        incident_actif.save()

            message = f"⚠️ Alerte Température anormale!\nTempérature: {temp:.1f}°C\nHumidité: {hum:.1f}%\nCompteur incidents: {incident_actif.compteur}"

            # Envoi des notifications
            try:
                send_mail(
                    subject="Alerte Température anormale",
                    message=message,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=["imanejennane23@gmail.com"],
                    fail_silently=False,
                )
                print("✅ Email envoyé avec succès")
            except Exception as e:
                print(f"❌ Erreur lors de l'envoi de l'email: {e}")

            try:
                send_telegram(message)
                print("✅ Message Telegram envoyé avec succès")
            except Exception as e:
                print(f"❌ Erreur lors de l'envoi du message Telegram: {e}")

            try:
                send_whatsapp(message)
                print("✅ Message WhatsApp envoyé avec succès")
            except Exception as e:
                print(f"❌ Erreur lors de l'envoi du message WhatsApp: {e}")

        else:
            # Température normale - fermer l'incident si actif
            if incident_actif:
                # Archiver l'incident avant de fermer
                ArchiveIncident.objects.create(
                    date_debut=incident_actif.date_debut,
                    date_fin=timezone.now(),
                    compteur=incident_actif.compteur,
                    nom_op1=incident_actif.nom_op1,
                    op1_checked=incident_actif.op1_checked,
                    op1_comment=incident_actif.op1_comment,
                    nom_op2=incident_actif.nom_op2,
                    op2_checked=incident_actif.op2_checked,
                    op2_comment=incident_actif.op2_comment,
                    nom_op3=incident_actif.nom_op3,
                    op3_checked=incident_actif.op3_checked,
                    op3_comment=incident_actif.op3_comment,
                )
                incident_actif.actif = False
                incident_actif.date_fin = timezone.now()
                incident_actif.last_increment = None
                incident_actif.save()
                print(f"✅ Incident {incident_actif.id} fermé - Température normale")