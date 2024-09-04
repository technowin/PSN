import json
import pydoc
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login ,logout,get_user_model
from Account.forms import RegistrationForm
from Account.models import *
import Db 
import bcrypt
from django.contrib.auth.decorators import login_required
from Masters.serializers import ScRosterSerializer
from Notification.models import notification_log
from Notification.serializers import NotificationSerializer
from PSN.encryption import *
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph
from Account.utils import decrypt_email, encrypt_email
import requests
import traceback
import pandas as pd
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.contrib import messages
import openpyxl
from openpyxl.styles import Font, Border, Side
import calendar
from datetime import datetime, timedelta
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q, Count

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import AccessToken
from django.utils import timezone
from .models import sc_roster, sc_employee_master, CustomUser 


def masters(request):
    Db.closeConnection()
    m = Db.get_connection()
    cursor=m.cursor()
    pre_url = request.META.get('HTTP_REFERER')
    header, data = [], []
    entity, type, name = '', '', ''

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
            cursor.callproc("stp_get_company_names")
            for result in cursor.stored_results():
                company_names = list(result.fetchall())
            if entity == 'r' and type == 'ed':
                month_year =str(request.GET.get('month', ''))
                if month_year == '':
                    year,month = '',''
                else: year,month = month_year.split('-')
                employee_id = request.GET.get('empid', '')
                cursor.callproc("stp_get_edit_roster",[employee_id,month,year,'1'])
                for result in cursor.stored_results():
                    data = list(result.fetchall())
                cursor.callproc("stp_get_edit_roster",[employee_id,month,year,'2'])
                for result in cursor.stored_results():
                    header = list(result.fetchall())
                
        if request.method=="POST":
            entity = request.POST.get('entity', '')
            type = request.POST.get('type', '')
            if entity == 'r' and type == 'ed':
                ids = request.POST.getlist('ids[]', '')
                shifts = request.POST.getlist('shifts[]', '')
                for id,shift in zip(ids, shifts):
                    cursor.callproc("stp_post_roster",[id,shift])
                    for result in cursor.stored_results():
                        datalist = list(result.fetchall())
            if datalist[0][0] == "success":
                type='i'
                messages.success(request, 'Data updated successfully !')
            else : messages.error(request, 'Oops...! Something went wrong!')
                             
    except Exception as e:
        tb = traceback.extract_tb(e.__traceback__)
        fun = tb[0].name
        cursor.callproc("stp_error_log",[fun,str(e),request.user.id])  
        messages.error(request, 'Oops...! Something went wrong!')
    finally:
        cursor.close()
        m.commit()
        m.close()
        Db.closeConnection()
        if request.method=="GET":
            return render(request,'Master/index.html', {'entity':entity,'type':type,'name':name,'header':header,'data':data,'company_names': company_names,'pre_url':pre_url})
        elif request.method=="POST":  
            new_url = f'/masters?entity={entity}&type={type}'
            return redirect(new_url) 
        
def gen_roster_xlsx_col(columns,month_input):
    year, month = map(int, month_input.split('-'))
    _, num_days = calendar.monthrange(year, month)
    date_columns = [(datetime(year, month, day)).strftime('%d-%m-%Y') for day in range(1, num_days + 1)]
    columns.extend(date_columns)
    return columns
        
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
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.title = 'Sample Format'
        columns = []
        if request.method=="GET":
            entity = request.GET.get('entity', '')
            type = request.GET.get('type', '')
        if request.method=="POST":
            entity = request.POST.get('entity', '')
            type = request.POST.get('type', '')
        file_name = {'em': 'Employee Master','sm': 'Worksite Master','cm': 'Company Master','r': 'Roster'}[entity]
        cursor.callproc("stp_get_masters", [entity, type, 'sample_xlsx'])
        for result in cursor.stored_results():
            columns = [col[0] for col in result.fetchall()]
        # columns = ['Column 1', 'Column 2', 'Column 3']
        if entity == "r":
            month = request.POST.get('month', '')
            columns = gen_roster_xlsx_col(columns,month)

        black_border = Border(
            left=Side(border_style="thin", color="000000"),
            right=Side(border_style="thin", color="000000"),
            top=Side(border_style="thin", color="000000"),
            bottom=Side(border_style="thin", color="000000")
        )
        
        for col_num, header in enumerate(columns, 1):
            cell = sheet.cell(row=1, column=col_num)
            cell.value = header
            cell.font = Font(bold=True)
            cell.border = black_border
        
        for col in sheet.columns:
            max_length = 0
            column = col[0].column_letter  
            for cell in col:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
                    
            adjusted_width = max_length + 2 
            sheet.column_dimensions[column].width = adjusted_width  
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="' + str(file_name) +" "+str(datetime.now().strftime("%d-%m-%Y")) + '.xlsx"'
        workbook.save(response)
    
    except Exception as e:
        tb = traceback.extract_tb(e.__traceback__)
        fun = tb[0].name
        cursor.callproc("stp_error_log",[fun,str(e),request.user.id])  
        messages.error(request, 'Oops...! Something went wrong!')
    finally:
        cursor.close()
        m.commit()
        m.close()
        Db.closeConnection()
        return response      
  
def roster_upload(request):
    Db.closeConnection()
    m = Db.get_connection()
    cursor = m.cursor()
    if request.method == 'POST' and request.FILES.get('roster_file'):
        try:
            excel_file = request.FILES['roster_file']
            file_name = excel_file.name
            df = pd.read_excel(excel_file)

            entity = request.POST.get('entity', '')
            type = request.POST.get('type', '')
            company_id = request.POST.get('company_id', '')
            month_input  =str(request.POST.get('month_year', ''))
            total_rows = len(df)
            update_count = error_count = success_count = 0
            checksum_id = None
            worksites = []

            if entity == 'r':
                year, month = map(int, month_input.split('-'))
                _, num_days = calendar.monthrange(year, month)
                date_columns = [(datetime(year, month, day)).strftime('%d-%m-%Y') for day in range(1, num_days + 1)]
                cursor.callproc("stp_get_masters", [entity, type, 'sample_xlsx'])
                for result in cursor.stored_results():
                    start_columns = [col[0] for col in result.fetchall()]

                if not all(col in df.columns for col in start_columns + date_columns):
                    messages.error(request, 'Oops...! The uploaded Excel file does not contain the required columns.!')
                    return redirect(f'/masters?entity={entity}&type={type}')
                
                cursor.callproc('stp_insert_checksum', ('roster',company_id,month,year,file_name))
                for result in cursor.stored_results():
                    c = list(result.fetchall())
                checksum_id = c[0][0]
                
                for index,row in df.iterrows():
                    employee_id = row.get('Employee Id', '')
                    employee_name = row.get('Employee Name', '')
                    worksite  = row.get('Worksite', '')
                    
                    for date_col in date_columns:
                        shift_date = datetime.strptime(date_col, '%d-%m-%Y').date()
                        shift_time = row.get(date_col, '')  
                        params = (str(employee_id),employee_name,int(company_id),worksite,shift_date,shift_time,checksum_id)
                        cursor.callproc('stp_insert_roster', params)
                        for result in cursor.stored_results():
                            r = list(result.fetchall())
                        if r[0][0] not in ("success", "updated"):
                            if worksite not in worksites:
                                worksites.append(worksite)
                            error_message = str(r[0][0])
                            error_params = ('roster', company_id,worksite,file_name,shift_date,error_message,checksum_id)
                            cursor.callproc('stp_insert_error_log', error_params)
                            messages.error(request, "Errors occurred during upload. Please check error logs.")
                    if r[0][0] == "success": success_count += 1
                    elif r[0][0] == "updated": update_count += 1  
                    else: error_count += 1
                checksum_msg = f"Total Rows Processed: {total_rows}, Successful Entries: {success_count}, Updates: {update_count}, Errors: {error_count}"
                cursor.callproc('stp_update_checksum', ('roster',company_id,', '.join(worksites),month,year,file_name,checksum_msg,error_count,update_count,checksum_id))
                if error_count == 0 and update_count == 0 and success_count > 0:
                    messages.success(request, f"All data uploaded successfully!.")
                elif error_count == 0 and success_count == 0 and update_count > 0:
                    messages.warning(request, f"All data updated successfully!.")
                else:
                    messages.warning(request, f"The upload processed {total_rows} rows, resulting in {success_count} successful entries, {update_count} updates, and {error_count} errors; please check the error logs for details.")
                    
        except Exception as e:
            tb = traceback.extract_tb(e.__traceback__)
            fun = tb[0].name
            cursor.callproc("stp_error_log", [fun, str(e), request.user.id])  
            messages.error(request, 'Oops...! Something went wrong!')
            m.commit()   

        finally:
            cursor.close()
            m.close()
            Db.closeConnection()
            return redirect(f'/masters?entity={entity}&type={type}')     
        
def site_master(request):
    Db.closeConnection()
    m = Db.get_connection()
    cursor=m.cursor()
    try:
        if request.user.is_authenticated ==True:                      
            global user
            user = request.user.id  
        
        if request.method == "GET":
            cursor.callproc("stp_get_roster_type")
            for result in cursor.stored_results():
                roster_types = list(result.fetchall())
                # Call stored procedure to get company names
            cursor.callproc("stp_get_company_names")
            for result in cursor.stored_results():
                company_names = list(result.fetchall())
            site_id = request.GET.get('site_id', '')
            if site_id == "0":
                if request.method == "GET":
                    context = {'company_names': company_names, 'roster_type': roster_types,'site_id':site_id}

            else:
                cursor.callproc("stp_edit_site_master", (site_id,)) 
                for result in cursor.stored_results():
                    data = result.fetchall()[0]  
                    context = {
                        'roster_types':roster_types,
                        'company_names':company_names,
                        'site_id' : data[0],
                        'site_name': data[1],
                        'site_address': data[2],
                        'pincode': data[3],
                        'contact_person_name': data[4],
                        'contact_person_email': data[5], 
                        'contact_person_mobile_no': data[6],
                        'is_active':data[7],
                        'no_of_days': data[8],               
                        'notification_time': data[9],
                        'reminder_time': data[10],
                        'company_name' :data[11],
                        'roster_type': data[13]
                    }

        if request.method == "POST":
            siteId = request.POST.get('site_id', '')
            if siteId == "0":
                response_data = {"status": "fail"}
                
                siteName = request.POST.get('siteName', '')
                siteAddress = request.POST.get('siteAddress', '')
                pincode = request.POST.get('pincode', '')
                contactPersonName = request.POST.get('contactPersonName', '')
                contactPersonEmail = request.POST.get('contactPersonEmail', '')
                contactPersonMobileNo = request.POST.get('Number', '')  
                # is_active = request.POST.get('status_value', '') 
                # noOfDays = request.POST.get('FieldDays', '')  
                # notificationTime = request.POST.get('notificationTime', '')
                # ReminderTime = request.POST.get('ReminderTime', '')
                companyId = request.POST.get('company_id', '')  
                # rosterType = request.POST.get('roster_type', '')
               
                params = [
                    siteName, 
                    siteAddress, 
                    pincode, 
                    contactPersonName, 
                    contactPersonEmail, 
                    contactPersonMobileNo, 
                    # is_active,
                    # noOfDays, 
                    # notificationTime, 
                    # ReminderTime, 
                    companyId
                    # rosterType
                ]
                
                cursor.callproc("stp_insert_site_master", params)
                messages.success(request, "Data successfully entered!")

            else:
                if request.method == "POST" :
                    siteId = request.POST.get('site_id', '')
                    siteName = request.POST.get('siteName', '')
                    siteAddress = request.POST.get('siteAddress', '')
                    pincode = request.POST.get('pincode', '')
                    contactPersonName = request.POST.get('contactPersonName', '')
                    contactPersonEmail = request.POST.get('contactPersonEmail', '')
                    contactPersonMobileNo = request.POST.get('Number', '')  
                    # noOfDays = request.POST.get('FieldDays', '') 
                    isActive = request.POST.get('status_value', '')
                    # notificationTime = request.POST.get('notificationTime', '')
                    # ReminderTime = request.POST.get('ReminderTime', '')
                    CompanyId = request.POST.get('company_id', '')
                    # Rostertype = request.POST.get('roster_type', '')
                    
                    params = [siteId,siteName,siteAddress,pincode,contactPersonName,contactPersonEmail,
                                        contactPersonMobileNo,isActive,CompanyId]
                    cursor.callproc("stp_update_site_master",params) 
                    messages.success(request, "Data updated successfully...!")

    except Exception as e:
        tb = traceback.extract_tb(e.__traceback__)
        fun = tb[0].name
        cursor.callproc("stp_error_log", [fun, str(e), request.user.id])  
        messages.error(request, 'Oops...! Something went wrong!')
    finally:
        cursor.close()
        m.commit()
        m.close()
        Db.closeConnection()
            
        if request.method=="GET":
            return render(request, "Master/site_master.html", context)
        elif request.method=="POST":  
            return redirect( f'/masters?entity=sm&type=i')
        
def company_master(request):
    Db.closeConnection()
    m = Db.get_connection()
    cursor=m.cursor()
    try:
        if request.user.is_authenticated ==True:                      
            global user
            user = request.user.id  
        
        if request.method == "GET":
        
            company_id = request.GET.get('company_id', '')
            if company_id == "0":
                if request.method == "GET":
                    context = {'company_id':company_id}
            else:
                cursor.callproc("stp_edit_company_master", (company_id,))  # Note the comma to make it a tuple
                for result in cursor.stored_results():
                    data = result.fetchall()[0]  
                        
                    context = {
                        'company_id' : data[0],
                        'company_name': data[1],
                        'company_address': data[2],
                        'pincode': data[3],
                        'contact_person_name': data[4],
                        'contact_person_email': data[5], 
                        'contact_person_mobile_no': data[6],
                        'is_active':data[7]
                    }

        if request.method == "POST" :
            company_id = request.POST.get('company_id', '')
            if company_id == '0':
                response_data = {"status": "fail"}
                company_name = request.POST.get('company_name', '')
                company_address = request.POST.get('company_address', '')
                pincode = request.POST.get('pincode', '')
                contact_person_name = request.POST.get('contact_person_name', '')
                contact_person_email = request.POST.get('contact_person_email', '')
                contact_person_mobile_no = request.POST.get('contact_person_mobile_no', '') 
                # is_active = request.POST.get('status_value', '') 
                params = [
                    company_name, 
                    company_address, 
                    pincode, 
                    contact_person_name,
                    contact_person_email,
                    contact_person_mobile_no
                    # is_active
                ]
                cursor.callproc("stp_insert_company_master", params)
                messages.success(request, "Data successfully entered...!")
            else :
                company_id = request.POST.get('company_id', '')
                company_name = request.POST.get('company_name', '')
                company_address = request.POST.get('company_address', '')
                pincode = request.POST.get('pincode', '')
                contact_person_name = request.POST.get('contact_person_name', '')
                contact_person_email = request.POST.get('contact_person_email', '')
                contact_person_mobile_no = request.POST.get('contact_person_mobile_no', '') 
                is_active = request.POST.get('status_value', '') 
                   
                params = [company_id,company_name,company_address,pincode,contact_person_name,contact_person_email,
                                            contact_person_mobile_no,is_active]    
                cursor.callproc("stp_update_company_master",params) 
                messages.success(request, "Data updated successfully ...!")
                
    except Exception as e:
        tb = traceback.extract_tb(e.__traceback__)
        fun = tb[0].name
        cursor.callproc("stp_error_log", [fun, str(e), request.user.id])  
        messages.error(request, 'Oops...! Something went wrong!')
    finally:
        cursor.close()
        m.commit()
        m.close()
        Db.closeConnection()

        encrypted_id = encrypt_parameter(company_id)
            
        if request.method=="GET":
            return render(request, "Master/company_master.html", context)
        elif request.method == "POST":
            return redirect(f'/masters?entity=cm&type=i')
        
def employee_master(request):
    Db.closeConnection()
    m = Db.get_connection()
    cursor=m.cursor()
    try:
        if request.user.is_authenticated ==True:                      
            global user
            user = request.user.id  
        if request.method == "GET":
            id = request.GET.get('id', '')

            cursor.callproc("stp_get_employee_status")
            for result in cursor.stored_results():
                employee_status = list(result.fetchall())
            if id == "0":
                if request.method == "GET":
                    context = {'id':id, 'employee_status':employee_status, 'employee_status_id': ''}

            else:
                cursor.callproc("stp_edit_employee_master", (id,))
                for result in cursor.stored_results():
                    data = result.fetchall()[0]  
                    context = {
                        'employee_status':employee_status,
                        'id':data[0],
                        'employee_id' : data[1],
                        'employee_name': data[2],
                        'mobile_no': data[3],
                        'current_location': data[4],
                        'employee_status_id': data[5],
                        'is_active': data[7]
                    }

        if request.method == "POST" :
            id = request.POST.get('id', '')
            if id == '0':

                employeeId = request.POST.get('employee_id', '')
                employeeName = request.POST.get('employee_name', '')
                mobileNo = request.POST.get('mobile_no', '')
                currentLocation = request.POST.get('current_location', '')
                # employeeStatus = request.POST.get('employee_status_name', '')
                # activebtn = request.POST.get('status_value', '')

                params = [
                    employeeId, 
                    employeeName, 
                    mobileNo, 
                    currentLocation
                    # employeeStatus,
                    # activebtn
                ]
                
                cursor.callproc("stp_insert_employee_master", params)
                messages.success(request, "Data successfully entered!")
            else:
                id = request.POST.get('id', '')
                employee_id = request.POST.get('employee_id', '')
                employee_name = request.POST.get('employee_name', '')
                mobile_no = request.POST.get('mobile_no', '')
                current_location = request.POST.get('current_location', '')
                employee_status = request.POST.get('employee_status_name', '')
                is_active = request.POST.get('status_value', '')  
                            
                params = [id,employee_id,employee_name,mobile_no,current_location,employee_status,is_active]    
                cursor.callproc("stp_update_employee_master",params) 
                messages.success(request, "Data successfully Updated!")

    except Exception as e:
        tb = traceback.extract_tb(e.__traceback__)
        fun = tb[0].name
        cursor.callproc("stp_error_log", [fun, str(e), request.user.id])  
        messages.error(request, 'Oops...! Something went wrong!')
    finally:
        cursor.close()
        m.commit()
        m.close()
        Db.closeConnection()
        if request.method=="GET":
            return render(request, "Master/employee_master.html", context)
        elif request.method=="POST":  
            return redirect(f'/masters?entity=em&type=i')
    
def upload_excel(request):

    if request.method == 'POST' and request.FILES.get('excelFile'):
        excel_file = request.FILES['excelFile']
        file_name = excel_file.name
        df = pd.read_excel(excel_file)
        total_rows = len(df)
        update_count = error_count = success_count = 0
        checksum_id = None
        r=None
        try:
            Db.closeConnection()
            m = Db.get_connection()
            cursor = m.cursor()
            entity = request.POST.get('entity', '')
            type = request.POST.get('type', '')
            company_id = request.POST.get('company_id', None)
            cursor.callproc("stp_get_masters", [entity, type, 'sample_xlsx'])
            for result in cursor.stored_results():
                columns = [col[0] for col in result.fetchall()]
            if not all(col in df.columns for col in columns):
                messages.error(request, 'Oops...! The uploaded Excel file does not contain the required columns.!')
                return redirect(f'/masters?entity={entity}&type={type}')
            upload_for = {'em': 'employee master','sm': 'site master','cm': 'company master','r': 'roster'}[entity]
            cursor.callproc('stp_insert_checksum', (upload_for,company_id,str(datetime.now().month),str(datetime.now().year),file_name))
            for result in cursor.stored_results():
                c = list(result.fetchall())
            checksum_id = c[0][0]

            if entity == 'em':
                for index,row in df.iterrows():
                    params = tuple(str(row.get(column, '')) for column in columns)
                    cursor.callproc('stp_insert_employee_master', params)
                    for result in cursor.stored_results():
                            r = list(result.fetchall())
                    if r[0][0] not in ("success", "updated"):
                        cursor.callproc('stp_insert_error_log', [upload_for, company_id,'',file_name,datetime.now().date(),str(r[0][0]),checksum_id])
                    if r[0][0] == "success": success_count += 1 
                    elif r[0][0] == "updated": update_count += 1  
                    else: error_count += 1
            elif entity == 'sm':
                for index,row in df.iterrows():
                    params = tuple(str(row.get(column, '')) for column in columns)
                    params += (str(company_id),)
                    cursor.callproc('stp_insert_site_master', params)
                    for result in cursor.stored_results():
                            r = list(result.fetchall())
                    if r[0][0] not in ("success", "updated"):
                        cursor.callproc('stp_insert_error_log', [upload_for, company_id,'',file_name,datetime.now().date(),str(r[0][0]),checksum_id])
                    if r[0][0] == "success": success_count += 1 
                    elif r[0][0] == "updated": update_count += 1  
                    else: error_count += 1
            elif entity == 'cm':
                for index,row in df.iterrows():
                    params = tuple(str(row.get(column, '')) for column in columns)
                    cursor.callproc('stp_insert_company_master', params)
                    for result in cursor.stored_results():
                            r = list(result.fetchall())
                    if r[0][0] not in ("success", "updated"):
                        cursor.callproc('stp_insert_error_log', [upload_for, company_id,'',file_name,datetime.now().date(),str(r[0][0]),checksum_id])
                    if r[0][0] == "success": success_count += 1 
                    elif r[0][0] == "updated": update_count += 1  
                    else: error_count += 1
            checksum_msg = f"Total Rows Processed: {total_rows}, Successful Entries: {success_count}" f"{f', Updates: {update_count}' if update_count > 0 else ''}" f"{f', Errors: {error_count}' if error_count > 0 else ''}"
            cursor.callproc('stp_update_checksum', (upload_for,company_id,'',str(datetime.now().month),str(datetime.now().year),file_name,checksum_msg,error_count,update_count,checksum_id))
            if error_count == 0 and update_count == 0 and success_count > 0:
                messages.success(request, f"All data uploaded successfully!.")
            elif error_count == 0 and success_count == 0 and update_count > 0:
                messages.warning(request, f"All data updated successfully!.")
            else:messages.warning(request, f"The upload processed {total_rows} rows, resulting in {success_count} successful entries"  f"{f', {update_count} updates' if update_count > 0 else ''}" f", and {error_count} errors; please check the error logs for details.")
                   
        except Exception as e:
            tb = traceback.extract_tb(e.__traceback__)
            fun = tb[0].name
            cursor.callproc("stp_error_log", [fun, str(e), request.user.id])  
            messages.error(request, 'Oops...! Something went wrong!')
            m.commit()   
        finally:
            cursor.close()
            m.close()
            Db.closeConnection()
            return redirect(f'/masters?entity={entity}&type=i')

class RosterDataAPIView(APIView):
    # Ensure the user is authenticated using JWT
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        # Extract user ID from the JWT token
        user = request.user  # This will get the user from the JWT token

        # Call the function to get the roster data
        roster_data = self.get_roster_data(user.id)

        return Response(roster_data)

    def get_roster_data(self, user_id):
        # Step 1: Get the user by user_id
        user = CustomUser.objects.get(id=user_id)
        
        # Step 2: Get the phone number of the user
        phone_number = user.phone

        # Step 3: Get the employee_id from sc_employee_master using the phone number
        try:
            employee = sc_employee_master.objects.get(mobile_no=phone_number)
        except sc_employee_master.DoesNotExist:
            return {
                'error': 'Employee not found'
            }
        employee_id = employee.employee_id

        # Step 4: Get the current date and the first date of the current month
        current_date = timezone.now().date()

        # Step 5: Query sc_roster for the current month and categorize the data
        current_roster_qs = sc_roster.objects.filter(
            employee_id=employee_id,
            shift_date__gte=current_date
        )
        
        current_roster_qsser = ScRosterSerializer(current_roster_qs, many=True)

        previous_roster_qs = sc_roster.objects.filter(
            employee_id=employee_id,
            shift_date__lt=current_date
        )
        previous_roster_qsser = ScRosterSerializer(previous_roster_qs, many=True)

        marked_roster_qs = sc_roster.objects.filter(
            employee_id=employee_id,
            confirmation__isnull=False 
        )
        marked_roster_qsser = ScRosterSerializer(marked_roster_qs, many=True)

        unmarked_roster_qs = sc_roster.objects.filter(
            employee_id=employee_id,
            confirmation__isnull=True ,
            shift_date__lt=current_date
        )
        unmarked_roster_qsser = ScRosterSerializer(unmarked_roster_qs, many=True)

        # Count the number of rows in each query set
        current_roster_count = len(current_roster_qsser.data)
        previous_roster_count = len(previous_roster_qsser.data)
        marked_roster_count = len(marked_roster_qsser.data)
        unmarked_roster_count = len(unmarked_roster_qsser.data)

        # Return the counts and the lists
        return {
            'current_roster_count': current_roster_count,
            'current_roster_list': list(current_roster_qsser.data ),  # Using .values() to serialize queryset
            'previous_roster_count': previous_roster_count,
            'previous_roster_list': list(previous_roster_qsser.data),  # Using .values() to serialize queryset
            'marked_roster_count': marked_roster_count,
            'marked_roster_list': list(marked_roster_qsser.data),  # Using .values() to serialize queryset
            'unmarked_roster_count': unmarked_roster_count,
            'unmarked_roster_list': list(unmarked_roster_qsser.data),  # Using .values() to serialize queryset
            'roster_list': list(current_roster_qsser.data)  # Same as Current Roster List
        }

class confirm_schedule(APIView):
    # Ensure the user is authenticated using JWT
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    # authentication_classes = []

    def post(self, request):
        try:
            data= request.data
            roster_id = request.data.get('id')
            confirmation = request.data.get('confirmation') == '1'
            user = request.user
            roster = sc_roster.objects.get(id=roster_id)
            roster.confirmation = confirmation
            roster.updated_at = timezone.now()
            roster.updated_by = user
            roster.save()
            ser = ScRosterSerializer(roster)

            return Response({'success': 'Confirmation updated successfully.','data':ser.data,'con':confirmation}, status=200)
        except sc_roster.DoesNotExist:
            return Response({'error': 'Roster not found.'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=500)



class confirm_notification(APIView):
    # Ensure the user is authenticated using JWT
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    # authentication_classes = []

    def post(self, request):
        try:
            data= request.data
            notification_id = request.data.get('id')
            confirmation = request.data.get('confirmation') == '1'
            user = request.user
            notification = notification_log.objects.get(id=notification_id)
            notification.notification_opened = timezone.now()
            notification.updated_at = timezone.now()
            notification.updated_by = user
            notification.save()
            ser = NotificationSerializer(notification)

            return Response({'success': 'Confirmation updated successfully.','data':ser.data,'con':confirmation}, status=200)
        except notification_log.DoesNotExist:
            return Response({'error': 'notification_log not found.'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=500)

    