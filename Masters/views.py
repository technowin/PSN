import json
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login ,logout,get_user_model
from Account.forms import RegistrationForm
from Account.models import AssignedCompany, CustomUser
# import mysql.connector as sql
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
import pandas as pd
import openpyxl
from openpyxl.styles import Font

def masters(request):
    Db.closeConnection()
    m = Db.get_connection()
    cursor=m.cursor()
    pre_url = request.META.get('HTTP_REFERER')
    header = []
    data = []
    name = ''
    entity = ''
    type = ''
    try:
        if request.user.is_authenticated ==True:                
                global user
                user = request.user.id   

        if request.method=="GET":
            entity = request.GET.get('entity', '')
            type = request.GET.get('type', '')
            cursor.callproc("stp_get_masters",[entity,type,'name'])
            for result in cursor.stored_results():
                datalist1 = list(result.fetchall())
            name = datalist1[0][0]
            cursor.callproc("stp_get_masters", [entity, type, 'header'])
            for result in cursor.stored_results():
                header = list(result.fetchall())
            cursor.callproc("stp_get_masters",[entity,type,'data'])
            for result in cursor.stored_results():
                data = list(result.fetchall())

        if request.method=="POST":
            para = []
            entity = request.POST.get('entity', '')
            type = request.POST.get('type', '')
            
            cursor.callproc("stp_post_masters",[entity,type,user])
            for result in cursor.stored_results():
                    datalist = list(result.fetchall())
            if datalist[0][0] == "inserted":
                messages = 'Data inserted successfully !'
            elif datalist[0][0] == "updated":
                messages = 'Data updated successfully !'
            else : messages =  ' something went wrong !'
            
            response = {'result': datalist[0][0],'messages':messages}                       
            messages.success(request, messages)
                 
    except Exception as e:
        tb = traceback.extract_tb(e.__traceback__)
        fun = tb[0].name
        cursor.callproc("stp_error_log",[fun,str(e),request.user.id])  
        print(f"error: {e}")
        messages.error(request, 'Oops...! Something went wrong!')
        response = {'result': 'fail','messages ':'something went wrong !'}        
    finally:
        cursor.close()
        m.commit()
        m.close()
        Db.closeConnection()
        if request.method=="GET":
            return render(request,'Master/index.html', {'entity':entity,'type':type,'name':name,'header':header,'data':data,'pre_url':pre_url})
        elif request.method=="POST":  
            return JsonResponse(response,safe=False)
        


def sample_xlsx(request):
    Db.closeConnection()
    m = Db.get_connection()
    cursor=m.cursor()
    pre_url = request.META.get('HTTP_REFERER')
    response =''
    try:
        if request.user.is_authenticated ==True:                
                global user
                user = request.user.id   
        # Create a new workbook and select the active worksheet
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.title = 'Sample Format'
        columns = []
        if request.method=="GET":
            entity = request.GET.get('entity', '')
            type = request.GET.get('type', '')
        # Define the column headers
        cursor.callproc("stp_get_masters", [entity, type, 'sample_header'])
        for result in cursor.stored_results():
            columns = [col[0] for col in result.fetchall()]
        # columns = ['Column 1', 'Column 2', 'Column 3', 'Column 4', 'Column 5', 'Column 6']
        # Set the headers in bold
        for col_num, header in enumerate(columns, 1):
            cell = sheet.cell(row=1, column=col_num)
            cell.value = header
            cell.font = Font(bold=True)
        # Auto-fit the column widths
        for col in sheet.columns:
            max_length = 0
            column = col[0].column_letter  # Get the column letter
            for cell in col:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except Exception as e:
                    print(f"Error calculating width: {e}")

            adjusted_width = max_length + 2  # Add some padding
            sheet.column_dimensions[column].width = adjusted_width  # Make the headers bold
            # Set the response with the correct content type for an Excel file
            response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename=sample_format.xlsx'
            # Save the workbook to the response
            workbook.save(response)
    
    except Exception as e:
        tb = traceback.extract_tb(e.__traceback__)
        fun = tb[0].name
        cursor.callproc("stp_error_log",[fun,str(e),request.user.id])  
        print(f"error: {e}")
        messages.error(request, 'Oops...! Something went wrong!')
        response = {'result': 'fail','messages ':'something went wrong !'}        
    finally:
        cursor.close()
        m.commit()
        m.close()
        Db.closeConnection()
        return response