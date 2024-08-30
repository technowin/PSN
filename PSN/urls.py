"""
URL configuration for PSN project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.Account, name='Account')
Class-based views
    1. Add an import:  from other_app.views import Account
    2. Add a URL to urlpatterns:  path('', Account.as_view(), name='Account')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static

from Account.views import *

from Masters.models import site_master
from Masters.views import *

from django.urls import path

from Notification.views import check_shift_for_next_day


urlpatterns = [
    path('admin/', admin.site.urls),
    # APP URLS
    path('refresh-token', CustomTokenRefreshView.as_view(), name='refresh-token'),
    path('Applogin', LoginView.as_view(), name='Applogin'),
    path('register_device_token', register_device_token.as_view(), name='register_device_token'),
    path("register",RegistrationView.as_view(),name='register'),
    path('home_fetch', RosterDataAPIView.as_view(), name='home_fetch'),
    path('confirm_schedule', confirm_schedule.as_view(), name='confirm_schedule'),
    
    
    # Account

    path("", Login,name='Account'),
    path("Login", Login,name='Login'),
    path("home", home,name='home'),
    path("logout",logoutView,name='logout'),
    
    
    path("forgot_password",forgot_password,name='forgot_password'),
    path('search/', search, name='search'),
    # Masters

    path('masters/', masters, name='masters'),
    path('sample_xlsx/', sample_xlsx, name='sample_xlsx'),
    path("roster_upload",roster_upload, name="roster_upload"),
    path("company_master",company_master,name="company_master"),
    path("employee_master",employee_master, name="employee_master"),
    path("upload_excel",upload_excel, name="upload_excel"),
    path("site_master",site_master, name="site_master"),
    
    # Bootstarp Pages

    path("dashboard",dashboard,name='dashboard'),
    path("buttons",buttons,name='buttons'),
    path("cards",cards,name='cards'),
    path("utilities_color",utilities_color,name='utilities_color'),
    path("utilities_border",utilities_border,name='utilities_border'),
    path("utilities_animation",utilities_animation,name='utilities_animation'),
    path("utilities_other",utilities_other,name='utilities_other'),
    path("error_page",error_page,name='error_page'),
    path("blank",blank,name='blank'),
    path("charts",charts,name='charts'),  
    path("tables",tables,name='tables'),  
    
    path('check_shift/<int:employee_id>/<int:site_id>/', check_shift_for_next_day, name='check_shift_for_next_day'),
    

]