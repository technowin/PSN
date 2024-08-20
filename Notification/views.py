from django.shortcuts import render
from django.http import JsonResponse
from django.utils.timezone import now
from datetime import timedelta

from Masters.models import *
# Create your views here.
def check_shift_for_next_day(request, employee_id, site_id):
    tomorrow = now().date() + timedelta(days=1)
    
    try:
        site = site_master.objects.get(site_id=site_id)
        
        shift = sc_roaster.objects.get(employee_id=employee_id, site=site, shift_date=tomorrow)
        
        response_data = {
            'has_shift': True,
            'notification_time': site.notification_time.strftime('%H:%M'),
            'shift_from': shift.shift_from.strftime('%H:%M'),
            'shift_to': shift.shift_to.strftime('%H:%M'),
        }
    except sc_roaster.DoesNotExist:
        response_data = {'has_shift': False}
    
    return JsonResponse(response_data)