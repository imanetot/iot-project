from django.core.mail import send_mail
from DHT.utils import send_telegram, send_whatsapp
from .models import Dht11, Incident
from .serializers import DHT11serialize
from rest_framework.decorators import api_view
from rest_framework import status, generics
from rest_framework.response import Response
from django.conf import settings


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

        # Seuil d'alerte (à ajuster selon vos besoins)
        SEUIL_TEMPERATURE = 25
        incident_actif = Incident.objects.filter(actif=True).first()
        # Si la température dépasse le seuil
        if temp > SEUIL_TEMPERATURE:
            if not incident_actif:
                # Créer nouvel incident
                incident_actif = Incident.objects.create(compteur=1)
            else:
                # Incrémenter compteur
                incident_actif.compteur += 1
                incident_actif.save()
            message = f"⚠️ Alerte Température élevée!\nTempérature: {temp:.1f}°C\nHumidité: {hum:.1f}%\nCompteur incidents: {incident_actif.compteur}"
            # 1) Envoi Email
            try:
                send_mail(
                    subject="Alerte Température élevée",
                    message=message,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=["imanejennane23@gmail.com"],
                    fail_silently=False,
                )
                print("Email envoyé avec succès")
            except Exception as e:
                print(f"Erreur lors de l'envoi de l'email: {e}")

            # 2) Envoi Telegram
            try:
                send_telegram(message)
                print("Message Telegram envoyé avec succès")
            except Exception as e:
                print(f"Erreur lors de l'envoi du message Telegram: {e}")

            # 3) Envoi WhatsApp
            try:
                send_whatsapp(message)
                print("Message WhatsApp envoyé avec succès")
            except Exception as e:
                print(f" Erreur lors de l'envoi du message WhatsApp: {e}")
                message = f"⚠️ Alerte Température élevée!\nTempérature: {temp:.1f}°C\nHumidité: {hum:.1f}%\nCompteur incidents: {incident_actif.compteur}"