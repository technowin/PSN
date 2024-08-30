from django.shortcuts import render
from django.http import JsonResponse
from django.utils.timezone import now
from datetime import timedelta

from Masters.models import *
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import CustomUser, sc_employee_master, sc_roster
import requests
# Create your views here.
def check_shift_for_next_day(request, employee_id, site_id):
    tomorrow = now().date() + timedelta(days=1)
    
    try:
        site = site_master.objects.get(site_id=site_id)
        
        shift = sc_roster.objects.get(employee_id=employee_id, site=site, shift_date=tomorrow)
        
        response_data = {
            'has_shift': True,
            'notification_time': site.notification_time.strftime('%H:%M'),
            'shift_from': shift.shift_from.strftime('%H:%M'),
            'shift_to': shift.shift_to.strftime('%H:%M'),
        }
    except sc_roster.DoesNotExist:
        response_data = {'has_shift': False}
    
    return JsonResponse(response_data)

def check_and_notify_all_users():
    users = CustomUser.objects.all()
    current_time = timezone.now()

    for user in users:
        employee = sc_employee_master.objects.filter(mobile_no=user.phone).first()

        if not employee:
            continue

        next_day = current_time.date() + timedelta(days=1)
        shifts = sc_roster.objects.filter(employee_id=employee.employee_id, shift_date=next_day)

        if shifts.exists():
            send_push_notification(user)

def send_push_notification(user):
     # Firebase Cloud Messaging server key
    FCM_SERVER_KEY = 'YOUR_FCM_SERVER_KEY'

    # The Firebase device token for the user. This should be saved in your user model or a related model.
    user_device_token = user.device_token  # Assuming you have this field

    if not user_device_token:
        print("No device token found for user.")
        return

    # Construct the notification payload
    payload = {
        'to': user_device_token,
        'notification': {
            'title': 'Upcoming Shift Reminder',
            'body': 'You have a shift scheduled for tomorrow.',
            'click_action': 'FLUTTER_NOTIFICATION_CLICK',
            'sound': 'default'
        },
        'data': {
            'type': 'shift_reminder'
        }
    }

    headers = {
        'Authorization': f'key={FCM_SERVER_KEY}',
        'Content-Type': 'application/json'
    }

    # Send the request to FCM
    response = requests.post('https://fcm.googleapis.com/fcm/send', json=payload, headers=headers)

    if response.status_code == 200:
        print("Notification sent successfully.")
    else:
        print(f"Failed to send notification. Status Code: {response.status_code}, Response: {response.text}")

