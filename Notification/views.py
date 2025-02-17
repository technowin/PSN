from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse
from django.utils.timezone import now
from datetime import date, timedelta

from Masters.models import *
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
from Notification.models import notification_log, test_table
from datetime import datetime, timedelta

from Notification.serializers import NotificationLogSerializer, TestTableSerializer
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
            current_date = datetime.now().date()
            next_day = current_date + timedelta(days=1)
            shifts = sc_roster.objects.filter(employee_id=employee.employee_id,confirmation__isnull=True,  shift_date__in=[current_date, next_day] ) # Filters for today or tomorrow )
            
            filtered_shifts = []

            # Current datetime
            if shifts.exists():
            
                current_datetime = datetime.now()
                ser =  ScRosterSerializer(shifts,many=True)
                for shift in shifts:
                    # shift = shifts.first() 
                    if '-' in shift.shift_time:
                        # Split 'shift_time' by '-'
                        start_time_str, end_time_str = shift.shift_time.split('-')
                        # Trim the whitespace from both parts
                        start_time_str = start_time_str.strip()
                        end_time_str = end_time_str.strip()

                        # Combine the shift_date and start_time to create a datetime object
                        shift_datetime_str = f"{shift.shift_date} {start_time_str}"
                        shift_datetime = datetime.strptime(shift_datetime_str, '%Y-%m-%d %H:%M')
                        shift_datetime_minus_4_hours = shift_datetime - timedelta(hours=4)
                        # Check if the shift_datetime is within the next 24 hours from the current datetime
                        if current_datetime <= shift_datetime <= current_datetime + timedelta(hours=24) and current_datetime <= shift_datetime_minus_4_hours:
                            
                            # Add to the filtered_shifts list if it meets the condition
                            existing_notification = notification_log.objects.filter(sc_roster_id=shift,type_id =11).exists()
                        
                            if not existing_notification:
                                filtered_shifts.append(shift)
                                
                                
                                serializer = ScRosterSerializer(shift)
                                
                                shift_data = serializer.data
                                parameter_type = parameter_master.objects.get(parameter_id=11)
                                notification_entry = notification_log.objects.create(
                                    sc_roster_id=shift,
                                    notification_sent=current_time,
                                    notification_message="Notification for shift confirmation",
                                    created_at=current_time,
                                    type=parameter_type ,
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

            

class check_and_notify_all_users_reminder(APIView):
    
    def get(self, request):
        users = CustomUser.objects.all()
        current_time = timezone.now()
        errors = []
        success = []
        for user in users:
            employee = sc_employee_master.objects.filter(mobile_no=user.phone).first()

            if not employee:
                continue

            current_date = current_time.date()
            next_day = current_date + timedelta(days=1)
            
            shifts = sc_roster.objects.filter(
                employee_id=employee.employee_id,
                confirmation__isnull=True,
                shift_date__in=[current_date, next_day]
            )

            if shifts.exists():
                current_datetime = current_time
                for shift in shifts:
                    if '-' in shift.shift_time:
                        start_time_str, end_time_str = shift.shift_time.split('-')
                        start_time_str = start_time_str.strip()
                        
                        shift_datetime_str = f"{shift.shift_date} {start_time_str}"
                        shift_datetime = timezone.datetime.strptime(shift_datetime_str, '%Y-%m-%d %H:%M').astimezone(timezone.get_current_timezone())
                        shift_datetime_minus_4_hours = shift_datetime - timedelta(hours=4)
                        shift_datetime_minus_8_hours = shift_datetime - timedelta(hours=8)

                        if shift_datetime_minus_8_hours <= current_datetime <= shift_datetime_minus_4_hours:
                            existing_notification = notification_log.objects.filter(sc_roster_id=shift, type_id=12).exists()
                            
                            if not existing_notification:
                                serializer = ScRosterSerializer(shift)
                                shift_data = serializer.data
                                parameter_type = parameter_master.objects.get(parameter_id=12)
                                
                                notification_entry = notification_log.objects.create(
                                    sc_roster_id=shift,
                                    notification_sent=current_time,
                                    notification_message="Notification for shift confirmation",
                                    created_at=current_time,
                                    type=parameter_type,
                                    created_by=user,
                                    updated_at=current_time,
                                    updated_by=user
                                )
                                notification_log_id = notification_entry.id
                                notification_status = send_push_notification(user, shift_data, notification_log_id)

                                if notification_status != "success":
                                    error_message = notification_status.split("--")
                                    if len(error_message) == 2:
                                        if error_message[1] == "Requested entity was not found.":
                                            notification_entry.notification_message = "App is not installed"
                                        elif error_message[1] == "The registration token is not a valid FCM registration token":
                                            notification_entry.notification_message = "User not correctly registered to the app. Please log in again."
                                    else:
                                        notification_entry.notification_message = notification_status
                                    notification_entry.save()
                                    errors.append(f"Error sending notification to {user.full_name} - {notification_status}")
                                else:
                                    notification_entry.notification_received = timezone.now()
                                    notification_entry.save()
                                    success.append(f"Successfully sent notification to {user.full_name}")

        response_data = {'success': success}
        if errors:
            response_data['error'] = errors
        return Response(response_data, status=status.HTTP_200_OK)
            
            
class TestApi(APIView):
    def post(self, request):
        # Create a new instance of TestTable with the current timestamp
        test_instance = test_table.objects.create(test_time=timezone.now())
        
        # Serialize the newly created instance
        serializer = TestTableSerializer(test_instance)
        
        # Return the serialized data with a 201 CREATED status
        return Response(serializer.data, status=status.HTTP_201_CREATED)



class check_and_notify_default_users(APIView):
    def get(self, request):
        errors=[]
        success=[]
# 1. Filter sc_roster records based on the provided conditions
        roster_records = sc_roster.objects.filter(
            attendance_date__isnull=False,
            confirmation=True,
            attendance_in__isnull=True
        )

        # 2. Get employee_ids from the filtered sc_roster records
        employee_ids = roster_records.values_list('employee_id', flat=True)

        # 3. Find matching employees in sc_employee_master using employee_id
        matching_employees = sc_employee_master.objects.filter(employee_id__in=employee_ids)

        # # 4. Get the mobile numbers of the matched employees
        # employee_phones = matching_employees.values_list('mobile_no', flat=True)

        # # 5. Find matching CustomUser records using mobile_no (phone field)
        # matching_users = CustomUser.objects.filter(phone__in=employee_phones)

        # 6. Loop through matching employees and process all roster records for each employee
        for employee in matching_employees:
            # Get all roster records for the current employee
            employee_roster_records = roster_records.filter(employee_id=employee.employee_id)

            # Find the corresponding CustomUser (based on phone number)
            user = CustomUser.objects.filter(phone=employee.mobile_no).first()

            # If the user is found, process each roster record for this employee
            if user:
                for shift in employee_roster_records:
                    # Send each roster record and user to the function
                    serializer = ScRosterSerializer(shift)
                    shift_data = serializer.data
                    parameter_type = parameter_master.objects.get(parameter_id=13)
                    current_time = timezone.now()
                    
                    notification_entry = notification_log.objects.create(
                        sc_roster_id=shift,
                        notification_sent=current_time,
                        notification_message="Defaulter Notice!!!",
                        created_at=current_time,
                        type=parameter_type ,
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
                    # process_notification(user, roster_record)
            
                    

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
                'notification': {
                    'title': 'Upcoming Shift Reminder',
                    'body': 'You have a shift scheduled for tomorrow.',
                    # "click_action": "FLUTTER_NOTIFICATION_CLICK"
                    # 'click_action': 'FLUTTER_NOTIFICATION_CLICK',
                    # 'sound': 'default'
                },
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

def process_notification(user, roster_record):
    print(1)
    # Example: processing each roster record and sending notification
    # send_notification(user, f"Attendance reminder for employee: {roster_record.employee_id} on date: {roster_record.shift_date}")

class DefaultRecords(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        try:
            # Step 1: Extract user from JWT token
            user = request.user  # This gets the user from the JWT token if authenticated

            # Step 2: Check if the user's role_id is 5
            if user.role_id != 5:
                return Response(
                    {"error": "You are not authorized to access this resource."},
                    status=status.HTTP_403_FORBIDDEN
                )

            # Step 3: Fetch all users with role_id = 5
            users = CustomUser.objects.filter(role_id=5)

            result = []

            for custom_user in users:
                try:
                    # Step 4: Fetch the employee_id from sc_employee_master using custom_user
                    employee_record = sc_employee_master.objects.filter(mobile_no=custom_user.phone).first()

                    if not employee_record:
                        # Skip this user if employee record doesn't exist
                        continue

                    # Step 5: Using the employee_id, fetch the sc_roster records with specified conditions
                    employee_id = employee_record.employee_id
                    roster_records = sc_roster.objects.filter(
                        employee_id=employee_id,
                        attendance_uploaded_date__isnull=True,  # attendance_date is not null
                        confirmation=True,  # confirmation is true
                        attendance_in__isnull=True # attendance_in is null
                    )

                    # Step 6: If roster records exist, serialize and add them to the result
                    if roster_records.exists():
                        data = ScRosterSerializer(roster_records, many=True)
                        result.append(data.data)

                except Exception as e:
                    # Log any errors encountered while processing each user
                    continue

            if not result:
                return Response(
                    {"message": "No valid records found."},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Step 7: Return a success response with all results
            return Response(result, status=status.HTTP_200_OK)

        except Exception as e:
            # Step 8: Return a generic error response for any unhandled exceptions
            return Response(
                {"error": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

# class DefaultRecords(APIView):
#     permission_classes = [IsAuthenticated]
#     authentication_classes = [JWTAuthentication]

#     def get(self, request):
#         try:
#             # Extract user from JWT token
#             user = request.user  # This gets the user from the JWT token if authenticated

#             # Check if the user's role_id is 5
#             if user.role_id != 5:
#                 return Response(
#                     {"error": "You are not authorized to access this resource."},
#                     status=status.HTTP_403_FORBIDDEN
#                 )
            
#             # Get employee_id from request parameters
#             employee_id = request.data.get("employee_id")
#             if not employee_id:
#                 return Response(
#                     {"error": "Employee ID is required."},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )
            
#             # Fetch records from sc_roster where confirmation=True and attendance_in is NULL
#             roster_records = sc_roster.objects.filter(
#                         employee_id=employee_id,
#                         attendance_uploaded_date__isnull=True,  # attendance_date is not null
#                         confirmation=True,  # confirmation is true
#                         attendance_in__isnull=True # attendance_in is null
#                     )
            
#             if not roster_records.exists():
#                 return Response(
#                     {"message": "No valid records found."},
#                     status=status.HTTP_404_NOT_FOUND
#                 )
            
#             # Serialize and return the data
#             data = ScRosterSerializer(roster_records, many=True)
#             return Response(data.data, status=status.HTTP_200_OK)

#         except Exception as e:
#             return Response(
#                 {"error": f"An error occurred: {str(e)}"},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )




class show_notification(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def get(self, request):
        employee_id = request.data.get('employee_id')

        if not employee_id:
            return Response({"error": "employeeId is required"}, status=400)

        try:
            # Get the current and yesterday's date
            current_date = date.today()
            yesterday_date = current_date - timedelta(days=1)

            # Fetch sc_roster IDs where shift_date is today or yesterday
            roster_ids = sc_roster.objects.filter(
                shift_date__in=[current_date, yesterday_date],
                employee_id=employee_id
            ).values_list('id', flat=True)

            # Check if roster IDs are found
            if not roster_ids:
                return Response({"message": "No roster data found for this employee"}, status=404)

            # Fetch notifications based on the roster IDs
            notifications = notification_log.objects.filter(
                sc_roster_id__in=roster_ids,
                notification_received__isnull=False,
                notification_opened__isnull=True
            )

            # Check if notifications exist
            if not notifications.exists():
                return Response({"message": "No notifications found for this employee"})

            # Serialize and return the notifications
            serializer = NotificationLogSerializer(notifications, many=True)
            return Response(serializer.data, status=200)

        except Exception as e:
            return Response({"error": str(e)}, status=500)

        
    
class save_notification(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        try:
            # Extract the notification ID from the request data
            notification_id = request.data.get('id')
            employee_id = request.data.get('employee_id')

            number = sc_employee_master.objects.get(employee_id=employee_id).mobile_no
            user = CustomUser.objects.get(phone=number).id
            

            
            if not notification_id:
                return Response({"error": "Notification ID is required."}, status=status.HTTP_400_BAD_REQUEST)

            # Fetch the specific notification log entry
            notification = notification_log.objects.filter(id=notification_id).first()

            if not notification:
                return Response({"error": "Notification not found."}, status=status.HTTP_404_NOT_FOUND)

            # Update the `noti_click_time` to the current time
            notification.notification_opened = now()
            notification.updated_by = get_object_or_404(CustomUser, id = user)
            notification.save()

            return Response({"message": "Notification updated successfully."}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



