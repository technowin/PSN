import json
import pydoc
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login ,logout,get_user_model
from Account.forms import RegistrationForm
from Account.models import AssignedCompany, CustomUser
import Db 
import bcrypt
from django.contrib.auth.decorators import login_required
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
            cursor.callproc("stp_get_company_names")
            for result in cursor.stored_results():
                company_names = list(result.fetchall())

        if request.method=="POST":
            entity = request.POST.get('entity', '')
            type = request.POST.get('type', '')
            cursor.callproc("stp_post_masters",[entity,type,user])
            for result in cursor.stored_results():
                    datalist = list(result.fetchall())
            if datalist[0][0] == "inserted":
                msg = 'Data inserted successfully !'
            elif datalist[0][0] == "updated":
                msg = 'Data updated successfully !'
            else : msg =  ' something went wrong !'
            
            messages.success(request, msg)
                 
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
        response['Content-Disposition'] = 'attachment; filename=sample_format.xlsx'
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
            new_url = f'/masters?entity={entity}&type={type}'
            
            total_row_inserted = 0
            count_error_log = 0
            deleted_count = 0
            inserted_error_id_list = []
            rows_inserted = 0
            inserted_error_id = 0

            if entity == 'r':
                year, month = map(int, month_input.split('-'))
                _, num_days = calendar.monthrange(year, month)
                date_columns = [(datetime(year, month, day)).strftime('%d-%m-%Y') for day in range(1, num_days + 1)]
                cursor.callproc("stp_get_masters", [entity, type, 'sample_xlsx'])
                for result in cursor.stored_results():
                    start_columns = [col[0] for col in result.fetchall()]

                if not all(col in df.columns for col in start_columns + date_columns):
                    # raise ValueError("The uploaded Excel file does not contain the required columns.")
                    messages.error(request, 'Oops...! The uploaded Excel file does not contain the required columns.!')
                    return redirect(new_url)

                # cursor.callproc("stp_delete_roster",[company_id, month, year])
                # for result in cursor.stored_results():
                #     datalist = list(result.fetchall())
                #     deleted_count = datalist[0][0]

                for index, row in df.iterrows():
                    employee_id = row.get('Employee Id', '')
                    employee_name = row.get('Employee Name', '')
                    worksite  = row.get('Worksite', '')
                    for date_col in date_columns:
                        shift_date = datetime.strptime(date_col, '%d-%m-%Y').date()
                        shift_time = row.get(date_col, '')  
                        params = (str(employee_id),employee_name,int(company_id),worksite,shift_date,shift_time)
                        cursor.callproc('stp_upload_roster', params)

                messages.success(request, "Data Uploaded successfully!")

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
            new_url = f'/masters?entity={entity}&type={type}'
            return redirect(new_url)     

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

            m.commit()
            
            site_id = request.GET.get('site_id', '')
            if site_id == "0":

                    if request.method == "GET":

                        m.commit()
                    
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
                is_active = request.POST.get('status_value', '') 
                noOfDays = request.POST.get('FieldDays', '')  
                notificationTime = request.POST.get('notificationTime', '')
                ReminderTime = request.POST.get('ReminderTime', '')
                companyId = request.POST.get('company_id', '')  
                rosterType = request.POST.get('roster_type', '')
               

                params = [
                    siteName, 
                    siteAddress, 
                    pincode, 
                    contactPersonName, 
                    contactPersonEmail, 
                    contactPersonMobileNo, 
                    is_active,
                    noOfDays, 
                    notificationTime, 
                    ReminderTime, 
                    companyId,
                    rosterType
                ]
                
                cursor.callproc("stp_insert_site_master", params)
                
                m.commit()

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
                    noOfDays = request.POST.get('FieldDays', '') 
                    isActive = request.POST.get('status_value', '')
                    notificationTime = request.POST.get('notificationTime', '')
                    ReminderTime = request.POST.get('ReminderTime', '')
                    CompanyId = request.POST.get('company_id', '')
                    Rostertype = request.POST.get('roster_type', '')
                    
                        
                    params = [siteId,siteName,siteAddress,pincode,contactPersonName,contactPersonEmail,
                                        contactPersonMobileNo,noOfDays,notificationTime,ReminderTime,isActive,CompanyId,Rostertype]
                    cursor.callproc("stp_update_site_master",params) 
                    m.commit()

                    messages.success(request, "Data updated successfully...!")

            
    except Exception as e:
        tb = traceback.extract_tb(e.__traceback__)
        fun = tb[0].name
        cursor.callproc("stp_error_log", [fun, str(e), request.user.id])  
        print(f"error: {e}")
        messages.error(request, 'Oops...! Something went wrong!')
        response = {'result': 'fail', 'messages': 'something went wrong!'} 


    finally:
        cursor.close()
        m.commit()
        m.close()
        Db.closeConnection()
            
        if request.method=="GET":
            return render(request, "Master/site_master.html", context)
        elif request.method=="POST":  
            new_url = f'/masters?entity=sm&type=i'
            return redirect(new_url)
        
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

                    m.commit()
                        
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
                is_active = request.POST.get('status_value', '') 

                params = [
                    company_name, 
                    company_address, 
                    pincode, 
                    contact_person_name,
                    contact_person_email,
                    contact_person_mobile_no,
                    is_active
                ]
                
                cursor.callproc("stp_insert_company_master", params)
                
                m.commit()

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
                m.commit()

                messages.success(request, "Data updated successfully ...!")

            
    except Exception as e:
        tb = traceback.extract_tb(e.__traceback__)
        fun = tb[0].name
        cursor.callproc("stp_error_log", [fun, str(e), request.user.id])  
        print(f"error: {e}")
        messages.error(request, 'Oops...! Something went wrong!')
        response = {'result': 'fail', 'messages': 'something went wrong!'} 

    finally:
        cursor.close()
        m.commit()
        m.close()
        Db.closeConnection()

        encrypted_id = encrypt_parameter(company_id)
            
        if request.method=="GET":
            return render(request, "Master/company_master.html", context)
        elif request.method == "POST":
            new_url = f'/masters?id={encrypted_id}'
            return redirect(new_url)
        
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

                            m.commit()
                        
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
                employeeStatus = request.POST.get('employee_status_name', '')
                activebtn = request.POST.get('status_value', '')

                params = [
                    employeeId, 
                    employeeName, 
                    mobileNo, 
                    currentLocation,
                    employeeStatus,
                    activebtn
                ]
                
                cursor.callproc("stp_insert_employee_master", params)
                
                m.commit()

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
                m.commit()

                messages.success(request, "Data successfully Updated!")


            
    except Exception as e:
        tb = traceback.extract_tb(e.__traceback__)
        fun = tb[0].name
        cursor.callproc("stp_error_log", [fun, str(e), request.user.id])  
        print(f"error: {e}")
        messages.error(request, 'Oops...! Something went wrong!')
        response = {'result': 'fail', 'messages': 'something went wrong!'} 

    finally:
        cursor.close()
        m.commit()
        m.close()
        Db.closeConnection()
            
        if request.method=="GET":
            return render(request, "Master/employee_master.html", context)
        elif request.method=="POST":  
            new_url = f'/masters?entity=em&type=i'
            return redirect(new_url)
    
def upload_excel(request):

    if request.method == 'POST' and request.FILES.get('excelFile'):
        excel_file = request.FILES['excelFile']
        fs = FileSystemStorage()
        filename = fs.save(excel_file.name, excel_file)
        uploaded_file_path = fs.path(filename)

        error_log_count = 0

        try:
            df = pd.read_excel(uploaded_file_path)
            Db.closeConnection()
            m = Db.get_connection()
            cursor = m.cursor()

            entity = request.GET.get('entity', '')

            if entity == 'em':
                df.rename(columns={
                    'Employee Id': 'employee_id',
                    'Employee Name': 'employee_name',
                    'Mobile No': 'mobile_no',
                    'Current Location': 'current_location',
                    'Is Active': 'is_active'
                }, inplace=True)

                for _, row in df.iterrows():
                    params = (
                        row.get('employee_id', ''),
                        row.get('employee_name', ''),
                        row.get('mobile_no', ''),
                        row.get('current_location', ''),
                        row.get('is_active', '')
                    )
                    try:
                        cursor.callproc('stp_insert_employee_master_excel', params)
                    except Exception as e:
                        # Handle the exception if needed
                        print(f"Error inserting employee data: {e}")


            elif entity == 'sm':
                company_id = request.POST.get('company_id', '')
                df.rename(columns={
                    'Site Name': 'site_name',
                    'Site Address': 'site_address',
                    'Pincode': 'pincode',
                    'Contact Person Name': 'contact_person_name',
                    'Contact Person Email': 'contact_person_email',
                    'Contact Person Mobile No': 'contact_person_mobile_no',
                    'Is Active': 'is_active',
                    'No of Days': 'no_of_days',
                    'Notifiication Time': 'notification_time',
                    'Reminder Time': 'reminder_time',
                    'Roster Type': 'roster_type'
                }, inplace=True)

                for _, row in df.iterrows():
                    
                    params = (
                        row.get('site_name', ''),
                        row.get('site_address', ''),
                        row.get('pincode', ''),
                        row.get('contact_person_name', ''),
                        row.get('contact_person_email', ''),
                        row.get('contact_person_mobile_no', ''),
                        int(row['is_active']) if not pd.isna(row['is_active']) else None,
                        int(row['no_of_days']) if not pd.isna(row['no_of_days']) else None,
                        row.get('notification_time', ''),
                        row.get('reminder_time', ''),
                        company_id,  
                        row.get('roster_type', '')
                    )
                    
                    try:
                        cursor.callproc('stp_insert_site_master', params)
                    except Exception as e:
                        # Handle the exception if needed
                        print(f"Error inserting site data: {e}")
            elif entity == 'cm':
                    
                    df.rename(columns={
                    'Company Name': 'company_name',
                    'Company Address': 'company_address',
                    'Pincode': 'pincode',
                    'Contact Person Name': 'contact_person_name',
                    'Contact Person Email': 'contact_person_email',
                    'Contact Person Mobile No': 'contact_person_mobile_no',
                    'Is Active': 'is_active',
                }, inplace=True)
                    

                    for _, row in df.iterrows():
                        params = (
                            row.get('company_name', ''),
                            row.get('company_address', ''),
                            row.get('pincode', ''),
                            row.get('contact_person_name', ''),
                            row.get('contact_person_email', ''),
                            row.get('contact_person_mobile_no', ''),
                            row.get('is_active', '')
                        )
                
                    try:
                        cursor.callproc('stp_insert_company_master', params)
                    except Exception as e:
                            # Handle the exception if needed
                            print(f"Error inserting site data: {e}")
                    
            messages.success(request, "Data Uploaded successfully!")


        except Exception as e:
            error_log_count += 1
            tb = traceback.extract_tb(e.__traceback__)
            fun = tb[0].name
            print(f"Error inserting row: {e}")
            cursor.callproc("stp_error_log", [fun, str(e), request.user.id])  
            print(f"error: {e}")
            messages.error(request, 'Oops...! Something went wrong!')
            response = {'result': 'fail', 'messages': 'something went wrong!'}   

            m.commit()   

        finally:
            cursor.close()
            m.close()
            Db.closeConnection()
            new_url = f'/masters?entity={entity}&type=i'
            return redirect(new_url)



    