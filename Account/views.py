import json
import random
import string
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render,redirect
from django.contrib.auth import authenticate, login ,logout,get_user_model
from Account.forms import RegistrationForm
from Account.models import AssignedCompany, CustomUser, OTPVerification, password_storage
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

from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
# Create your views here.
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
                request.session["username"]=(str(username))
                request.session["full_name"]=(str(user.full_name))
                request.session["user_id"]=(str(user.id))
                if remember_me == 'on':
                    request.session.set_expiry(1209600)  # 2 weeks
                else:
                    request.session.set_expiry(0)  # Browser close
                return redirect('home') 
            else:
                Error=True
                # Authentication failed
                return render(request, 'Account/login.html', {'Error': Error,'ErrorMessage':'Invalid Credentials!!'})
        return redirect("Account")
    if request.method=="GET":
       return render(request,'Account/login.html',{'Error': Error,'next':next})                 
    return render(request,'Account/login.html',{'Error': Error}) 

def home(request):
    return render(request,'Account/home.html') 
def generate_otp(length=6):
    return ''.join(random.choices(string.digits, k=length))

class LoginView(APIView):
    def post(self, request):
        try:
            serializer = LoginSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            username = serializer.validated_data['username']
            password = serializer.validated_data['password']

            # Manually check the provided username and password
            user = get_object_or_404(CustomUser, username=username)

            if user.check_password(password):
                login(request, user)
                serializer = UserSerializer(user).data
                
                refresh = RefreshToken.for_user(user)
                return JsonResponse({'access_token': str(refresh.access_token),'refresh_token': str(refresh),'data':serializer}, status=status.HTTP_200_OK,safe=False)
                # return JsonResponse(serializer, status=status.HTTP_200_OK,safe=False)
            else:
                return JsonResponse({'message': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED,safe=False)
        except Exception as e:
            print(str(e))
            return Response( status=status.HTTP_400_BAD_REQUEST)

class RegistrationView(APIView):
    def post(self, request):
        try:
            data = request.data.copy()
            
            # Check if role_id is provided, otherwise set default value to 1
            role_id = data.pop('role_id', 1)

            # Check if is_active is provided, otherwise set default value to False
            is_active = data.pop('is_active', True)
            serializer = RegistrationSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            raw_password = serializer.validated_data.get('password')
            user = CustomUser.objects.create(**serializer.validated_data)
            user.set_password(raw_password)
            user.username = user.email
            user.is_active = is_active  # Default is_active value
            user.role_id =role_id  # Default role_id value
            user.save()
            password_storage.objects.create(user=user, raw_password=raw_password)
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
            return Response( status=status.HTTP_400_BAD_REQUEST)


def forgot_password(request):
    return render(request,'Account/forgot-password.html') 

def logoutView(request):
    logout(request)

    return redirect("Account")  

from django.db.models import Q
from Account.models import Item 

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