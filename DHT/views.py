from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from .models import Dht11, Incident, ArchiveIncident
import csv
from .serializers import DHT11serialize
from django.shortcuts import render
import datetime
from django.db.models import Count
from django.db.models.functions import TruncDate
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from django.core.mail import send_mail
from DHT.utils import send_telegram, send_whatsapp
from django.conf import settings


def index_view(request):
    """Page d'accueil - redirige vers le dashboard"""
    return render(request, 'dashboard.html')


def graphique(request):
    """Ancienne page graphique - garde pour compatibilité"""
    data = Dht11.objects.all()
    return render(request, 'chart.html', {'data': data})


def test(request):
    return HttpResponse('IoT Project')


def table(request):
    """Ancienne page table - garde pour compatibilité"""
    derniere_ligne = Dht11.objects.last()
    if not derniere_ligne:
        return render(request, 'value.html', {'valeurs': None})

    derniere_date = derniere_ligne.dt
    delta_temps = timezone.now() - derniere_date
    difference_minutes = delta_temps.seconds // 60

    temps_ecoule = ' il y a ' + str(difference_minutes) + ' min'
    if difference_minutes > 60:
        temps_ecoule = ('il y a ' + str(difference_minutes // 60) + 'h ' +
                        str(difference_minutes % 60) + 'min')

    valeurs = {
        'date': temps_ecoule,
        'id': derniere_ligne.id,
        'temp': derniere_ligne.temp,
        'hum': derniere_ligne.hum
    }
    return render(request, 'value.html', {'valeurs': valeurs})


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


def dashboard(request):
    """Dashboard principal - page d'accueil"""
    return render(request, "dashboard.html")


def graph_temp(request):
    """Page graphique température"""
    return render(request, "graph_temp.html")


def graph_hum(request):
    """Page graphique humidité"""
    return render(request, "graph_hum.html")


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


def incident_status(request):
    """API - Statut incident actuel"""
    incident = Incident.objects.filter(actif=True).first()

    if incident:
        return JsonResponse({
            "incident_actif": True,
            "compteur": incident.compteur,
            "date_debut": incident.date_debut.isoformat(),
            "op1_checked": incident.op1_checked,
            "op1_comment": incident.op1_comment or "",
            "op2_checked": incident.op2_checked,
            "op2_comment": incident.op2_comment or "",
            "op3_checked": incident.op3_checked,
            "op3_comment": incident.op3_comment or "",
        })
    else:
        return JsonResponse({
            "incident_actif": False,
            "compteur": 0
        })


def update_incident(request):
    """API - Mettre à jour incident - COMMENTAIRES OPTIONNELS"""
    if request.method == 'POST':
        incident = Incident.objects.filter(actif=True).first()
        if not incident:
            return JsonResponse({"error": "Aucun incident actif"}, status=400)

        data = json.loads(request.body)

        # Mise à jour sans validation obligatoire des commentaires
        if 'op1_checked' in data:
            incident.op1_checked = data['op1_checked']
        if 'op1_comment' in data:
            incident.op1_comment = data['op1_comment']
        if 'op2_checked' in data:
            incident.op2_checked = data['op2_checked']
        if 'op2_comment' in data:
            incident.op2_comment = data['op2_comment']
        if 'op3_checked' in data:
            incident.op3_checked = data['op3_checked']
        if 'op3_comment' in data:
            incident.op3_comment = data['op3_comment']

        incident.save()
        return JsonResponse({"success": True})

    return JsonResponse({"error": "Méthode non autorisée"}, status=405)


def archive_incidents(request):
    """Page archive des incidents avec détails complets"""
    archives = ArchiveIncident.objects.all().order_by('-date_debut')
    return render(request, 'archives_incidents.html', {'archives': archives})


def download_incidents_excel(request):
    """Téléchargement Excel de tous les incidents"""
    wb = Workbook()
    ws = wb.active
    ws.title = "Incidents DHT11"

    # Styles
    header_font = Font(bold=True, color="FFFFFF", size=12)
    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    header_alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )

    # En-têtes
    headers = [
        'ID', 'Date Début', 'Date Fin', 'Compteur', 'Statut',
        'Opération 1', 'Commentaire Op1',
        'Opération 2', 'Commentaire Op2',
        'Opération 3', 'Commentaire Op3'
    ]

    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num)
        cell.value = header
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_alignment
        cell.border = border

    # Récupérer tous les incidents
    incidents = list(Incident.objects.all().order_by('-date_debut'))
    archives = list(ArchiveIncident.objects.all().order_by('-date_debut'))
    all_incidents = incidents + archives

    # Remplir les données
    for row_num, incident in enumerate(all_incidents, 2):
        if hasattr(incident, 'actif'):
            ws.cell(row=row_num, column=1).value = incident.id
            statut = 'Actif' if incident.actif else 'Fermé'
        else:
            ws.cell(row=row_num, column=1).value = f"A{incident.id}"
            statut = 'Archivé'

        ws.cell(row=row_num, column=2).value = incident.date_debut.strftime('%d/%m/%Y %H:%M:%S')
        date_fin = incident.date_fin.strftime('%d/%m/%Y %H:%M:%S') if incident.date_fin else 'En cours'
        ws.cell(row=row_num, column=3).value = date_fin
        ws.cell(row=row_num, column=4).value = incident.compteur

        statut_cell = ws.cell(row=row_num, column=5)
        statut_cell.value = statut

        if statut == 'Actif':
            statut_cell.fill = PatternFill(start_color="FFE699", end_color="FFE699", fill_type="solid")
        elif statut == 'Fermé':
            statut_cell.fill = PatternFill(start_color="C6E0B4", end_color="C6E0B4", fill_type="solid")
        else:
            statut_cell.fill = PatternFill(start_color="D9D9D9", end_color="D9D9D9", fill_type="solid")

        # Opérations
        op1_cell = ws.cell(row=row_num, column=6)
        op1_cell.value = '✓' if incident.op1_checked else '✗'
        op1_cell.font = Font(color="00B050" if incident.op1_checked else "FF0000", bold=True)
        ws.cell(row=row_num, column=7).value = incident.op1_comment or ''

        op2_cell = ws.cell(row=row_num, column=8)
        op2_cell.value = '✓' if incident.op2_checked else '✗'
        op2_cell.font = Font(color="00B050" if incident.op2_checked else "FF0000", bold=True)
        ws.cell(row=row_num, column=9).value = incident.op2_comment or ''

        op3_cell = ws.cell(row=row_num, column=10)
        op3_cell.value = '✓' if incident.op3_checked else '✗'
        op3_cell.font = Font(color="00B050" if incident.op3_checked else "FF0000", bold=True)
        ws.cell(row=row_num, column=11).value = incident.op3_comment or ''

        for col in range(1, 12):
            ws.cell(row=row_num, column=col).border = border
            ws.cell(row=row_num, column=col).alignment = Alignment(vertical="center")

    # Ajuster largeurs
    column_widths = {
        'A': 8, 'B': 20, 'C': 20, 'D': 12, 'E': 12,
        'F': 15, 'G': 30, 'H': 15, 'I': 30, 'J': 15, 'K': 30
    }

    for col, width in column_widths.items():
        ws.column_dimensions[col].width = width

    ws.freeze_panes = 'A2'

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="incidents_dht11_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx"'

    wb.save(response)
    return response


@csrf_exempt
@require_http_methods(["POST"])
def check_create_incident(request):
    """Vérifie la température et crée/met à jour un incident si nécessaire"""
    try:
        data = json.loads(request.body)
        temperature = float(data.get('temperature', 0))

        if temperature < 2 or temperature > 8:
            incident = Incident.objects.filter(actif=True).first()
            now = timezone.now()

            if incident:
                if incident.compteur < 9:
                    if (not incident.last_increment) or ((now - incident.last_increment).total_seconds() >= 10):
                        incident.compteur += 1
                        incident.last_increment = now
                        incident.save()

                return JsonResponse({
                    'success': True,
                    'message': 'Incident mis à jour',
                    'compteur': incident.compteur,
                    'created': False
                })
            else:
                incident = Incident.objects.create(
                    actif=True,
                    compteur=1,
                    date_debut=timezone.now(),
                    last_increment=now
                )

                return JsonResponse({
                    'success': True,
                    'message': 'Incident créé',
                    'compteur': incident.compteur,
                    'created': True
                })
        else:
            incident = Incident.objects.filter(actif=True).first()
            if incident:
                # Archiver l'incident
                ArchiveIncident.objects.create(
                    date_debut=incident.date_debut,
                    date_fin=timezone.now(),
                    compteur=incident.compteur,
                    nom_op1=incident.nom_op1,
                    op1_checked=incident.op1_checked,
                    op1_comment=incident.op1_comment,
                    nom_op2=incident.nom_op2,
                    op2_checked=incident.op2_checked,
                    op2_comment=incident.op2_comment,
                    nom_op3=incident.nom_op3,
                    op3_checked=incident.op3_checked,
                    op3_comment=incident.op3_comment,
                )
                incident.delete()

                return JsonResponse({
                    'success': True,
                    'message': 'Incident fermé',
                    'closed': True
                })

            return JsonResponse({
                'success': True,
                'message': 'Pas d\'incident à créer'
            })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def manual_data_entry(request):
    """
    Permet l'entrée manuelle de données de température et d'humidité
    FONCTION MANQUANTE - MAINTENANT AJOUTÉE!
    """
    try:
        data = json.loads(request.body)
        temperature = float(data.get('temp', 0))
        humidity = float(data.get('hum', 0))

        # Validation
        if humidity < 0 or humidity > 100:
            return JsonResponse({
                'success': False,
                'error': 'L\'humidité doit être entre 0 et 100%'
            }, status=400)

        # Créer une nouvelle entrée DHT11
        dht_entry = Dht11.objects.create(
            temp=temperature,
            hum=humidity
        )

        # Vérifier si température anormale pour créer/mettre à jour incident
        if temperature < 2 or temperature > 8:
            now = timezone.now()
            incident = Incident.objects.filter(actif=True).first()

            if incident:
                # Incident existe déjà, incrémenter le compteur toutes les 10s max
                if incident.compteur < 9:
                    if (not incident.last_increment) or ((now - incident.last_increment).total_seconds() >= 10):
                        incident.compteur += 1
                        incident.last_increment = now
                        incident.save()
            else:
                # Créer un nouvel incident
                incident = Incident.objects.create(
                    actif=True,
                    compteur=1,
                    date_debut=timezone.now(),
                    last_increment=now
                )

            message = f"⚠️ Alerte Température anormale!\nTempérature: {temperature:.1f}°C\nHumidité: {humidity:.1f}%\nCompteur incidents: {incident.compteur}"

            # Envoi des notifications
            try:
                send_mail(
                    subject="Alerte Température - Entrée Manuelle",
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
            incident = Incident.objects.filter(actif=True).first()
            if incident:
                # Archiver l'incident
                ArchiveIncident.objects.create(
                    date_debut=incident.date_debut,
                    date_fin=timezone.now(),
                    compteur=incident.compteur,
                    nom_op1=incident.nom_op1,
                    op1_checked=incident.op1_checked,
                    op1_comment=incident.op1_comment,
                    nom_op2=incident.nom_op2,
                    op2_checked=incident.op2_checked,
                    op2_comment=incident.op2_comment,
                    nom_op3=incident.nom_op3,
                    op3_checked=incident.op3_checked,
                    op3_comment=incident.op3_comment,
                )
                incident.delete()
                print(f"✅ Incident fermé - Température normale")

        return JsonResponse({
            'success': True,
            'message': 'Données enregistrées avec succès',
            'id': dht_entry.id,
            'temperature': temperature,
            'humidity': humidity
        })

    except ValueError as e:
        return JsonResponse({
            'success': False,
            'error': 'Valeurs invalides'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)