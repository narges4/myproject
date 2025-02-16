from django import template
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import Avg, Count, Min, Sum, F, Value, CharField
from customer.models import *
from master.models import *
from exchange.models import *
from exchange.func.public import *
from account.models import *
from currency.models import *
from datetime import timedelta, datetime
import json
from django.utils import timezone
import ast 
import pytz
from customer.func.public import *
from ticket.models import Ticket
from wallet.models import *
from itertools import chain
import random
from django.utils.safestring import SafeString
from django.db.models import Max
from django.db.models import Q
from django.db.models.functions import Concat
from django.contrib.postgres.aggregates import StringAgg
from decimal import Decimal
import math
from dateutil.relativedelta import relativedelta 
from django import template
from datetime import datetime
import jdatetime
from master.models import UTM, UTMLog
from django import template

import boto3
import logging

register = template.Library()

@register.filter(name='googlecaptcha')
def googlecaptcha(str):
    if str == "sitekey" : return settings.GOOGLE_RECAPTCHA_SITE_KEY
    return None


@register.simple_tag
def qr_code_ticket(pk):
    return 'customer/ticket/detail/' + str(pk) + '/'


@register.simple_tag
def siteData():
    return Site_Settings.objects.get(code=1001)


@register.simple_tag
def khayyam_date():
    return JalaliDate.today().strftime('%A %d %B %Y')


@register.simple_tag
def detail(req):
    try :
        try:
            customer = Customer.objects.get(req_user=req)
            return customer
        except:
            master = Master.objects.get(req_user=req)
            return master
    except : return ['نامشخص','']



@register.simple_tag
def master_detail(req):
    return Master.objects.get(req_user=req)


@register.simple_tag
def customer_detail(req):

    try : customer = Customer.objects.get(req_user=req)
    except : return ['نامشخص','']
    return [customer.first_name, customer.last_name, customer.pk, customer.mobile, customer.profile_pic_name, customer.national_id]


@register.simple_tag
def get_master_detail(req):


    if req == 'robat' : return ['ربات','']
    try : master = Master.objects.get(req_user=req)
    except : return ['نامشخص','']
    else: return [master.first_name, master.last_name, master.nick_name, master.pk, master.mobile, master.profile_pic_name]


@register.simple_tag
def ticket_count():
    return Ticket.objects.filter(status="Waitting").count()


@register.simple_tag
def ticket_answer_count():
    tickets = Ticket.objects.filter(status="Waitting")
    count=0
    for i in tickets:
        count += i.count
    return count


@register.filter(name='patternCounter')
def patternCounter(value):
    return Site_Sms_log.objects.filter(pattern=value).count()



@register.simple_tag
def creat_date_array(rng):
    
    a = get_date_time()['datetime']
    my_array = []
    
    for i in range(int(rng)):

        x = a - timedelta(days=(i))
        y = str(x.date()).split('-')
        my_array.append(shamsiDate(int(y[0]),int(y[1]),int(y[2])))
    
    return my_array[::-1]



@register.simple_tag
def return_coounter_sms(acc,rng):
    
    a = get_date_time()['datetime']
    success_array = []
    unsuccess_array = []
    success_count = 0
    unsuccess_count = 0
    
    for i in range(int(rng)):

        x = a - timedelta(days=(i))
        y = str(x.date()).split('-')

        earlier = y[0] + '-' + y[1] + '-' + y[2] + ' 00:00:00'
        last = y[0] + '-' + y[1] + '-' + y[2] + ' 23:59:59'

        earlier = datetime.strptime(earlier,"%Y-%m-%d %H:%M:%S").timestamp()
        last = datetime.strptime(last,"%Y-%m-%d %H:%M:%S").timestamp()
        
        s_count = Site_Sms_log.objects.filter(acc=acc, success=True, datetime__range=(earlier,last)).count()
        success_count += s_count
        success_array.append(s_count)

        us_count = Site_Sms_log.objects.filter(acc=acc, success=False, datetime__range=(earlier,last)).count()
        unsuccess_count += us_count
        unsuccess_array.append(us_count)
    
    return [success_array[::-1], unsuccess_array[::-1], success_count, unsuccess_count]


@register.simple_tag
def get_price_log(asset):
    return Account_Price_log.objects.filter(symbol=asset).order_by('-pk')[:5]


@register.simple_tag
def get_balance_log(asset):
    return Account_Balance_log.objects.filter(symbol=asset).order_by('-pk')[:9]



@register.simple_tag
def return_symbol_price_chart(asset,rng):
    
    a = get_date_time()['datetime']
    buy_array = []
    sell_array = []
    buy_count = 0
    sell_count = 0
    buy_counter = 1
    sell_counter = 1

    for i in range(int(rng)):

        x = a - timedelta(days=(i))
        y = str(x.date()).split('-')

        earlier = y[0] + '-' + y[1] + '-' + y[2] + ' 00:00:00'
        last = y[0] + '-' + y[1] + '-' + y[2] + ' 23:59:59'

        earlier = datetime.strptime(earlier,"%Y-%m-%d %H:%M:%S").timestamp()
        last = datetime.strptime(last,"%Y-%m-%d %H:%M:%S").timestamp()
        
        b_count = Account_Price_log.objects.filter(symbol=asset, date__range=(earlier,last)).aggregate(Avg('buy'))['buy__avg']
        if str(b_count) == 'None' : b_count = 0  
        buy_count += b_count
        if b_count > 0 : buy_counter += 1 
        buy_array.append(int(b_count))


    return [buy_array[::-1], sell_array[::-1], int(int(buy_count) / buy_counter), int(int(sell_count) / sell_counter)]



@register.simple_tag
def return_symbol_balance_chart(asset,rng):
    
    a = get_date_time()['datetime']
    balance_array = []

    for i in range(int(rng)):

        x = a - timedelta(days=(i))
        y = str(x.date()).split('-')

        earlier = y[0] + '-' + y[1] + '-' + y[2] + ' 00:00:00'
        last = y[0] + '-' + y[1] + '-' + y[2] + ' 23:59:59'

        earlier = datetime.strptime(earlier,"%Y-%m-%d %H:%M:%S").timestamp()
        last =datetime.strptime(last,"%Y-%m-%d %H:%M:%S").timestamp()
        
        balance = Account_Balance_log.objects.filter(symbol=asset, date__range=(earlier,last)).aggregate(Avg('active_balance'))['active_balance__avg']

        if str(balance) == 'None' : balance = 0
        balance_array.append(float(balance))


    return [balance_array[::-1]]


@register.simple_tag
def get_country_list():
    return Site_Country.objects.all()


# delete others code
# delete others code
# delete others code
# delete others code
# delete others code
# .
# .
# .