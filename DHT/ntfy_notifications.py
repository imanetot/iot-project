# DHT/ntfy_notifications.py
"""
Ntfy.sh push notification system for temperature alarms
This sends urgent push notifications to mobile devices via ntfy.sh
"""

import requests
from django.conf import settings


def send_ntfy_alarm(temperature, humidity, incident_count=None):
    """
    Send an urgent push notification via ntfy.sh when temperature is abnormal

    Args:
        temperature: Current temperature value
        humidity: Current humidity value
        incident_count: Optional incident counter value
    """

    # Get ntfy configuration from settings
    ntfy_topic = getattr(settings, 'NTFY_TOPIC', 'dht11_temp_alarm_default')
    ntfy_enabled = getattr(settings, 'NTFY_ENABLED', False)

    if not ntfy_enabled:
        print("ℹ️ Ntfy notifications are disabled in settings")
        return False

    # Prepare message content
    if incident_count:
        message = f"TEMPERATURE ALERT!\n\nTemp: {temperature:.1f}C\nHumidity: {humidity:.1f}%\nIncident Count: {incident_count}"
    else:
        message = f"TEMPERATURE ALERT!\n\nTemp: {temperature:.1f}C\nHumidity: {humidity:.1f}%"

    # Ntfy.sh endpoint
    url = f"https://ntfy.sh/{ntfy_topic}"

    try:
        response = requests.post(
            url,
            data=message.encode('utf-8'),
            headers={
                'Title': 'TEMPERATURE ALARM',
                'Priority': 'urgent',
                'Tags': 'warning,thermometer',
            },
            timeout=5
        )

        if response.status_code == 200:
            print(f"✅ Ntfy alarm sent successfully to topic: {ntfy_topic}")
            return True
        else:
            print(f"❌ Ntfy alarm failed: {response.status_code}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"❌ Error sending ntfy alarm: {e}")
        return False


def send_ntfy_to_multiple_users(temperature, humidity, incident_count=None):
    """
    Send notifications to multiple ntfy topics (multiple users)
    Configure user topics in settings.NTFY_TOPICS list

    Example in settings.py:
    NTFY_TOPICS = [
        'temp_alarm_user1_xyz',
        'temp_alarm_user2_abc',
    ]
    """

    ntfy_topics = getattr(settings, 'NTFY_TOPICS', [])
    ntfy_enabled = getattr(settings, 'NTFY_ENABLED', False)

    if not ntfy_enabled:
        print("ℹ️ Ntfy notifications are disabled in settings")
        return False

    if not ntfy_topics:
        print("⚠️ No ntfy topics configured in settings.NTFY_TOPICS")
        return False

    # Prepare message - NO EMOJIS to avoid encoding issues
    if incident_count:
        message = f"TEMPERATURE ALERT!\n\nTemp: {temperature:.1f}C\nHumidity: {humidity:.1f}%\nIncident Count: {incident_count}"
    else:
        message = f"TEMPERATURE ALERT!\n\nTemp: {temperature:.1f}C\nHumidity: {humidity:.1f}%"

    success_count = 0

    # Send to each configured topic
    # Send 3 times for maximum attention
    import time
    for repeat in range(3):
        for topic in ntfy_topics:
            url = f"https://ntfy.sh/{topic}"

            try:
                response = requests.post(
                    url,
                    data=message.encode('utf-8'),
                    headers={
                        'Title': f'ALARM {repeat + 1}/3',
                        'Priority': 'urgent',
                        'Tags': 'warning,thermometer',
                    },
                    timeout=5
                )

                if response.status_code == 200:
                    print(f"✅ Ntfy alarm {repeat + 1}/3 sent to: {topic}")
                    success_count += 1
                else:
                    print(f"❌ Failed to send to {topic}: {response.status_code}")

            except requests.exceptions.RequestException as e:
                print(f"❌ Error sending to {topic}: {e}")

        # Small delay between bursts
        if repeat < 2:
            time.sleep(0.5)

    return success_count > 0