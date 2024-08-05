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

def register(request):
    return render(request,'Account/register.html') 

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