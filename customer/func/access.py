
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User , Group , Permission
from customer.func.public import error_logs_access_check
from customer.models import *
import datetime
from exchange.func.public import *
from exchange.models import Site_Settings

from django.utils.timezone import datetime
from datetime import datetime, timezone


def customer_access_check(req):

    panel_redirect =  [101, 'account']
    is_from_pwa = False
    
    referer = req.META.get('HTTP_REFERER', 'Unknown')

    if 'pwa/' in referer: 

        is_from_pwa = True
        panel_redirect = [101, 'pwa_coustomer_account']

    # Login Check Start
    if not req.user.is_authenticated :  return panel_redirect
    # Login Check End
    
    if is_from_pwa == False:
        if (int(get_date_time()['timestamp']) -  int(customer.last_login))  > 3600 : return panel_redirect




    if Site_Settings.objects.get(code=1001).is_customer_login == False : return panel_redirect

    # Admin General Access Check Start
    if Permission.objects.filter(user=req.user, codename='customer_exchange_access').count() == 0 : return panel_redirect
    # Admin General Access Check End

    # Mobile Ownership Verify Check Start
    if customer.is_mobile_ownership == False : 

        if customer.is_from_pwa == True : 
            return [401, 'pwa_customer_complete_registration']
        else :    
            return [401, 'customer_complete_registration']
    # Mobile Ownership Verify Check End

    # Mobile Verify Check Start
    if customer.is_mobile == False : 

        if customer.is_from_pwa == True : 
            return [401, 'pwa_customer_complete_registration']
        else :    
            return [401, 'customer_complete_registration']
        
    # Mobile Verify Check End

    # Rulls Accepted Check Start
    if customer.is_rulls == False : 

        if customer.is_from_pwa == True : 
            return [402, 'pwa_customer_complete_registration']
        else :    
           return [402, 'customer_complete_registration']
        
        
    # Rulls Accepted Check End

    # Profile Complated Check Start
    if customer.is_profile == False : 

        if customer.is_from_pwa == True : 
            return [403, 'pwa_customer_complete_registration']
        else :    
           return  [403, 'customer_complete_registration']
        
    # Profile Complated Check End

    # Profile Complated Check Start
    if customer.is_bank == False : return [405, 'customer_complete_registration']
    # Profile Complated Check End

    # Profile Complated Check Start
    if customer.is_toverification_requird == True : 

        if customer.is_from_pwa == True : 
            return [404, 'pwa_customer_two_step']
        else :    
           return [404, 'customer_two_step']
    # Profile Complated Check End

    # Admin General Access Check Start
    if Permission.objects.filter(user=req.user, codename='customer_authentication_suspended').count() == 1 or customer.status == 'Suspended' : return panel_redirect
    # Admin General Access Check End

              

    return [100, '-', customer]
