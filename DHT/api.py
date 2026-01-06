from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from rest_framework.decorators import api_view

from .models import Dht11, Incident, IncidentComment, ArchiveIncident, UserProfile, TemperatureThreshold
import csv
from .serializers import DHT11serialize
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User
import json
from django.core.mail import send_mail
from DHT.utils import send_telegram, send_whatsapp
from django.conf import settings
import datetime
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from rest_framework import viewsets, generics
from DHT.ntfy_notifications import send_ntfy_to_multiple_users

# ==================== AUTHENTICATION ====================

def login_view(request):
    """Page de connexion"""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        else:
            messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')

    return render(request, 'auth/login.html')


def logout_view(request):
    """Déconnexion"""
    logout(request)
    return redirect('login')


@login_required
def profile_view(request):
    """Page de profil utilisateur"""
    return render(request, 'auth/profile.html')


# ==================== HELPER FUNCTION ====================

def get_user_role(user):
    """Get user role safely"""
    if hasattr(user, 'profile'):
        return user.profile.role
    return 'visiteur'


# ==================== DASHBOARD ====================

@login_required
def dashboard(request):
    """Dashboard principal - page d'accueil"""
    return render(request, "dashboard.html")


# ==================== DATA VIEWS ====================

def latest_json(request):
    """API - Dernière mesure en JSON"""
    last = Dht11.objects.order_by('-dt').values('temp', 'hum', 'dt').first()
    if not last:
        return JsonResponse({"detail": "Aucune donnée disponible"}, status=404)
    return JsonResponse({
        "temperature": last["temp"],
        "humidity": last["hum"],
        "timestamp": last["dt"].isoformat()
    })


def chart_data(request):
    """API - Toutes les données pour graphiques"""
    dht = Dht11.objects.all().order_by('dt')
    data = {
        'temps': [dt.dt.isoformat() for dt in dht],
        'temperature': [temp.temp for temp in dht],
        'humidity': [hum.hum for hum in dht]
    }
    return JsonResponse(data)


def chart_data_jour(request):
    """API - Données des dernières 24h"""
    now = timezone.now()
    last_24_hours = now - timezone.timedelta(hours=24)
    dht = Dht11.objects.filter(dt__range=(last_24_hours, now)).order_by('dt')
    data = {
        'temps': [dt.dt.isoformat() for dt in dht],
        'temperature': [temp.temp for temp in dht],
        'humidity': [hum.hum for hum in dht]
    }
    return JsonResponse(data)


def chart_data_semaine(request):
    """API - Données de la dernière semaine"""
    date_debut_semaine = timezone.now() - datetime.timedelta(days=7)
    dht = Dht11.objects.filter(dt__gte=date_debut_semaine).order_by('dt')
    data = {
        'temps': [dt.dt.isoformat() for dt in dht],
        'temperature': [temp.temp for temp in dht],
        'humidity': [hum.hum for hum in dht]
    }
    return JsonResponse(data)


def chart_data_mois(request):
    """API - Données du dernier mois"""
    date_debut_mois = timezone.now() - datetime.timedelta(days=30)
    dht = Dht11.objects.filter(dt__gte=date_debut_mois).order_by('dt')
    data = {
        'temps': [dt.dt.isoformat() for dt in dht],
        'temperature': [temp.temp for temp in dht],
        'humidity': [hum.hum for hum in dht]
    }
    return JsonResponse(data)


# ==================== GRAPH PAGES ====================

@login_required
def graph_temp(request):
    """Page graphique température"""
    return render(request, "graph_temp.html")


@login_required
def graph_hum(request):
    """Page graphique humidité"""
    return render(request, "graph_hum.html")


# ==================== INCIDENT MANAGEMENT ====================

@login_required
def incident_status(request):
    """API - Statut incident actuel avec permissions"""
    incident = Incident.objects.filter(actif=True).first()
    
    user_role = get_user_role(request.user)
    
    # Check permissions based on role
    can_edit_op1 = user_role in ['admin', 'operateur1']
    can_edit_op2 = user_role in ['admin', 'operateur2']
    can_edit_op3 = user_role in ['admin', 'operateur3']
    can_comment = user_role != 'visiteur'
    can_accuse_reception = user_role != 'visiteur'

    if incident:
        comments = incident.comments.all().order_by('created_at')
        comments_data = [{
            'author': comment.author.username,
            'content': comment.content,
            'created_at': comment.created_at.isoformat()
        } for comment in comments]

        return JsonResponse({
            "incident_actif": True,
            "compteur": incident.compteur,
            "date_debut": incident.date_debut.isoformat(),
            "temperature": incident.temperature,
            "humidity": incident.humidity,
            "accuse_reception": incident.accuse_reception,
            "accuse_reception_operateur": incident.accuse_reception_operateur.username if incident.accuse_reception_operateur else None,
            "accuse_reception_date": incident.accuse_reception_date.isoformat() if incident.accuse_reception_date else None,
            "op1_checked": incident.op1_checked,
            "op1_comment": incident.op1_comment or "",
            "op1_operateur": incident.op1_operateur.username if incident.op1_operateur else None,
            "op1_date": incident.op1_date.isoformat() if incident.op1_date else None,
            "op2_checked": incident.op2_checked,
            "op2_comment": incident.op2_comment or "",
            "op2_operateur": incident.op2_operateur.username if incident.op2_operateur else None,
            "op2_date": incident.op2_date.isoformat() if incident.op2_date else None,
            "op3_checked": incident.op3_checked,
            "op3_comment": incident.op3_comment or "",
            "op3_operateur": incident.op3_operateur.username if incident.op3_operateur else None,
            "op3_date": incident.op3_date.isoformat() if incident.op3_date else None,
            "comments": comments_data,
            "permissions": {
                "user_role": user_role,
                "can_edit_op1": can_edit_op1,
                "can_edit_op2": can_edit_op2,
                "can_edit_op3": can_edit_op3,
                "can_comment": can_comment,
                "can_accuse_reception": can_accuse_reception
            }
        })
    else:
        return JsonResponse({
            "incident_actif": False,
            "compteur": 0,
            "permissions": {
                "user_role": user_role,
                "can_edit_op1": can_edit_op1,
                "can_edit_op2": can_edit_op2,
                "can_edit_op3": can_edit_op3,
                "can_comment": can_comment,
                "can_accuse_reception": can_accuse_reception
            }
        })


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def update_incident(request):
    """API - Mettre à jour incident avec vérification des permissions"""
    incident = Incident.objects.filter(actif=True).first()
    if not incident:
        return JsonResponse({"error": "Aucun incident actif"}, status=400)

    user_role = get_user_role(request.user)
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    # Check permissions for accusé de réception
    if 'accuse_reception' in data:
        if user_role == 'visiteur':
            return JsonResponse({"error": "Permission refusée"}, status=403)
        incident.accuse_reception = data['accuse_reception']
        if data['accuse_reception']:
            incident.accuse_reception_operateur = request.user
            incident.accuse_reception_date = timezone.now()

    # Check permissions for each operation
    if 'op1_checked' in data or 'op1_comment' in data:
        if user_role not in ['admin', 'operateur1']:
            return JsonResponse({"error": "Permission refusée pour op1"}, status=403)
        
        if 'op1_checked' in data:
            incident.op1_checked = data['op1_checked']
            if data['op1_checked']:
                incident.op1_operateur = request.user
                incident.op1_date = timezone.now()
        if 'op1_comment' in data:
            incident.op1_comment = data['op1_comment']

    if 'op2_checked' in data or 'op2_comment' in data:
        if user_role not in ['admin', 'operateur2']:
            return JsonResponse({"error": "Permission refusée pour op2"}, status=403)
        
        if 'op2_checked' in data:
            incident.op2_checked = data['op2_checked']
            if data['op2_checked']:
                incident.op2_operateur = request.user
                incident.op2_date = timezone.now()
        if 'op2_comment' in data:
            incident.op2_comment = data['op2_comment']

    if 'op3_checked' in data or 'op3_comment' in data:
        if user_role not in ['admin', 'operateur3']:
            return JsonResponse({"error": "Permission refusée pour op3"}, status=403)
        
        if 'op3_checked' in data:
            incident.op3_checked = data['op3_checked']
            if data['op3_checked']:
                incident.op3_operateur = request.user
                incident.op3_date = timezone.now()
        if 'op3_comment' in data:
            incident.op3_comment = data['op3_comment']

    incident.save()
    return JsonResponse({"success": True})


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def add_incident_comment(request, incident_id):
    """Ajouter un commentaire à un incident"""
    user_role = get_user_role(request.user)
    
    if user_role == 'visiteur':
        return JsonResponse({'success': False, 'error': 'Permission refusée'}, status=403)
    
    try:
        incident = Incident.objects.get(id=incident_id, actif=True)
        data = json.loads(request.body)
        content = data.get('content', '').strip()

        if not content:
            return JsonResponse({'success': False, 'error': 'Commentaire vide'}, status=400)

        comment = IncidentComment.objects.create(
            incident=incident,
            author=request.user,
            content=content
        )

        return JsonResponse({
            'success': True,
            'comment': {
                'id': comment.id,
                'author': request.user.username,
                'content': comment.content,
                'created_at': comment.created_at.isoformat()
            }
        })

    except Incident.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Incident non trouvé'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# ==================== DOWNLOAD/EXPORT ====================

def download_csv(request):
    """Téléchargement CSV de toutes les données"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="dht11_data.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID', 'Temperature (°C)', 'Humidite (%)', 'Date et Heure'])

    model_values = Dht11.objects.values_list('id', 'temp', 'hum', 'dt')
    for row in model_values:
        writer.writerow(row)

    return response


# ==================== ARCHIVE ====================

@login_required
def archive_incidents(request):
    """Page archive des incidents avec détails complets"""
    archives = ArchiveIncident.objects.all().order_by('-date_debut')
    return render(request, 'archives_incidents.html', {'archives': archives})


@login_required
def archive_incident_detail(request, incident_id):
    """Page détail d'un incident archivé"""
    try:
        incident = ArchiveIncident.objects.get(id=incident_id)
    except ArchiveIncident.DoesNotExist:
        return render(request, '404.html', {'message': 'Incident non trouvé'})

    return render(request, 'archive_incident_detail.html', {'incident': incident})


# ==================== ADMIN PANEL ====================

@login_required
def admin_panel(request):
    """Panneau d'administration unifié (Admin seulement)"""
    user_role = get_user_role(request.user)
    
    if user_role != 'admin':
        messages.error(request, 'Accès non autorisé.')
        return redirect('dashboard')

    # Handle POST actions
    if request.method == 'POST':
        action = request.GET.get('action')
        if action == 'update_thresholds':
            min_temp = request.POST.get('min_temp')
            max_temp = request.POST.get('max_temp')
            if min_temp and max_temp:
                try:
                    min_temp = float(min_temp)
                    max_temp = float(max_temp)
                    if min_temp < max_temp:
                        threshold = TemperatureThreshold.objects.first()
                        if not threshold:
                            threshold = TemperatureThreshold.objects.create(min_temp=min_temp, max_temp=max_temp, updated_by=request.user)
                        else:
                            threshold.min_temp = min_temp
                            threshold.max_temp = max_temp
                            threshold.updated_by = request.user
                            threshold.save()
                        messages.success(request, f'Seuils mis à jour: {min_temp}°C - {max_temp}°C')
                    else:
                        messages.error(request, 'La température minimum doit être inférieure à la maximum.')
                except ValueError:
                    messages.error(request, 'Valeurs invalides.')
            else:
                messages.error(request, 'Veuillez saisir les deux valeurs.')
            return redirect('admin_panel')
    
    operateurs = UserProfile.objects.exclude(role='admin').select_related('user')
    threshold = TemperatureThreshold.objects.first()
    if not threshold:
        threshold = TemperatureThreshold.objects.create(min_temp=2.0, max_temp=8.0)

    context = {
        'operateurs': operateurs,
        'threshold': threshold,
        'ROLE_CHOICES': UserProfile.ROLE_CHOICES
    }

    return render(request, 'admin/admin_panel.html', context)

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

    # ========== NOTICE: perform_create MUST BE INDENTED INSIDE THE CLASS ==========
    def perform_create(self, serializer):
        # Sauvegarder l'instance
        instance = serializer.save()
        temp = instance.temp
        hum = instance.hum

        # Get temperature thresholds
        threshold = TemperatureThreshold.objects.first()
        if not threshold:
            threshold = TemperatureThreshold.objects.create(min_temp=2.0, max_temp=8.0)

        min_temp = threshold.min_temp
        max_temp = threshold.max_temp

        # Chercher incident actif
        incident_actif = Incident.objects.filter(actif=True).first()
        now = timezone.now()

        # Si la température est anormale (EN DEHORS de la plage)
        if temp < min_temp or temp > max_temp:
            if not incident_actif:
                # Créer nouvel incident
                incident_actif = Incident.objects.create(
                    actif=True,
                    compteur=1,
                    last_increment=now,
                    temperature=temp,
                    humidity=hum,
                    status='en_cours'
                )
            else:
                # Incrémenter compteur (max 9)
                if incident_actif.compteur < 9:
                    if (not incident_actif.last_increment) or ((now - incident_actif.last_increment).total_seconds() >= 10):
                        incident_actif.compteur += 1
                        incident_actif.last_increment = now
                        incident_actif.temperature = temp
                        incident_actif.humidity = hum
                        incident_actif.save()

            message = f"⚠️ Alerte Température anormale!\nTempérature: {temp:.1f}°C\nHumidité: {hum:.1f}%\nCompteur incidents: {incident_actif.compteur}"

            # ========== ADD NTFY PUSH NOTIFICATION HERE ==========
            # Send urgent push notification to mobile devices via ntfy.sh
            try:
                send_ntfy_to_multiple_users(
                    temperature=temp,
                    humidity=hum,
                    incident_count=incident_actif.compteur
                )
                print("✅ Ntfy push notification sent to mobile devices")
            except Exception as e:
                print(f"❌ Error sending ntfy notification: {e}")
            # ========== END NTFY NOTIFICATION ==========

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
            # *** FIX: Température NORMALE (ENTRE min et max) - FERMER l'incident ***
            if incident_actif:
                # Archiver l'incident avant de fermer
                ArchiveIncident.objects.create(
                    date_debut=incident_actif.date_debut,
                    date_fin=timezone.now(),
                    compteur=incident_actif.compteur,
                    status='termine',
                    temperature=incident_actif.temperature,
                    humidity=incident_actif.humidity,
                    nom_op1=incident_actif.nom_op1,
                    op1_checked=incident_actif.op1_checked,
                    op1_comment=incident_actif.op1_comment or '',
                    op1_operateur_name=incident_actif.op1_operateur.username if incident_actif.op1_operateur else '',
                    op1_date=incident_actif.op1_date,
                    nom_op2=incident_actif.nom_op2,
                    op2_checked=incident_actif.op2_checked,
                    op2_comment=incident_actif.op2_comment or '',
                    op2_operateur_name=incident_actif.op2_operateur.username if incident_actif.op2_operateur else '',
                    op2_date=incident_actif.op2_date,
                    nom_op3=incident_actif.nom_op3,
                    op3_checked=incident_actif.op3_checked,
                    op3_comment=incident_actif.op3_comment or '',
                    op3_operateur_name=incident_actif.op3_operateur.username if incident_actif.op3_operateur else '',
                    op3_date=incident_actif.op3_date,
                )

                # Fermer l'incident
                incident_actif.actif = False
                incident_actif.date_fin = timezone.now()
                incident_actif.status = 'termine'
                incident_actif.last_increment = None
                incident_actif.save()

                print(f"✅ Incident {incident_actif.id} fermé - Température normale: {temp}°C")