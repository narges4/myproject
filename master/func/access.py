

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User , Group , Permission
from django.urls import resolve
from master.models import *
import datetime
from exchange.func.public import *

def master_access_check(req):


    # Login Check Start
    if not req.user.is_authenticated :
        return [401,"master_login","-"]
    # Login Check End
    
    # Admin Exist Check Start
    try : master = Master.objects.get(req_user=req.user)
    except : return [401,"master_login","-"]
    # Admin Exist Check End

    if (int(get_date_time()['timestamp']) -  int(master.last_modify))  > 10800 : return [401,"master_login","-"]

    if Site_Settings.objects.get(code=1001).is_customer_login == False :  

        return [401,"master_login","-"]
    
    # Admin General Access Check Start
    if Permission.objects.filter(user=req.user, codename='master_exchange_access').count() == 0 :
        return [401,"master_login","-"]
    # Admin General Access Check End

    # Admin Change Ip 
    manager_ip = get_ip(req)

    ip_check = False
    ip =  [i.ip   for i in  master.master_ip.all() ] 
    for i in ip :

        if manager_ip.startswith(i):
            ip_check = True
            break

    if master.last_ip != str(manager_ip) : 
        if (int(get_date_time()['timestamp']) - int(master.last_modify)) > 300 :
            return [401,"master_login","-"]
        
    # if master.master_agent != str(req.META.get('HTTP_USER_AGENT', '')) :  return [401,"master_login","-"]           



    return [100,"-","-", master]
