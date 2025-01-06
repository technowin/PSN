import json
import random
import string
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render,redirect
from django.contrib.auth import authenticate, login ,logout,get_user_model
from Account.forms import RegistrationForm
from Account.models import AssignedCompany, CustomUser,MenuMaster,RoleMenuMaster,UserMenuDetails, OTPVerification, password_storage
# import mysql.connector as sql
from Account.serializers import *
import Db 
import bcrypt
from django.contrib.auth.decorators import login_required
# from .models import SignUpModel
# from .forms import SignUpForm
from Masters.models import sc_employee_master
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
from django.contrib.auth.hashers import check_password
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth.backends import ModelBackend
class LoginView(APIView):
    authentication_classes = []
    def post(self, request):
        try:
            serializer = LoginSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            # email = serializer.validated_data['email']
            phone = serializer.validated_data['phone']
            # password = serializer.validated_data['password']
            device_token = serializer.validated_data['device_token']

            # Manually check the provided username and password
            user = get_object_or_404(CustomUser, phone=phone)
            if(user):
                try:
                    if user.role_id != 5:
                        return Response({'message': 'User Does Not Have Necessary Role To Login  '}, status=status.HTTP_400_BAD_REQUEST)  
                except Exception as e:
                    print(str(e))
                    return Response({'message': 'User Not Found'}, status=status.HTTP_400_BAD_REQUEST)  
                 
            try:
                employee = get_object_or_404(sc_employee_master,mobile_no=phone)
                if(employee):
                    # if user.check_password(password):
                    login(request, user,backend='django.contrib.auth.backends.ModelBackend')
                    user.device_token  = device_token
                    user.save()
                    serializer = UserSerializer(user).data
                    employee_id = employee.employee_id
                    
                    refresh = RefreshToken.for_user(user)
                    return JsonResponse({'access_token': str(refresh.access_token),'refresh_token': str(refresh),'data':serializer,'employee_id':employee_id}, status=status.HTTP_200_OK,safe=False)
            except Exception as e:
                print(str(e))
                return Response({'message': 'User Not Found In Employee Master  '}, status=status.HTTP_400_BAD_REQUEST)  
                # return JsonResponse(serializer, status=status.HTTP_200_OK,safe=False)
            # else:
            #     return JsonResponse({'message': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED,safe=False)
        except Exception as e:
            print(str(e))
            return Response({'message': 'Invalid credentials  '}, status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
def Login(request):
    Db.closeConnection()
    m = Db.get_connection()
    cursor=m.cursor()
    user_info_cookie = request.COOKIES.get('user_info', None)
    my_variable_from_session = request.session.get('test', 'Default Value if not found')
    next =request.GET.get('next', '')
    logins=True
    Error=False
    if request.method=="POST":
        next =request.POST.get('next', '')
        if request.method =="POST":
            username = request.POST.get('username')
            password = request.POST.get('password')
            remember_me = request.POST.get('remember_me')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                request.session.cycle_key()
                request.session["username"]=(str(username))
                request.session["full_name"]=(str(user.full_name))
                request.session["user_id"]=(str(user.id))
                request.session["role_id"] = str(user.role_id)
                if remember_me == 'on':
                    request.session.set_expiry(1209600)  # 2 weeks
                else:
                    request.session.set_expiry(0)  # Browser close
                return redirect('newdashboard') 
            else:
                Error=True
                # Authentication failed
                return render(request, 'Account/login.html', {'Error': Error,'ErrorMessage':'Invalid Credentials!!'})
        return redirect("Account")
    if request.method=="GET":
       return render(request,'Account/login.html',{'Error': Error,'next':next})                 
    return render(request,'Account/login.html',{'Error': Error}) 

@login_required
def register_new_user(request):
    Db.closeConnection()
    m = Db.get_connection()
    cursor=m.cursor()
    if request.method=="GET":
        id = request.GET.get('id', '')
        cursor.callproc("stp_get_dropdown_values",['roles'])
        for result in cursor.stored_results():
            roles = list(result.fetchall())

        if id != '0':
            id1 = decrypt_parameter(id)
            users = get_object_or_404(CustomUser, id=id1)
            full_name = users.full_name.split(" ", 1) 
            first_name = full_name[0] 
            last_name = full_name[1] if len(full_name) > 1 else ""  


            context = {'users':users,'first_name':first_name,'last_name':last_name,'roles':roles}
           
        else:

            context = {'id':id,'roles': roles}


    if request.method == "POST":
        id = request.POST.get('id', '')
        try:  
            if id == '0':
               # Extract data from the request
                
                firstname = request.POST.get('firstname')
                lastname = request.POST.get('lastname')
                email = request.POST.get('email')
                password = request.POST.get('password') 
                phone = request.POST.get('mobileNumber')
                role_id = request.POST.get('role_id')
                full_name = f"{firstname} {lastname}"

                user = CustomUser(
                    full_name=full_name, email=email, phone=phone,
                    role_id=role_id,
                )
                user.username = user.email
                user.is_active = True 
                try:
                    validate_password(password, user=user)
                    user.set_password(password)
                    user.save()
                    password_storage.objects.create(user=user, passwordText=password)
                    assigned_menus = RoleMenuMaster.objects.filter(role_id=role_id)

                # Insert assigned menus into userMenuMaster
                    for menu in assigned_menus:
                        UserMenuDetails.objects.create(
                            user_id=user.id,
                            menu_id=menu.menu_id,
                            role_id=role_id
                    )

                    messages.success(request, "User registered successfully!")

                except ValidationError as e:
                    messages.error(request, ' '.join(e.messages))
                    
            else:
                firstname = request.POST.get('firstname')
                lastname = request.POST.get('lastname')
                email = request.POST.get('email')
                full_name = f"{firstname} {lastname}"
                phone = request.POST.get('mobileNumber')
                role_id = request.POST.get('role_id')

                user = CustomUser.objects.get(id=id)
                user.full_name = full_name
                user.email = email
                user.phone = phone
                user.role_id = role_id
                user.save()

                messages.success(request, "User details updated successfully!")

        except Exception as e:
            tb = traceback.extract_tb(e.__traceback__)
            fun = tb[0].name
            cursor.callproc("stp_error_log",[fun,str(e),request.user.id])  
            print(f"error: {e}")
            messages.error(request, 'Oops...! Something went wrong!')
            response = {'result': 'fail','messages ':'something went wrong !'}   

    if request.method=="GET":
        return render(request,'Account/register_new_user.html',context)
    elif request.method == "POST":
        return redirect('/masters?entity=user&type=i')

class register_device_token(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    def post(self, request):
        try:
            user = request.user
            device_token = request.data.get('device_token')

            if device_token:
                user.device_token = device_token
                user.save()
                return Response({"message": "Device token registered successfully."}, status=200)
            else:
                return Response({"message": "Device token not provided."}, status=400)
        except Exception as e:
            print(str(e))
            return Response( status=status.HTTP_400_BAD_REQUEST)
def home(request):
    return render(request,'Account/home.html') 
def generate_otp(length=6):
    return ''.join(random.choices(string.digits, k=length))

class RegistrationView(APIView):
    authentication_classes=[]
    def post(self, request):
        try:
            data = request.data.copy()
            
            # Check if role_id is provided, otherwise set default value to 1
            role_id = data.pop('role_id', 5)

            # Check if is_active is provided, otherwise set default value to False
            is_active = data.pop('is_active', True)
            device_token = data.pop('device_token', True)
            serializer = RegistrationSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            raw_password = serializer.validated_data.get('password')
            user = CustomUser.objects.create(**serializer.validated_data)
            user.set_password(raw_password)
            user.username = user.email
            user.is_active = is_active  # Default is_active value
            user.role_id =role_id  # Default role_id value
            user.device_token = device_token
            user.save()
            password_storage.objects.create(user=user, passwordText=raw_password)
            otp = generate_otp()
            
            # Save OTP to database
            otp_instance = OTPVerification.objects.create(user=user, otp_text=otp)
            
            # Send OTP via email
            # send_mail(
            #     'OTP Verification',
            #     f'Your OTP is: {otp}',
            #     'sender@example.com',
            #     [user.email],
            #     fail_silently=False,
            # )
            serializer = UserSerializer(user).data
            return JsonResponse(serializer, status=status.HTTP_200_OK,safe=False)
        except Exception as e:
            print(str(e))
            return Response({'error':str(e)}, status=status.HTTP_400_BAD_REQUEST)

class CustomTokenRefreshView(APIView):

    def get(self, request, *args, **kwargs):
        refresh = request.GET.get('refresh')  # Retrieve the 'refresh' parameter from the query string

        if not refresh:  # If 'refresh' parameter not found in query string, try to retrieve from request body
            refresh = request.data.get('refresh')

        if refresh:
            try:
                refresh_token = RefreshToken(refresh)
                access_token = str(refresh_token.access_token)
                # Generate a new refresh token
                new_refresh_token = str(refresh_token.access_token)
                return Response({'access-token': access_token, 'refresh-token': str(refresh_token)})
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'Refresh token not provided'}, status=status.HTTP_400_BAD_REQUEST)


def forgot_password(request):
    Db.closeConnection()  
    m = Db.get_connection()  
    cursor = m.cursor()
    
    try:
        if request.method =="GET":
            type = request.GET.get('type')
        if request.method == "POST":
            email = request.POST.get('email')
            if CustomUser.objects.filter(email=email).exists():
                messages.success(request, 'User id valid...Please update your password')
                type = 'pass'
            else:
                messages.error(request, 'User does not exist.Please Enter Correct Email.')
                type='email'

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

    if request.method =="GET":
        return render(request,'Account/forgot-password.html',{'type':type}) 
    elif request.method =="POST":
        return render(request,'Account/forgot-password.html',{'type':type,'email':email}) 

def logoutView(request):
    logout(request)

    return redirect("Account")  

from django.db.models import Q
from Account.models import Item 

@login_required
def search(request):
    Db.closeConnection()
    m = Db.get_connection()
    cursor=m.cursor()
    results = []
    try:
        query = request.GET.get('q')
        if query != "":
           cursor.callproc("stp_get_application_search",[query])        
           for result in cursor.stored_results():
               results = list(result.fetchall()) 
    except Exception as e:
        print("error-"+e)
    finally:
        cursor.close()
        m.commit()
        m.close()
        Db.closeConnection()
        return render(request, 'Bootstrap/search_results.html', {'query': query, 'results': results})

@login_required
def menu_admin(request):
    Db.closeConnection()
    m = Db.get_connection()
    cursor=m.cursor()
    pre_url = request.META.get('HTTP_REFERER')
    header = []
    data = []
    name = ''
    entity = ''
    type = ''
    global user
    user  = request.session.get('user_id', '')
    try:
       
        if request.method=="GET":
            entity = request.GET.get('entity', '')
            type = request.GET.get('type', '')
            cursor.callproc("stp_get_masters",[entity,type,'name',user])
            for result in cursor.stored_results():
                datalist1 = list(result.fetchall())
            name = datalist1[0][0]
            cursor.callproc("stp_get_masters", [entity, type, 'header',user])
            for result in cursor.stored_results():
                header = list(result.fetchall())
            cursor.callproc("stp_get_masters",[entity,type,'data',user])
            # Encrypt each row's ID before rendering
            data = []
            for result in cursor.stored_results():
                rows = result.fetchall()
                for row in rows:
                    encrypted_id = encrypt_parameter(str(row[0]))
                    data.append((encrypted_id,) + row[1:])





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
            return render(request,'Master/menu_admin.html', {'entity':entity,'type':type,'name':name,'header':header,'data':data,'pre_url':pre_url})
        elif request.method=="POST":  
            new_url = f'/masters?entity={entity}&type={type}'
            return redirect(new_url) 
@login_required        
def delete_menu(request):
    Db.closeConnection()
    m = Db.get_connection()
    cursor = m.cursor()
    try:
        type = request.GET.get('type', '')
        if request.method == "POST" and type == 'delete':
            menu_id1 = request.POST.get('menu_id', '')
            menu_id = decrypt_parameter(menu_id1)
            try:
                menu = get_object_or_404(MenuMaster, menu_id=menu_id)
                menu.delete()
        
                return JsonResponse({'success': True, 'message': 'Menu Successfully Deleted!'})
            except Exception as e:
                print(f"An error occurred: {e}")
                return JsonResponse({'success': False, 'message': 'An error occurred while deleting the menu.'})
    except Exception as e:
        tb = traceback.extract_tb(e.__traceback__)
        cursor.callproc("stp_error_log", [tb[0].name, str(e), request.user.id])
        print(f"error: {e}")
        messages.error(request, 'Oops...! Something went wrong!')
        response = {'result': 'fail', 'messages': 'something went wrong!'}

    finally:
        cursor.close()
        m.commit()
        m.close()
        Db.closeConnection()
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})


@login_required
def menu_master(request):
    Db.closeConnection()
    m = Db.get_connection()
    cursor = m.cursor()
    try:
        type = request.GET.get('type', '')
        if request.method == "POST" and type == 'delete':
            menu_id = request.POST.get('menu_id', '')
            try:
                menu = get_object_or_404(MenuMaster, menu_id=menu_id)
                menu.delete()
        
                return JsonResponse({'success': True, 'message': 'Menu Successfully Deleted!'})
            except Exception as e:
                print(f"An error occurred: {e}")
                return JsonResponse({'success': False, 'message': 'An error occurred while deleting the menu.'})


        if request.method == "GET":
            menu_id = request.GET.get('menu_id', '')
            if menu_id != '0':
                menu_id1 = decrypt_parameter(menu_id)
            cursor.callproc("stp_get_dropdown_values",['menu'])
            for result in cursor.stored_results():
                menu = list(result.fetchall())
            cursor.callproc("stp_get_dropdown_values",['roles'])
            for result in cursor.stored_results():
                roles = list(result.fetchall())
            cursor.callproc("stp_get_dropdown_values",['user'])
            for result in cursor.stored_results():
                users = list(result.fetchall())


            if menu_id != '0':
                menus = get_object_or_404(MenuMaster, menu_id=menu_id1)

        elif request.method == "POST" and type == 'create':
            menu_id = request.POST.get('menu_id', '')
            if menu_id != '0':
                menu_id1 = decrypt_parameter(menu_id)
            fields = ['menu_name', 'menu_action', 'parent', 'menu_parent', 'sub_parent', 'sub_menu_parent', 'sub_parent1', 'sub_menu_parent1']
            menu_name, menu_action, parent, menu_parent, sub_parent, sub_menu_parent, sub_parent1, sub_menu_parent1= [request.POST.get(field, '') for field in fields]

            menu_parent_id = menu_parent if menu_parent else -1
            sub_menu_id = sub_menu_parent if sub_menu_parent else -1
            sub_menu_id1 = sub_menu_parent1 if sub_menu_parent1 else -1
            menu_action_value = menu_action if menu_action else '#'


            user_id = request.session.get('user_id', '')

            # if user_id:
            #     try:
            #         user = CustomUser.objects.get(id=user_id)
            #     except CustomUser.DoesNotExist:
            #         user = None

            if menu_id == '0':
                menu_count = MenuMaster.objects.count() + 1
                icon = 'fas fa ' + request.POST.get('menu_icon','')

                try:
                    MenuMaster.objects.create(
                        menu_name=menu_name, menu_action=menu_action_value, menu_is_parent=parent,
                        menu_parent_id=menu_parent_id, is_sub_menu=sub_parent, sub_menu=sub_menu_id,
                        is_sub_menu2=sub_parent1, sub_menu2=sub_menu_id1, menu_order=menu_count,menu_icon=icon,created_by=user_id)
                    messages.success(request, "Menu Successfully Created!")
                except Exception as e:
                    print(f"An error occurred: {e}")
            else:
                try:
                    MenuMaster.objects.filter(menu_id=menu_id1).update(
                        menu_name=menu_name,
                        menu_action=menu_action_value,
                        menu_is_parent=parent,
                        menu_parent_id=menu_parent_id,
                        is_sub_menu=sub_parent,
                        sub_menu=sub_menu_id,
                        is_sub_menu2=sub_parent1,
                        sub_menu2=sub_menu_id1,
                        updated_by=user_id
                    )
                    messages.success(request, "Menu Successfully Updated!")

                except Exception as e:
                    print(f"An error occurred: {e}")
                    messages.error(request, "An error occurred while updating the menu.")

    except Exception as e:
        tb = traceback.extract_tb(e.__traceback__)
        cursor.callproc("stp_error_log", [tb[0].name, str(e), request.user.id])
        print(f"error: {e}")
        messages.error(request, 'Oops...! Something went wrong!')
        response = {'result': 'fail', 'messages': 'something went wrong!'}

    finally:
        cursor.close()
        m.commit()
        m.close()
        Db.closeConnection()
        if request.method == "GET":
            return render(request, 'Master/menu_master.html', {'menu': menu,'type': type,'roles': roles, 'users': users,'menu_id': menu_id,'order': 'order' if type == 'order' else None,'menus': menus if menu_id != '0' else None})
        elif request.method == "POST":
            return redirect('/menu_admin?entity=menu&type=i')
@login_required
def assign_menu(request):
    Db.closeConnection()
    m = Db.get_connection()
    cursor = m.cursor()
    try:  
       if request.method == "POST":
        type= request.POST.get('type','')
        if type ==  'role':
            user_id = request.session.get('user_id', '')
            if user_id:
                try:
                    user = CustomUser.objects.get(id=user_id)
                except CustomUser.DoesNotExist:
                    user = None
            roleId = request.POST.get('role_id', '')
            menuIds = request.POST.getlist('menu_list')  

            try:
                RoleMenuMaster.objects.filter(role_id=roleId).delete()
                
                for menu_id in menuIds:
                    RoleMenuMaster.objects.create(
                        role_id=roleId,
                        menu_id=menu_id,
                        created_by = user
                    )
            except Exception as e:
                print(f"An error occurred: {e}")
                messages.error(request, "An error occurred while updating menus.")

                    
            try:
                UserMenuDetails.objects.filter(role_id=roleId).delete()

                users = CustomUser.objects.filter(role_id=roleId)

                for user in users:
                    for menu_id in menuIds:
                        UserMenuDetails.objects.create(
                            user_id=user.id,
                            menu_id=menu_id,
                            role_id=roleId,
                            created_by = user
                        )
                
                messages.success(request, "Menus successfully Assigned to Selected Role!")
            
            except Exception as e:
                print(f"An error occurred: {e}")
                messages.error(request, "An error occurred while updating menus.")

        if type == 'user':
            userId = request.POST.get('user_id', '')
            menuIds = request.POST.getlist('menu_list') 

            try:
                user_id = request.session.get('user_id', '')
                if user_id:
                    try:
                        user = CustomUser.objects.get(id=user_id)
                    except CustomUser.DoesNotExist:
                        user = None
                user = CustomUser.objects.get(id=userId)
                roleId = user.role_id

                existing_count = UserMenuDetails.objects.filter(user_id=userId).count()

                if existing_count > 0:
                    UserMenuDetails.objects.filter(user_id=userId).delete()
                
                for menu_id in menuIds:
                    UserMenuDetails.objects.create(
                        user_id=userId,
                        menu_id=menu_id,
                        role_id=roleId,
                        created_by = user
                    )

                messages.success(request, "User menu details successfully updated!")

            except CustomUser.DoesNotExist:
                messages.error(request, "User does not exist.")
            except Exception as e:
                print(f"An error occurred: {e}")
                messages.error(request, "An error occurred while updating user menu details.")

            

    except Exception as e:
        tb = traceback.extract_tb(e.__traceback__)
        cursor.callproc("stp_error_log", [tb[0].name, str(e), request.user.id])
        print(f"error: {e}")
        messages.error(request, 'Oops...! Something went wrong!')
        response = {'result': 'fail', 'messages': 'something went wrong!'}

    finally:
        cursor.close()
        m.commit()
        m.close()
        Db.closeConnection()
    if request.method == "POST":
        return redirect('/menu_admin?entity=menu&type=i')
    
@login_required    
def get_assigned_values(request):
    menu_array = []
    try:
        if request.method == "POST":
            data_type = request.POST.get('type','')
            selected_id = request.POST.get('id', '')
            m = Db.get_connection()  
            cursor = m.cursor()

            cursor.callproc("stp_get_assign_menu_values", [selected_id, data_type])
            for result in cursor.stored_results():
                menu_array = list(result.fetchall())

            cursor.close()
            m.commit()
            m.close()

            response = {'result': 'success', 'menu_array': menu_array}
        else:
            response = {'result': 'fail', 'message': 'Invalid request method'}

    except Exception as e:
        tb = traceback.extract_tb(e.__traceback__)
        cursor.callproc("stp_error_log", [tb[0].name, str(e), request.user.id])
        print(f"error: {e}")
        response = {'result': 'fail', 'message': 'Something went wrong!'}

    finally:
        Db.closeConnection()

    return JsonResponse(response)

@login_required
def menu_order(request):
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
            type = request.GET.get('type', '')
            menu_id = request.GET.get('menu_id', '')
            menu_id1 = decrypt_parameter(menu_id)
            cursor.callproc("stp_get_menu_order",[menu_id1])
            for result in cursor.stored_results():
                data = list(result.fetchall())
       

        if request.method=="POST":
             for key, value in request.POST.items():
                if key.startswith('menu_order_'):
                    try:
                        row_number = key.split('_')[2]  
                        menu_id = request.POST.get(f'menu_id_{row_number}')
                        menu_item = MenuMaster.objects.get(menu_id=menu_id)
                        menu_item.menu_order = value
                        menu_item.save()
                        messages.success(request, "Menu Order Succesfully Updated!")
                        
                    except Exception as e:
                        print(f"An error occurred: {e}")
                        messages.error(request, "An error occurred while updating the menu.")
                 
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
            return render(request,'Master/menu_master.html', {'type':type,'name':name,'header':header,'data':data})
        elif request.method=="POST":  
            new_url = f'/menu_admin?entity=menu&type=i'
            return redirect(new_url) 

@login_required       
def change_password(request):
    Db.closeConnection()  
    m = Db.get_connection()  
    cursor = m.cursor()
    try:
        if request.method == "POST":
            password = request.POST.get('password')  # The password entered by the user
            username = request.session.get('username', '')  # The username from the session

            user = CustomUser.objects.get(email=username)
                    
            if check_password(password, user.password):
                status = "1"
            else:
                status = "0" 

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
        if request.method == "GET":
            return render(request,'Account/change_password.html')
        else:
           return JsonResponse({'status': status})
        
@login_required
def reset_password(request):
    Db.closeConnection()  
    m = Db.get_connection()  
    cursor = m.cursor()
    
    try:
        email = request.POST.get('email')
        if not email:
            email = request.session.get('username', '')
            

        password = request.POST.get('password')
        user = CustomUser.objects.get(email=email)

        # Update password
        user.set_password(password)
        user.save()

        messages.success(request, 'Password has been successfully updated.')

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
        return redirect( f'change_password')
       
def forget_password_change(request):
    Db.closeConnection()  
    m = Db.get_connection()  
    cursor = m.cursor()
    
    try:
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = CustomUser.objects.get(email=email)

        user.set_password(password)
        user.save()

        messages.success(request, 'Password has been successfully updated.')

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
        return redirect( f'Login')
        
def dashboard(request):
    return render(request,'Bootstrap/index.html') 

def buttons(request):
    return render(request,'Bootstrap/buttons.html') 

def cards(request):
    return render(request,'Bootstrap/cards.html') 

def utilities_color(request):
    return render(request,'Bootstrap/utilities-color.html') 

def utilities_border(request):
    return render(request,'Bootstrap/utilities-border.html') 

def utilities_animation(request):
    return render(request,'Bootstrap/utilities-animation.html') 

def utilities_other(request):
    return render(request,'Bootstrap/utilities-other.html') 

def error_page(request):
    return render(request,'Bootstrap/404.html')

def blank(request):
    return render(request,'Bootstrap/blank.html')

def charts(request):
    return render(request,'Bootstrap/charts.html')

def tables(request):
    return render(request,'Bootstrap/tables.html')





            

