from django.conf import settings
from PSN.encryption import decrypt_parameter
from Masters.models import Company
import Db
from Masters.models import Role 

def logged_in_user(request):
    user =''
    session_cookie_age_seconds = settings.AUTO_LOGOUT['IDLE_TIME']
    session_timeout_minutes = session_cookie_age_seconds 
    username = request.session.get('username', '')
    full_name = request.session.get('full_name', '')
    if request.user.is_authenticated ==True:
        user = str(request.user.id or '')
    return {'username':username,'full_name':full_name,'session_timeout_minutes':session_timeout_minutes}