from django.shortcuts import render
import json
import random
import string
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render,redirect
from django.contrib.auth import authenticate, login ,logout,get_user_model
from Account.forms import RegistrationForm
from Account.models import AssignedCompany, CustomUser,MenuMaster,RoleMenuMaster,UserMenuDetails, OTPVerification, password_storage
from Masters.models import sc_roster
# import mysql.connector as sql
from Account.serializers import *
import Db 
import bcrypt
from django.contrib.auth.decorators import login_required
# from .models import SignUpModel
# from .forms import SignUpForm
from PSN.encryption import *
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph

from Account.utils import decrypt_email, encrypt_email
import requests
import traceback
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

# Counts Import
from django.db.models import Count


from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

def newdashboard(request):
    Db.closeConnection()
    m = Db.get_connection()
    cursor = m.cursor()
    
    try:
        # Call the procedure to get all counts at once
        cursor.callproc("stp_get_today_roster_graph",['1'])

        for result in cursor.stored_results():
            fetched_result = result.fetchone() 
            if fetched_result:
                yes_count = fetched_result[0] 
                no_count = fetched_result[1]
                pending_count = fetched_result[2]
                total_count = fetched_result[3]
                less_than_8_hours_count = fetched_result[4]
                more_than_8_hours_count = fetched_result[5]

        cursor.callproc("stp_get_tommorow_roster_graph",['1'])

        for result in cursor.stored_results():
            fetched_result = result.fetchone() 
            if fetched_result:
                nxtyes_count = fetched_result[0] 
                nxtno_count = fetched_result[1]
                nxtpending_count = fetched_result[2]
                nxttotal_count = fetched_result[3]
                nxtless_than_8_hours_count = fetched_result[4]
                nxtmore_than_8_hours_count = fetched_result[5]
        
        # Calculate percentages if total_count is greater than 0
        if total_count > 0:
            no_percentage = (int(no_count) / int(total_count)) * 100
            no_percentage = min(max(no_percentage, 0), 100)
            
            yes_percentage = (int(yes_count) / int(total_count)) * 100
            yes_percentage = min(max(yes_percentage, 0), 100)
        else:
            no_percentage = 0
            yes_percentage = 0
        
        # Fetch dropdown values for companies and sites
        cursor.callproc("stp_get_dropdown_values", ['company'])
        for result in cursor.stored_results():
            company_names = list(result.fetchall())

        cursor.callproc("stp_get_dropdown_values", ['site'])
        for result in cursor.stored_results():
            site_names = list(result.fetchall())
        
        # Context data to pass to the template
        context = {
            'total_count': total_count,
            'yes_count': yes_count,
            'no_count': no_count,
            'pending_count': pending_count,
            'no_percentage': no_percentage,
            'yes_percentage': yes_percentage,
            'less_than_8_hours_count': less_than_8_hours_count,
            'more_than_8_hours_count': more_than_8_hours_count,
            'nxttotal_count': nxttotal_count,
            'nxtyes_count': nxtyes_count,
            'nxtno_count': nxtno_count,
            'nxtpending_count': nxtpending_count,
            'nxtless_than_8_hours_count': nxtless_than_8_hours_count,
            'nxtmore_than_8_hours_count': nxtmore_than_8_hours_count,
            'company_names': company_names,
            'site_names': site_names,
        }
    
    except Exception as e:
        tb = traceback.extract_tb(e.__traceback__)
        fun = tb[0].name
        cursor.callproc("stp_error_log", [fun, str(e), request.user.id])
        print(f"error: {e}")
        messages.error(request, 'Oops...! Something went wrong!')
        response = {'result': 'fail', 'messages': 'something went wrong !'}
    
    # Render the dashboard template with the context data
    if request.method == "GET":
        return render(request, 'Dashboard/index.html', context)
    
from django.http import JsonResponse
import traceback

def GetRosterCount(request):
    Db.closeConnection()
    m = Db.get_connection()
    cursor = m.cursor()
    
    try:
        company_id = request.POST.get('companyName', '')
        worksite = request.POST.get('siteName', '')
        date = request.POST.get('selectedDate', '')
        cursor.callproc("stp_get_today_roster_graph_filter", [company_id, worksite, date])

        for result in cursor.stored_results():
            fetched_result = result.fetchone() 
            if fetched_result:
                yes_count = fetched_result[0] 
                no_count = fetched_result[1]
                pending_count = fetched_result[2]
                total_count = fetched_result[3]
                less_than_8_hours_count = fetched_result[4]
                more_than_8_hours_count = fetched_result[5]

            data = {
                'total_count': total_count,
                'yes_count': yes_count,
                'no_count': no_count,
                'pending_count': pending_count,
                'less_than_8_hours_count': less_than_8_hours_count,
                'more_than_8_hours_count': more_than_8_hours_count,
            }

    except Exception as e:
        tb = traceback.extract_tb(e.__traceback__)
        fun = tb[0].name
        cursor.callproc("stp_error_log", [fun, str(e), request.user.id])
        print(f"error: {e}")
        return JsonResponse({'result': 'fail', 'message': 'something went wrong!'}, status=500)

    return JsonResponse(data)



