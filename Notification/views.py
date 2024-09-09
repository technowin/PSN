from django.shortcuts import render
from django.http import JsonResponse
from django.utils.timezone import now
from datetime import timedelta

from Masters.models import *
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from rest_framework.response import Response
import requests
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
# Create your views here.
# def check_shift_for_next_day(request, employee_id, site_id):
#     tomorrow = now().date() + timedelta(days=1)
    
#     try:
#         site = site_master.objects.get(site_id=site_id)
        
#         shift = sc_roster.objects.get(employee_id=employee_id, site=site, shift_date=tomorrow)
        
#         response_data = {
#             'has_shift': True,
#             'notification_time': site.notification_time.strftime('%H:%M'),
#             'shift_from': shift.shift_from.strftime('%H:%M'),
#             'shift_to': shift.shift_to.strftime('%H:%M'),
#         }
#     except sc_roster.DoesNotExist:
#         response_data = {'has_shift': False}
    
#     return JsonResponse(response_data)
import json
import google.auth
from google.oauth2 import service_account
import google.auth.transport.requests
import os

import base64
import json
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from rest_framework import status

from Masters.serializers import ScRosterSerializer
from Notification.models import notification_log

class check_and_notify_user(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    def post(self, request):
        # Get user from request (JWT token will give us the user)
        user = request.user
        current_time = timezone.now()

        # Get the employee from sc_employee_master based on the user's phone number
        employee = sc_employee_master.objects.filter(mobile_no=user.phone).first()

        if not employee:
            return Response({"message": "Employee not found."}, status=404)

        # Check if there are any shifts for the employee for the next day
        next_day = current_time.date() + timedelta(days=1)
        shifts = sc_roster.objects.filter(employee_id=employee.employee_id, shift_date=next_day)

        if shifts.exists():
            # Send notification logic here
            send_push_notification(user)  # Function to send push notification
            return Response({"message": "Notification sent."}, status=200)
        else:
            return Response({"message": "No shifts found for the next day."}, status=200)

class check_and_notify_all_users(APIView):
    
    def get(self, request):
        users = CustomUser.objects.all()
        current_time = timezone.now()
        errors = []
        success = []
        for user in users:
            employee = sc_employee_master.objects.filter(mobile_no=user.phone).first()

            if not employee:
                continue

            next_day = current_time.date() + timedelta(days=1)
            shifts = sc_roster.objects.filter(employee_id=employee.employee_id, shift_date=next_day,confirmation__isnull=True )
            
            
            if shifts.exists():
                shift = shifts.first() 
                serializer = ScRosterSerializer(shift)
                
                shift_data = serializer.data
                notification_entry = notification_log.objects.create(
                    sc_roster_id=shift,
                    notification_sent=current_time,
                    notification_message="Notification for shift confirmation",
                    created_at=current_time,
                    created_by=user,  # assuming the current user is the creator
                    updated_at=current_time,
                    updated_by=user  # assuming the current user is the updater
                )
                notification_log_id = notification_entry.id
                a = send_push_notification(user,shift_data,notification_log_id)
                if(a!= "success"):
                    c = a.split("--")
                    if(len(c) == 2):
                        if(c[1] == "Requested entity was not found."):
                            notification_entry.notification_message = "App Is Not Installed"  # Update with the error message
                            notification_entry.save()     
                        elif(c[1] == "The registration token is not a valid FCM registration token")  :
                            notification_entry.notification_message = "User Not Correctly Registered to the App. Please Login Again."  # Update with the error message
                            notification_entry.save()     
                            
                        
                    else:
                        notification_entry.notification_message = a  # Update with the error message
                        notification_entry.save()
                    errors.append(f"Error sending notification to {user.full_name} - {a}")
                else :
                    notification_entry.notification_received = timezone.now()
                    notification_entry.save()
                    success.append(f"successfully sent notification to {user.full_name} - {a}")
        if len(errors)>0:
            return Response({'error':errors,'success':success}, status=status.HTTP_200_OK)
        else:
            return Response({'success':success}, status=status.HTTP_200_OK)
            
                    

def send_push_notification(user,shift_data,notification_log_id):
    try:
        
        # Retrieve and decode the base64-encoded credentials
        credentials_base64 = os.getenv('GOOGLE_APPLICATION_CREDENTIALS_BASE64')
        if not credentials_base64:
            raise ValueError("GOOGLE_APPLICATION_CREDENTIALS_BASE64 environment variable is not set")

        credentials_json = base64.b64decode(credentials_base64).decode('utf-8')
        credentials_dict = json.loads(credentials_json)

        # Create credentials object
        SCOPES = ['https://www.googleapis.com/auth/firebase.messaging']
        
        credentials = service_account.Credentials.from_service_account_info(credentials_dict,scopes=SCOPES)

        # Now use credentials as needed
        request = Request()
        credentials.refresh(request)
        access_token = credentials.token
        user_device_token = user.device_token

        print("Credentials have been set up successfully.")
        # SERVICE_ACCOUNT_FILE="./service-account-file.json"
        # SCOPES = ['https://www.googleapis.com/auth/firebase.messaging']
        
        # credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE,scopes=SCOPES)
        # request = google.auth.transport.requests.Request()
        # credentials.refresh(request)
        # access_token = credentials.token
        # # The Firebase device token for the user. This should be saved in your user model or a related model.
        # user_device_token = user.device_token  # Assuming you have this field
        if not user_device_token:
            print("No device token found for user.")
            return  f"error sending no device for user"
        serialized_shift_data = json.dumps(shift_data)
        # Construct the notification payload
        payload = {
            "message":{
                'token': user_device_token,
                # 'notification': {
                #     'title': 'Upcoming Shift Reminder',
                #     'body': 'You have a shift scheduled for tomorrow.',
                #     # 'click_action': 'FLUTTER_NOTIFICATION_CLICK',
                #     # 'sound': 'default'
                # },
                'data': {
                    'title': 'Upcoming Shift Reminder',
                    'body': 'You have a shift scheduled for tomorrow.',
                    'type': 'shift_reminder',
                    'shift_data':serialized_shift_data,
                    'notification_log_id':str(notification_log_id),
                }
            }
        }
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        # Send the request to FCM
        response = requests.post('https://fcm.googleapis.com/v1/projects/appnotification-85128/messages:send', json=payload, headers=headers)
        if response.status_code == 200:
            print("Notification sent successfully.")
            return "success"
        else:
            response_data = json.loads(response.text)
            message = response_data.get('error', {}).get('message', '')
            print(f"Failed to send notification. Status Code: {response.status_code}, Response: {message}")
            return f"error sending {response.status_code}--{message}"
            
    except Exception as e:
        print(str(e))
        return f"error sending {str(e)}--{str(e)}"

