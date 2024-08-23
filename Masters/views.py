import json
import pydoc
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login ,logout,get_user_model
import openpyxl
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
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.contrib import messages
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

            # Call stored procedure to get company names
            cursor.callproc("stp_get_company_names")
            for result in cursor.stored_results():
                company_names = list(result.fetchall())

            m.commit()

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
            return render(request,'Master/index.html', {'entity':entity,'type':type,'name':name,'header':header,'data':data,'company_names': company_names,'pre_url':pre_url})
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
        cursor.callproc("stp_get_masters", [entity, type, 'sample_xlsx'])
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

                cursor.callproc("stp_edit_site_master", (site_id,))  # Note the comma to make it a tuple
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
                        'roster_type': data[12]
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
                
                # Execute stored procedure
                cursor.callproc("stp_insert_site_master", params)
                
                # Commit the transaction
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

                # Retrieve form data
                company_name = request.POST.get('company_name', '')
                company_address = request.POST.get('company_address', '')
                pincode = request.POST.get('pincode', '')
                contact_person_name = request.POST.get('contact_person_name', '')
                contact_person_email = request.POST.get('contact_person_email', '')
                contact_person_mobile_no = request.POST.get('contact_person_mobile_no', '') 
                is_active = request.POST.get('status_value', '') 

                # Parameters for the stored procedure
                params = [
                    company_name, 
                    company_address, 
                    pincode, 
                    contact_person_name,
                    contact_person_email,
                    contact_person_mobile_no,
                    is_active
                ]
                
                # Execute stored procedure
                cursor.callproc("stp_insert_company_master", params)
                
                # Commit the transaction
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
            
        if request.method=="GET":
            return render(request, "Master/company_master.html", context)
        elif request.method == "POST":
            new_url = f'/masters?entity=cm&type=i'
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
                cursor.callproc("stp_edit_employee_master", (id,))  # Note the comma to make it a tuple
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
                        'is_active': data[6]
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
                        print(f"Error inserting site data: {e}")

            elif entity == 'sm':
                company_id = request.POST.get('company_id', '')

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


    