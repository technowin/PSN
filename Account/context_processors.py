from django.conf import settings
from PSN.encryption import decrypt_parameter
import Db

def logged_in_user(request):
    Db.closeConnection()
    m = Db.get_connection()
    cursor=m.cursor()
    user =''
    session_cookie_age_seconds = settings.AUTO_LOGOUT['IDLE_TIME']
    session_timeout_minutes = session_cookie_age_seconds 
    username = request.session.get('username', '')
    full_name = request.session.get('full_name', '')
    if request.user.is_authenticated ==True:
        user = str(request.user.id or '')
        
    cursor.callproc("stp_get_all_reports", [user])
    for result in cursor.stored_results():
        for items in result.fetchall():
            reports = items[0]     
    
    cursor.close()
    m.commit()
    cursor.close()
    m.close()
    Db.closeConnection()        
    return {'username':username,'full_name':full_name,'session_timeout_minutes':session_timeout_minutes,'reports':reports}