from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User, Permission
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse, JsonResponse
from currency.models import *
from exchange.func.theme import *
from .models import *
from exchange.func.public import *
from .func.access import *
import time
import datetime
from wallet.models import *
from customer.func.public import *
from account.func.currency_buySell import *
from ticket.models import *

from itertools import chain

import random
from django.db.models import Sum
from openpyxl import Workbook
from django.conf import settings
import numpy as np
from django.db.models import Sum, F
from decimal import Decimal
import khayyam
from django.http import QueryDict

from datetime import datetime
from django.utils.html import escape


def customer_panel(request):
  

    # customer check start
    try :
        pattern_url = customer_access_check(request)
        if pattern_url[0] != 100 : return redirect(pattern_url[1])
    except: return redirect('account')
    # customer check end

    message = None

    if request.session.get('notification') != None :
        message = request.session.get('notification')
    request.session['notification'] = None
 


    return render(request, get_customer_theme(pattern_url[2]) + 'panel.html', {})


def customer_register_code_verify_request(request):

    # Login Check Start
    if not request.user.is_authenticated :
        return redirect('account')
    # Login Check End

    if request.method == 'POST' :

        mobile = request.POST.get('mobile')

        customer = Customer.objects.get(req_user=request.user)

        m_check = mobile_check(mobile)
        if m_check[0] == False :
            return JsonResponse({'type':'danger', 'msg':m_check[1]})

        if Customer.objects.filter(req_user__startswith='customer-',mobile=mobile).exclude(req_user=request.user).count() != 0 :
            return JsonResponse({'type':'danger', 'msg':'تلفن همراه وارد شده قبلا در سیستم ثبت شده است'})

        if (int(customer.last_code_datetime) + 60 ) > int(time.time()) :
            return JsonResponse({'type':'danger', 'msg':'زمان دریافت کد جدید هر یک دقیقه است'})
        
        if customer.mobile != mobile : 
            
            customer.mobile = mobile
            customer.is_mobile_ownership = False
            customer.is_mobile = False
            customer.save()
            
            return JsonResponse({'type':'redirect', 'msg':'استعلام مالکیت تلفن همراه الزامیست'})
        
        code = code_generator(4)
        result = code_sender(mobile, '', code)
            
        if result[0] == True :

            customer.mobile = mobile
            customer.last_code = code
            customer.last_code_datetime = get_date_time()['timestamp']
            customer.save()
            if customer.is_from_pwa == True :
                add_static_report(request, 'درخواست کد ورود', None, True, customer.req_user, get_ip(request))
            else :
                add_static_report(request, 'درخواست کد ورود')

        return JsonResponse({'type':'success', 'msg':'کد با موفقیت ارسال شد'})

    return JsonResponse({'type':'danger', 'msg':'در ارسال کد خطایی رخ داده'})


def customer_register_code_verify_request_submit(request):

    # Login Check Start
    if not request.user.is_authenticated :
        return redirect('account')
    # Login Check End

    if request.method == 'POST' :

        number1 = request.POST.get('number1')
        number2 = request.POST.get('number2')
        number3 = request.POST.get('number3')
        number4 = request.POST.get('number4')

        if number1 == "" or number2 == "" or number3 == "" or number4 == "" :
            return JsonResponse({'type':'danger', 'msg':'لطفا کد را به صورت صحیح وارد نمایید'})
        
        customer = Customer.objects.get(req_user=request.user)
        
        if (int(customer.last_code_datetime) + 60 ) < int(time.time()) :
            return JsonResponse({'type':'danger', 'msg':'کد دریافتی منقضی شده. لطفا کد جدید دریافت نمایید'})
        
        code = str(number1) + str(number2) + str(number3) + str(number4)

        if int(code) == int(customer.last_code) :

            customer.last_code_datetime = 0
            customer.is_mobile = True
            customer.save()

            if customer.is_from_pwa == True :
                add_static_report(request, 'تایید کد ثبت نام',None, True, customer.req_user, get_ip(request))   
            else:   
                add_static_report(request, 'تایید کد ثبت نام')

            return JsonResponse({'type':'success', 'msg':'کد با موفقیت تایید شد'})

        else:

            customer.last_code_datetime = 0
            customer.is_mobile = False
            customer.save()
            if customer.is_from_pwa == True :
                add_static_report(request, 'کد اشتباه برای تایید کد ثبت نام',None, True, customer.req_user, get_ip(request))   
            else:
                add_static_report(request, 'کد اشتباه برای تایید کد ثبت نام')

            return JsonResponse({'type':'danger', 'msg':'کد وارد شده صحیح نیست'})

    return JsonResponse({'type':'danger', 'msg':'پردازش مورد نظر با مشکل مواجه شده است'})


def customer_rulls_accept(request):

    # Login Check Start
    if not request.user.is_authenticated :
        return redirect('account')
    # Login Check End

    customer = Customer.objects.get(req_user=request.user)
    if customer.is_rulls == True : return redirect('customer_profile_complate')


    return render(request, get_customer_theme(customer) + 'rulls_accept.html')



def customer_national_code_verify_request(request):

    # Login Check Start
    if not request.user.is_authenticated :
        return redirect('account')
    # Login Check End

    if request.method == 'POST' :

        is_rulls = request.POST.get('is_rulls')
        customer = Customer.objects.get(req_user=request.user)

        if is_rulls == 'on' : customer.is_rulls = True
        else : customer.is_rulls = False

        
        customer.save()
        
        if customer.is_from_pwa == True :
            add_static_report(request, 'تایید قوانین سایت', 'success', True, customer.req_user, get_ip(request))   
        else:
            add_static_report(request, 'تایید قوانین سایت', 'success')
        
        return JsonResponse({'type':'success', 'msg':'قوانین سایت با موفقیت پذیرفته شد'})

        # else:

        #     return JsonResponse({'type':'danger', 'msg':'کد ملی شما صحیح نیست'})

    return JsonResponse({'type':'danger', 'msg':'پردازش مورد نظر با مشکل مواجه شده است'})


def customer_profile_complate(request):

    # Login Check Start
    if not request.user.is_authenticated :
        return redirect('account')
    # Login Check End

    customer = Customer.objects.get(req_user=request.user)
    if customer.is_profile == True : return redirect('customer_panel')


    today = int(get_date_time()['shamsi_date'][:4])


    return render(request, get_customer_theme(customer) + 'profile_complate.html',{'year':range((today-81),today),'month': range(1,13) ,'days':range(1,32),'introduction':Method_Introduction.objects.filter(act=True).order_by('pk')})


def customer_profile_complate_submit(request):

    # Login Check Start
    if not request.user.is_authenticated :
        return redirect('account')
    # Login Check End

    if request.method == 'POST' :


        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        # father_name = request.POST.get('father_name')
        country = request.POST.get('country')
        state = request.POST.get('state')
        city = request.POST.get('city')
        user_type = request.POST.get('user_type')
        # birth_date = request.POST.get('birth_date')
        address = request.POST.get('address')
        # nick_name = request.POST.get('nick_name')
        brith_year = request.POST.get('brith_year')
        brith_month = request.POST.get('brith_month')
        birth_day = request.POST.get('birth_day')
        introduction = request.POST.get('introduction')

        

        if first_name == "" or last_name == ""  or country == "select" or state == "select" or city == "select" or user_type == "select" or brith_year == "-"  or brith_month == "-"  or birth_day == "-" or introduction == "-" :
            return JsonResponse({'type':'danger', 'msg':'لطفا موارد خواسته شده را وارد نمایید'})

 
        if len(first_name) > 100 or len(last_name) > 100 :
            return JsonResponse({'type':'danger', 'msg':'تعداد کاراکترهای وارد شده بیش از حد مجاز است'})

        if birth_day == "31" and brith_month in ["07" , "08" , "09" , "10" , "11" , "12"] :
            return JsonResponse({'type':'danger', 'msg':'تاریخ وارد شده صحیح نیست'})

        customer = Customer.objects.get(req_user=request.user)

        try :

            uploader = upload_file(request.FILES['profile'],'media/profile')
            if uploader[0] != True : return JsonResponse({'type':'danger', 'msg':uploader[1]})
            profile_name = uploader[2]

        except : profile_name = 'melli_user_1.png'

        first_name = escape(first_name)

        last_name = escape(last_name)


        if address == '' : address = 'ثبت نشده'

        address = escape(address)

        customer.first_name = first_name
        customer.last_name = last_name
        customer.father_name = '-'
        customer.sex = user_type
        customer.country = country
        customer.state = state
        customer.city = city
        customer.address = address
        customer.profile_pic_name = profile_name
        customer.is_profile = True
        customer.nick_name = first_name
        customer.brith_year = brith_year
        customer.brith_month = brith_month
        customer.birth_day = birth_day
        customer.method_introduction = Method_Introduction.objects.get(pk=introduction)
        customer.save()

        if customer.is_from_pwa == True :
            add_static_report(request, 'تکمیل مشخصات پروفایل کاربری', 'success', True, customer.req_user, get_ip(request))   
        else:
            add_static_report(request, 'تکمیل مشخصات پروفایل کاربری', 'success')

        return JsonResponse({'type':'success', 'msg':'اطلاعات شما با موفقیت ثبت شد','picture':profile_name})
    

    return render(request, get_customer_theme(customer) + 'profile_complate.html')


def customer_login_nationalId_check(request):

    if Site_Settings.objects.get(code=1001).is_customer_login == False :
        return JsonResponse({'type':'danger', 'msg':'در حال حاضر به دلیل بروزرسانی امکان ورود به سایت وجود ندارد'})
    
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    user_ip = get_ip(request)

    request_access_check = error_logs_access_check(user_ip, "customer_login", 3, {'type':'minutes', "value":5}, {'type':'hours', "value":6}, 'ip', user_agent)
    if request_access_check['type'] == 'danger': return JsonResponse(request_access_check)

    if request.method == 'POST' :

        national_id = request.POST.get('nationalId')

        if national_id == "" :
            return JsonResponse({'type':'danger', 'msg':'کد ملی وارد شده صحیح نیست'})

        if national_id != '0000000000':

            nid_check = national_id_check(national_id)
            if nid_check[0] == False :
                Customer_Requests_Logs.objects.create(ip = user_ip, user_agent = user_agent, identify = "customer_login", error = nid_check[1], datetime = get_date_time()['timestamp'])
                return JsonResponse({'type':'danger', 'msg':nid_check[1]})

        try: 
            customer = Customer.objects.get(req_user__startswith='customer', national_id=national_id)
            ouruser = "True"

            request_access_check_user = error_logs_access_check(customer.pk, "customer_login", 3, {'type':'minutes', "value":5}, {'type':'hours', "value":6})
            if request_access_check_user['type'] == 'danger': return JsonResponse(request_access_check_user)

        except:
            Customer_Requests_Logs.objects.create(ip=user_ip, user_agent=user_agent, identify="customer_login", error="کدملی صحیح نمی باشد", datetime=get_date_time()['timestamp'])
            ouruser = "False"
            return JsonResponse({'type':'danger', 'msg':'کد ملی وارد شده صحیح نیست ,لطفا مجددا وارد نمایید ','ouruser':ouruser,'national_id': national_id})
    

        if (int(customer.last_code_datetime) + 60 ) > int(time.time()) :
            return JsonResponse({'type':'danger', 'msg':'زمان دریافت کد جدید هر یک دقیقه است'})

        code = code_generator(4)
        result = code_sender(customer.mobile, '', code)
        
        if result[0] == True :

            customer.last_code = code
            # customer.is_mobile = True
            customer.last_code_datetime = get_date_time()['timestamp']
            customer.save()

        else : return JsonResponse({'type':'danger', 'msg':'در ارسال کد خطایی رخ داده'})


        return JsonResponse({'type':'success', 'msg':'به بخش ورود خوش آمدید', 'nationalID':national_id,'ouruser':ouruser})

    return JsonResponse({'type':'danger', 'msg':'نام کاربری یا رمزعبور صحیح نیست','ouruser':ouruser})


def customer_login_pass(request):

    user_agent = request.META.get('HTTP_USER_AGENT', '')
    user_ip = get_ip(request)

    request_access_check = error_logs_access_check(user_ip, "customer_login", 3, {'type':'minutes', "value":5}, {'type':'hours', "value":6}, 'ip', user_agent)
    if request_access_check['type'] == 'danger': return JsonResponse(request_access_check)

    if request.method == 'POST' :

        uname = request.POST.get('uname')
        upass = request.POST.get('upass')

        if Site_Settings.objects.get(code=1001).is_customer_login == False and uname != '0000000000' :
            return JsonResponse({'type':'danger', 'msg':'در حال حاضر به دلیل بروزرسانی امکان ورود به سایت وجود ندارد'})

        if uname == "" or upass == "" :
            return JsonResponse({'type':'danger', 'msg':'نام کاربری یا رمزعبور صحیح نیست'})

        
        customer = Customer.objects.filter(req_user=f'customer-{uname}', national_id=uname)

        if customer.count() != 1 :
            ouruser = "False"
            Customer_Requests_Logs.objects.create(ip = user_ip, user_agent = user_agent, identify = "customer_login", error = "کدملی صحیح نمی باشد", datetime = get_date_time()['timestamp'])
            return JsonResponse({'type':'danger', 'msg':'کد ملی وارد شده صحیح نیست.','ouruser':ouruser,'national_id': uname})
        
        request_access_check_user = error_logs_access_check(customer.last().pk, "customer_login", 3, {'type':'minutes', "value":5}, {'type':'hours', "value":6})
        if request_access_check_user['type'] == 'danger': return JsonResponse(request_access_check_user)

        user = authenticate(username="customer-" + uname, password=upass)

        if user != None : 

            login(request, user)

            time_stamp = get_date_time()['timestamp']

            customer = Customer.objects.get(req_user__startswith='customer',national_id=uname)
            customer.last_login = time_stamp
            customer.is_from_pwa = False
            customer.last_ip = get_ip(request)
            customer.day_of_login = datetime.fromtimestamp(time_stamp).strftime('%A')
            customer.day_of_register = datetime.fromtimestamp(int(customer.reg_date)).strftime('%A')
            customer.user_agent = request.META.get('HTTP_USER_AGENT', '')
            if customer.is_toverification == True : customer.is_toverification_requird = True
            customer.save()
            if customer.is_from_pwa == True :
                add_static_report(request, 'ورود به سایت با رمزعبور', 'success', True, customer.req_user, get_ip(request))   
            else: add_static_report(request, 'ورود به سایت با رمزعبور', 'success')

            return JsonResponse({'type':'success', 'msg':'ورود با موفقیت انجام شد ...'})

        else: 
            Customer_Requests_Logs.objects.create(uname = customer.last(), identify = "customer_login", error = "رمز عبور صحیح نمی باشد", datetime = get_date_time()['timestamp'])
            ouruser = "True"
            return JsonResponse({'type':'danger', 'msg':'کد ملی یا رمز عبور صحیح نیست، لطفا مجددا وارد نمایید.','ouruser':ouruser,'national_id': uname})
            
    return JsonResponse({'type':'danger', 'msg':'نام کاربری یا رمزعبور صحیح نیست'})


def customer_code_verify_request(request,uname): 
 
    if Site_Settings.objects.get(code=1001).is_customer_login == False :
        return JsonResponse({'type':'danger', 'msg':'در حال حاضر به دلیل بروزرسانی امکان ورود به سایت وجود ندارد'})

    user_agent = request.META.get('HTTP_USER_AGENT', '')
    user_ip = get_ip(request)

    request_access_check = error_logs_access_check(user_ip, "customer_login", 3, {'type':'minutes', "value":5}, {'type':'hours', "value":6}, 'ip', user_agent)
    if request_access_check['type'] == 'danger': return JsonResponse(request_access_check)

    try :
        customer = Customer.objects.get(req_user__startswith='customer', national_id=uname)
        
        request_access_check_user = error_logs_access_check(customer.pk, "customer_login", 3, {'type':'minutes', "value":5}, {'type':'hours', "value":6})
        if request_access_check_user['type'] == 'danger': return JsonResponse(request_access_check_user)

    except :
        Customer_Requests_Logs.objects.create(ip=user_ip, user_agent=user_agent, identify="customer_login", error="کدملی صحیح نمی باشد", datetime=get_date_time()['timestamp'])
        return JsonResponse({'type':'danger', 'msg':'کدملی وارد شده صحیح نمی باشد ,لطفا مجددا وارد نمایید '})
    

    if (int(customer.last_code_datetime) + 60 ) > int(time.time()) :
        return JsonResponse({'type':'danger', 'msg':'زمان دریافت کد جدید هر یک دقیقه است'})

    code = code_generator(4)
    result = code_sender(customer.mobile, '', code)
 
    if result[0] == True :
       
        customer.last_code = code
        customer.last_code_datetime = get_date_time()['timestamp']
        customer.save()
       
    else : return JsonResponse({'type':'danger', 'msg':'در ارسال کد خطایی رخ داده'})

    if customer.is_from_pwa == True :
        add_static_report(request, 'درخواست کد ورود',None, True, customer.req_user, get_ip(request))
    else:
        add_static_report(request, 'درخواست کد ورود')


    return JsonResponse({'type':'success', 'msg':'کد با موفقیت ارسال شد', 'nationalID':uname,'phone_number':f"{customer.mobile[:4]} ***** {customer.mobile[-2:]}"})


def customer_code_verify_submit(request, pk):

    
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    user_ip = get_ip(request)

    request_access_check = error_logs_access_check(user_ip, "customer_login", 3, {'type':'minutes', "value":5}, {'type':'hours', "value":6}, 'ip', user_agent)
    if request_access_check['type'] == 'danger': return JsonResponse(request_access_check)

    try: customer = Customer.objects.get(req_user__startswith='customer', national_id=pk)
    except:
        Customer_Requests_Logs.objects.create(ip = user_ip, user_agent = user_agent, identify = "customer_login", error = "کدملی وارد شده صحیح نیست.", datetime = get_date_time()['timestamp'])
        return JsonResponse({'type':'danger', 'msg':'کدملی وارد شده صحیح نمی باشد .لطفا کدملی خود را مجددا وارد نمایید '})
        
    request_access_check_user = error_logs_access_check(customer.pk, "customer_login", 3, {'type':'minutes', "value":5}, {'type':'hours', "value":6})
    if request_access_check_user['type'] == 'danger': return JsonResponse(request_access_check_user)

    if request.method == 'POST' :

        number1 = request.POST.get('number1')
        number2 = request.POST.get('number2')
        number3 = request.POST.get('number3')
        number4 = request.POST.get('number4')

        if number1 == "" or number2 == "" or number3 == "" or number4 == "" :
            return JsonResponse({'type':'danger', 'msg':'لطفا کد دریافتی خود را به صورت صحیح وارد نمایید'})

        if Site_Settings.objects.get(code=1001).is_customer_login == False :
            return JsonResponse({'type':'danger', 'msg':'در حال حاضر به دلیل بروزرسانی امکان ورود به سایت وجود ندارد'})

        try:
            number1 = int(number1)
            number2 = int(number2)
            number3 = int(number3)
            number4 = int(number4)
        except:
            if customer.is_from_pwa == True:
                add_static_report(request, 'وارد کردن کد نادرست برای ورود', 'danger', True, customer.req_user, get_ip(request))   
            else:
                add_static_report(request, 'وارد کردن کد نادرست برای ورود', 'danger')
            Customer_Requests_Logs.objects.create(uname = customer, identify = "customer_login", error = "کد وارد شده صحیح نیست.", datetime = get_date_time()['timestamp'])
            return JsonResponse({'type':'danger', 'msg':'کد وارد شده صحیح نیست'})
        
        code = str(number1) + str(number2) + str(number3) + str(number4)

        if (int(customer.last_code_datetime) + 60 ) < int(time.time()) :
            return JsonResponse({'type':'danger', 'msg':'کد دریافتی منقضی شده. لطفا کد جدید دریافت نمایید'})

        if int(customer.last_code) == int(code) : 
            
            time_stamp = get_date_time()['timestamp']

            customer.last_ip = get_ip(request)
            customer.is_mobile = True
            customer.last_login = time_stamp
            customer.is_from_pwa = False
            customer.last_code_datetime = 0
            customer.day_of_login = datetime.fromtimestamp(time_stamp).strftime('%A')
            customer.day_of_register = datetime.fromtimestamp(int(customer.reg_date)).strftime('%A')
            customer.user_agent = request.META.get('HTTP_USER_AGENT', '')
            if customer.is_toverification == True : customer.is_toverification_requird = True
            customer.save()

            user = User.objects.get(username="customer-" + str(pk))
            login(request, user)

            if customer.is_from_pwa == True :
                add_static_report(request, 'ورود به اپلیکیشن با کد یکبارمصرف', 'success', True, customer.req_user, get_ip(request))   
            else:
                add_static_report(request, 'ورود به سایت با کد یکبارمصرف', 'success')
           
            return JsonResponse({'type':'success', 'msg':'ورود با موفقیت انجام شد ...'}) 

        else: 

            customer.last_code_datetime = 0
            customer.save()
            if customer.is_from_pwa == True :
                add_static_report(request, 'وارد کردن کد نادرست برای ورود', None, True, customer.req_user, get_ip(request))   
            else:
                add_static_report(request, 'وارد کردن کد نادرست برای ورود')
        Customer_Requests_Logs.objects.create(uname = customer, identify = "customer_login", error = "کد وارد شده صحیح نیست.", datetime = get_date_time()['timestamp']) 
        return JsonResponse({'type':'danger', 'msg':'کد وارد شده صحیح نیست'})   


def customer_register_submit(request):

    if request.method == 'POST' :

        national_id = request.POST.get('register_uname')
        mobile = request.POST.get('register_mobile')
        register_Identification = request.POST.get('register_Identification')

        Site_setting = Site_Settings.objects.get(code=1001)
        
        if Site_setting.is_customer_register == False :
            return JsonResponse({'type':'danger', 'msg':'در حال حاضر به دلیل بروزرسانی امکان ثبت نام در سایت وجود ندارد'})

        if national_id == "" or mobile == "" :
            return JsonResponse({'type':'danger', 'msg':'لطفا کد ملی و تلفن همراه خود را وارد نمایید'})

        nid_check = national_id_check(national_id)
        if nid_check[0] == False :
            return JsonResponse({'type':'danger', 'msg':nid_check[1]})

        m_check = mobile_check(mobile)
        if m_check[0] == False :
            return JsonResponse({'type':'danger', 'msg':m_check[1]})


        if Customer.objects.filter(req_user='customer-' + national_id).count() != 0 or User.objects.filter(username='customer-' + national_id).count() != 0 :
            return JsonResponse({'type':'danger', 'msg':'کد ملی قبلا در سیستم ثبت شده است'})

        if Customer.objects.filter(req_user__startswith='customer-',mobile=mobile).count() != 0 :
            return JsonResponse({'type':'danger', 'msg':'تلفن همراه قبلا در سیستم ثبت شده است'})

        if register_Identification != "" :    

            if Customer.objects.filter(referral_link=register_Identification, req_user__startswith='customer-').count() == 0 : 
                return JsonResponse({'type':'danger', 'msg':'کد معرف وارد شده نامعتبر است'})
            
        else  : 
            try :    
                invite = InviteUserWithSms.objects.get(mobile=mobile)
                register_Identification = invite.uname.referral_link
            except : 
                pass   
            
        
        mobile_ownership_description_reject = None
        if Site_setting.is_nationalid_mobile_check == False :

            is_mobile_ownership = True

        user_pass = pass_generator(12)

        User.objects.create_user(username='customer-' + national_id, email="customer@exchange.com", password=user_pass)
        u = User.objects.get(username='customer-' + national_id)

        customer = Customer(
            
            user = u,
            national_id = national_id,
            mobile = mobile,
            up_referral_link = register_Identification,
            referral_link = 'MG' + create_introduced_link(),
            reg_date = get_date_time()['timestamp'],
            change_mobile_datetime = get_date_time()['timestamp'],
            req_user = 'customer-' + national_id,
            status = 'PreRegister',
            is_mobile_ownership = is_mobile_ownership,
            last_ip = get_ip(request),
            user_agent = request.META.get('HTTP_USER_AGENT', ''),
            hour_to_pending = 0,
            mobile_ownership_description_reject = mobile_ownership_description_reject,
            mobile_ownership_time = get_date_time()['timestamp'] + 900 if mobile_ownership_description_reject == None else 0,
            is_bank = False

        )
        customer.save()

        sett = Site_Gift.objects.get(code=1001)
        if sett.registration_gift_amount != float(0) or  sett.introduced_gift_amount != float(0) :

            c = Customer.objects.get(req_user=customer.req_user)
            c.get_gift = True
            c.save()
            if sett.people == 'all': registration_gift_amount = sett.registration_gift_amount
            elif sett.people == 'up_referral_link' and customer.up_referral_link != '': registration_gift_amount = sett.registration_gift_amount
            else: registration_gift_amount = 0


            Customer_gift(uname=Customer.objects.get(req_user=customer.req_user), amount_user=registration_gift_amount,wallet_user=sett.registration_gift,amount_interduce=sett.introduced_gift_amount,wallet_interduce=sett.intro_gift,min_buy=sett.register_buy,up_referral_link = register_Identification,min_transaction_user=sett.introduced_transaction).save()


        General_permission = Permission.objects.get(codename='customer_exchange_access')
        u.user_permissions.add(General_permission)

        user = authenticate(username="customer-" + national_id)
        if user != None : login(request, user)


        Send_Sms_Queue(phone=mobile,name ='',text=user_pass).save()

        code = code_generator(4)
        result = code_sender(customer.mobile, '', code)
        
        if result[0] == True :

            customer.last_code = code
            customer.last_code_datetime = get_date_time()['timestamp']
            customer.save()


        if customer.is_from_pwa == True :
             add_static_report(request, 'ثبت نام در سیستم','success', True, customer.req_user, get_ip(request))   
        else:
            add_static_report(request, 'ثبت نام در سیستم', 'success')

        return JsonResponse({'type':'success', 'msg':'ثبت نام با موفقیت انجام شد'})

    return JsonResponse({'type':'danger', 'msg':'در ارسال کد خطایی رخ داده'})


def customer_register_ref_submit(request, code):

    if request.method == 'POST' :
        
        national_id = request.POST.get('register_uname')
        mobile = request.POST.get('register_mobile')

        Site_setting = Site_Settings.objects.get(code=1001)

        if Site_setting.is_customer_register == False:
            return JsonResponse({'type':'danger', 'msg':'در حال حاضر به دلیل بروزرسانی امکان ثبت نام در سایت وجود ندارد'})

        if national_id == "" or mobile == "":
            return JsonResponse({'type':'danger', 'msg':'لطفا کد ملی و تلفن همراه خود را وارد نمایید'})

        nid_check = national_id_check(national_id)
        if nid_check[0] == False:
            return JsonResponse({'type':'danger', 'msg':nid_check[1]})

        m_check = mobile_check(mobile)
        if m_check[0] == False:
            return JsonResponse({'type':'danger', 'msg':m_check[1]})

        if Customer.objects.filter(req_user='customer-' + national_id).count() != 0 or User.objects.filter(username='customer-' + national_id).count() != 0 :
            return JsonResponse({'type':'danger', 'msg':'کد ملی قبلا در سیستم ثبت شده است'})

        if Customer.objects.filter(req_user__startswith='customer-',mobile=mobile).count() != 0 :
            return JsonResponse({'type':'danger', 'msg':'تلفن همراه قبلا در سیستم ثبت شده است'})

        if Customer.objects.filter(referral_link=code, req_user__startswith='customer-').count() == 0 : code = '-'

        mobile_ownership_description_reject = None
        if Site_setting.is_nationalid_mobile_check == True :

            is_mobile_ownership = False


        user_pass = pass_generator(12)


        User.objects.create_user(username='customer-' + national_id, email="customer@exchange.com", password=user_pass)
        u = User.objects.get(username='customer-' + national_id)

        customer = Customer(

            user = u,
            national_id = national_id,
            mobile = mobile,
            up_referral_link = code,
            referral_link = 'MG' + create_introduced_link(),
            reg_date = get_date_time()['timestamp'],
            change_mobile_datetime = get_date_time()['timestamp'],
            req_user = 'customer-' + national_id,
            status = 'PreRegister',
            is_mobile_ownership = is_mobile_ownership,
            last_ip = get_ip(request),
            user_agent = request.META.get('HTTP_USER_AGENT', ''),
            hour_to_pending = 0,
            mobile_ownership_description_reject = mobile_ownership_description_reject,
            mobile_ownership_time = get_date_time()['timestamp'] + 900 if mobile_ownership_description_reject == None else 0,
            is_bank = False

        )
        customer.save()

        sett = Site_Gift.objects.get(code=1001)
        if sett.registration_gift_amount != float(0) or  sett.introduced_gift_amount != float(0) :

            c = Customer.objects.get(req_user=customer.req_user)
            c.get_gift = True
            c.save()

            Customer_gift(uname=Customer.objects.get(req_user=customer.req_user),amount_user=sett.registration_gift_amount,wallet_user=sett.registration_gift,amount_interduce=sett.introduced_gift_amount,wallet_interduce=sett.intro_gift,min_buy=sett.register_buy,up_referral_link = code,min_transaction_user=sett.introduced_transaction).save()

        
        General_permission = Permission.objects.get(codename='test')
        u.user_permissions.add(General_permission)




        user = authenticate(username="customer-" + national_id)
        if user != None : login(request, user)



        Send_Sms_Queue(phone=mobile,name ='',text=user_pass).save()

        code = code_generator(4)
        result = code_sender(customer.mobile, '', code)
        
        if result[0] == True :

            customer.last_code = code
            customer.last_code_datetime = get_date_time()['timestamp']
            customer.save()

        

        if customer.is_from_pwa == True :
            add_static_report(request, 'ثبت نام در سیستم', 'success', True, customer.req_user, get_ip(request))   
        else:
            add_static_report(request, 'ثبت نام در سیستم', 'success')

        return JsonResponse({'type':'success', 'msg':'ثبت نام با موفقیت انجام شد'})


    return JsonResponse({'type':'danger', 'msg':'در ارسال کد خطایی رخ داده'})


def customer_forget_password(request):

    user_agent = request.META.get('HTTP_USER_AGENT', '')
    user_ip = get_ip(request)

    request_access_check = error_logs_access_check(user_ip, "customer_forget_password", 3, {'type':'minutes', "value":5}, {'type':'hours', "value":6}, 'ip', user_agent)
    if request_access_check['type'] == 'danger': return JsonResponse(request_access_check)

    if request.method == 'POST' :

        national_id = request.POST.get('nationalId')

        if national_id == "" : return JsonResponse({'type':'danger', 'msg':'کد ملی وارد شده صحیح نیست'})

        nid_check = national_id_check(national_id)
        if nid_check[0] == False:
            Customer_Requests_Logs.objects.create(ip = user_ip, user_agent = user_agent, identify = "customer_forget_password", error = nid_check[1], datetime = get_date_time()['timestamp'])
            return JsonResponse({'type':'danger', 'msg':nid_check[1]})
        
        if Customer.objects.filter(req_user__startswith='customer', national_id=national_id).count() != 1 :
            Customer_Requests_Logs.objects.create(ip = user_ip, user_agent = user_agent, identify = "customer_forget_password", error = 'کد ملی صحیح نیست', datetime = get_date_time()['timestamp'])
            return JsonResponse({'type':'danger', 'msg':'کد ملی وارد شده صحیح نیست'})

        customer = Customer.objects.get(req_user__startswith='customer', national_id=national_id)

        request_access_check_user = error_logs_access_check(customer.pk, "customer_forget_password", 3, {'type':'minutes', "value":5}, {'type':'hours', "value":6})
        if request_access_check_user['type'] == 'danger': return JsonResponse(request_access_check_user)

        if (int(customer.last_code_datetime) + 60 ) > int(time.time()) :
            return JsonResponse({'type':'danger', 'msg':'زمان دریافت کد جدید هر یک دقیقه است'})

        code = code_generator(4)
        result = code_sender(customer.mobile, '', code)
            
        if result[0] == True :

            customer.last_code = code
            customer.last_code_datetime = get_date_time()['timestamp']
            customer.save()

            if customer.is_from_pwa == True :
                add_static_report(request, 'درخواست کد فراموشی رمزعبور',None, True, customer.req_user, get_ip(request))   
            else:
                add_static_report(request, 'درخواست کد فراموشی رمزعبور')

            
            return JsonResponse({'type':'success', 'msg':'کد با موفقیت ارسال شد',"national_id_forget_password":national_id})    

    return JsonResponse({'type':'danger', 'msg':'در ارسال کد خطایی رخ داده'})


def customer_forget_password_check(request, pk):

    user_agent = request.META.get('HTTP_USER_AGENT', '')
    user_ip = get_ip(request)

    request_access_check = error_logs_access_check(user_ip, "customer_forget_password", 3, {'type':'minutes', "value":5}, {'type':'hours', "value":6}, 'ip', user_agent)
    if request_access_check['type'] == 'danger': return JsonResponse(request_access_check)

    try: customer = Customer.objects.get(req_user__startswith='customer', national_id=pk) 
    except: 
        Customer_Requests_Logs.objects.create(ip = user_ip, user_agent = user_agent, identify = "customer_forget_password", error = 'کاربر یافت نشد', datetime = get_date_time()['timestamp'])
        return JsonResponse({'type':'danger', 'msg':'کاربر یافت نشد'})
  
    request_access_check_user = error_logs_access_check(customer.pk, "customer_forget_password", 3, {'type':'minutes', "value":5}, {'type':'hours', "value":6})
    if request_access_check_user['type'] == 'danger': return JsonResponse(request_access_check_user)

    if request.method == 'POST' :

        number1 = request.POST.get('number1')
        number2 = request.POST.get('number2')
        number3 = request.POST.get('number3')
        number4 = request.POST.get('number4')

        if number1 == "" or number2 == "" or number3 == "" or number4 == "" :
            return JsonResponse({'type':'danger', 'msg':'لطفا کد دریافتی خود را به صورت صحیح وارد نمایید'})

        try:
            number1 = int(number1)
            number2 = int(number2)
            number3 = int(number3)
            number4 = int(number4)
        except: 
            if customer.is_from_pwa == True :
                add_static_report(request, 'وارد کردن کد نادرست برای ورود', 'danger', True, customer.req_user, get_ip(request))   
            else:
                add_static_report(request, 'وارد کردن کد نادرست برای ورود', 'danger') 

            Customer_Requests_Logs.objects.create(
                uname = customer,
                identify = "customer_forget_password",
                error = "کد وارد شده صحیح نیست.", 
                datetime = get_date_time()['timestamp']
            )
            return JsonResponse({'type':'danger', 'msg':'کد وارد شده صحیح نیست'})

        code = str(number1) + str(number2) + str(number3) + str(number4)

        if (int(customer.last_code_datetime) + 60 ) < int(time.time()):

            return JsonResponse({'type':'danger', 'msg':'کد دریافتی منقضی شده. لطفا کد جدید دریافت نمایید'})

        if int(customer.last_code) == int(code) : 
    
            new_pass = pass_generator(8)
            user = User.objects.get(username="customer-" + str(pk))
            user.set_password(new_pass)
            user.save()

            customer.is_force_to_change_pass = True
            customer.last_code_datetime = 0
            customer.save()

            result = code_sender(customer.mobile, '', new_pass)

            if result[0] != True :
                return JsonResponse({'type':'danger', 'msg':'در ارسال رمزعبور جدید خطایی رخ داده است'}) 
            if customer.is_from_pwa == True :
                add_static_report(request, 'دریافت رمزعبور جدید', 'success', True, customer.req_user, get_ip(request))   
            else:
                add_static_report(request, 'دریافت رمزعبور جدید', 'success')
            return JsonResponse({'type':'success', 'msg':'رمزعبور جدید با موفقیت برای شما ارسال شد'}) 

        else:

            customer.last_code_datetime = 0
            customer.save()
            if customer.is_from_pwa == True :
                add_static_report(request, 'وارد کردن کد نادرست برای فراموشی رمز',None, True, customer.req_user, get_ip(request))   
            else:
                add_static_report(request, 'وارد کردن کد نادرست برای فراموشی رمز') 
            
            Customer_Requests_Logs.objects.create(
                uname = customer,
                identify = "customer_forget_password",
                error = "وارد کردن کد نادرست برای فراموشی رمز.", 
                datetime = get_date_time()['timestamp']
            )
        return JsonResponse({'type':'danger', 'msg':'کد وارد شده صحیح نیست'})    


def customer_profile_edit(request):

    # customer check start
    try :
        pattern_url = customer_access_check(request)
        if pattern_url[0] != 100 : return redirect(pattern_url[1])
    except: return redirect('account')
    # customer check end

    customer = pattern_url[2]
    # auths = Auth.objects.filter(customer=customer,).order_by('-pk')[:3]

    path = request.path
    if 'gold' in path : active_tab = '2'
    elif 'irt' in path : active_tab = '3'
    else : active_tab = '1' 


    catauth = Auth_Category.objects.filter(active=True)
    customerauth = []
    for catauth in catauth:
        if Auth.objects.filter(customer=customer, category=catauth).count() != 0:
            customerauth.append(Auth.objects.filter(customer=customer, category=catauth).last)

    today = int(get_date_time()['shamsi_date'][:4])

    if customer.pyotp_hash in ['-', ''] :

        new_hash = generate_pyotp_hash()

        customer.pyotp_hash = new_hash[1]
        customer.save()


    site_name = Site_Settings.objects.get(code=1001).title_en
    qr_code_link = pyotp.totp.TOTP(customer.pyotp_hash).provisioning_uri(name=customer.national_id, issuer_name=site_name)
    qr_code_secret = qr_code_link.split('secret=')[1].split('&issuer')[0]

    durations = Heredity_Duration.objects.filter(act=True)

    heirs = Customer_Heir.objects.filter(uname=customer).order_by('-pk')
    heirs_count = heirs.count()

    heirs_paginator = Paginator(heirs, 10)
    heirs_page = request.GET.get('heirs_page', 1)

    try:
        heirs = heirs_paginator.page(heirs_page)
    except PageNotAnInteger:
        heirs = heirs_paginator.page(1)
    except EmptyPage:
        heirs = heirs_paginator.page(heirs_paginator.num_page)

    activities = Site_Static_log.objects.filter(uname=customer).order_by('-pk')
    activities_paginator = Paginator(activities, 10)
    act_page = request.GET.get('act_page', 1)

    try:
        user_activities = activities_paginator.page(act_page)
    except PageNotAnInteger:
        user_activities = activities_paginator.page(1)
    except EmptyPage:
        user_activities = activities_paginator.page(activities_paginator.num_page)

    return render(request, get_customer_theme(pattern_url[2]) + 'profile_edit.html',{'year':range((today-81),today),'month': range(1,13) ,'days':range(1,32),'customer':customer, 'qr_code_secret': qr_code_secret, 'auths':customerauth,'qrcode':qr_code_link,'user_activities':user_activities,'user_activities_count':activities.count(),'count_auth':Auth.objects.filter(customer=customer, status="Accepted").count(), 'heirs': heirs, 'heirs_count': heirs_count, 'durations': durations})


def customer_profile_edit_submit(request):

    # customer check start
    try :
        pattern_url = customer_access_check(request)
        if pattern_url[0] != 100 : return redirect(pattern_url[1])
    except: return redirect('account')
    # customer check end

    if request.method == 'POST' :


        customer = pattern_url[2]
        if customer.is_auth == True :

            nick_name = request.POST.get('nick_name')

            if len(nick_name) > 100 :
                return JsonResponse({'type':'danger', 'msg':'تعداد کاراکترهای وارد شده بیش از حد مجاز است'})     

            nick_name = escape(nick_name)

            try :

                uploader = upload_file(request.FILES['select_img'],'media/profile')
                if uploader[0] != True : return JsonResponse({'type':'danger', 'msg':uploader[1]})

                fs = FileSystemStorage(location='media/profile')
                fs.delete(customer.profile_pic_name)
        
                profile_name = uploader[2]

            except : profile_name = customer.profile_pic_name

            customer.profile_pic_name = profile_name
            customer.nick_name = nick_name
            customer.save()

        else :


            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            father_name = request.POST.get('father_name')
            country = request.POST.get('country')
            state = request.POST.get('state')
            city = request.POST.get('city')
            user_type = request.POST.get('user_type')
            address = request.POST.get('address')
            nick_name = request.POST.get('nick_name')
            brith_year = request.POST.get('brith_year')
            brith_month = request.POST.get('brith_month')
            birth_day = request.POST.get('birth_day')


            if first_name == "" or last_name == "" or father_name == "" or country == "select" or state == "select" or city == "select" or user_type == "select" or brith_year == "-" or  brith_month == "-" or birth_day == "-" :
                return JsonResponse({'type':'danger', 'msg':'لطفا موارد خواسته شده را وارد نمایید'})


            if len(first_name) > 100 or len(last_name) > 100 or len(father_name) > 100 :
                return JsonResponse({'type':'danger', 'msg':'تعداد کاراکترهای وارد شده بیش از حد مجاز است'})     

            if birth_day == "31" and brith_month in ["07" , "08" , "09" , "10" , "11" , "12"] :
                return JsonResponse({'type':'danger', 'msg':'تاریخ وارد شده صحیح نیست'})

            try :

                uploader = upload_file(request.FILES['select_img'],'media/profile')
                if uploader[0] != True : return JsonResponse({'type':'danger', 'msg':uploader[1]})
                fs = FileSystemStorage(location='media/profile')
                fs.delete(customer.profile_pic_name)
                profile_name = uploader[2]

            except : profile_name = customer.profile_pic_name


            first_name = escape(first_name)  

            last_name = escape(last_name)

            father_name = escape(father_name) 

            nick_name = escape(nick_name) 

            address = escape(address)

            customer.first_name = first_name
            customer.last_name = last_name
            customer.father_name = father_name
            # customer.birth_date = birth_date
            customer.sex = user_type
            customer.country = country
            customer.state = state
            customer.city = city
            customer.address = address
            customer.profile_pic_name = profile_name
            customer.nick_name = nick_name
            customer.brith_year = brith_year
            customer.brith_month = brith_month
            customer.birth_day = birth_day
            customer.save()

        if customer.sex == 'Male' : user_type =  'مرد'
        elif customer.sex == 'FeMale' : user_type =  'زن'
        elif customer.sex == 'Other' : user_type =  'دیگر'
        else : user_type = 'نامشخص'

        if customer.is_from_pwa == True :
            add_static_report(request, 'ویرایش مشخصات کاربری',None, True, customer.req_user, get_ip(request))
        else:
            add_static_report(request, 'ویرایش مشخصات کاربری')

        return JsonResponse({'type':'success', 'msg':'اطلاعات شما با موفقیت ویرایش شد','picture':profile_name,'first_name':customer.first_name,'last_name':customer.last_name,'father_name':customer.father_name,'user_type':user_type,'country':customer.country,'state':customer.state,'city':customer.city,'address':customer.address,'nick_name':customer.nick_name,'brith_year':customer.brith_year,'brith_month':customer.brith_month,'birth_day':customer.birth_day})

    return render(request, get_customer_theme(pattern_url[2]) + 'profile_complate.html')


def customer_toman_wallet(request):
    # customer check start
    try :
        pattern_url = customer_access_check(request)
        if pattern_url[0] != 100 : return redirect(pattern_url[1])
    except: return redirect('account')
    # customer check end

    active_tab = '3' 

    wallet = Currency_List.objects.filter(is_wallet=True,is_show=True).order_by('sort')
    customer = pattern_url[2]


    trans_irt = Wallet.objects.filter(uname=customer, wallet='IRT', is_verify=True).exclude(is_locked=True).order_by('-pk')
    count_trans_irt = trans_irt.count()

    irt_page = request.GET.get('irt_page', 1)
    paginator_irt = Paginator(trans_irt, 10)

    try:
        trans_irt = paginator_irt.page(irt_page)
    except PageNotAnInteger:
        trans_irt = paginator_irt.page(1)
    except EmptyPage:
        trans_irt = paginator_irt.page(paginator_irt.num_pages)


    gram_equivalent_of_Toman_balance = get_customer_balance(request.user,'IRT')["balance"] / Currency_List.objects.get(symbol='XAU18').BuySellPrice['buy']

    return render(request, get_customer_theme(pattern_url[2]) + 'toman_wallet.html', {'customer':customer, 'active_tab': active_tab, 'trans_irt':trans_irt,'gram_equivalent_of_Toman_balance':gram_equivalent_of_Toman_balance, 'count_trans_irt':count_trans_irt})


def customer_gold_wallet(request):

    # customer check start
    try :
        pattern_url = customer_access_check(request)
        if pattern_url[0] != 100 : return redirect(pattern_url[1])
    except: return redirect('account')
    # customer check end

    active_tab = '2' 

    wallet = Currency_List.objects.filter(is_wallet=True,is_show=True).order_by('sort')
    customer = pattern_url[2]

    trans_gold = Wallet.objects.filter(uname=customer, wallet='XAU18', is_verify=True).order_by('-pk')
    count_trans_gold = trans_gold.count()


    gold_page = request.GET.get('gold_page', 1)
    paginator_gold = Paginator(trans_gold, 10)
    
    try: trans_gold = paginator_gold.page(gold_page)
    except PageNotAnInteger: trans_gold = paginator_gold.page(1)
    except EmptyPage: trans_gold = paginator_gold.page(paginator_gold.num_pages)

    toman_equivalent_of_gold_balance = int(round(get_customer_balance(request.user,'XAU18')["balance"] * Currency_List.objects.get(symbol='XAU18').BuySellPrice['sell']))
    return render(request, get_customer_theme(pattern_url[2]) + 'gold_wallet.html', {'wallet':wallet, 'active_tab': active_tab, 'customer':customer,'trans_gold':trans_gold,'toman_equivalent_of_gold_balance':toman_equivalent_of_gold_balance,'count_trans_gold':count_trans_gold})

def customer_wallet_online_increase_inventory(request):

    # customer check start
    try :
        pattern_url = customer_access_check(request)
        if pattern_url[0] != 100 : return redirect(pattern_url[1])
    except: return redirect('account')
    # customer check end

    customer = pattern_url[2]
    date = get_date_time()['timestamp']

    last_online_wallet = Online_Wallet.objects.filter(owner=customer).order_by('pk')
    if last_online_wallet.exists():
        if (int(last_online_wallet.last().datetime) + 10) > date:
            return JsonResponse({'type':'danger', 'msg':'برای ثبت درخواست مجدد لطفا کمی صبر کنید و سپس دوباره تلاش کنید.'})


    
    if request.method == 'POST' :

        if customer.status == 'Suspended' :
            return redirect('account')
        

        if Permission.objects.filter(user=request.user, codename='customer_authentication_complated').count() == 0 or customer.status != 'Authenticated' :
            return JsonResponse({'type':'redirect', 'msg':'برای اتصال به درگاه میبایست احراز هویت خود را تکمیل نمایید'})
        
        if Customer_card.objects.filter(uname=customer,is_verify=True,is_show=True).count()  == 0 :
            return JsonResponse({'type':'redirect', 'msg':'برای اتصال به درگاه میبایست کارت بانکی شما ثبت و تایید شده باشد'})
            
        setting = Site_Settings.objects.get(code=1001)

        if setting.is_increase_credit == False : return JsonResponse({'type':'danger', 'msg':'در حال حاضر اتصال به درگاه موقتا غیرفعال است'})


        if not customer.instant_increase:

            amount = request.POST.get('amount')

          
            try : amount = int(str(amount).replace(',',""))
            except : return JsonResponse({'type':'danger', 'msg':'لطفا مبلغ افزایش کیف پول خود را به صورت عددی وارد کنید'})

            if amount < 10000 or  amount > 200000000  :
                return JsonResponse({'type':'danger', 'msg':'افزایش اعتبار کیف پول نمیتواند کمتر از ۱۰ هزار تومان و بیشتر از ۲۰۰ میلیون باشد'})
        

            celling_increase = get_customer_CeilingRemain(customer.req_user)["increase"]

            if int(celling_increase) < amount :
                return JsonResponse({'type':'danger', 'msg':f'مانده سقف مجاز افزایش کیف پول شما {celling_increase:,} است'})

            totalPrice = amount
            
            ow = Online_Wallet(owner=customer, amount=amount, datetime=get_date_time()['timestamp'])
            ow.save()
            
        else:
            currency = Currency_List.objects.get(symbol='XAU18')
            Unitprice = currency.BuySellPrice['buy']
               
            minimum_buy_price = calculate_lower_amount_irt(Unitprice)
                    
            if not setting.is_buy_port: 
                return JsonResponse({'type':'danger', 'msg':'در حال حاضر خرید از درگاه بانکی غیرفعال است'})

            if not setting.is_instant_buysell:
                return JsonResponse({'type':'danger', 'msg':'در حال حاضر تبدیل آنی موقتا غیرفعال است'})
                
        
            amount = request.POST.get('amount')
            
            try: 
                amount = round(float(amount),4)
            
            except: 
                return JsonResponse({'type':'danger', 'msg':'لطفا مبلغ  را به صورت عددی وارد کنید'})
            
           
            if float(currency.buy_fee) != float(0) :

                f = ((currency.buy_fee * amount) / 100)
                if f < currency.buy_fee_lower : fee = currency.buy_fee_lower
                elif f > currency.buy_fee_upper : fee = currency.buy_fee_upper
                else : fee = f
                fee_price = round(fee * Unitprice , 0)

            else:

                fee = 0
                fee_price = 0


            maintenance_cost = int(amount * currency.maintenance_cost)

            totalPrice = round((amount * Unitprice) + fee_price + maintenance_cost)

            if amount > 200000000:
                return JsonResponse({'type':'danger', 'msg':'افزایش اعتبار کیف پول نمیتواند بیشتر از ۲۰۰ میلیون تومان باشد'})


            if totalPrice < minimum_buy_price:
                return JsonResponse({'type':'danger', 'msg':f'در تبدیل آنی حداقل مقدار خرید {minimum_buy_price:,} تومان می باشد'})

            balance =  currency.Balance - (((currency.Balance * currency.acc_fee) / 100) + (round(get_asset_wallet_reserved('XAMU18')['reserved'], 6))  +  (round(get_asset_bill_reserved('XAMU18')['pendding'], 6)))

            if amount + ((amount * currency.acc_fee) / 100) > (balance):
                return JsonResponse({'type':'danger', 'msg':'میزان درخواستی بیشتر از موجودی فعلی است.'})

            buy_celling = get_customer_CeilingRemain(customer.req_user)["buy"]
            if int(buy_celling) < totalPrice :
                return JsonResponse({'type':'danger', 'msg':f'مانده سقف مجاز افزایش کیف پول شما {buy_celling:,} است'})

            ow = Online_Wallet(
                owner=customer, 
                amount=totalPrice, 
                datetime=get_date_time()['timestamp'], 
                currency=currency,
                amount_buy=amount,
                deposite_on_wallet=False,
                getway_buy=True,
                is_reservation=False, 
                fee_amount=fee, 
                fee_price=fee_price,
                unit_price=Unitprice,
                maintenance_cost=maintenance_cost,
                is_instant_exchange=True, 
            )
            ow.save()

        if setting.default_payment_gateway == 'mellipay' :
            result = 'my_api'

        elif setting.default_payment_gateway == 'idpay' :
            result = 'my_api'

        elif setting.default_payment_gateway == 'paystar' :
            result = 'my_api'

        else : return JsonResponse({'type':'danger', 'msg':'در اتصال به درگاه خطایی رخ داده لطفا با پشتیبانی تماس بگیرید'})
        


        if setting.default_payment_gateway in ['mellipay', 'idpay'] and result["status"] == 201 :


            ow = Online_Wallet.objects.get(pk=ow.pk)
            ow.mellipay_track_id = 'my_result_api'
            ow.default_payment_gateway = setting.default_payment_gateway
            ow.save()
            if customer.is_from_pwa == True :
                add_static_report(request, 'اتصال به درگاه جهت افزایش اعتبار کیف پول',None, True, customer.req_user, get_ip(request))   
            else:
                add_static_report(request, 'اتصال به درگاه جهت افزایش اعتبار کیف پول')

            result = {"link": 'my_result_api'}
            response = JsonResponse({'type': 'success', 'msg': 'در حال انتقال به درگاه بانکی ...', 'redirect': result["link"]})
            response.set_cookie('return_url', request.META.get('HTTP_REFERER', 'Unknown'), max_age=3600) 
            
            return response



            # response.set_cookie('return_url', request.path, max_age=3600)      

            # return JsonResponse({'type':'success', 'msg':'در حال انتقال به درگاه بانکی ...', 'redirect':result["link"]})
        
        elif setting.default_payment_gateway in ['paystar'] and 'my_result_api' == 1 :
            
            ow = Online_Wallet.objects.get(pk=ow.pk)
            ow.mellipay_track_id = 'my_result_api'
            ow.default_payment_gateway = setting.default_payment_gateway
            ow.save()
            if customer.is_from_pwa == True :
                add_static_report(request, 'اتصال به درگاه جهت افزایش اعتبار کیف پول',None, True, customer.req_user, get_ip(request))   
            else:
                add_static_report(request, 'اتصال به درگاه جهت افزایش اعتبار کیف پول')

            paystar_link = 'my_link'

            return JsonResponse({'type':'success', 'msg':'در حال انتقال به درگاه بانکی ...', 'redirect':'my_result_api'})

        else: return JsonResponse({'type':'danger', 'msg':'در اتصال به درگاه خطایی رخ داده لطفا با پشتیبانی تماس بگیرید'})

    return redirect('customer_increase_inventory')




def customer_wallet_online_increase_confirm(request,pk,pid):



    if Online_Wallet.objects.filter(mellipay_track_id=pid).count() == 1:


        wO = Online_Wallet.objects.get(pk=pk)
        customer = Customer.objects.get(user=wO.owner.user)
        default_gateway = wO.default_payment_gateway


        if customer.status != 'Authenticated' :

            wO.is_completed = False
            wO.error_mellipay = "کاربر مسدود"
            wO.save()

            return render(request, get_customer_theme(customer) + 'error_getway.html', {'msg':'تراکنش نامعتبر'})

        if default_gateway == 'mellipay' : res = 'my_api'
        elif default_gateway == 'idpay' : res = 'my_api'
        elif default_gateway == 'paystar' : res = 'my_api'
        else :
            if wO.is_physical_delivery == True :

                order = Customer_Gold_Order.objects.get(pk=wO.order.pk)
                order.status = 'Rejected'
                order.error_gateway = "تراکنش یافت نشد"
                order.save()
              
                working_day = order.delivery_date
                working_day.capacity = working_day.capacity + 1
                working_day.save()

                
            wO.is_completed = False
            wO.error_mellipay = "تراکنش یافت نشد"
            wO.save()

            return render(request, get_customer_theme(customer) + 'error_getway.html', {'msg':'پرداخت تایید نشده است . در حال انتقال ...'})
            
        wO = Online_Wallet.objects.get(pk=pk)

        if res["status"] == 1 and wO.is_completed == True :

            if default_gateway == 'mellipay' : 'my_api'
            elif default_gateway == 'idpay' : 'my_api'
            elif default_gateway == 'paystar' : 'my_api'
            else :
                if wO.is_physical_delivery == True :

                    order = Customer_Gold_Order.objects.get(pk=wO.order.pk)
                    order.status = 'Rejected'
                    order.error_gateway = "تراکنش یافت نشد"
                    order.save()
                    
                    working_day = order.delivery_date
                    working_day.capacity = working_day.capacity + 1
                    working_day.save()

                        
                wO.is_completed = False
                wO.error_mellipay = "تراکنش یافت نشد"
                wO.save()

                return render(request, get_customer_theme(customer) + 'error_getway.html', {'msg':'پرداخت تایید نشده است . در حال انتقال ...'})
        

            wO = Online_Wallet.objects.get(pk=pk)
  

            if 'my_result_api' == 1 :

                time = get_date_time()['timestamp']

                need_to_wait = False
                delay_time = time

                if customer.hour_to_pending > 0 and int(wO.amount) > 1000000 : 
                    
                    need_to_wait = True
                    delay_time = time + (customer.hour_to_pending * 3600)

                if wO.getway_buy  == True and wO.is_instant_exchange == False and wO.is_currency_custom_price == False:
                    
                    if Currency_BuySell_List.objects.filter(uname = wO.owner, acc = wO.currency.acc, currency = wO.currency, amount = wO.amount_buy, is_gate = True, online_wallet_id=wO.pk, status='Pendding').count() == 0 :

                        Currency_BuySell_List(
    
                            uname = wO.owner,
                            acc = wO.currency.acc,
                            currency = wO.currency,
                            amount = wO.amount_buy,
                            fee_amount = wO.fee_amount,
                            fee_price = wO.fee_price,
                            unit_price = wO.unit_price,
                            total_price = wO.amount,
                            datetime = time,
                            is_gate = True,
                            ip = get_ip(request),
                            online_wallet_id = wO.pk,
                            deposite_on_wallet = wO.deposite_on_wallet,
                            is_reservation = wO.is_reservation,
                            need_pending = need_to_wait,
                            proccess_time = delay_time,

                            is_wallet_direct = wO.is_wallet_direct,
                            wallet_address =  wO.wallet_address,
                            wallet_chain = wO.wallet_chain,
                            maintenance_cost = wO.maintenance_cost

    
                        ).save()
    
                        return render(request, get_customer_theme(customer) + 'error_getway.html', {'msg':'خرید با موفقیت انجام شد', 'redirect':'buysell', 'color':'green'})
                        
                    else :

                        return render(request, get_customer_theme(customer) + 'error_getway.html', {'msg':'خرید با موفقیت انجام شد', 'redirect':'buysell', 'color':'green'})
                
                
                elif wO.is_physical_delivery == True :
                    

                    #physical-start

                    if Customer_Gold_Order.objects.filter(uname = wO.owner, pk=wO.order.pk, status='Connection_getway').count() == 1 :

                        order = Customer_Gold_Order.objects.get(uname = wO.owner, pk=wO.order.pk, status='Connection_getway')

                        if order.payment_status == 2 :

                            if Wallet.objects.filter(physical_delivery_pk = order.pk).count() != 0 :

                                order.status = 'Rejected'
                                order.error_gateway = "تراکنش تکراری"
                                order.save()
                               
                                working_day = order.delivery_date
                                working_day.capacity = working_day.capacity + 1
                                working_day.save()
                            
                                return render(request, get_customer_theme(customer) + 'error_getway.html', {'msg':'پرداخت تایید نشده است . در حال انتقال ...'})

                            else:

                                asset = Currency_List.objects.filter(is_show=True).first()
                                fund_balance = get_customer_balance(wO.owner.user, asset.symbol)['balance']

                                if fund_balance < order.gram_remaining :

                                    order.status = 'Rejected'
                                    order.error_gateway = "عدم موجودی صندوق طلا"
                                    order.save()

                                    return render(request, get_customer_theme(customer) + 'error_getway.html', {'msg':'پرداخت تایید نشده است . در حال انتقال ...'})
                                    
                                else :

                                    w = Wallet(

                                        uname = customer,
                                        wallet = asset,
                                        desc = f'بابت پرداخت تحویل فیزیکی  : {order.pk}',
                                        amount = order.gram_remaining * (-1),
                                        datetime = get_date_time()['timestamp'],
                                        confirmed_datetime = get_date_time()['timestamp'],
                                        ip = get_ip(request),
                                        is_verify = True,
                                        physical_delivery_pk = order.pk,

                                    )
                                    w.save()


                                    order.status = 'Pending'
                                    order.save()

                                    
                                    return render(request, get_customer_theme(customer) + 'error_getway.html', {'msg':'خرید با موفقیت انجام شد', 'redirect':'physical', 'color':'green'})


                        elif order.payment_status ==  1 : 

                            order.status = 'Pending'
                            order.save()

                            return render(request, get_customer_theme(customer) + 'error_getway.html', {'msg':'خرید با موفقیت انجام شد', 'redirect':'physical', 'color':'green'})

                    else :

                        return render(request, get_customer_theme(customer) + 'error_getway.html', {'msg':'پرداخت تایید نشده است . در حال انتقال ...'})
                
                    #physical-end

                elif wO.is_instant_exchange:

                    c = Currency_BuySell_List(
                        is_instant_exchange = True,

                        uname = wO.owner,
                        acc = wO.currency.acc,
                        currency = wO.currency,

                        online_wallet_id = wO.pk,

                        amount = wO.amount_buy,
                        fee_amount = wO.fee_amount,

                        fee_price = wO.fee_price,
                        unit_price = wO.unit_price,
                        total_price = wO.amount,
                        maintenance_cost =  wO.maintenance_cost,

                        deposite_on_wallet = False,
                        is_gate=wO.getway_buy,

                        bill_type = 'buy',
                        datetime = get_date_time()['timestamp'],
                        ip = get_ip(request),

                    )
                    c.save()

                    return render(request, get_customer_theme(customer) + 'error_getway.html', {'msg':'خرید با موفقیت انجام شد', 'redirect':'buysell', 'color':'green'})

                elif wO.is_currency_custom_price == True :

                    if Currency_BuySell_Custom_Price.objects.filter(uname = wO.owner, acc = wO.currency.acc, currency = wO.currency, amount = wO.amount_buy, is_gate = True, online_wallet_id=wO.pk).count() == 0 :

                        trans = Currency_BuySell_Custom_Price(

                            uname =  wO.owner,
                            acc = wO.currency.acc,
                            currency = wO.currency,
                            online_wallet_id = wO.pk,
                            desired_price = wO.desired_price,
                            amount = wO.amount_buy,
                            fee_amount = wO.fee_amount,
                            fee_price = wO.fee_price,
                            unit_price = wO.unit_price,
                            total_price = wO.amount,
                            datetime = time,
                            ip = get_ip(request),
                            amount_type =  wO.type_method,
                            process_based_on = wO.process_based_on,
                            irt_amount = wO.request_user_buy,
                            status = 'Pendding',
                            is_gate = True
                        )
                        trans.save()

                        return render(request, get_customer_theme(customer) + 'error_getway.html', {'msg':'درخواست خرید با موفقیت ثبت شد', 'redirect':'buy_request', 'color':'green'})

                    return render(request, get_customer_theme(customer) + 'error_getway.html', {'msg':'درخواست خرید با موفقیت ثبت شد', 'redirect':'buy_request', 'color':'green'})
                
                else :

                    if Wallet.objects.filter(online_wallet_id = wO.pk).count() != 0 or wO.wallet != None :

                        wO.is_completed = False
                        wO.error_mellipay = "تراکنش تکراری"
                        wO.save()

                        return render(request, get_customer_theme(customer) + 'error_getway.html', {'msg':'پرداخت تایید نشده است . در حال انتقال ...'})

                    else :

                        if need_to_wait == True :

                            wallt = Wallet(uname=customer, wallet='IRT', amount=int(wO.amount) , datetime=time, ip=get_ip(request), is_verify=False, desc="افزایش اعتبار آنلاین",online_wallet_id = wO.pk, need_pending=need_to_wait, proccess_time = delay_time)
                            wallt.save()

                        else : 

                            wallt = Wallet(uname=customer, wallet='IRT', amount=int(wO.amount) , datetime=time, ip=get_ip(request), is_verify=False, desc="افزایش اعتبار آنلاین",online_wallet_id = wO.pk)
                            wallt.save()

                        wO.wallet = wallt
                        wO.save()

                        return render(request, get_customer_theme(customer) + 'error_getway.html', {'msg':'افزایش اعتبار آنلاین با موفقیت انجام شد. در حال انتقال ...', 'redirect':'deposite', 'color':'green'})
              

            else :


                if wO.is_physical_delivery == True :
                    
                    order = Customer_Gold_Order.objects.get(pk=wO.order.pk)
                    order.status = 'Rejected'
                    order.error_gateway = 'my_result_api'
                    order.save()
                     
                    working_day = order.delivery_date
                    working_day.capacity = working_day.capacity + 1
                    working_day.save()

                
                

                wO.is_completed = False
                wO.error_mellipay = 'my_result_api'
                wO.save()

                return render(request, get_customer_theme(customer) + 'error_getway.html', {'msg':'پرداخت تایید نشده است و در صورت کسر وجه به صورت خودکار به حسابتان بازگشت خواهد خورد. در حال انتقال ...'})

        else :


            if wO.is_physical_delivery == True :

                order = Customer_Gold_Order.objects.get(pk=wO.order.pk)
                order.status = 'Rejected'
                order.error_gateway = 'my_result_api'
                order.save()
                 
                working_day = order.delivery_date
                working_day.capacity = working_day.capacity + 1
                working_day.save()

           
                
            
            wO.is_completed = False
            wO.error_mellipay = 'my_result_api'
            wO.save()

            return render(request, get_customer_theme(customer) + 'error_getway.html', { 'msg':'پرداخت تایید نشده است و در صورت کسر وجه به صورت خودکار به حسابتان بازگشت خواهد خورد. در حال انتقال ...'})

    return render(request, get_customer_theme() + 'error_getway.html', { 'msg':'تراکنش ناموفق ... در حال انتقال ...'})


def customer_cards(request):

    # customer check start
    try :
        pattern_url = customer_access_check(request)
        if pattern_url[0] != 100 : return redirect(pattern_url[1])
    except: return redirect('account')
    # customer check end

    customer = pattern_url[2]
    cards = Customer_card.objects.filter(uname=customer,is_show=True).order_by('-pk')
    cards1 = cards.exclude(is_verify=True).order_by('-pk')
    banks = Site_Banks.objects.filter(act=True)

    all_count = cards.count()
    accept = cards.filter(is_verify=True).count()
    rejected = cards.filter(is_verify=False).count()
    waitting = cards.filter(is_verify=None).count()

    return render(request, get_customer_theme(pattern_url[2]) + 'cards.html',{'cards':cards,'banks':banks,'cards1':cards1, 'all':all_count, 'accept':accept, 'rejected':rejected, 'waitting':waitting})


def customer_card_add_submit(request):


    # Login Check Start
    if not request.user.is_authenticated :
        return redirect('account')
    # Login Check End

    try: customer = Customer.objects.get(req_user=request.user)
    except: return JsonResponse({'type':'danger', 'msg':'کاربر یافت نشد.'})  
    
    request_access_check = error_logs_access_check(customer.pk, "customer_card_add_submit", 3, {'type':'hours', "value":24}, {'type':'hours', "value":12}) 
    if request_access_check['type'] == 'danger': return JsonResponse(request_access_check)

    if request.method == 'POST' :

        card_number = request.POST.get('card_number')
       
        if card_number == "" :
            return JsonResponse({'type':'danger', 'msg':'لطفا موارد خواسته شده را وارد نمایید'})

        isascii = lambda s: len(s) == len(s.encode())
        if str(isascii(card_number)) == 'False'  :
            return JsonResponse({'type':'danger', 'msg':'لطفا از اعداد انگلیسی برای ثبت مشخصات استفاده نمایید'})
        
        if len(card_number) != 16 :
            Customer_Requests_Logs.objects.create(uname = customer, identify = "customer_card_add_submit", error = "شماره کارت وارد شده صحیح نیست.", datetime = get_date_time()['timestamp'])
            return JsonResponse({'type':'danger', 'msg':' شماره کارت وارد شده صحیح نیست'})
        
        if Customer_card.objects.filter(uname__req_user__startswith='customer-', card_number=card_number, is_show=True).exclude(is_verify=False).count() != 0:
            Customer_Requests_Logs.objects.create(uname = customer, identify = "customer_card_add_submit", error = "شماره کارت وارد شده صحیح نیست.", datetime = get_date_time()['timestamp'])
            return JsonResponse({'type':'danger', 'msg':'شماره کارت وارد شده از قبل در سایت وجود دارد'})

        
        try: bank = Site_Banks.objects.get(code=card_number[:6])
        except: return JsonResponse({'type':'danger', 'msg':'شماره کارت وارد شده نامعتبر است'})    


        card = Customer_card(card_number=card_number, bank=bank, datetime=get_date_time()['timestamp'], uname=customer)
        card.save()

        card_detail = Shahkar_APi().check_card(customer.mobile,card_number)
        if card_detail['is_match'] == True :

            card.card_ownership = True
            card.save()

        if customer.is_bank == False :
            customer.is_bank = True
            customer.save()
        
        if customer.is_from_pwa == True :
            add_static_report(request, 'ثبت کارت بانکی جدید', None, True, customer.req_user, get_ip(request))   
        else:
            add_static_report(request, 'ثبت کارت بانکی جدید')
        return JsonResponse({'type':'success', 'msg':'کارت شما با موفقیت ثبت شد','card_number':card.card_number,'Shaba_number':'در انتظار استعلام','bank_title':card.bank.title,'logo_bank':card.bank.logo_name,'first_name':f'{card.uname.first_name} {card.uname.last_name}','status':"در انتظار تایید"})
  

def customer_request_ceiling_increase(request):

    # customer check start
    try :
        pattern_url = customer_access_check(request)
        if pattern_url[0] != 100 : return redirect(pattern_url[1])
    except: return redirect('account')
    # customer check end

    customer = pattern_url[2]

    counter = Customer_Ceiling_List.objects.filter(uname=customer)
    all_count = counter.count()
    waitting_count = counter.filter(uname=customer,is_verify=None).count()
    Confirmed_count = counter.filter(uname=customer,is_verify=True).count()
    Rejected_count = counter.filter(uname=customer,is_verify=False).count()

    paginator = Paginator(counter.order_by("-pk"),10)
    page = request.GET.get('page')

    try:
        querySet = paginator.page(page)
    except PageNotAnInteger:
        querySet = paginator.page(1)
    except EmptyPage:
        querySet = paginator.page(1)

    return render(request, get_customer_theme(pattern_url[2]) + 'request_ceiling_increase.html',{'querySet':querySet, "all_count":all_count, "waitting_count":waitting_count, "Confirmed_count":Confirmed_count, "Rejected_count":Rejected_count})


def customer_request_ceiling_increase_submit(request):

    # customer check start
    try :
        pattern_url = customer_access_check(request)
        if pattern_url[0] != 100 : return redirect(pattern_url[1])
    except: return redirect('account')
    # customer check end

    customer = pattern_url[2]
    date = get_date_time()['timestamp']

    last_request = Customer_Ceiling_List.objects.filter(uname=customer).order_by('pk')
    if last_request.exists():
        if (int(last_request.last().datetime) + 10) > date:
            return JsonResponse({'type':'danger', 'msg':'برای ثبت درخواست مجدد لطفا کمی صبر کنید و سپس دوباره تلاش کنید.'})
    

    if request.method == 'POST' :

        ceiling = request.POST.get('ceiling')

        if  ceiling == "" :
            return JsonResponse({'type':'danger', 'msg':'لطفا موارد خواسته شده را وارد نمایید'})

        customer = pattern_url[2]
        ceilings = Customer_Ceiling_List.objects.filter(uname=customer,ceiling=ceiling,is_verify=None)

        if ceilings.count() > 0 :
            if customer.is_from_pwa == True :
                add_static_report(request, 'عدم ثبت درخواست افزایش سقف به دلیل وجود درخواست مشابه با وضعیت در انتظار','danger', True, customer.req_user, get_ip(request))   
            else:
                add_static_report(request, 'عدم ثبت درخواست افزایش سقف به دلیل وجود درخواست مشابه با وضعیت در انتظار','danger')
            return JsonResponse({'type':'danger', 'msg':'شما یک درخواست با وضعیت در انتظار برای سقف مورد نظر دارید '})
        
        if ceiling == "transfer" :

            amount = request.POST.get('gram')
            amount = amount.replace(',','')

            if  ceiling == "" :
                return JsonResponse({'type':'danger', 'msg':'لطفا موارد خواسته شده را وارد نمایید'})


            try : amount = float(amount)
            except : return JsonResponse({'type':'danger', 'msg':'میزان سقف را به صورت عددی وارد نمایید'})

            if amount < 1 :
                return JsonResponse({'type':'danger', 'msg':' حداقل مبلغ سقف انتقال 1 گرم است'})

            if amount > 10 :
                return JsonResponse({'type':'danger', 'msg':' حداکثر مبلغ سقف انتقال 10 گرم است'})

        else: 

            amount = request.POST.get('amount')
            amount = amount.replace(',','')

            if  ceiling == "" :
                return JsonResponse({'type':'danger', 'msg':'لطفا موارد خواسته شده را وارد نمایید'})


            try : amount = int(amount)
            except : return JsonResponse({'type':'danger', 'msg':'میزان سقف را به صورت عددی وارد نمایید'})

            if amount < 100000 :
                return JsonResponse({'type':'danger', 'msg':' حداقل مبلغ سقف مورد نظر 100,000 تومان است'})

            if amount > 50000000 :
                return JsonResponse({'type':'danger', 'msg':' حداکثر مبلغ سقف مورد نظر 50,000,000 میلیون تومان است'})

        Customer_Ceiling_List(amount=amount,ceiling=ceiling,datetime=get_date_time()['timestamp'],uname=customer).save()

        if ceiling == "buy" : ceiling = 'خرید'
        elif ceiling == "sell" : ceiling = 'فروش'
        elif ceiling == "transfer" : ceiling = 'انتقال'

        date = get_date_time()['timestamp']
        date = jdatetime.datetime.fromtimestamp(int(date))

        if customer.is_from_pwa == True :
            add_static_report(request, f'ثبت درخواست افزایش سقف {ceiling}', 'success', True, customer.req_user, get_ip(request))   
        else:
            add_static_report(request, f'ثبت درخواست افزایش سقف {ceiling}','success')

        return JsonResponse({'type':'success', 'msg':'درخواست شما با موفقیت ثبت شد', 'amount':f'{amount:,}', 'ceiling':ceiling, 'dateinnum':str(date).split()[0], 'time':str(date).split()[1]})



def customer_change_password(request):

    # customer check start
    try :
        pattern_url = customer_access_check(request)
        if pattern_url[0] != 100 : return redirect(pattern_url[1])
    except: return redirect('account')
    # customer check end

    return render(request, get_customer_theme(pattern_url[2]) + 'change_password.html')


def customer_change_password_verify_request(request):

    # customer check start
    try :
        pattern_url = customer_access_check(request)
        if pattern_url[0] != 100 : return redirect(pattern_url[1])
    except: return redirect('account')
    # customer check end

    customer = pattern_url[2]

    request_access_check = error_logs_access_check(customer.pk, "customer_change_password_verify_request", 3, {'type':'minutes', "value":5}, {'type':'hours', "value":6})
    if request_access_check['type'] == 'danger': return JsonResponse(request_access_check)

    if request.method == 'POST' :

        current_pass = request.POST.get('current_pass')
        new_pass = request.POST.get('new_pass')
        new_pass1 = request.POST.get('new_pass1')
        number1 = request.POST.get('number1')
        number2 = request.POST.get('number2')
        number3 = request.POST.get('number3')
        number4 = request.POST.get('number4')

        try:

            int(number1)
            int(number2)
            int(number3)
            int(number4)

            code = f"{number1}{number2}{number3}{number4}" 

        except:  
            Customer_Requests_Logs.objects.create(uname = customer, identify = "customer_change_password_verify_request", error = "کد وارد شده صحیح نیست.", datetime = get_date_time()['timestamp'])
            return JsonResponse({'type':'danger', 'msg':'کد وارد شده صحیح نیست'})  


        if int(customer.last_code) != int(code) :

            customer.last_code_datetime = 0
            customer.save()


            if customer.is_from_pwa == True :
                add_static_report(request, 'کد اشتباه برای تغییر رمز عبور',None, True, customer.req_user, get_ip(request))   
            else: 
                add_static_report(request, 'کد اشتباه برای تغییر رمز عبور')

            Customer_Requests_Logs.objects.create(uname = customer, identify = "customer_change_password_verify_request", error = "کد اشتباه برای تغییر رمز عبور.", datetime = get_date_time()['timestamp'])
            return JsonResponse({'type':'danger', 'msg':'کد وارد شده صحیح نیست'})

        if (int(customer.last_code_datetime) + 60 ) < int(time.time()) :
            return JsonResponse({'type':'danger', 'msg':'کد وارد شده منقضی شده است'})



        User = authenticate(username=request.user,password=current_pass)
        if User != None:

            if new_pass == new_pass1:

                if passwordValidator(new_pass) < 4 :
                    return JsonResponse({'type':'danger', 'msg':'رمزعبور میبایست ۸ حرفی و شامل حروف کوچک و بزرگ به همراه اعداد و کاراکتر باشد'})

                User.set_password(new_pass)
                User.save()

                customer.last_code_datetime = 0
                customer.save()

                Send_Sms_Queue(phone=customer.mobile,name ='',text=f'{customer.first_name}' ).save()

                if customer.is_from_pwa == True :
                    add_static_report(request, 'تغییر رمز عبور', 'success', True, customer.req_user, get_ip(request))
                    return JsonResponse({'type':'success', 'msg':'رمزعبور شما با موفقیت تغییر کرد','redirect':'pwa_coustomer_account'})
                else:
                    add_static_report(request, 'تغییر رمز عبور', 'success')
                  
                return JsonResponse({'type':'success', 'msg':'رمزعبور شما با موفقیت تغییر کرد'})
            
            Customer_Requests_Logs.objects.create(uname = customer, identify = "", error = "رمز عبور وارد شده یکسان نیست.", datetime = get_date_time()['timestamp'])
            return JsonResponse({'type':'danger', 'msg':'رمز عبور وارد شده یکسان نیست'})
        
        Customer_Requests_Logs.objects.create(uname = customer, identify = "", error = "رمز عبور فعلی شما صحیح نیست.", datetime = get_date_time()['timestamp'])
        return JsonResponse({'type':'danger', 'msg':'رمز عبور فعلی شما صحیح نیست'})

    return JsonResponse({'type':'danger', 'msg':'در ارسال کد خطایی رخ داده'})


def customer_toverification_authenticated_submit(request):

    # customer check start
    try :
        pattern_url = customer_access_check(request)
        if pattern_url[0] != 100 : return redirect(pattern_url[1])
    except: return redirect('account')
    # customer check end

    customer = pattern_url[2]
        
    request_access_check = error_logs_access_check(customer.pk, "", 3, {'type':'minutes', "value":5}, {'type':'hours', "value":6})
    if request_access_check['type'] == 'danger': return JsonResponse(request_access_check)

    if request.method == 'POST' :

        is_toverification = request.POST.get('is_toverification')
        number1 = request.POST.get('number1')
        number2 = request.POST.get('number2')
        number3 = request.POST.get('number3')
        number4 = request.POST.get('number4')        
        code_hash = request.POST.get('code_hash')

        if number1 == "" or number2 == "" or number3 == "" or number4 == "" :
            return JsonResponse({'type':'danger', 'msg':'لطفا کد را به صورت صحیح وارد نمایید'})
        
        code = str(number1) + str(number2) + str(number3) + str(number4)


        if (int(customer.last_code_datetime) + 60 ) < int(time.time()) :
            return JsonResponse({'type':'danger', 'msg':'کد وارد شده منقضی شده است. لطفا کد جدید دریافت نمایید.'})

            
        if int(customer.last_code) != int(code) or pyotp_hash_verify() != True :
            
            customer.last_code_datetime = 0
            customer.save()

            if customer.is_from_pwa == True :
                add_static_report(request, 'کد اشتباه در تنظیمات دو مرحله ای', None, True, customer.req_user, get_ip(request))   
            else:
                add_static_report(request, 'کد اشتباه در تنظیمات دو مرحله ای')
            Customer_Requests_Logs.objects.create(uname = customer, identify = "customer_toverification_authenticated_submit", error = "کد وارد شده صحیح نیست.", datetime = get_date_time()['timestamp'])
            return JsonResponse({'type':'danger', 'msg':'کد وارد شده صحیح نیست'})

        if is_toverification == 'True' :

            customer.is_toverification = True
            customer.last_code_datetime = 0
            customer.save()

            if customer.is_from_pwa == True :
                add_static_report(request, 'فعال سازی ورود دو مرحله ای',None, True, customer.req_user, get_ip(request))   
            else:
                add_static_report(request, 'فعال سازی ورود دو مرحله ای')

        else :

            customer.is_toverification = False
            customer.last_code_datetime = 0
            customer.save()

            if customer.is_from_pwa == True :
                add_static_report(request, 'غیرفعال سازی ورود دو مرحله ای',None, True, customer.req_user, get_ip(request))   
            else:
                add_static_report(request, 'غیرفعال سازی ورود دو مرحله ای')

        return JsonResponse({'type':'success', 'msg':'ورود دو مرحله ای ویرایش شد'})

    return JsonResponse({'type':'danger', 'msg':'در ارسال کد خطایی رخ داده'})


def customer_two_step(request):

    try :  
        customer = Customer.objects.get(req_user=request.user)
        customer.is_from_pwa = is_from_pwa
        customer.save()

    except: return redirect(panel_redirect) 

    set = ContactUs.objects.get(code=1001)

    return render(request, get_customer_theme(customer) + 'two_step.html',{'set':set})


def customer_two_step_check(request):

    try : 
        customer = Customer.objects.get(req_user=request.user)
        customer.is_from_pwa = is_from_pwa
        customer.save()

    except: return redirect(panel_redirect) 

    if request.method == 'POST' :

        first = request.POST.get('first')
        second = request.POST.get('second')
        third = request.POST.get('third')
        fourth = request.POST.get('fourth')
        fifth = request.POST.get('fifth')
        sixth = request.POST.get('sixth')

        code = first + second + third + fourth + fifth + sixth

        if pyotp_hash_verify() == True :

            customer.is_toverification_requird = False
            customer.save()

            if customer.is_from_pwa == True :
                add_static_report(request, 'تایید رمز ورود دو مرحله ای', 'success', True, customer.req_user, get_ip(request))   
            else:
                add_static_report(request, 'تایید رمز ورود دو مرحله ای', 'success')

            return JsonResponse({'type':'success', 'msg':'در حال انتقال به پنل کاربری ...'})

        else : return JsonResponse({'type':'danger', 'msg':'کد وارد شده صحیح نیست'})

    return JsonResponse({'type':'danger', 'msg':'در تایید ورود دو مرحله ای خطایی رخ داده است'})


def customer_currency_buy_submit(request, symbol):
    

    # customer check start
    try :
        pattern_url = customer_access_check(request)
        if pattern_url[0] != 100 : return redirect(pattern_url[1])
    except: return redirect('account')
    # customer check end

    customer = pattern_url[2]
    date = get_date_time()['timestamp']

    last_buy = Currency_BuySell_List.objects.filter(uname=customer, bill_type='buy').order_by('pk')
    if last_buy.exists(): 
        if (int(last_buy.last().datetime) + 10) > date:
            return JsonResponse({'type':'danger', 'msg':'برای ثبت درخواست مجدد لطفا کمی صبر کنید و سپس دوباره تلاش کنید.'})
    
    if request.method == 'POST' :

        if customer.status == 'Suspended' :
            return redirect('account')

        now_time = get_date_time()['timestamp']

        try:
            if request.session.get('time') != None:
                time_req = request.session.get('time')
            request.session['time'] = None

            if int(time_req[0]) + 90  < int(now_time):
                return JsonResponse({'type':'danger', 'msg':'زمان خرید شما به پایان رسیده است لطفا مجددا اقدام نمایید'})
        except: return JsonResponse({'type':'danger', 'msg':'زمان خرید شما به پایان رسیده است لطفا مجددا اقدام نمایید'})

        try: currency = Currency_List.objects.get(symbol=symbol)
        except: return JsonResponse({'type':'danger', 'msg':'در خرید طلا خطایی رخ داده است'})
    


        if int(currency.BuySellPrice['last_price_query']) >  int(time_req[0]) :
            return JsonResponse({'type':'danger', 'msg':'قیمت خرید طلا تغییر کرده است لطفا مجددا اقدام نمایید'})

       


        if currency.is_sell == False :
            return JsonResponse({'type':'danger', 'msg':'در حال حاضر خرید طلا موقتا غیرفعال گردیده'})
        
        amount = request.POST.get('amount')
        paymentMethod = request.POST.get('paymentMethod')
        paymentDepositeType = request.POST.get('paymentDepositeType')
        is_reservation = request.POST.get('is_reservation')
        

        DepositeType = False

        try : 
            amount = float(amount)
            if amount <= 0 :
                return JsonResponse({'type':'danger', 'msg':'لطفا میزان خرید خود را به درستی وارد نمایید'})

        except : return JsonResponse({'type':'danger', 'msg':'لطفا میزان خرید خود را وارد نمایید'})
        
        if paymentMethod == 'ApWallet' :
            return JsonResponse({'type':'danger', 'msg':'در حال حاضر خرید از کیف پول آپ غیرفعال است'})
        
        if currency.acc == 'handly' : amount = round(amount,4)
     
        if amount < currency.lower_amount :
            return JsonResponse({'type':'danger', 'msg':f'حداقل میزان خرید {currency.lower_amount} است'})

        is_reservation = False  

        Unitprice = float(currency.BuySellPrice['buy'])

        if float(currency.buy_fee) != float(0) :

            f = ((currency.buy_fee * amount) / 100)
            if f < currency.buy_fee_lower : fee = currency.buy_fee_lower
            elif f > currency.buy_fee_upper : fee = currency.buy_fee_upper
            else : fee = f
            fee_price = round(fee * Unitprice , 0)

        else:

            fee = 0
            fee_price = 0


        maintenance_cost = int(amount * currency.maintenance_cost)

        totalPrice = round((amount * Unitprice) + fee_price + maintenance_cost)

        celling_buy = get_customer_CeilingRemain(customer.req_user)["buy"]

        if float(celling_buy) < float(totalPrice):
            return JsonResponse({'type':'danger', 'msg':f'مانده سقف مجاز خرید روزانه شما {celling_buy:,} تومان است'})
        
        balance =  currency.Balance - (((currency.Balance * currency.acc_fee) / 100) + (round(get_asset_wallet_reserved(symbol)['reserved'], 6))  +  (round(get_asset_bill_reserved(symbol)['pendding'], 6)))

        if amount + ((amount * currency.acc_fee) / 100) > (balance):
            return JsonResponse({'type':'danger', 'msg':'میزان درخواستی بیشتر از موجودی فعلی است.'})

        setting = Site_Settings.objects.get(code=1001)

        if paymentMethod == '' :

            if setting.is_buy_port == False : return JsonResponse({'type':'danger', 'msg':'در حال حاضر خرید از درگاه بانکی غیرفعال است'})
            
            if Permission.objects.filter(user=request.user, codename='customer_authentication_complated').count() == 0 or customer.status != 'Authenticated' :
                return JsonResponse({'type':'danger', 'msg':'برای خرید از درگاه میبایست احراز هویت خود را تکمیل نمایید'})
            

            if Customer_card.objects.filter(uname=Customer.objects.get(user=request.user),is_verify=True,is_show=True).count()  == 0 :
                return JsonResponse({'type':'redirect', 'msg':'برای خرید از درگاه میبایست ابتدا کارت بانکی شما ثبت و تایید شده باشد','link':'card'})

            if totalPrice > 200000000 and paymentMethod == '' :
                return JsonResponse({'type':'danger', 'msg':'حداکثر میزان خرید از درگاه به ازای هر تراکنش 200.000.000 تومان است'})

            if totalPrice < 10000 and paymentMethod == '' :
                return JsonResponse({'type':'danger', 'msg':'حداقل میزان خرید از درگاه به ازای هر تراکنش 10.000 تومان است'})

            # if Auth.objects.filter(customer=customer,status='Accepted').count() == 0 and  customer.buy_price == float(0) :
            #     return JsonResponse({'type':'redirect', 'msg':'ارسال مدارک برای خرید طلای آبشده الزامی است'})  

            if customer.status != "Authenticated" :
                return JsonResponse({'type':'danger', 'msg':'امکان خرید از درگاه برای شما فعال نمیباشد.'})   
            
           
            ow = Online_Wallet(owner=Customer.objects.get(user=request.user), amount=totalPrice, datetime=get_date_time()['timestamp'],currency=currency,amount_buy=amount,getway_buy=True, deposite_on_wallet=DepositeType,is_reservation=is_reservation, fee_amount=fee, fee_price=fee_price,unit_price=Unitprice,maintenance_cost=maintenance_cost)
            ow.save() 

            if customer.is_from_pwa == True :
                add_static_report(request, f'خرید {currency.fa_title}', 'success', True, customer.req_user, get_ip(request))   
            else:
                add_static_report(request, f'خرید {currency.fa_title}', 'success')

            if setting.default_payment_gateway == '' :
                result = 'my_api'

            elif setting.default_payment_gateway == 'idpay' :
                result = 'my_api'

            elif setting.default_payment_gateway == 'paystar' :
                result = 'my_api'


            else : return JsonResponse({'type':'danger', 'msg':'در خرید طلا خطایی رخ داده است'})
       

            if setting.default_payment_gateway in [] and 'my_result_api' == 201 :
                
                ow = Online_Wallet.objects.get(pk=ow.pk)
                ow.mellipay_track_id = 'my_result_api'
                ow.default_payment_gateway = setting.default_payment_gateway
                ow.save()

                if customer.is_from_pwa == True :
                    add_static_report(request, 'انتقال به درگاه بانکی',None, True, customer.req_user, get_ip(request))   
                else:
                    add_static_report(request, 'انتقال به درگاه بانکی')

                result = {"link": 'my_result_api'}
                response = JsonResponse({'type': 'success', 'msg': 'در حال انتقال به درگاه بانکی ...', 'redirect': 'my_result_api'})
                response.set_cookie('return_url', request.META.get('HTTP_REFERER', 'Unknown'), max_age=3600) 
                
                return response    

                

            elif setting.default_payment_gateway in ['paystar'] and 'my_result_api' == 1 :
            
                ow = Online_Wallet.objects.get(pk=ow.pk)
                ow.mellipay_track_id = 'my_result_api'
                ow.default_payment_gateway = setting.default_payment_gateway
                ow.save()

                if customer.is_from_pwa == True :
                    add_static_report(request, 'اتصال به درگاه جهت افزایش اعتبار کیف پول',None, True, customer.req_user, get_ip(request))   
                else:
                    add_static_report(request, 'اتصال به درگاه جهت افزایش اعتبار کیف پول')

                paystar_link = 'my_link'

                return JsonResponse({'type':'success', 'msg':'در حال انتقال به درگاه بانکی ...', 'redirect':'my_result_api'})

            else :

                return JsonResponse({'type':'danger', 'msg':'در خرید طلا خطایی رخ داده است'})


        elif paymentMethod == 'Wallet' :

        
            if setting.is_buy_wallet == False : return JsonResponse({'type':'danger', 'msg':'در حال حاضر خرید از کیف پول غیرفعال است'})

            if totalPrice >  float(get_customer_balance(request.user,'IRT')["balance"]) :
                return JsonResponse({'type':'danger', 'msg':'مبلغ فاکتور شما بیشتر از موجودی کیف پول است'})

            else :


                time = get_date_time()['timestamp']

                # if Currency_BuySell_List.objects.filter(datetime__range=(time - 1 , time), acc=currency.acc, uname=customer, currency=currency, amount=amount, bill_type='buy').count() != 0 :
                #     return JsonResponse({'type':'danger', 'msg':'به دلیل خرید مشابه در یک ثانیه خرید شما لغو گردید. لطفا پس از ۱۰ ثانیه مجدد اقدام به خرید نمایید.'})

                w = Wallet(

                    uname = customer,
                    wallet = 'IRT',
                    desc = f'بابت خرید : {currency.fa_title}',
                    amount = totalPrice * (-1),
                    datetime = time,
                    confirmed_datetime = time,
                    ip = get_ip(request),
                    is_verify = True,

                )
                w.save()
                

                Currency_BuySell_List(

                    uname = customer,
                    acc = currency.acc,
                    currency = currency,

                    wallet_id = w.pk,

                    amount = amount,
                    fee_amount = fee,

                    fee_price = fee_price,
                    unit_price = Unitprice,
                    total_price = totalPrice,

                    deposite_on_wallet = DepositeType,

                    datetime = time,
                    ip = get_ip(request),
                    is_reservation = is_reservation,
                    maintenance_cost = maintenance_cost


                ).save()
                
                if customer.is_from_pwa == True :
                    add_static_report(request, f'خرید {currency.fa_title}', 'success', True, customer.req_user, get_ip(request))   
                else:
                    add_static_report(request, f'خرید {currency.fa_title}', 'success')

                return JsonResponse({'type':'success', 'msg':'خرید با موفقیت انجام شد', 'redirect':'None'})


    return JsonResponse({'type':'danger', 'msg':'در خرید طلا خطایی رخ داده است'})



def customer_buysell_list(request):
    
    # customer check start
    try :
        pattern_url = customer_access_check(request)
        if pattern_url[0] != 100 : return redirect(pattern_url[1])
    except: return redirect('account')
    # customer check end

    customer = pattern_url[2]
    paginator = Paginator(Currency_BuySell_List.objects.filter(uname=customer).order_by('-pk'),10)
    page = request.GET.get('page')

    try:
        bill = paginator.page(page)
    except PageNotAnInteger:
        bill = paginator.page(1)
    except EmptyPage:
        bill = paginator.page(paginator.num_page)

    return render(request, get_customer_theme(pattern_url[2]) + 'buySell_list.html', {'bill': bill,'count_bills':Currency_BuySell_List.objects.filter(uname=customer).count(),'set':ContactUs.objects.get(code=1001),'type':'list','today': get_date_time()["shamsi_date"],})


def customer_currency_sell_submit(request, symbol):

    # customer check start
    try :
        pattern_url = customer_access_check(request)
        if pattern_url[0] != 100 : return redirect(pattern_url[1])
    except: return redirect('account')
    # customer check end

    customer = pattern_url[2]
    date = get_date_time()['timestamp']

    last_sell = Currency_BuySell_List.objects.filter(uname=customer, bill_type='sell').order_by('pk')
    if last_sell.exists():
        if (int(last_sell.last().datetime) + 10) > date:
               return JsonResponse({'type':'danger', 'msg':'برای ثبت درخواست مجدد لطفا کمی صبر کنید و سپس دوباره تلاش کنید.'})
    

    if request.method == 'POST':

        if customer.status == 'Suspended' :
            return redirect('account')

        now_time = get_date_time()['timestamp']

        try:

            if request.session.get('time') != None :
                time_req = request.session.get('time')
            request.session['time'] = None

            if int(time_req[0]) + 90  < int(now_time) :
                return JsonResponse({'type':'danger', 'msg':'زمان فروش شما به پایان رسیده است لطفا مجددا اقدام نمایید'})
        except:   
            return JsonResponse({'type':'danger', 'msg':'زمان فروش شما به پایان رسیده است لطفا مجددا اقدام نمایید'})

        
        try : currency = Currency_List.objects.get(symbol=symbol)
        except : return JsonResponse({'type':'danger', 'msg':'در فروش طلا خطایی رخ داده است'})

        if currency.is_buy == False :
            return JsonResponse({'type':'danger', 'msg':'در حال حاضر فروش طلا موقتا غیرفعال گردیده'})
        
        
        if int(currency.BuySellPrice['last_price_query']) >  int(time_req[0]) :
            return JsonResponse({'type':'danger', 'msg':'قیمت فروش طلا تغییر کرده است لطفا مجددا اقدام نمایید'})

        if Currency_BuySell_List.objects.filter(bill_type='sell',uname = customer,status ='Pendding' ).count() >= 2:
            return JsonResponse({'type':'danger', 'msg':'فاکتورهای در انتظار بیش از حد مجاز است, لطفا بعد از بررسی فاکتورهای فروش خود مجددا اقدام نمایید'})     
        
        cards = 0
        payment = 0
        withdraw_method = 0
        setting = Site_Settings.objects.get(code=1001)

        if currency.acc == 'handly' :

            amount = request.POST.get('amountt')
            paymentMethod = request.POST.get('paymentMethod')

            if paymentMethod != "" and  paymentMethod != "" :
                return JsonResponse({'type':'danger', 'msg':'روش فروش انتخاب شده نامعتبر است'})

            Unitprice = float(currency.BuySellPrice['sell'])
            
            if paymentMethod == "":

                if setting.is_withdraw_request == False :
                    return JsonResponse({'type':'danger', 'msg':'در حال حاضر درخواست برداشت موقتا غیرفعال گردیده'})
    

                cards = request.POST.get('cards')
                payment = request.POST.get('payment')

                if cards == "" or cards == None or cards == "None" or cards == "0":
                    return JsonResponse({'type':'danger', 'msg':'لطفا شماره کارت را انتخاب نمایید'})

                if payment == "" or payment == "0" :
                    return JsonResponse({'type':'danger', 'msg':'لطفا روش برداشت را انتخاب نمایید'})    
                

                try :
                    Customer_card.objects.get(is_verify=True,uname=customer,is_show=True,pk=cards)
                except : return JsonResponse({'type':'danger', 'msg':'کارت نامعتبر است'})    
                    

                try:
                    withdraw_method = WithdrawPaymentMethodIRT.objects.get(pk=payment).wage
                except:   
                    return JsonResponse({'type':'danger', 'msg':'روش برداشت نامعتبر است'})

                now_timestamp = get_date_time()['timestamp']
                    
                datetime = jdatetime.datetime.fromtimestamp(int(now_timestamp))
                today_date = datetime.date()

                today_start_time = jdatetime.datetime.combine(today_date, jdatetime.time(0, 0))  
                today_end_time = jdatetime.datetime.combine(today_date, jdatetime.time(23, 59, 59)) 
                
                today_start_timestamp = int(today_start_time.timestamp())
                today_end_timestamp = int(today_end_time.timestamp())

                today_transactions = WalletWithdrawIRT.objects.filter(
                    uname=customer, 
                    datetime__gt=today_start_timestamp, 
                    datetime__lt=today_end_timestamp, 
                    status__in=['WaitingBankSend', 'Deposited']
                )

                if today_transactions.exists():
                    sum_of_today_withdraws = today_transactions.aggregate(Sum('amount'))['amount__sum']
                else:
                    sum_of_today_withdraws = 0

                if float(currency.sell_fee) != float(0) :

                    f = ((currency.sell_fee * float(amount)) / 100)
                    if f < currency.sell_fee_lower : fee = currency.sell_fee_lower
                    elif f > currency.sell_fee_upper : fee = currency.sell_fee_upper
                    else : fee = f
                    fee_price = round(fee * Unitprice , 0)

                else:

                    fee = 0
                    fee_price = 0

                toman_amount = (float(amount) - fee) * Unitprice

                if sum_of_today_withdraws + toman_amount > 200000000:
                    return JsonResponse({'type':'danger', 'msg':f'سقف برداشت روزانه ۲۰۰ میلیون تومان می باشد.مانده سقف امروز: {200000000-sum_of_today_withdraws:,}'})       
    

            try : amount = round(float(amount), 4)
            except : return JsonResponse({'type':'danger', 'msg':'لطفا میزان فروش خود را وارد نمایید'})

            if amount < currency.lower_amount :
                return JsonResponse({'type':'danger', 'msg':f'حداقل میزان فروش {currency.lower_amount} است'})

        totalPrice = round(amount * Unitprice)

        

        if setting.is_sale == False :
            return JsonResponse({'type':'danger', 'msg':'در حال حاضر فروش به سایت غیرفعال است'})

        customer = pattern_url[2]

        celling_sell = get_customer_CeilingRemain(customer.req_user)["sell"]

        if float(celling_sell) < float(totalPrice):
            return JsonResponse({'type':'danger', 'msg':f'مانده سقف مجاز فروش روزانه شما {celling_sell:,} تومان است'})

     
        if currency.acc == 'handly' :

            if float(currency.sell_fee) != float(0) :

                f = ((currency.sell_fee * amount) / 100)
                if f < currency.sell_fee_lower : fee = currency.sell_fee_lower
                elif f > currency.sell_fee_upper : fee = currency.sell_fee_upper
                else : fee = f
                fee_price = round(fee * Unitprice , 0)

            else:

                fee = 0
                fee_price = 0

            if float(get_customer_balance(request.user, currency.symbol)["balance"]) < amount :
                return JsonResponse({'type':'danger', 'msg':'موجودی کیف پول شما کمتر از میزان فروش است'}) 


            if totalPrice - fee_price <= 0 :
                return JsonResponse({'type':'danger', 'msg':'میزان فروش وارد شده نامعتبر است'})

            else:

                time = get_date_time()['timestamp']

                w = Wallet(

                    uname = customer,
                    wallet = currency.symbol,
                    desc = f'بابت فروش : {currency.fa_title}',
                    amount = amount * (-1),
                    datetime = time,
                    confirmed_datetime = time,
                    ip = get_ip(request),
                    is_verify = True,

                )
                w.save()

                Currency_BuySell_List(

                    uname = customer,
                    acc = currency.acc,
                    currency = currency,

                    wallet_id = w.pk,
                    amount = amount,

                    fee_amount = fee,
                    fee_price = fee_price,

                    bill_type='sell',

                    unit_price = Unitprice,
                    total_price = (totalPrice - fee_price) - withdraw_method,

                    datetime = time,
                    ip = get_ip(request),
                    sell_payment_method = paymentMethod,
                    card_withdrawal_sell = cards,
                    payment_method_withdrawal = payment


                ).save()
                
                if customer.is_from_pwa == True :
                    add_static_report(request, f'فروش {currency.fa_title}', 'danger', True, customer.req_user, get_ip(request))   
                else:
                    add_static_report(request, f'فروش {currency.fa_title}', 'danger')

                return JsonResponse({'type':'success', 'msg':'درخواست فروش شما با موفقیت در صف انتظار قرار گرفت', 'redirect':'None'})
        
    return JsonResponse({'type':'danger', 'msg':'در فروش طلا خطایی رخ داده است'})

   
def customer_wallet_irt_list(request):

    # customer check start
    try :
        pattern_url = customer_access_check(request)
        if pattern_url[0] != 100 : return redirect(pattern_url[1])
    except: return redirect('account')
    # customer check end

    customer = pattern_url[2]
    paginator = Paginator(Wallet.objects.filter(uname=customer,wallet='IRT').order_by('-pk'),10)
    page = request.GET.get('page')

    try:
        wallet = paginator.page(page)
    except PageNotAnInteger:
        wallet = paginator.page(1)
    except EmptyPage:
        wallet = paginator.page(paginator.num_page)

    return render(request, get_customer_theme(pattern_url[2]) + 'wallet_irt_list.html',{"wallet":wallet})


def customer_harvest_list(request):

    # customer check start
    try :
        pattern_url = customer_access_check(request)
        if pattern_url[0] != 100 : return redirect(pattern_url[1])
    except: return redirect('account')
    # customer check end

    customer = pattern_url[2]

    withdraw = WalletWithdrawIRT.objects.filter(uname=customer).order_by('-pk')
    count_withdrawals = withdraw.count()

    paginator = Paginator(withdraw, 10)
    page = request.GET.get('page')

    try:
        withdrawal = paginator.page(page)
    except PageNotAnInteger:
        withdrawal = paginator.page(1)
    except EmptyPage:
        withdrawal = paginator.page(paginator.num_page)

    return render(request, get_customer_theme(pattern_url[2]) + 'harvest_list.html', {"withdrawal": withdrawal,'payment_method':WithdrawPaymentMethodIRT.objects.filter(is_active=True),'count_withdrawals':count_withdrawals,'type':'list'})


def customer_currency_buysell_2(request,symbol):

    # customer check start
    try :
        pattern_url = customer_access_check(request)
        if pattern_url[0] != 100 : return redirect(pattern_url[1])
    except: return redirect('account')
    # customer check end

    if request.session.get('notification') != None :
        message = request.session.get('notification')
    request.session['notification'] = None

    customer = pattern_url[2]
    bill = Currency_BuySell_List.objects.filter(uname=customer).order_by('-pk')[:5]


    customer_card = Customer_card.objects.filter(uname=customer,is_verify=True,is_show=True)

    payment_method = WithdrawPaymentMethodIRT.objects.filter(is_active= True).exclude(pk=4)

    return render(request, get_customer_theme(pattern_url[2]) + 'buysell.html',{'payment_method':payment_method,'customer_card':customer_card,'currencies':Currency_List.objects.filter(is_show=True).order_by("sort"),'currency':Currency_List.objects.get(symbol=symbol),'bill':bill,'customer_card':customer_card})


def inperson_delivery_list(request):
    
    # customer check start
    try :
        pattern_url = customer_access_check(request)
        if pattern_url[0] != 100 : return redirect(pattern_url[1])
    except: return redirect('account')
    # customer check end

    if Site_Settings.objects.get(code=1001).physical_delivery_show == False :
        request.session['notification'] = ['تحویل فیزیکی غیرفعال است']
        return redirect('customer_panel')

    gold_orders = Customer_Gold_Order.objects.filter(uname=pattern_url[2]).order_by("-pk")
    paginator = Paginator(gold_orders,10)
    page = request.GET.get('page')
    try:
        orders = paginator.page(page)
    except PageNotAnInteger:
        orders = paginator.page(1)
    except EmptyPage:
        orders = paginator.page(1)

    return render(request, get_customer_theme(pattern_url[2]) + 'inperson_delivery_list.html',{'orders':orders,'orders_count':gold_orders.count()})



def inperson_delivery(request):

    # customer check start
    try :
        pattern_url = customer_access_check(request)
        if pattern_url[0] != 100 : return redirect(pattern_url[1])
    except: return redirect('account')
    # customer check end

    if Site_Settings.objects.get(code=1001).physical_delivery_show == False :
        request.session['notification'] = ['تحویل فیزیکی غیرفعال است']
        return redirect('customer_panel')
    
    return render(request, get_customer_theme(pattern_url[2]) + 'inperson_delivery.html',{'cities':Site_Cities_With_Represent.objects.filter(act=True).order_by('sort')})
    

def customer_select_city(request,pk):

    # customer check start
    try :
        pattern_url = customer_access_check(request)
        if pattern_url[0] != 100 : return redirect(pattern_url[1])
    except: return redirect('account')
    # customer check end

    if Site_Settings.objects.get(code=1001).physical_delivery_show == False :
        request.session['notification'] = ['تحویل فیزیکی غیرفعال است']
        return redirect('customer_panel')
    
    try : city = Site_Cities_With_Represent.objects.get(pk=pk)
    except : return JsonResponse({'type':'danger', 'msg':'پردازش مورد نظر با مشکل مواجه شده است'})

    return JsonResponse({'type':'success', 'msg':'شهر موردنظر با موفقیت ثبت شد'})


def customer_select_products(request,pk):

    # checks customer access
    try :
        pattern_url = customer_access_check(request)
        if pattern_url[0] != 100 : return redirect(pattern_url[1])
    except: return redirect('account')

    # checks if physical delivery is active
    if Site_Settings.objects.get(code=1001).physical_delivery_show == False :
        request.session['notification'] = ['تحویل فیزیکی غیرفعال است']
        return redirect('customer_panel')
    
    # checks if city exists and is active
    try : city = Site_Cities_With_Represent.objects.get(pk=pk,act=True)
    except : return redirect('inperson_delivery')

    order = Customer_Gold_Order.objects.filter(status='Pending_payment',uname=pattern_url[2],city=city).first()

    if not order:
        total_products = 0
        products_in_cart = []
        quantities_in_cart = []
        pk_order = 0

    else: 
        total_products = Customer_Cart_Products.objects.filter(order=order).aggregate(total_quantity=models.Sum('quantity'))['total_quantity'] or 0
        products_in_cart = Customer_Cart_Products.objects.filter(order=order).values_list('product_id', flat=True)
        quantities_in_cart = Customer_Cart_Products.objects.filter(order=order).values('product_id', 'quantity')
        pk_order = order.pk
        
    branches_count = Site_Branches_Each_Representative.objects.filter(city=city,act=True).count()

    active_branch_with_working_day = Site_Branches_Each_Representative.objects.filter(
        Q(site_branch_working_days__act=True) &
        Q(site_branch_working_days__jalali_date__gte=jdatetime.datetime.now().strftime('%Y/%m/%d')),
        Q(site_branch_working_days__capacity__gt=0),
        city=city,
        act=True,
    ).exists()

    if active_branch_with_working_day:

        molten_gold_with_inventory = Site_Products.objects.annotate(total_quantity=Sum('site_product_inventory__quantity'))
        molten_gold_with_zero_inventory = molten_gold_with_inventory.filter(total_quantity__gt=0,type_gold="gold1",city=city,act=True).order_by('-pk')
        count_molten_gold_with_zero_inventory = molten_gold_with_zero_inventory.count()

        molten_gold_page = request.GET.get('molten_gold_page', 1)
        paginator_molten_gold = Paginator(molten_gold_with_zero_inventory, 8)
        try:
            molten_gold = paginator_molten_gold.page(molten_gold_page)
        except PageNotAnInteger:
            molten_gold = paginator_molten_gold.page(1)
        except EmptyPage:
            molten_gold = paginator_molten_gold.page(paginator_molten_gold.num_pages)


        bullion_coin_with_inventory = Site_Products.objects.annotate(total_quantity=Sum('site_product_inventory__quantity'))
        bullion_coin_with_zero_inventory = bullion_coin_with_inventory.filter(total_quantity__gt=0,type_gold__in=["gold2", "gold3"],city=city,act=True).order_by('-pk')
        count_bullion_coin_with_zero_inventory = bullion_coin_with_zero_inventory.count()

        paginator = Paginator(bullion_coin_with_zero_inventory,8)
        page = request.GET.get('page')
        try:
            bullion_coin = paginator.page(page)
        except PageNotAnInteger:
            bullion_coin = paginator.page(1)
        except EmptyPage:
            bullion_coin = paginator.page(1)

    else:
        molten_gold = []
        bullion_coin = []
        count_molten_gold_with_zero_inventory = 0
        count_bullion_coin_with_zero_inventory = 0


    asset = Currency_List.objects.get(symbol='XAU18')
    customer_balance = get_customer_balance(request.user, asset.symbol)['balance']
    last_gold_price = Currency_List.objects.get(symbol='XAU18').BuySellPrice['buy']

    return render(
        request, get_customer_theme(pattern_url[2]) + 'select_products.html', {
            'pk_order':pk_order,
            'molten_gold':molten_gold,
            'bullion_coin':bullion_coin,
            'count_products':total_products,
            'products_in_cart':products_in_cart,
            'branches_count':branches_count,
            'order':order,
            'quantities_in_cart': quantities_in_cart,
            'city':city,
            'fund_balance':customer_balance,
            'last_gold_price': last_gold_price,
            'asset':asset,
            'count_molten_gold_with_zero_inventory':count_molten_gold_with_zero_inventory,
            'count_bullion_coin_with_zero_inventory':count_bullion_coin_with_zero_inventory
            
            }
        )

def customer_search_products(request,pk):

    # checks customer access
    try :
        pattern_url = customer_access_check(request)
        if pattern_url[0] != 100 : return redirect(pattern_url[1])
    except: return redirect('account')
    # checks customer access

    error = False

    if request.method == 'POST':
        product_type = request.POST.get('product_type', '0')
        amount = request.POST.get('amount', '')
        path = request.path

        request.session['product_type'] = product_type
        request.session['amount'] = amount
        request.session['path'] = path
        
    else:
        product_type = request.session.get('product_type', '0')
        amount = request.session.get('amount', '0')
        path = request.session.get('path', request.path)
        active_tab = 'tab_1'
        if not amount:
            amount = 0

    try:
        city = Site_Cities_With_Represent.objects.get(pk=pk,act=True)
    except Site_Cities_With_Represent.DoesNotExist:
        pass



    active_branch_with_working_day = Site_Branches_Each_Representative.objects.filter(
        Q(site_branch_working_days__act=True) &
        Q(site_branch_working_days__jalali_date__gte=jdatetime.datetime.now().strftime('%Y/%m/%d')),
        Q(site_branch_working_days__capacity__gt=0),
        city=city,
        act=True,
    ).exists()

    if active_branch_with_working_day:

        gold_with_inventory = Site_Products.objects.annotate(total_quantity=Sum('site_product_inventory__quantity'))
        
        molten_gold_with_zero_inventory = gold_with_inventory.filter(total_quantity__gt=0,type_gold="gold1",city=city,act=True).order_by('-pk')
        count_molten_gold_with_zero_inventory = molten_gold_with_zero_inventory.count()

        bullion_coin_with_zero_inventory = gold_with_inventory.filter(total_quantity__gt=0,type_gold__in=["gold2", "gold3"],city=city,act=True).order_by('-pk')
        count_bullion_coin_with_zero_inventory = bullion_coin_with_zero_inventory.count()

        molten_gold_with_inventory = gold_with_inventory.filter(type_gold="gold1")
        bullion_coin_with_inventory = gold_with_inventory.filter(type_gold__in=["gold2", "gold3"])

    else:
        molten_gold = []
        molten_gold_with_inventory = []
        bullion_coin = []
        bullion_coin_with_inventory = []
        count_molten_gold_with_zero_inventory = 0
        count_bullion_coin_with_zero_inventory = 0

   
    if city and molten_gold_with_inventory != [] and bullion_coin_with_inventory != []:

        if not amount == 'more_than_10' and amount in ['2', '4', '6', '8', '10']:
            amount = int(amount) 
        elif amount == 'more_than_10': amount = 'more_than_10'
        else:
            error = True

        if amount == 'more_than_10':
            molten_gold_with_inventory = molten_gold_with_inventory.filter(grams__gt=10) if product_type == 'gold1' else molten_gold_with_inventory
            bullion_coin_with_inventory = bullion_coin_with_inventory.filter(grams__gt=10) if product_type in ["gold2", "gold3"] else bullion_coin_with_inventory
        elif amount in [2, 4, 6, 8, 10]:
            molten_gold_with_inventory = molten_gold_with_inventory.filter(grams__lt=amount) if product_type == 'gold1' else molten_gold_with_inventory
            bullion_coin_with_inventory = bullion_coin_with_inventory.filter(grams__lt=amount) if product_type in ["gold2", "gold3"] else bullion_coin_with_inventory
        else:
            error = True

  


        molten_gold_with_zero_inventory = molten_gold_with_inventory.filter(city=city,total_quantity__gt=0, act=True).order_by('-pk')
        bullion_coin_with_zero_inventory = bullion_coin_with_inventory.filter(city=city,total_quantity__gt=0, act=True).order_by('-pk')   
        count_molten_gold_with_zero_inventory = molten_gold_with_zero_inventory.count()
        count_bullion_coin_with_zero_inventory = bullion_coin_with_zero_inventory.count()     

    else :
        molten_gold_with_zero_inventory = []
        bullion_coin_with_zero_inventory = []

        count_molten_gold_with_zero_inventory = 0
        count_bullion_coin_with_zero_inventory =  0



  
    molten_gold_page = request.GET.get('molten_gold_page', 1)
    paginator_molten_gold = Paginator(molten_gold_with_zero_inventory, 8)
    try:
        molten_gold = paginator_molten_gold.page(molten_gold_page)
    except PageNotAnInteger:
        molten_gold = paginator_molten_gold.page(1)
    except EmptyPage:
        molten_gold = paginator_molten_gold.page(paginator_molten_gold.num_pages)

    page = request.GET.get('page')
    paginator_bullion_coin = Paginator(bullion_coin_with_zero_inventory, 8)
    try:
        bullion_coin = paginator_bullion_coin.page(page)
    except PageNotAnInteger:
        bullion_coin = paginator_bullion_coin.page(1)
    except EmptyPage:
        bullion_coin = paginator_bullion_coin.page(1)

  
    
    asset = Currency_List.objects.get(symbol='XAU18')
    customer_balance = get_customer_balance(request.user, asset.symbol)['balance']
    last_gold_price = Currency_List.objects.get(symbol='XAU18').BuySellPrice['buy']
    order = Customer_Gold_Order.objects.filter(status='Pending_payment',uname=pattern_url[2],city=city).first()
    branches_count = Site_Branches_Each_Representative.objects.filter(city=city,act=True).count()

    if not order:
        total_products = 0
        products_in_cart = []
        quantities_in_cart = []
        pk_order = 0

    else: 
        customer_card_products = Customer_Cart_Products.objects.filter(order=order)
        total_products = customer_card_products.aggregate(total_quantity=models.Sum('quantity'))['total_quantity'] or 0
        products_in_cart = customer_card_products.values_list('product_id', flat=True)
        quantities_in_cart = customer_card_products.values('product_id', 'quantity')
        pk_order = order.pk

    if product_type == 'gold1':
        active_tab = 'tab_1'
    elif product_type == 'gold2' or product_type == 'gold3' :
        active_tab = 'tab_2'


    return render(
        request, get_customer_theme(pattern_url[2]) + 'select_products.html', {
            'pk_order': pk_order,
            'error':error,
            'path' : path,
            'active_tab' : active_tab,
            'molten_gold': molten_gold,
            'bullion_coin': bullion_coin,
            'fund_balance':customer_balance,
            'count_products':total_products,
            'products_in_cart':products_in_cart,
            'last_gold_price': last_gold_price,
            'quantities_in_cart': quantities_in_cart,
            'branches_count':branches_count,
            'count_molten_gold_with_zero_inventory': count_molten_gold_with_zero_inventory,
            'count_bullion_coin_with_zero_inventory': count_bullion_coin_with_zero_inventory,
            'asset':asset,
            'city': city,
            'type':'search',
        }
    )


def customer_add_to_order(request, pk):



    # customer check start
    try :
        pattern_url = customer_access_check(request)
        if pattern_url[0] != 100 : return redirect(pattern_url[1])
    except: return redirect('account')
    # customer check end

    if Site_Settings.objects.get(code=1001).physical_delivery_show == False :
        
        request.session['notification'] = ['تحویل فیزیکی غیرفعال است']
        return redirect('customer_panel')
    
    customer = pattern_url[2]
    product = Site_Products.objects.get(pk=pk,act=True)

    if Customer_Gold_Order.objects.filter(status__in=['Pending','Connection_getway'],uname=customer,city=product.city).count() == 1 :
        return JsonResponse({'type':'danger', 'msg':'امکان ثبت فاکتور جدید وجود ندارد'})

    order = Customer_Gold_Order.objects.filter(status='Pending_payment',uname=customer,city=product.city).first()

    if not order:
        order = Customer_Gold_Order(city=product.city,uname=customer)
        order.save()


    total_products = Customer_Cart_Products.objects.filter(order=order).aggregate(total_quantity=models.Sum('quantity'))['total_quantity'] or 0
    product_quantity = Customer_Cart_Products.objects.filter(order=order, product=Site_Products.objects.get(pk=pk,act=True)).aggregate(total_quantity=models.Sum('quantity'))['total_quantity'] or 0
    if calculate_product_inventory(pk)['product_inventory'] < int(product_quantity) + 1:
        return JsonResponse({'type':'danger', 'msg':f'موجودی محصول {product.title} به اتمام رسیده است'})


    if product.type_gold == "gold1" :
        if not Customer_Cart_Products.objects.filter(order=order, product=product).exists():
            Customer_Cart_Products.objects.create(order=order, product=product, is_gold_melt=True, quantity=1)
        else:
            return JsonResponse({'type':'danger', 'msg':'امکان خرید بیشتر طلای موردنظر وجود ندارد'})
        
    else:
        order_product, created = Customer_Cart_Products.objects.get_or_create(order=order, product=product, is_gold_melt=False)
        if not created:
            order_product.quantity += 1
            order_product.save()

    total_products = Customer_Cart_Products.objects.filter(order=order).aggregate(total_quantity=models.Sum('quantity'))['total_quantity'] or 0
    product_quantity = Customer_Cart_Products.objects.filter(order=order, product=Site_Products.objects.get(pk=pk,act=True)).aggregate(total_quantity=models.Sum('quantity'))['total_quantity'] or 0

    cart_products = Customer_Cart_Products.objects.filter(order=order)
    # current_gold_price = Site_Dollar_log.objects.last().dollar_price_new
    current_gold_price = Currency_List.objects.get(symbol='XAU18').BuySellPrice['buy']

    total_toman = 0
    total_grams = 0
    wages_coins_toman = 0
    wages_ingots_toman = 0
    fee_order = 0

    for cart_product in cart_products:
        product = cart_product.product
 
        product_weight = product.grams if product.grams is not None else 0
        wages = product.wages if product.wages is not None else 0

        result = calculate_price_or_grams(current_gold_price, wages, product.fee, product.grams)

        total_product_price = result['final_toman'] * cart_product.quantity
        total_toman += total_product_price

        total_product_gram = result['final_gram'] * cart_product.quantity
        total_grams += total_product_gram

        product_price_in_toman = product_weight * current_gold_price
        wages_in_toman = (wages * product_price_in_toman) / 100
        wages_in_toman = cart_product.quantity * wages_in_toman


        if product.type_gold == "gold2":
            wages_coins_toman += wages_in_toman
        elif product.type_gold == "gold3":
            wages_ingots_toman += wages_in_toman

        fee_order += Decimal(cart_product.quantity) * Decimal(product.fee)

    total_wages_toman = wages_coins_toman + wages_ingots_toman

    order.toman_total = round(total_toman)
    order.gram_total = total_grams
    order.save()

    total_grams = cart_products.aggregate(total_grams=Sum(F('quantity') * F('product__grams')))['total_grams'] or 0 

    total_wages = cart_products.aggregate(total_wages=Sum(F('quantity') * F('product__wages')))['total_wages'] or 0

    total_fee = cart_products.aggregate(total_fee=Sum(F('quantity') * F('product__fee')))['total_fee'] or 0

    melted = Customer_Cart_Products.objects.filter(order=order,is_gold_melt=True)
    weight_melted = melted.aggregate(total_grams=Sum(F('quantity') * F('product__grams')))['total_grams'] or 0 

    count_melted = melted.aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
    count_melted = count_melted or 0

    coins = Customer_Cart_Products.objects.filter(order=order,product__type_gold="gold2")

    Weight_coins = coins.aggregate(total_grams=Sum(F('quantity') * F('product__grams')))['total_grams'] or 0
    count_coins = coins.aggregate(total_quantity=Sum('quantity'))['total_quantity'] 
    count_coins = count_coins or 0

    wages_coins = coins.aggregate(total_wages=Sum(F('quantity') * F('product__wages')))['total_wages'] or 0 
    
    ingots = Customer_Cart_Products.objects.filter(order=order,product__type_gold="gold3")

    Weight_ingots = ingots.aggregate(total_grams=Sum(F('quantity') * F('product__grams')))['total_grams'] or 0 

    count_ingots = ingots.aggregate(total_quantity=Sum('quantity'))['total_quantity']
    count_ingots = count_ingots or 0

    wages_ingots = ingots.aggregate(total_wages=Sum(F('quantity') * F('product__wages')))['total_wages'] or  0

    asset = Currency_List.objects.get(symbol='XAU18')

    fund_balance = get_customer_balance(request.user, asset.symbol)['balance']

    if  Decimal(fund_balance) <  Decimal(order.gram_total) :
        
        remaining_gold =  Decimal(order.gram_total) - Decimal(fund_balance)
        remaining_toman = (remaining_gold * current_gold_price)

        
        gram_fee_gateway = remaining_gold

    else : 
        remaining_toman = 0
        gram_fee_gateway = order.gram_total


    if float(asset.buy_fee) != float(0) :

        f = ((Decimal(asset.buy_fee) * Decimal(gram_fee_gateway)) / 100)
        if f < Decimal(asset.buy_fee_lower) : fee = asset.buy_fee_lower
        elif f > Decimal(asset.buy_fee_upper) : fee = asset.buy_fee_upper
        else : fee = f
        fee_price = int(round(fee * current_gold_price , 0))

    else:

        fee = 0
        fee_price = 0

    return JsonResponse({'type':'success', 'msg':'محصول به سبد خرید اضافه شد.','pk_order':order.pk,'count_products':total_products,'product_quantity':product_quantity,'weight_melted':custom_float_format(weight_melted, 4),'Weight_coins':round(Weight_coins,4),'Weight_ingots':round(Weight_ingots,4),'count_melted':count_melted,'count_coins':count_coins,'count_ingots':count_ingots,'wages_coins':f'{round(wages_coins_toman):,}','wages_ingots':f'{round(wages_ingots_toman):,}','total_wages':f'{round(total_wages_toman):,}','total_grams':round(total_grams,4),'total_fee':custom_float_format(fee_order, 4),'toman_total':f'{round(order.toman_total):,}','geram_total':round(order.gram_total,4),'remaining_toman':f'{round(remaining_toman):,}','product_inventory':calculate_product_inventory(product.pk)['product_inventory'],'fee_price_gateway':f'{fee_price:,}'})



def customer_remove_from_order(request, pk):


    # customer check start
    try :
        pattern_url = customer_access_check(request)
        if pattern_url[0] != 100 : return redirect(pattern_url[1])
    except: return redirect('account')
    # customer check end

    if Site_Settings.objects.get(code=1001).physical_delivery_show == False :
        request.session['notification'] = ['تحویل فیزیکی غیرفعال است']
        return redirect('customer_panel')

    if request.method == 'POST' :

        delete = request.POST.get('delete')
            
        product = Site_Products.objects.get(pk=pk)

        try : order = Customer_Gold_Order.objects.get(status='Pending_payment',uname=pattern_url[2],city=product.city)
        except : return JsonResponse({'type':'danger', 'msg':'پردازش مورد نظر با مشکل مواجه شده است'})

        try:

            order_product = Customer_Cart_Products.objects.get(order=order, product=product)

            if order_product.is_gold_melt:
                order_product.delete()
            else:
                if order_product.quantity > 1 and delete == 'true':

                    order_product.delete()
                elif order_product.quantity > 1 and delete == None:

                    order_product.quantity -= 1
                    order_product.save()
                else:

                    order_product.delete()
            
        except Customer_Cart_Products.DoesNotExist:
            return JsonResponse({'type':'danger', 'msg':'محصول در سبد خرید یافت نشد.'})

        cart_products = Customer_Cart_Products.objects.filter(order=order)
        current_gold_price = Currency_List.objects.get(symbol='XAU18').BuySellPrice['buy']

        total_toman = 0
        total_grams = 0
        wages_coins_toman = 0
        wages_ingots_toman = 0
        fee_order = 0

        for cart_product in cart_products:
            product = cart_product.product

            product_weight = product.grams if product.grams is not None else 0
            wages = product.wages if product.wages is not None else 0       

            result = calculate_price_or_grams(current_gold_price, wages, product.fee, product.grams)

            total_product_price = result['final_toman'] * cart_product.quantity
            total_toman += total_product_price

            total_product_gram = result['final_gram'] * cart_product.quantity
            total_grams += total_product_gram

            product_price_in_toman = product_weight * current_gold_price
            wages_in_toman = (wages * product_price_in_toman) / 100
            wages_in_toman = cart_product.quantity * wages_in_toman

            if product.type_gold == "gold2":
                wages_coins_toman += wages_in_toman
            elif product.type_gold == "gold3":
                wages_ingots_toman += wages_in_toman

            fee_order += Decimal(cart_product.quantity) * Decimal(product.fee)

        total_wages_toman = wages_coins_toman + wages_ingots_toman

        order.toman_total = round(total_toman)
        order.gram_total = total_grams
        order.save()

        total_products = cart_products.aggregate(total_quantity=models.Sum('quantity'))['total_quantity'] or 0
        product_quantity = Customer_Cart_Products.objects.filter(order=order, product=Site_Products.objects.get(pk=pk)).aggregate(total_quantity=models.Sum('quantity'))['total_quantity'] or 0
        
        total_grams = cart_products.aggregate(total_grams=Sum(F('quantity') * F('product__grams')))['total_grams']
        total_grams = total_grams or 0 


        total_wages = cart_products.aggregate(total_wages=Sum(F('quantity') * F('product__wages')))['total_wages']
        total_wages = total_wages or 0 

        total_fee = cart_products.aggregate(total_fee=Sum(F('quantity') * F('product__fee')))['total_fee']
        total_fee = total_fee or 0 
        
        melted = Customer_Cart_Products.objects.filter(order=order,is_gold_melt=True)
        weight_melted = melted.aggregate(total_grams=Sum(F('quantity') * F('product__grams')))['total_grams'] or 0


        count_melted = melted.aggregate(total_quantity=Sum('quantity'))['total_quantity']
        count_melted = count_melted or 0

        coins = Customer_Cart_Products.objects.filter(order=order,product__type_gold="gold2")

        Weight_coins = coins.aggregate(total_grams=Sum(F('quantity') * F('product__grams')))['total_grams']
        Weight_coins = Weight_coins or 0

        count_coins = coins.aggregate(total_quantity=Sum('quantity'))['total_quantity']
        count_coins = count_coins or 0

        wages_coins = coins.aggregate(total_wages=Sum(F('quantity') * F('product__wages')))['total_wages']
        wages_coins = wages_coins or 0

        ingots = Customer_Cart_Products.objects.filter(order=order,product__type_gold="gold3")
        Weight_ingots = ingots.aggregate(total_grams=Sum(F('quantity') * F('product__grams')))['total_grams']
        Weight_ingots = Weight_ingots or 0

        count_ingots = ingots.aggregate(total_quantity=Sum('quantity'))['total_quantity']
        count_ingots = count_ingots or 0

        wages_ingots = ingots.aggregate(total_wages=Sum(F('quantity') * F('product__wages')))['total_wages']
        wages_ingots = wages_ingots or 0

        asset = Currency_List.objects.get(symbol='XAU18')
        fund_balance = get_customer_balance(request.user, asset.symbol)['balance']

        if  Decimal(fund_balance) <  Decimal(order.gram_total) :

            remaining_gold =  Decimal(order.gram_total) - Decimal(fund_balance)
            remaining_toman = (remaining_gold * current_gold_price)


            gram_fee_gateway = remaining_gold

        else : 

            remaining_toman = 0
            gram_fee_gateway = order.gram_total  


        if float(asset.buy_fee) != float(0) :

            f = ((Decimal(asset.buy_fee) * Decimal(gram_fee_gateway)) / 100)
            if f < Decimal(asset.buy_fee_lower) : fee = asset.buy_fee_lower
            elif f > Decimal(asset.buy_fee_upper) : fee = asset.buy_fee_upper
            else : fee = f
            fee_price = int(round(fee * current_gold_price , 0))

        else:

            fee = 0
            fee_price = 0

    
        if Customer_Cart_Products.objects.filter(order=order).count() == 0 : order.delete()

        return JsonResponse({'type':'success', 'msg':'محصول از سبد خرید حذف شد.','count_products':total_products,'product_quantity':product_quantity,'weight_melted':custom_float_format(weight_melted, 4),'Weight_coins':round(Weight_coins,4),'Weight_ingots':round(Weight_ingots,4),'count_melted':count_melted,'count_coins':count_coins,'count_ingots':count_ingots,'wages_coins':f'{round(wages_coins_toman):,}','wages_ingots':f'{round(wages_ingots_toman):,}','total_wages':f'{round(total_wages_toman):,}','total_fee':custom_float_format(fee_order, 4),'total_grams':round(total_grams,4),'toman_total':f'{round(order.toman_total):,}','geram_total':round(order.gram_total,4),'remaining_toman':f'{round(remaining_toman):,}','product_inventory':calculate_product_inventory(product.pk)['product_inventory'],'fee_price_gateway': f'{fee_price:,}'})


def customer_select_branch(request,pk):


    # customer check start
    try :
        pattern_url = customer_access_check(request)
        if pattern_url[0] != 100 : return redirect(pattern_url[1])
    except: return redirect('account')
    # customer check end

    if Site_Settings.objects.get(code=1001).physical_delivery_show == False :

        request.session['notification'] = ['تحویل فیزیکی غیرفعال است']
        return redirect('customer_panel')

    try : 
        order = Customer_Gold_Order.objects.get(pk=pk)
    except : return redirect('inperson_delivery')

    
    cart_products = Customer_Cart_Products.objects.filter(order=order)

    asset = Currency_List.objects.get(symbol='XAU18')
    fund_balance = get_customer_balance(request.user, asset.symbol)['balance']
    show_time = int(get_date_time()['timestamp']) - 86500

    working_days = Site_Branch_Working_Days.objects.filter(branch__city=order.city,act=True,capacity__gt=0,working_date__gt=show_time).order_by('working_date')

    result = []

    for day in working_days:
        branch = day.branch
        if branch.act == True :
            branch_info = {'branch_pk': branch.pk,'address': branch.address,'working_time': branch.working_time,'capacity': day.capacity}

            existing_date = next((item for item in result if item['Time'] == day.working_date), None)
            
            if existing_date : existing_date['branch'].append(branch_info)
            else : 
                if len(result) <= 6 :
                    result.append({'Time': day.working_date,'branch': [branch_info]})

    current_gold_price = Currency_List.objects.get(symbol='XAU18').BuySellPrice['buy']

    total_toman = 0
    total_grams = 0
    
    if order.status == 'Pending_payment' :  

        for cart_product in cart_products:

            product = cart_product.product

            if cart_product.is_gold_melt : wages = 0
            else : wages = product.wages if product.wages is not None else 0         

            cal = calculate_price_or_grams(current_gold_price, wages, product.fee, product.grams)

            total_product_price = cal['final_toman'] * cart_product.quantity
            total_toman += total_product_price

            total_product_gram = cal['final_gram'] * cart_product.quantity
            total_grams += total_product_gram


        order.toman_total = round(total_toman)
        order.gram_total = total_grams
        order.save()

    if  Decimal(fund_balance) < Decimal(order.gram_total) :

        remaining_gold =  Decimal(order.gram_total) - Decimal(fund_balance)
        remaining_toman = (remaining_gold * current_gold_price)

        gram_fee_gateway = remaining_gold
      
    else : 
        remaining_toman = 0
        gram_fee_gateway = order.gram_total 

    if float(asset.buy_fee) != float(0) :

        f = ((Decimal(asset.buy_fee) * Decimal(gram_fee_gateway)) / 100)
        if f < Decimal(asset.buy_fee_lower) : fee = asset.buy_fee_lower
        elif f > Decimal(asset.buy_fee_upper) : fee = asset.buy_fee_upper
        else : fee = f
        fee_price = int(round(fee * current_gold_price , 0))

    else:

        fee = 0
        fee_price = 0

    if order.delivery_date and order.delivery_date.jalali_date :
        if order.delivery_date.jalali_date < jdatetime.datetime.now().strftime('%Y/%m/%d'): is_delivered = False
        else: is_delivered = True
    else: is_delivered = False 

    return render(request, get_customer_theme(pattern_url[2]) + 'invoice_products.html', {'cart_products':cart_products,'order':order,'fund_balance':fund_balance,'list_date':result,'last_gold_price':Currency_List.objects.get(symbol='XAU18').BuySellPrice['buy'],'remaining_toman':round(remaining_toman),'fee_price_gateway':f'{fee_price:,}','is_delivered':is_delivered})



def customer_cart_payment_wallet(request, pk):

    # customer check start
    try :
        pattern_url = customer_access_check(request)
        if pattern_url[0] != 100 : return redirect(pattern_url[1])
    except: return redirect('account')
    # customer check end

    if Site_Settings.objects.get(code=1001).physical_delivery_show == False :

        request.session['notification'] = ['تحویل فیزیکی غیرفعال است']
        return redirect('customer_panel')
    
    customer = pattern_url[2]

    if request.method == 'POST' :

        timestamp = request.POST.get('date')
        branch_pk = request.POST.get('branch')
        accept_invoice = request.POST.get('accept_invoice')
        accept_rulls = request.POST.get('accept_rulls')
        

        if Site_Settings.objects.get(code=1001).is_buy_wallet == False : return JsonResponse({'type':'danger', 'msg':'در حال حاضر خرید از کیف پول غیرفعال است'})

        if timestamp == "":
            return JsonResponse({'type':'danger', 'msg':'لطفا تاریخ مراجعه تحویل طلا را انتخاب نمایید'})

        if branch_pk == "" or branch_pk == None :
            return JsonResponse({'type':'danger', 'msg':'لطفا شعبه تحویل طلا را انتخاب نمایید'})

        if accept_invoice != 'on' :
            return JsonResponse({'type':'danger', 'msg':'لطفا فاکتور فوق را تایید نمایید'})

        if accept_rulls != 'on' :
            return JsonResponse({'type':'danger', 'msg':'لطفا قوانین و مقررات تحویل فیزیکی طلا را تایید نمایید'})
        
        try : 

            branch = Site_Branches_Each_Representative.objects.get(pk=branch_pk,act=True)
            if Site_Branch_Working_Days.objects.filter(working_date=timestamp,branch=branch,act=True).count() != 1 :
                return JsonResponse({'type':'danger', 'msg':'تحویل طلا در تاریخ مورد نظر امکان پذیر نمی باشد لطفا تاریخ دیگری انتخاب نمایید'})
            
        except : return JsonResponse({'type':'danger', 'msg':'تحویل طلا از شعبه مورد نظر امکان پذیر نمی باشد لطفا شعبه دیگری انتخاب نمایید'})

        try : order = Customer_Gold_Order.objects.get(pk=pk,uname=customer)
        except : return JsonResponse({'type':'danger', 'msg':'پردازش مورد نظر با مشکل مواجه شده است'})

        if order.city.act == False :
            return JsonResponse({'type':'danger', 'msg':'امکان تحویل فیزیکی محصول موردنظر وجود ندارد'})

        cart_products = Customer_Cart_Products.objects.filter(order=order)
        current_gold_price = Currency_List.objects.get(symbol='XAU18').BuySellPrice['buy']

        total_toman = 0
        total_grams = 0
        wages_coins_toman = 0
        wages_ingots_toman = 0

        for cart_product in cart_products :

            product = cart_product.product

            if product.act != True :
                return JsonResponse({'type':'danger', 'msg':f'محصول {product.title} موجود نمی باشد'})
            
            if calculate_product_inventory(product.pk)['product_inventory'] < int(cart_product.quantity) :
                return JsonResponse({'type':'danger', 'msg':f'موجودی محصول {product.title} به اتمام رسیده است'})

            product_weight = product.grams if product.grams is not None else 0
            wages = product.wages if product.wages is not None else 0

            result = calculate_price_or_grams(current_gold_price, wages, product.fee, product.grams)

            total_product_price = result['final_toman'] * cart_product.quantity
            total_toman += total_product_price

            total_product_gram = result['final_gram'] * cart_product.quantity
            total_grams += total_product_gram

            product_price_in_toman = product_weight * current_gold_price
            wages_in_toman = (wages * product_price_in_toman) / 100
            wages_in_toman = cart_product.quantity * wages_in_toman

            if product.type_gold == "gold2":
                wages_coins_toman += wages_in_toman
            elif product.type_gold == "gold3":
                wages_ingots_toman += wages_in_toman


            info_product = cart_product
            info_product.title = product.title
            info_product.cutie = product.cutie
            info_product.grams = product.grams
            info_product.fee = product.fee
            info_product.type_gold = product.type_gold
            info_product.wages = product.wages
            info_product.tracking_code = product.tracking_code
            info_product.desc = product.desc
            info_product.price = int(round(result['final_toman']))
            info_product.pure_grams = product.pure_grams
            info_product.lab = product.lab
            info_product.save()

        order.wages_coins_toman = round(wages_coins_toman)
        order.wages_ingots_toman = round(wages_ingots_toman)
        order.total_wages_toman = round(wages_coins_toman) + round(wages_ingots_toman)
        order.gram_remaining = total_grams
        order.toman_total = int(round(total_toman))
        order.gram_total = total_grams
        order.payment_status = 0
        order.gold_price = current_gold_price
        order.datetime = get_date_time()['timestamp']
        order.deliverer_first_name = branch.deliverer.first_name
        order.deliverer_last_name = branch.deliverer.last_name
        order.deliverer_personal_code = branch.deliverer.personal_code
        order.deliverer_organizational_position = branch.deliverer.organizational_position
        order.save()


        asset = Currency_List.objects.get(symbol='XAU18')
        fund_balance = get_customer_balance(request.user, asset.symbol)['balance']

        if fund_balance >= order.gram_total:

            try: 
                working_day = Site_Branch_Working_Days.objects.get(working_date=timestamp,branch=branch,act=True)
                if working_day.capacity <= 0 :
                    return JsonResponse({'type':'danger', 'msg':'ظرفیت تاریخ موردنظر در این شعبه پر شده است'})
                working_day.capacity = working_day.capacity - 1
                working_day.save()
            except : return JsonResponse({'type':'danger', 'msg':'تحویل طلا در تاریخ مورد نظر امکان پذیر نمی باشد لطفا تاریخ دیگری انتخاب نمایید'})
            
            order.branch = branch
            if branch.deliverer is not None:
                order.deliverer_first_name = branch.deliverer.first_name
                order.deliverer_last_name = branch.deliverer.last_name
                order.deliverer_personal_code = branch.deliverer.personal_code
                order.deliverer_organizational_position = branch.deliverer.organizational_position
            order.delivery_date = working_day
            
            w = Wallet(

                uname = customer,
                wallet = asset,
                desc = f'بابت پرداخت تحویل فیزیکی  : {order.pk}',
                amount = (order.gram_total) * (-1),
                datetime = get_date_time()['timestamp'],
                confirmed_datetime = get_date_time()['timestamp'],
                ip = get_ip(request),
                is_verify = True,
                physical_delivery_pk = order.pk,

            )
            w.save()
            order.status = 'Pending'

            order.save()
            return JsonResponse({'type':'success', 'msg':'پرداخت از صندوق طلا انجام شد.'})

        else:
            return JsonResponse({'type':'danger', 'msg':'موجودی صندوق طلای شما کافی نیست.'})
            


def customer_cart_payment_port(request, pk, id):

    # customer check start
    try :
        pattern_url = customer_access_check(request)
        if pattern_url[0] != 100 : return redirect(pattern_url[1])
    except: return redirect('account')
    # customer check end

    customer = pattern_url[2]
    setting = Site_Settings.objects.get(code=1001)

    if customer.status == 'Suspended' :
        return redirect('account')
    
    if request.method == 'POST' :
        
        timestamp = request.POST.get('date')
        branch_pk = request.POST.get('branch')
        accept_invoice = request.POST.get('accept_invoice')
        accept_rulls = request.POST.get('accept_rulls')

        if timestamp == "":
            return JsonResponse({'type':'danger', 'msg':'لطفا تاریخ مراجعه تحویل طلا را انتخاب نمایید'})

        if branch_pk == "" or branch_pk == None :
            return JsonResponse({'type':'danger', 'msg':'لطفا شعبه تحویل طلا را انتخاب نمایید'})

        if accept_invoice != 'on' :
            return JsonResponse({'type':'danger', 'msg':'لطفا فاکتور فوق را تایید نمایید'})

        if accept_rulls != 'on' :
            return JsonResponse({'type':'danger', 'msg':'لطفا قوانین و مقررات تحویل فیزیکی طلا را تایید نمایید'})
        
        try : 

            branch = Site_Branches_Each_Representative.objects.get(pk=branch_pk)
            if Site_Branch_Working_Days.objects.filter(working_date=timestamp,branch=branch,act=True).count() != 1 :
                return JsonResponse({'type':'danger', 'msg':'تحویل طلا در تاریخ مورد نظر امکان پذیر نمی باشد لطفا تاریخ دیگری انتخاب نمایید'})
            
        except : return JsonResponse({'type':'danger', 'msg':'تحویل طلا از شعبه مورد نظر امکان پذیر نمی باشد لطفا شعبه دیگری انتخاب نمایید'})

        try : order = Customer_Gold_Order.objects.get(pk=pk)
        except : return JsonResponse({'type':'danger', 'msg':'پردازش مورد نظر با مشکل مواجه شده است'})


        cart_products = Customer_Cart_Products.objects.filter(order=order)
        current_gold_price = Currency_List.objects.get(symbol='XAU18').BuySellPrice['buy']

        if Permission.objects.filter(user=request.user, codename='customer_authentication_complated').count() == 0 or customer.status != 'Authenticated' :
            return JsonResponse({'type':'danger', 'msg':'برای اتصال به درگاه میبایست احراز هویت خود را تکمیل نمایید'}) 
        
        if Auth.objects.filter(customer=customer,status='Accepted').count() == 0 and  customer.buy_price == float(0) :
           return JsonResponse({'type':'danger', 'msg':'ارسال مدرک شناسایی برای تحویل فیزیکی الزامی است'}) 

        if setting.is_buy_port == False : return JsonResponse({'type':'danger', 'msg':'در حال حاضر خرید از درگاه بانکی غیرفعال است'})

        if Customer_card.objects.filter(uname=customer,is_verify=True,is_show=True).count()  == 0 :
            return JsonResponse({'type':'redirect', 'msg':'برای اتصال به درگاه میبایست کارت بانکی شما ثبت و تایید شده باشد'})

        total_toman = 0
        total_grams = 0
        wages_coins_toman = 0
        wages_ingots_toman = 0

        for cart_product in cart_products :

            product = cart_product.product

            if product.act != True :
                return JsonResponse({'type':'danger', 'msg':f'محصول {product.title} موجود نمی باشد'})
           
            if calculate_product_inventory(product.pk)['product_inventory'] < int(cart_product.quantity) :
                return JsonResponse({'type':'danger', 'msg':f'موجودی محصول {product.title} به اتمام رسیده است'})

            product_weight = product.grams if product.grams is not None else 0
            if cart_product.is_gold_melt : wages = 0
            else : wages = product.wages if product.wages is not None else 0  

            result = calculate_price_or_grams(current_gold_price, wages, product.fee, product.grams)

            total_product_price = result['final_toman'] * cart_product.quantity
            total_toman += total_product_price

            total_product_gram = result['final_gram'] * cart_product.quantity
            total_grams += total_product_gram

            product_price_in_toman = product_weight * current_gold_price
            wages_in_toman = (wages * product_price_in_toman) / 100
            wages_in_toman = cart_product.quantity * wages_in_toman

            if product.type_gold == "gold2":
                wages_coins_toman += wages_in_toman
            elif product.type_gold == "gold3":
                wages_ingots_toman += wages_in_toman

            info_product = cart_product
            info_product.title = product.title
            info_product.cutie = product.cutie
            info_product.grams = product.grams
            info_product.fee = product.fee
            info_product.type_gold = product.type_gold
            info_product.wages = product.wages
            info_product.tracking_code = product.tracking_code
            info_product.desc = product.desc
            info_product.price = int(round(result['final_toman']))
            info_product.pure_grams = product.pure_grams
            info_product.lab = product.lab
            info_product.save()

        order.wages_coins_toman = round(wages_coins_toman)
        order.wages_ingots_toman = round(wages_ingots_toman)
        order.total_wages_toman = round(wages_coins_toman) + round(wages_ingots_toman)
        order.toman_total = int(round(total_toman))
        order.gram_total = total_grams
        order.gold_price = current_gold_price
        order.deliverer_first_name = branch.deliverer.first_name
        order.deliverer_last_name = branch.deliverer.last_name
        order.deliverer_personal_code = branch.deliverer.personal_code
        order.deliverer_organizational_position = branch.deliverer.organizational_position
        order.save()

        asset = Currency_List.objects.get(symbol='XAU18')
        fund_balance = get_customer_balance(request.user, asset.symbol)['balance']

        


        if id == 'false' :
        #ما به التفاوت


            if setting.is_buy_port == False and setting.is_buy_wallet == False : return JsonResponse({'type':'danger', 'msg':'در حال حاضر تحویل فیزیکی غیرفعال است'})
            
            if fund_balance <= 0 : return JsonResponse({'type':'danger', 'msg':'موجودی صندوق طلای شما کافی نیست '})
            if fund_balance < order.gram_total  :



                toman_remaining =  Decimal(order.gram_total) -  Decimal(fund_balance)
                gram_remaining =  Decimal(order.gram_total) -  Decimal(toman_remaining)
                amount = int(round(Decimal(toman_remaining) *  Decimal(current_gold_price)))


                if float(asset.buy_fee) != float(0) :

                    f = ((Decimal(asset.buy_fee) * toman_remaining) / 100)
                    if f < Decimal(asset.buy_fee_lower) : fee = asset.buy_fee_lower
                    elif f > Decimal(asset.buy_fee_upper) : fee = asset.buy_fee_upper
                    else : fee = f
                    fee_price = round(fee * current_gold_price , 0)

                else:

                    fee = 0
                    fee_price = 0

                amount = int(round((amount) + fee_price))


                if amount > 200000000  :
                    return JsonResponse({'type':'danger', 'msg':'مبلغ فاکتور نمیتواند بیشتر از ۲۰۰ میلیون باشد'})
            


                if int(amount) < 10000  :

                   
                    ow = Online_Wallet(owner=customer, amount=int(10000), datetime=get_date_time()['timestamp'], is_physical_delivery=True, order=order,additional_amount=(10000 - int(amount)) ,fee_price=fee_price)
                    ow.save()

                else :

                    ow = Online_Wallet(owner=customer, amount=int(amount), datetime=get_date_time()['timestamp'], is_physical_delivery=True, order=order,fee_price=fee_price)
                    ow.save()

                try: 

                    working_day = Site_Branch_Working_Days.objects.get(working_date=timestamp,branch=branch,act=True)
                    if working_day.capacity <= 0 :
                        return JsonResponse({'type':'danger', 'msg':'ظرفیت تاریخ موردنظر در این شعبه پر شده است'})
                    working_day.capacity = working_day.capacity - 1
                    working_day.save()

                except : return JsonResponse({'type':'danger', 'msg':'تحویل طلا در تاریخ مورد نظر امکان پذیر نمی باشد لطفا تاریخ دیگری انتخاب نمایید'})

                if setting.default_payment_gateway == 'mellipay' :

                    if amount < 10000 :    
                        result = 'my_api'
                    else :   result = 'my_api'

                elif setting.default_payment_gateway == 'idpay' :

                    if amount < 10000 :
                        result = 'my_api'
                    else :   result = 'my_api'

                elif setting.default_payment_gateway == 'paystar' :

                    if amount < 10000 :
                        result = 'my_api'
                    else :    
                        result = 'my_api'

                else : return JsonResponse({'type':'danger', 'msg':'در اتصال به درگاه خطایی رخ داده لطفا با پشتیبانی تماس بگیرید'})


                if setting.default_payment_gateway in ['', ''] and result["status"] == 201 :


                    ow = Online_Wallet.objects.get(pk=ow.pk)
                    ow.mellipay_track_id = result[""]
                    ow.default_payment_gateway = setting.default_payment_gateway
                    ow.save()

                    if branch.deliverer is not None:
                        order.deliverer_first_name = branch.deliverer.first_name
                        order.deliverer_last_name = branch.deliverer.last_name
                        order.deliverer_personal_code = branch.deliverer.personal_code
                        order.deliverer_organizational_position = branch.deliverer.organizational_position

                    order.status = 'Connection_getway'
                    order.branch = branch
                    order.delivery_date = working_day
                    order.gram_remaining = gram_remaining
                    order.toman_remaining = int(amount)
                    order.datetime=get_date_time()['timestamp']
                    order.payment_status = 2
                    order.gateway_buy_fee = fee_price
                    order.save()

                    
                    if customer.is_from_pwa == True :
                        add_static_report(request, 'اتصال به درگاه جهت پرداخت تحویل فیزیکی',None, True, customer.req_user, get_ip(request))   
                    else:
                        add_static_report(request, 'اتصال به درگاه جهت پرداخت تحویل فیزیکی')


                    result = {"link": result[""]}
                    response = JsonResponse({'type': 'success', 'msg': 'در حال انتقال به درگاه بانکی ...', 'redirect': result[""]})
                    response.set_cookie('return_url', request.META.get('HTTP_REFERER', 'Unknown'), max_age=3600) 
                    
                    return response    

                  

                elif setting.default_payment_gateway in [''] and result[""] == 1 :

                    ow = Online_Wallet.objects.get(pk=ow.pk)
                    ow.mellipay_track_id = result[""][""]
                    ow.default_payment_gateway = setting.default_payment_gateway
                    ow.save()


                    if branch.deliverer is not None:
                        order.deliverer_first_name = branch.deliverer.first_name
                        order.deliverer_last_name = branch.deliverer.last_name
                        order.deliverer_personal_code = branch.deliverer.personal_code
                        order.deliverer_organizational_position = branch.deliverer.organizational_position


                    order.status = 'Connection_getway'
                    order.branch = branch
                    order.delivery_date = working_day
                    order.gram_remaining = gram_remaining
                    order.toman_remaining = int(amount)
                    order.datetime=get_date_time()['timestamp']
                    order.payment_status = 2
                    order.gateway_buy_fee = fee_price
                    order.save()

                    if customer.is_from_pwa == True :
                        add_static_report(request, 'اتصال به درگاه جهت پرداخت تحویل فیزیکی',None, True, customer.req_user, get_ip(request))   
                    else:
                        add_static_report(request, 'اتصال به درگاه جهت پرداخت تحویل فیزیکی')

                    paystar_link = 'my_link'

                    return JsonResponse({'type':'success', 'msg':'در حال انتقال به درگاه بانکی ...', 'redirect':f'{}{result[""]["tokn"]}'})

                else : return JsonResponse({'type':'danger', 'msg':'در اتصال به درگاه خطایی رخ داده لطفا با پشتیبانی تماس بگیرید'})

            elif fund_balance > order.gram_total :
                return JsonResponse({'type':'danger', 'msg':'ما‌به‌التفاوت خرید شما صفر می باشد'})
            return JsonResponse({'type':'danger', 'msg':'امکان پرداخت وجود ندارد'})
        
        else:


            #کل فاکتور
          

            if float(asset.buy_fee) != float(0) :


                f = ((Decimal(asset.buy_fee) * order.gram_total) / 100)
                if f < Decimal(asset.buy_fee_lower) : fee = asset.buy_fee_lower
                elif f > Decimal(asset.buy_fee_upper) : fee = asset.buy_fee_upper
                else : fee = f
                fee_price = round(fee * current_gold_price , 0)

            else:

                fee = 0
                fee_price = 0

            amount = int(round((order.toman_total) + fee_price))    

            if amount > 200000000  :
                return JsonResponse({'type':'danger', 'msg':'مبلغ فاکتور نمیتواند بیشتر از ۲۰۰ میلیون باشد'})
        


            ow = Online_Wallet(owner=customer, amount=int(amount), datetime=get_date_time()['timestamp'], is_physical_delivery=True, order=order,fee_price=fee_price)
            ow.save()           

            if setting.default_payment_gateway == 'mellipay' :
                result = 'my_api'
                
            elif setting.default_payment_gateway == 'idpay' :
                result = 'my_api'

            elif setting.default_payment_gateway == 'paystar' :
                result = 'my_api'
            else : return JsonResponse({'type':'danger', 'msg':'در اتصال به درگاه خطایی رخ داده لطفا با پشتیبانی تماس بگیرید'})
    

            try: 

                working_day = Site_Branch_Working_Days.objects.get(working_date=timestamp,branch=branch,act=True)
                if working_day.capacity - 1 < 0 :
                    return JsonResponse({'type':'danger', 'msg':'ظرفیت تاریخ موردنظر در این شعبه پر شده است'})
                working_day.capacity = working_day.capacity - 1
                working_day.save()

            except : return JsonResponse({'type':'danger', 'msg':'تحویل طلا در تاریخ مورد نظر امکان پذیر نمی باشد لطفا تاریخ دیگری انتخاب نمایید'})
                    
            if setting.default_payment_gateway in ['', ''] and result[""] == 201 :

                ow = Online_Wallet.objects.get(pk=ow.pk)
                ow.mellipay_track_id = result[""]
                ow.default_payment_gateway = setting.default_payment_gateway
                ow.save()


                if branch.deliverer is not None:
                    order.deliverer_first_name = branch.deliverer.first_name
                    order.deliverer_last_name = branch.deliverer.last_name
                    order.deliverer_personal_code = branch.deliverer.personal_code
                    order.deliverer_organizational_position = branch.deliverer.organizational_position

                order.status = 'Connection_getway'
                order.branch = branch
                order.delivery_date = working_day
                order.toman_remaining = 0
                order.toman_total = int(amount)
                order.datetime=get_date_time()['timestamp']
                order.payment_status = 1
                order.gateway_buy_fee = fee_price
                order.save()
                if customer.is_from_pwa == True :
                    add_static_report(request, 'اتصال به درگاه جهت پرداخت تحویل فیزیکی',None, True, customer.req_user, get_ip(request))   
                else:
                    add_static_report(request, 'اتصال به درگاه جهت پرداخت تحویل فیزیکی')

                result = {"link": result["link"]}
                response = JsonResponse({'type': 'success', 'msg': 'در حال انتقال به درگاه بانکی ...', 'redirect': result["link"]})
                response.set_cookie('return_url', request.META.get('HTTP_REFERER', 'Unknown'), max_age=3600) 
                
                return response        

                
            
            elif setting.default_payment_gateway in [''] and result[""] == 1 :

                ow = Online_Wallet.objects.get(pk=ow.pk)
                ow.mellipay_track_id = result[""][""]
                ow.default_payment_gateway = setting.default_payment_gateway
                ow.save()

                if branch.deliverer is not None:
                    order.deliverer_first_name = branch.deliverer.first_name
                    order.deliverer_last_name = branch.deliverer.last_name
                    order.deliverer_personal_code = branch.deliverer.personal_code
                    order.deliverer_organizational_position = branch.deliverer.organizational_position

                order.status = 'Connection_getway'
                order.branch = branch
                order.delivery_date = working_day
                order.toman_remaining = 0
                order.toman_total = int(amount)
                order.datetime=get_date_time()['timestamp']
                order.payment_status = 1
                order.gateway_buy_fee = fee_price
                order.save()

                if customer.is_from_pwa == True :
                    add_static_report(request, 'اتصال به درگاه جهت پرداخت تحویل فیزیکی',None, True, customer.req_user, get_ip(request))   
                else:
                    add_static_report(request, 'اتصال به درگاه جهت پرداخت تحویل فیزیکی')

                paystar_link = 'my_link'   

                return JsonResponse({'type':'success', 'msg':'در حال انتقال به درگاه بانکی ...', 'redirect':f'{}{result[""][""]}'})

            else : return JsonResponse({'type':'danger', 'msg':'در اتصال به درگاه خطایی رخ داده لطفا با پشتیبانی تماس بگیرید'})


    else:       
        return JsonResponse({'type':'danger', 'msg':'خطایی رخ داده.'})
        


def customer_cancellation_physical_delivery(request, pk):

    # customer check start
    try :
        pattern_url = customer_access_check(request)
        if pattern_url[0] != 100 : return redirect(pattern_url[1])
    except: return redirect('account')
    # customer check end

    customer = pattern_url[2]

    try : order = Customer_Gold_Order.objects.get(pk=pk,status='Pending_delivery')
    except : return JsonResponse({'type':'danger', 'msg':'امکان لغو تحویل فیزیکی وجود ندارد'})
    
    if order.delivery_date.jalali_date < jdatetime.datetime.now().strftime('%Y/%m/%d'):
        return JsonResponse({'type': 'danger', 'msg': 'تاریخ تحویل گذشته است و امکان لغو وجود ندارد'})

    asset = Currency_List.objects.get(symbol='XAU18')

    working_day = order.delivery_date

    if order.payment_status == 0 :

        w = Wallet(

            uname = customer,
            wallet = asset,
            desc = f'بابت لغو تحویل فیزیکی  : {order.pk}',
            amount = order.gram_total ,
            datetime = get_date_time()['timestamp'],
            confirmed_datetime = get_date_time()['timestamp'],
            ip = get_ip(request),
            is_verify = False,
            physical_delivery_pk = order.pk,

        )
        w.save()

    elif order.payment_status == 2 :  

        w = Wallet(

            uname = customer,
            wallet = asset,
            desc = f'بابت لغو تحویل فیزیکی  : {order.pk}',
            amount = order.gram_remaining ,
            datetime = get_date_time()['timestamp'],
            confirmed_datetime = get_date_time()['timestamp'],
            ip = get_ip(request),
            is_verify = False,
            physical_delivery_pk = order.pk,

        )
        w.save()


        Wallet(
                    
            uname = customer, 
            wallet = 'IRT', 
            desc = f'بابت لغو تحویل فیزیکی : {order.pk}',
            amount = order.toman_remaining, 
            datetime = get_date_time()['timestamp'] ,
            confirmed_datetime = get_date_time()['timestamp'] ,
            ip = '0.0.0.0', 
            is_verify = False,
        
        ).save()

    elif order.payment_status == 1 : 


        try : 

            wO = Online_Wallet.objects.get(order=order,is_physical_delivery=True,owner=order.uname)
            wallet_amount = int(int(wO.transactionAmount) / 10) 


            Wallet(
                        
                uname = customer, 
                wallet = 'IRT', 
                desc = f'بابت لغو تحویل فیزیکی : {order.pk}',
                amount = (wallet_amount) , 
                datetime = get_date_time()['timestamp'] ,
                confirmed_datetime = get_date_time()['timestamp'] ,
                ip = '0.0.0.0', 
                is_verify = False,
            
            ).save()

        except : pass

    
    working_day.capacity = working_day.capacity + 1
    working_day.save()
 

    for cart_product in Customer_Cart_Products.objects.filter(order=order) :
        inventory = Site_Product_Inventory(product=cart_product.product, quantity=cart_product.quantity , datetime=get_date_time()['timestamp'])
        inventory.save()

    order.status = 'Canceled'
    order.save()

    if customer.is_from_pwa == True :
        add_static_report(request,'لغو تحویل فیزیکی',None, True, customer.req_user, get_ip(request))   
    else:
        add_static_report(request,'لغو تحویل فیزیکی')

    return JsonResponse({'type':'success', 'msg':'تحویل فیزیکی طلا لغو شد.'})

    # else:
    #     return JsonResponse({'type':'danger', 'msg':'موجودی صندوق طلای شما کافی نیست.'})
            


def customer_wallet_irt_search(request):

    # customer check start
    try :
        pattern_url = customer_access_check(request)
        if pattern_url[0] != 100 : return redirect(pattern_url[1])
    except: return redirect('account')
    # customer check end

    path = request.path

    if 'gold' in path : active_tab = '2'
    elif 'irt' in path : active_tab = '3'
    else : active_tab = '1' 

    wallet = Currency_List.objects.filter(is_wallet=True,is_show=True).order_by('sort')
    customer = pattern_url[2]

    try: instant_price_default = Currency_List.objects.get(is_instant_price_default=True).BuySellPrice['buy'] 
    except: instant_price_default = Currency_List.objects.get(symbol='XAU18').BuySellPrice['buy'] 
    
    trans_gold = Wallet.objects.filter(uname=customer,wallet='XAU18',is_verify=True).order_by('-pk')
    count_trans_gold = trans_gold.count()

    paginator = Paginator(trans_gold,5)
    gold_page = request.GET.get('gold_page')

    try:
        trans_gold = paginator.page(gold_page)
    except PageNotAnInteger:
        trans_gold = paginator.page(1)
    except EmptyPage:
        trans_gold = paginator.page(paginator.num_page) 


    trans_irt = Wallet.objects.filter(uname=customer,wallet='IRT',is_verify=True).exclude(is_locked=True).order_by('-pk')

    if request.method == 'POST':
        
        invoice_number = request.POST.get('invoice_number')
        date_str = request.POST.get('date')

        request.session['invoice_number'] = invoice_number
        request.session['date_str'] = date_str

    else:

        invoice_number = request.session.get('invoice_number', "")
        date_str = request.session.get('date_str', "")

    filters = {}

    if invoice_number : filters['pk'] = invoice_number

    if date_str:

        try:

            sdata = date_str.split('/')
            newdata = khayyam.JalaliDate(int(sdata[0]), int(sdata[1]), int(sdata[2])).todate()
            newdata = str(newdata).split('-')

            start_datetime = f"{newdata[0]}-{newdata[1]}-{newdata[2]} 00:00:00"
            end_datetime = f"{newdata[0]}-{newdata[1]}-{newdata[2]} 23:59:59"

            start_timestamp = int(datetime.strptime(start_datetime, "%Y-%m-%d %H:%M:%S").timestamp())
            end_timestamp = int(datetime.strptime(end_datetime, "%Y-%m-%d %H:%M:%S").timestamp())

            filters['datetime__gte'] = start_timestamp
            filters['datetime__lte'] = end_timestamp

        except:
            pass

    bills = trans_irt.filter(**filters)

    count_trans_irt = bills.count()
    
    paginator = Paginator(bills, 5)
    irt_page = request.GET.get('irt_page')

    try:
        trans_irt = paginator.page(irt_page)
    except PageNotAnInteger:
        trans_irt = paginator.page(1)
    except EmptyPage:
        trans_irt = paginator.page(paginator.num_pages)

    toman_equivalent_of_gold_balance = get_customer_balance(request.user,'XAU18')["balance"] * Currency_List.objects.get(symbol='XAU18').BuySellPrice['sell']
    gram_equivalent_of_Toman_balance = get_customer_balance(request.user,'IRT')["balance"] / Currency_List.objects.get(symbol='XAU18').BuySellPrice['buy']

    return render(request, get_customer_theme(pattern_url[2]) + 'toman_wallet.html', {'wallet':wallet, 'customer':customer,'instant_price_default':instant_price_default,'trans_irt':trans_irt,'trans_gold':trans_gold,'active_tab':active_tab,'toman_equivalent_of_gold_balance':toman_equivalent_of_gold_balance,'gram_equivalent_of_Toman_balance':gram_equivalent_of_Toman_balance,'count_trans_gold':count_trans_gold,'count_trans_irt':count_trans_irt})


def customer_wallet_gold_search(request):

    # customer check start
    try :
        pattern_url = customer_access_check(request)
        if pattern_url[0] != 100 : return redirect(pattern_url[1])
    except: return redirect('account')
    # customer check end

    path = request.path

    if 'gold' in path : active_tab = '2'
    elif 'irt' in path : active_tab = '3'
    else : active_tab = '1' 

    wallet = Currency_List.objects.filter(is_wallet=True,is_show=True).order_by('sort')
    customer = pattern_url[2]


    try: instant_price_default = Currency_List.objects.get(is_instant_price_default=True).BuySellPrice['buy'] 
    except: instant_price_default = Currency_List.objects.get(symbol='XAU18').BuySellPrice['buy'] 

    trans_irt = Wallet.objects.filter(uname=customer, wallet='IRT', is_verify=True).exclude(is_locked=True).order_by('-pk')
    count_trans_irt = trans_irt.count()

    paginator = Paginator(trans_irt,5)
    irt_page = request.GET.get('irt_page')

    try:
        trans_irt = paginator.page(irt_page)
    except PageNotAnInteger:
        trans_irt = paginator.page(1)
    except EmptyPage:
        trans_irt = paginator.page(paginator.num_page) 
    

    trans_gold = Wallet.objects.filter(uname=customer,wallet='XAU18',is_verify=True).order_by('-pk')

    if request.method == 'POST':
        
        invoice_number = request.POST.get('invoice_number')
        date_str = request.POST.get('date')

        request.session['invoice_number'] = invoice_number
        request.session['date_str'] = date_str

    else:

        invoice_number = request.session.get('invoice_number', "")
        date_str = request.session.get('date_str', "")

    filters = {}


    if invoice_number : filters['pk'] = invoice_number

    if date_str:
        
        try:
            sdata = date_str.split('/')
            newdata = khayyam.JalaliDate(int(sdata[0]), int(sdata[1]), int(sdata[2])).todate()
            newdata = str(newdata).split('-')

            start_datetime = f"{newdata[0]}-{newdata[1]}-{newdata[2]} 00:00:00"
            end_datetime = f"{newdata[0]}-{newdata[1]}-{newdata[2]} 23:59:59"

            start_timestamp = int(datetime.strptime(start_datetime, "%Y-%m-%d %H:%M:%S").timestamp())
            end_timestamp = int(datetime.strptime(end_datetime, "%Y-%m-%d %H:%M:%S").timestamp())

            filters['datetime__gte'] = start_timestamp
            filters['datetime__lte'] = end_timestamp

        except:
            pass

    bills = trans_gold.filter(**filters)

    count_trans_gold = bills.count()
    
    paginator = Paginator(bills, 5)
    gold_page = request.GET.get('gold_page')

    try:
        trans_gold = paginator.page(gold_page)
    except PageNotAnInteger:
        trans_gold = paginator.page(1)
    except EmptyPage:
        trans_gold = paginator.page(paginator.num_pages)

    toman_equivalent_of_gold_balance = get_customer_balance(request.user,'XAU18')["balance"] * Currency_List.objects.get(symbol='XAU18').BuySellPrice['sell']
    gram_equivalent_of_Toman_balance = get_customer_balance(request.user,'IRT')["balance"] / Currency_List.objects.get(symbol='XAU18').BuySellPrice['buy']

    return render(request, get_customer_theme(pattern_url[2]) + 'gold_wallet.html', {'wallet':wallet,  'customer':customer,'instant_price_default':instant_price_default,'trans_irt':trans_irt,'trans_gold':trans_gold,'active_tab':active_tab,'toman_equivalent_of_gold_balance':toman_equivalent_of_gold_balance,'gram_equivalent_of_Toman_balance':gram_equivalent_of_Toman_balance,'count_trans_gold':count_trans_gold,'count_trans_irt':count_trans_irt})



def customer_buysell_list_search(request):

    # customer check start
    try:
        pattern_url = customer_access_check(request)
        if pattern_url[0] != 100: return redirect(pattern_url[1])
    except: return redirect('account')
    # customer check end

    customer = pattern_url[2]
    bills = Currency_BuySell_List.objects.filter(uname=customer).order_by('-pk')

    if request.method == 'POST':
        bill_number = request.POST.get('bill_number')
        status = request.POST.get('status', "all") or "all"
        from_date_str = request.POST.get('fdate')
        to_date_str = request.POST.get('tdate')
        bill_type = request.POST.get('bill_type')
        amount = request.POST.get('amount', "0") or "0"

        request.session['bill_number'] = bill_number
        request.session['status'] = status
        request.session['from_date_str'] = from_date_str
        request.session['to_date_str'] = to_date_str
        request.session['bill_type'] = bill_type
        request.session['amount'] = amount

    else:

        bill_number = request.session.get('bill_number', "")
        status = request.session.get('status', "all")
        from_date_str = request.session.get('from_date_str', "")
        to_date_str = request.session.get('to_date_str', "")
        bill_type = request.session.get('bill_type', "all")
        amount = request.session.get('amount', "0")

    filters = {}

    if bill_number: filters['pk'] = bill_number

    if status != "all": filters['status'] = status

    if bill_type != "all": filters['bill_type'] = bill_type

    if amount != "0":
        if amount == "more_than_10": filters['amount__gt'] = 10
        else: filters['amount__lte'] = amount


    if from_date_str and to_date_str:
        try:
            from_sdata = from_date_str.split('/')
            to_sdata = to_date_str.split('/')

            from_date = khayyam.JalaliDate(int(from_sdata[0]), int(from_sdata[1]), int(from_sdata[2])).todate()
            to_date = khayyam.JalaliDate(int(to_sdata[0]), int(to_sdata[1]), int(to_sdata[2])).todate()

            from_date_str = str(from_date)
            to_date_str = str(to_date)

            start_datetime = f"{from_date_str} 00:00:00"
            end_datetime = f"{to_date_str} 23:59:59"

            start_timestamp = int(datetime.strptime(start_datetime, "%Y-%m-%d %H:%M:%S").timestamp())
            end_timestamp = int(datetime.strptime(end_datetime, "%Y-%m-%d %H:%M:%S").timestamp())

            filters['datetime__gte'] = start_timestamp
            filters['datetime__lte'] = end_timestamp
        except :
            pass


    bills = bills.filter(**filters)
    
    count_bills = bills.count()

    paginator = Paginator(bills, 10)
    page = request.GET.get('page')

    query_params = QueryDict(mutable=True)
    query_params.update({ 'bill_number': bill_number, 'status': status, 'from_date_str': from_date_str,'to_date_str':to_date_str, 'bill_type': bill_type, 'amount': amount,'today': get_date_time()["shamsi_date"], })

    try:
        bills = paginator.page(page)
    except PageNotAnInteger:
        bills = paginator.page(1)
    except EmptyPage:
        bills = paginator.page(paginator.num_pages)

    return render(request, get_customer_theme(pattern_url[2]) + 'buySell_list.html', {'bill': bills, 'count_bills': count_bills, 'query_params': query_params.urlencode(),'type':'search','today': get_date_time()["shamsi_date"],})


def customer_gold_buy_request(request, symbol):

    # customer check start
    try :
        pattern_url = customer_access_check(request)
        if pattern_url[0] != 100 : return redirect(pattern_url[1])
    except: return redirect('account')
    # customer check end

    customer = pattern_url[2]
    time = get_date_time()['timestamp']
    setting = Site_Settings.objects.get(code=1001)

    if setting.is_timer_buysell == False : return JsonResponse({'type':'danger', 'msg':'در حال حاضر خرید و فروش زماندار غیرفعال است'})

    date = get_date_time()['timestamp']

    last_buy = Currency_BuySell_Custom_Price.objects.filter(uname=customer, bill_type='buy').order_by('pk')
    if last_buy.exists():
        if (int(last_buy.last().datetime) + 10) > date:
            return JsonResponse({'type':'danger', 'msg':'برای ثبت درخواست مجدد لطفا کمی صبر کنید و سپس دوباره تلاش کنید.'})
    
    if request.method == 'POST' :

        if customer.status == 'Suspended' :
            return redirect('account')

        try: currency = Currency_List.objects.get(symbol=symbol)
        except: return JsonResponse({'type':'danger', 'msg':'در خرید طلا خطایی رخ داده است'})
    
        if currency.is_sell == False :
            return JsonResponse({'type':'danger', 'msg':'در حال حاضر خرید طلا موقتا غیرفعال گردیده'})

        process_based_on = request.POST.get('process_based_on')
        gold_amount = request.POST.get('gold_amount')
        irt_amount = request.POST.get('irt_amount') or "0"
        typeMethod = request.POST.get('typeMethod')
        paymentMethod = request.POST.get('paymentMethod')   

        if typeMethod == 'irt' :   
            return JsonResponse({'type':'danger', 'msg':'در حال حاضر امکان خرید با قیمت ثابت وجود ندارد'}) 


        if process_based_on == 'price':

            if setting.is_getprice_buy == False :
                return JsonResponse({'type':'danger', 'msg':'در حال حاضر خرید براساس قیمت غیرفعال گردیده'})
            
            today = datetime.now()
            y = str(today.date()).split('-')

            start_of_day = y[0] + '-' + y[1] + '-' + y[2] + ' 00:00:00'
            start_of_day_timestamp = int(datetime.strptime(start_of_day,"%Y-%m-%d %H:%M:%S").timestamp())

            end_of_day = y[0] + '-' + y[1] + '-' + y[2] + ' 23:59:59'
            end_of_day_timestamp = int(datetime.strptime(end_of_day,"%Y-%m-%d %H:%M:%S").timestamp())

            requests_today = Currency_BuySell_Custom_Price.objects.filter(datetime__gte=start_of_day_timestamp,datetime__lte=end_of_day_timestamp,uname=customer,process_based_on='price').exclude(status='Canceled')
            
            if requests_today.count() >= 3:
                return JsonResponse({"type": "danger", "msg": "تعداد درخواست‌های شما برای این تاریخ به حد مجاز رسیده است. لطفاً تاریخ دیگری را انتخاب نمایید" })

        
            desired_price = request.POST.get('desired_price')
            desired_price = desired_price.replace(",", "")

            Unitprice = float(desired_price)

            if typeMethod == 'gram' :

                try : 
                    amount = float(gold_amount)
                    if amount <= 0 :
                        return JsonResponse({'type':'danger', 'msg':'لطفا میزان خرید خود را به درستی وارد نمایید'})
                except : return JsonResponse({'type':'danger', 'msg':'لطفا میزان خرید خود را وارد نمایید'})
                amount = round(amount,4)

                if float(currency.buy_fee) != float(0) :

                    f = ((currency.buy_fee * amount) / 100)
                    if f < currency.buy_fee_lower : fee = currency.buy_fee_lower
                    elif f > currency.buy_fee_upper : fee = currency.buy_fee_upper
                    else : fee = f
                    fee_price = round(fee * Unitprice , 0)

                else:

                    fee = 0
                    fee_price = 0
                
                maintenance_cost = int(amount * currency.maintenance_cost)
                totalPrice = round((amount * Unitprice) + fee_price + maintenance_cost)

            celling_buy = get_customer_CeilingRemain(customer.req_user)["buy"]

            if float(celling_buy) < float(totalPrice):
                return JsonResponse({'type':'danger', 'msg':f'مانده سقف مجاز خرید روزانه شما {celling_buy:,} تومان است'})

            if amount < currency.lower_amount :
                return JsonResponse({'type':'danger', 'msg':f'حداقل میزان خرید {currency.lower_amount} است'})

            if paymentMethod == 'wallet' :

                if setting.is_buy_wallet == False : return JsonResponse({'type':'danger', 'msg':'در حال حاضر خرید از کیف پول غیرفعال است'})

                if totalPrice >  float(get_customer_balance(request.user,'IRT')["balance"]) :
                    return JsonResponse({'type':'danger', 'msg':'مبلغ فاکتور شما بیشتر از موجودی کیف پول است'})
                
                else :

                    w = Wallet(

                        uname = customer,
                        wallet = 'IRT',
                        desc = f'بابت درخواست خرید با تعیین قیمت : {currency.fa_title}',
                        amount = totalPrice * (-1),
                        datetime = time,
                        confirmed_datetime = time,
                        ip = get_ip(request),
                        is_verify = True,

                    )
                    w.save()

                    
                    trans = Currency_BuySell_Custom_Price(

                        uname = customer,
                        acc = currency.acc,
                        currency = currency,
                        wallet_id = w.pk,
                        desired_price = desired_price,
                        amount = amount,
                        fee_amount = fee,
                        fee_price = fee_price,
                        unit_price = Unitprice,
                        total_price = totalPrice,
                        datetime = time,
                        ip = get_ip(request),
                        maintenance_cost = maintenance_cost,
                        amount_type = typeMethod,
                        process_based_on = process_based_on,
                        irt_amount = irt_amount


                    )
                    trans.save()

                    w.desc = f'بابت درخواست خرید با تعیین قیمت به شناسه : {trans.pk}'
                    w.save()

                    if customer.is_from_pwa == True :
                        add_static_report(request, f'درخواست خرید با قیمت مورد نظر کاربر  {currency.fa_title}', 'success', True, customer.req_user, get_ip(request))   
                    else:
                        add_static_report(request, f'درخواست خرید با قیمت مورد نظر کاربر  {currency.fa_title}', 'success')

            elif paymentMethod == 'gateway' :

                if setting.is_buy_port == False : return JsonResponse({'type':'danger', 'msg':'در حال حاضر خرید از درگاه بانکی غیرفعال است'})

                if Permission.objects.filter(user=request.user, codename='customer_authentication_complated').count() == 0 or customer.status != 'Authenticated' :
                    return JsonResponse({'type':'redirect', 'msg':'برای خرید از درگاه میبایست احراز هویت خود را تکمیل نمایید','link':'auth'})

                if Customer_card.objects.filter(uname=customer,is_verify=True,is_show=True).count()  == 0 :
                    return JsonResponse({'type':'redirect', 'msg':'برای خرید از درگاه میبایست ابتدا کارت بانکی شما ثبت و تایید شده باشد','link':'card'})

                if totalPrice > 200000000 and paymentMethod == 'gateway' :
                    return JsonResponse({'type':'danger', 'msg':'حداکثر میزان خرید از درگاه به ازای هر تراکنش 200.000.000 تومان است'})

                if totalPrice < 10000 and paymentMethod == 'gateway' :
                    return JsonResponse({'type':'danger', 'msg':'حداقل میزان خرید از درگاه به ازای هر تراکنش 10.000 تومان است'})
                
            
                ow = Online_Wallet(owner=customer, amount=totalPrice, datetime=get_date_time()['timestamp'],currency=currency,amount_buy=amount,getway_buy=True, deposite_on_wallet=False,is_reservation=False, fee_amount=fee, fee_price=fee_price,unit_price=Unitprice,maintenance_cost=maintenance_cost,is_currency_custom_price = True,desired_price=desired_price,type_method=typeMethod,process_based_on=process_based_on,request_user_buy = irt_amount)
                ow.save() 


                if customer.is_from_pwa == True :
                    add_static_report(request, f'درخواست خرید با تعیین قیمت {currency.fa_title}', 'success', True, customer.req_user, get_ip(request))   
                else:
                    add_static_report(request, f'درخواست خرید با تعیین قیمت {currency.fa_title}', 'success')

                if setting.default_payment_gateway == 'mellipay' :
                    result = 'my_api'

                elif setting.default_payment_gateway == 'idpay' :
                    result = 'my_api'

                elif setting.default_payment_gateway == 'paystar' :
                    result = 'my_api'
                

                else : return JsonResponse({'type':'danger', 'msg':'برای درخواست خرید طلا خطایی رخ داده است'})
        

                if setting.default_payment_gateway in ['', ''] and result[""] == 201 :
                    
                    ow = Online_Wallet.objects.get(pk=ow.pk)
                    ow.mellipay_track_id = result[""]
                    ow.default_payment_gateway = setting.default_payment_gateway
                    ow.save()

                    if customer.is_from_pwa == True :
                        add_static_report(request, 'انتقال به درگاه بانکی جهت پرداخت درخواست خرید',None, True, customer.req_user, get_ip(request))   
                    else:
                        add_static_report(request, 'انتقال به درگاه بانکی جهت پرداخت درخواست خرید')

                    result = {"link": result[""]}
                    response = JsonResponse({'type': 'success', 'msg': 'در حال انتقال به درگاه بانکی ...', 'redirect': result[""]})
                    response.set_cookie('return_url', request.META.get('HTTP_REFERER', 'Unknown'), max_age=3600) 
                    
                    return response    

                    

                elif setting.default_payment_gateway in ['paystar'] and result["status"] == 1 :
                
                    ow = Online_Wallet.objects.get(pk=ow.pk)
                    ow.mellipay_track_id = result["data"]["ref_num"]
                    ow.default_payment_gateway = setting.default_payment_gateway
                    ow.save()

                    if customer.is_from_pwa == True :
                        add_static_report(request, 'اتصال به درگاه جهت پرداخت درخواست خرید',None, True, customer.req_user, get_ip(request))   
                    else:
                        add_static_report(request, 'اتصال به درگاه جهت پرداخت درخواست خرید')

                    paystar_link = 'my_link'

                    return JsonResponse({'type':'success', 'msg':'در حال انتقال به درگاه بانکی ...', 'redirect':f'{}{result[""][""]}'})

                else :

                    return JsonResponse({'type':'danger', 'msg':'برای درخواست خرید طلا خطایی رخ داده است'})
            
            if trans.amount_type == 'gram': amount = str(trans.amount)
            else : amount = f"{int(trans.irt_amount):,}"
            
            return JsonResponse(
                {
                    'type':'success', 
                    'msg':'درخواست خرید شما با موفقیت ثبت شد', 
                    'redirect':'None',
                    'pk':trans.pk,
                    'amount_type':trans.amount_type,
                    'amount':amount,
                    'desired_price':f"{int(trans.desired_price):,}",
                    'ToshamsiDate':str(trans.ToshamsiDate),
                    'status':trans.status,
                    'ToStatusShow':trans.ToStatusShow,
                    'bill_type':trans.bill_type,
                    'ToTypeShow':trans.ToTypeShow,
                    'fund_balance' : get_customer_balance(request.user, currency.symbol)['balance'],
                    'Wallet_balance' : get_customer_balance(request.user, 'IRT')['balance']

                }
            )
        
        
        elif process_based_on == 'datetime':


            amount = 0

            if setting.is_timer_sell == False :
                
                return JsonResponse({'type':'danger', 'msg':'در حال حاضر درخواست خرید براساس زمان غیرفعال گردیده'})

            if typeMethod == 'gram' :

                try : 
                    amount = float(gold_amount)
                    if amount <= 0 :
                        return JsonResponse({'type':'danger', 'msg':'لطفا میزان درخواست خرید خود را به درستی وارد نمایید'})
                except : return JsonResponse({'type':'danger', 'msg':'لطفا میزان درخواست خرید خود را وارد نمایید'})
                amount = round(amount,4)

            # else :

            #     irt_amount = int(irt_amount.replace(",", ""))

            
            desired_date = request.POST.get('desired_date')
            desired_time = request.POST.get('desired_time')


            if desired_date == "" or desired_date == None or desired_date == "None":
                return JsonResponse({"type": "danger", "msg": "وارد کردن تاریخ الزامی است"})

            if desired_time == "" or desired_time == None or desired_time == "None":
                return JsonResponse({"type": "danger", "msg": "وارد کردن ساعت الزامی است"})

            try:

                sdata = desired_date.split("/")
                newdata = khayyam.JalaliDate(sdata[0], sdata[1], sdata[2]).todate()
                newdata = str(newdata).split("-")

                earlier = (newdata[0] + "-" + newdata[1] + "-" + newdata[2] + f" {desired_time}:00:00")
                desired_datetime = int(datetime.strptime(earlier, "%Y-%m-%d %H:%M:%S").timestamp())

                start_of_day = (newdata[0] + "-" + newdata[1] + "-" + newdata[2] +  " 00:00:00")
                start_of_day = int(datetime.strptime(start_of_day, "%Y-%m-%d %H:%M:%S").timestamp())

                end_of_day = (newdata[0] + "-" + newdata[1] + "-" + newdata[2] + " 23:59:59")
                end_of_day = int(datetime.strptime(end_of_day, "%Y-%m-%d %H:%M:%S").timestamp())


                requests_today = Currency_BuySell_Custom_Price.objects.filter(desired_time__gte=start_of_day,desired_time__lte=end_of_day,uname=customer,process_based_on='datetime').exclude(status='Canceled')
                if requests_today.count() >= 3 :
                    return JsonResponse({"type": "danger", "msg":  "تعداد درخواست‌های شما برای این تاریخ به حد مجاز رسیده است. لطفاً تاریخ دیگری را انتخاب نمایید"})
                
                if time > desired_datetime :
                    return JsonResponse({"type": "danger", "msg": "زمان وارد شده نامعتبر است"})

            except:

                return JsonResponse({"type": "danger", "msg": "زمان وارد شده نامعتبر است"})


            trans = Currency_BuySell_Custom_Price(

                uname = customer,
                acc = currency.acc,
                currency = currency,
                desired_time = desired_datetime,
                amount = amount,
                datetime = time,
                process_based_on = process_based_on,
                ip = get_ip(request),
                amount_type = typeMethod,
                irt_amount = irt_amount

            )
            trans.save()


            if customer.is_from_pwa == True :
                add_static_report(request, f'درخواست خرید با زمان مورد نظر کاربر  {currency.fa_title}', 'success', True, customer.req_user, get_ip(request))   
            else:
                add_static_report(request, f'درخواست خرید با زمان مورد نظر کاربر  {currency.fa_title}', 'success')
            
            if trans.amount_type == 'gram': 
                amount = str(trans.amount)
            else : amount = f"{int(trans.irt_amount):,}"

            return JsonResponse(
                {
                    'type':'success', 
                    'msg':'درخواست خرید شما با موفقیت ثبت شد', 
                    'redirect':'None',
                    'pk':trans.pk,
                    'amount_type':trans.amount_type,
                    'amount':amount,
                    'datetime':str(trans.ToshamsiDate_desired),
                    'ToshamsiDate':str(trans.ToshamsiDate),
                    'status':trans.status,
                    'ToStatusShow':trans.ToStatusShow,
                    'ToTypeShow':trans.ToTypeShow,
                    'bill_type':trans.bill_type
                }
            )

    return JsonResponse({'type':'danger', 'msg':'در درخواست خرید طلا خطایی رخ داده است'})



def customer_gold_sell_request(request, symbol):

    # customer check start
    try :
        pattern_url = customer_access_check(request)
        if pattern_url[0] != 100 : return redirect(pattern_url[1])
    except: return redirect('account')
    # customer check end

    customer = pattern_url[2]
    setting = Site_Settings.objects.get(code=1001)
    time = get_date_time()['timestamp']

    if setting.is_timer_buysell == False : return JsonResponse({'type':'danger', 'msg':'در حال حاضر خرید و فروش زماندار غیرفعال است'})

    date = get_date_time()['timestamp']

    last_sell = Currency_BuySell_Custom_Price.objects.filter(uname=customer,bill_type='sell').order_by('pk')
    if last_sell.exists():
        if (int(last_sell.last().datetime) + 10) > date:
            return JsonResponse({'type':'danger', 'msg':'برای ثبت درخواست مجدد لطفا کمی صبر کنید و سپس دوباره تلاش کنید.'})
    
    if request.method == 'POST' :

        if customer.status == 'Suspended' :
            return redirect('account')

        try : currency = Currency_List.objects.get(symbol=symbol)
        except : return JsonResponse({'type':'danger', 'msg':'در فروش طلا خطایی رخ داده است'})
    
        if Currency_BuySell_List.objects.filter(bill_type='sell',uname = customer,status ='Pendding' ).count() >= 2:
            return JsonResponse({'type':'danger', 'msg':'فاکتورهای در انتظار بیش از حد مجاز است, لطفا بعد از بررسی فاکتورهای فروش خود مجددا اقدام نمایید'})     
        
        process_based_on = request.POST.get('process_based_on')
        gold_amount = request.POST.get('gold_amount')
        irt_amount = request.POST.get('irt_amount') or "0"
        typeMethod = request.POST.get('typeMethod')
        paymentMethod = request.POST.get('paymentMethod')

        if typeMethod == 'irt' :   
            return JsonResponse({'type':'danger', 'msg':'در حال حاضر امکان فروش با قیمت ثابت وجود ندارد'}) 

        if paymentMethod != "IrtWallet" and  paymentMethod != "DirectWithdrawal" :
            return JsonResponse({'type':'danger', 'msg':'روش فروش انتخاب شده نامعتبر است'})

        cards = 0
        payment = 0
        withdraw_method = 0

        if paymentMethod == "DirectWithdrawal" :
            
            cards = request.POST.get('cards')
            payment = request.POST.get('payment')

            if cards == "" or cards == None or cards == "None" or cards == "0":
                return JsonResponse({'type':'danger', 'msg':'لطفا شماره کارت را انتخاب نمایید'})

            if payment == "" or payment == "0" :
                return JsonResponse({'type':'danger', 'msg':'لطفا روش برداشت را انتخاب نمایید'})    
            
            try :
                Customer_card.objects.get(is_verify=True,uname=customer,is_show=True,pk=cards)
            except : return JsonResponse({'type':'danger', 'msg':'کارت نامعتبر است'})    
                
            try:
                withdraw_method = WithdrawPaymentMethodIRT.objects.get(pk=payment).wage
            except:   
                return JsonResponse({'type':'danger', 'msg':'روش برداشت نامعتبر است'})    
                

        if process_based_on == 'price':

            if setting.is_getprice_sell == False :
                return JsonResponse({'type':'danger', 'msg':'در حال حاضر فروش براساس قیمت غیرفعال گردیده'})
        
            today = datetime.now()
            y = str(today.date()).split('-')

            start_of_day = y[0] + '-' + y[1] + '-' + y[2] + ' 00:00:00'
            start_of_day_timestamp = int(datetime.strptime(start_of_day,"%Y-%m-%d %H:%M:%S").timestamp())

            end_of_day = y[0] + '-' + y[1] + '-' + y[2] + ' 23:59:59'
            end_of_day_timestamp = int(datetime.strptime(end_of_day,"%Y-%m-%d %H:%M:%S").timestamp())

            requests_today = Currency_BuySell_Custom_Price.objects.filter(datetime__gte=start_of_day_timestamp,datetime__lte=end_of_day_timestamp,uname=customer,process_based_on='price').exclude(status='Canceled')
            
            if requests_today.count() >= 3:
                return JsonResponse({"type": "danger", "msg": "تعداد درخواست‌های شما برای این تاریخ به حد مجاز رسیده است. لطفاً تاریخ دیگری را انتخاب نمایید" })

            desired_price = request.POST.get('desired_price')
            desired_price = desired_price.replace(",", "")

            Unitprice = float(desired_price)
            if typeMethod == 'gram' :

                try : 
                    amount = round(float(gold_amount) , 4)
                    if amount <= 0 :
                        return JsonResponse({'type':'danger', 'msg':'لطفا میزان فروش خود را به درستی وارد نمایید'})
                except : return JsonResponse({'type':'danger', 'msg':'لطفا میزان فروش خود را وارد نمایید'})


                if float(currency.sell_fee) != float(0) :

                    f = ((currency.sell_fee * amount) / 100)
                    if f < currency.sell_fee_lower : fee = currency.sell_fee_lower
                    elif f > currency.sell_fee_upper : fee = currency.sell_fee_upper
                    else : fee = f
                    fee_price = round(fee * Unitprice , 0)

                else:

                    fee = 0
                    fee_price = 0

                totalPrice = round((amount * Unitprice) -  fee_price) - withdraw_method

            if totalPrice - fee_price <= 0 :
                return JsonResponse({'type':'danger', 'msg':'میزان فروش وارد شده نامعتبر است'})

            if amount < currency.lower_amount :
                return JsonResponse({'type':'danger', 'msg':f'حداقل میزان فروش {currency.lower_amount} است'})

            if float(get_customer_balance(request.user, currency.symbol)["balance"]) < amount :
                return JsonResponse({'type':'danger', 'msg':'موجودی کیف پول شما کمتر از میزان فروش است'}) 

            else:
                    
                w = Wallet(

                    uname = customer,
                    wallet = currency.symbol,
                    desc = f'بابت درخواست فروش با تعیین قیمت : {currency.fa_title}',
                    amount = amount * (-1),
                    datetime = time,
                    confirmed_datetime = time,
                    ip = get_ip(request),
                    is_verify = True,

                )
                w.save()

                trans = Currency_BuySell_Custom_Price(

                    uname = customer,
                    acc = currency.acc,
                    currency = currency,

                    wallet_id = w.pk,
                    amount = amount,

                    fee_amount = fee,
                    fee_price = fee_price,

                    bill_type='sell',

                    unit_price = Unitprice,
                    total_price = totalPrice,
                    desired_price = desired_price,

                    datetime = time,
                    ip = get_ip(request),
                    sell_payment_method = paymentMethod,
                    card_withdrawal_sell = cards,
                    payment_method_withdrawal = payment,

                    process_based_on = process_based_on,
                    amount_type = typeMethod,
                    irt_amount = irt_amount

                )
                trans.save()

                w.desc=f'بابت درخواست فروش با تعیین قیمت به شناسه : {trans.pk}'
                w.save()

                if customer.is_from_pwa == True :
                    add_static_report(request, f'درخواست فروش با قیمت مورد نظر کاربر  {currency.fa_title}', 'success', True, customer.req_user, get_ip(request))   
                else:
                    add_static_report(request, f'درخواست فروش با قیمت مورد نظر کاربر  {currency.fa_title}', 'success')

                if trans.amount_type == 'gram': amount = str(trans.amount)
                else : amount = f"{int(trans.irt_amount):,}"
                
                return JsonResponse(
                    {
                        'type':'success', 
                        'msg':'درخواست فروش شما با قیمت مورد نظر  با موفقیت ثبت شد', 
                        'redirect':'None',
                        'pk':trans.pk,
                        'amount_type':trans.amount_type,
                        'amount':amount,
                        'desired_price':f"{int(trans.desired_price):,}",
                        'ToshamsiDate':str(trans.ToshamsiDate),
                        'status':trans.status,
                        'ToStatusShow':trans.ToStatusShow,
                        'ToTypeShow':trans.ToTypeShow,
                        'bill_type':trans.bill_type,
                        'fund_balance' : get_customer_balance(request.user, currency.symbol)['balance'],
                        'Wallet_balance' : get_customer_balance(request.user, 'IRT')['balance']
                    }
                )

        elif process_based_on == 'datetime':

            if setting.is_timer_sell == False :
                return JsonResponse({'type':'danger', 'msg':'در حال حاضر فروش براساس زمان غیرفعال گردیده'})

            desired_date = request.POST.get('desired_date')
            desired_time = request.POST.get('desired_time')



            if desired_date == "" or desired_date == None or desired_date == "None":
                return JsonResponse({"type": "danger", "msg": "وارد کردن تاریخ الزامی است"})

            if desired_time == "" or desired_time == None or desired_time == "None":
                return JsonResponse({"type": "danger", "msg": "وارد کردن ساعت الزامی است"})

            try:

                sdata = desired_date.split("/")
                newdata = khayyam.JalaliDate(sdata[0], sdata[1], sdata[2]).todate()
                newdata = str(newdata).split("-")

                earlier = (newdata[0] + "-" + newdata[1] + "-" + newdata[2] + f" {desired_time}:00:00")
                desired_datetime = int(datetime.strptime(earlier, "%Y-%m-%d %H:%M:%S").timestamp())


                start_of_day = (newdata[0] + "-" + newdata[1] + "-" + newdata[2] + " 00:00:00")
                start_of_day = int(datetime.strptime(start_of_day, "%Y-%m-%d %H:%M:%S").timestamp())

                end_of_day = (newdata[0] + "-" + newdata[1] + "-" + newdata[2] + " 23:59:59")
                end_of_day = int(datetime.strptime(end_of_day, "%Y-%m-%d %H:%M:%S").timestamp())


                requests_today = Currency_BuySell_Custom_Price.objects.filter(desired_time__gte=start_of_day,desired_time__lte=end_of_day,uname=customer,process_based_on='datetime').exclude(status='Canceled')
                if requests_today.count() >= 3 :
                    return JsonResponse({"type": "danger", "msg":  "تعداد درخواست‌های شما برای این تاریخ به حد مجاز رسیده است. لطفاً تاریخ دیگری را انتخاب نمایید"})
                
                if time > desired_datetime :
                    return JsonResponse({"type": "danger", "msg": "زمان وارد شده نامعتبر است"})

            except:

                return JsonResponse({"type": "danger", "msg": "زمان وارد شده نامعتبر است"})

            Unitprice = float(Currency_List.objects.get(symbol=symbol).BuySellPrice['sell'])

            amount = 0
            if typeMethod == 'gram' :


                try : 

                    amount = round(float(gold_amount), 4)

                    if float(currency.sell_fee) != float(0) :

                        f = ((currency.sell_fee * amount) / 100)
                        if f < currency.sell_fee_lower : fee = currency.sell_fee_lower
                        elif f > currency.sell_fee_upper : fee = currency.sell_fee_upper
                        else : fee = f
                        fee_price = round(fee * Unitprice , 0)

                    else:

                        fee = 0
                        fee_price = 0

                      
                    
                    totalPrice = round((amount * Unitprice) - fee_price) - withdraw_method

                    if amount <= 0 :
                        return JsonResponse({'type':'danger', 'msg':'لطفا میزان فروش خود را به درستی وارد نمایید'})
                except : 
                    return JsonResponse({'type':'danger', 'msg':'لطفا میزان فروش خود را وارد نمایید'})

            if totalPrice - fee_price <= 0 :
                return JsonResponse({'type':'danger', 'msg':'میزان فروش وارد شده نامعتبر است'})

            if amount < currency.lower_amount :
                return JsonResponse({'type':'danger', 'msg':f'حداقل میزان فروش {currency.lower_amount} است'})

            if float(get_customer_balance(request.user, currency.symbol)["balance"]) < amount :
                return JsonResponse({'type':'danger', 'msg':'موجودی کیف پول شما کمتر از میزان فروش است'}) 


            trans = Currency_BuySell_Custom_Price(

                uname = customer,
                acc = currency.acc,
                currency = currency,

                amount = amount,
                bill_type='sell',

                datetime = time,
                ip = get_ip(request),
                sell_payment_method = paymentMethod,
                card_withdrawal_sell = cards,
                payment_method_withdrawal = payment,

                process_based_on = process_based_on,
                amount_type = typeMethod,
                desired_time = desired_datetime,
                irt_amount = irt_amount


            )
            trans.save()

            if customer.is_from_pwa == True :
                add_static_report(request, f'درخواست فروش با زمان مورد نظر کاربر  {currency.fa_title}', 'success', True, customer.req_user, get_ip(request))   
            else:
                add_static_report(request, f'درخواست فروش با زمان مورد نظر کاربر  {currency.fa_title}', 'success')

            if trans.amount_type == 'gram': amount = str(trans.amount)
            else : amount = f"{int(trans.irt_amount):,}"
            
            return JsonResponse(
                {
                    'type':'success',
                      'msg':'درخواست فروش شما با زمان مورد نظر با موفقیت ثبت شد',
                        'redirect':'None',
                        'pk':trans.pk,
                        'amount_type':trans.amount_type,
                        'amount':amount,
                        'datetime':str(trans.ToshamsiDate_desired),
                        'ToshamsiDate':str(trans.ToshamsiDate),
                        'ToStatusShow':trans.ToStatusShow,
                        'status':trans.status,
                        'bill_type':trans.bill_type,
                        'ToTypeShow':trans.ToTypeShow
                }
            )
    
    return JsonResponse({'type':'danger', 'msg':'در درخواست فروش طلا خطایی رخ داده است'})


def customer_gold_buysell_request_cancel(request, pk):

    # customer check start
    try :
        pattern_url = customer_access_check(request)
        if pattern_url[0] != 100 : return redirect(pattern_url[1])
    except: return redirect('account')
    # customer check end

    customer = pattern_url[2]

    if Site_Settings.objects.get(code=1001).is_timer_buysell == False : return JsonResponse({'type':'danger', 'msg':'در حال حاضر خرید و فروش زماندار غیرفعال است'})

    try : cancellation_request = Currency_BuySell_Custom_Price.objects.get(pk=pk,status='Pendding',transaction_id="-")
    except : return JsonResponse({'type':'danger', 'msg':'امکان لغو درخواست موردنظر وجود ندارد'})

    if cancellation_request.bill_type == 'buy' : description = f'لغو درخواست خرید زماندار'
    elif cancellation_request.bill_type == 'sell' : description = f'لغو درخواست فروش زماندار'    

    if Wallet.objects.filter(refund_buysell_request_pk=cancellation_request.pk).count() != 0 :
        return JsonResponse({'type':'danger', 'msg':'امکان لغو درخواست موردنظر وجود ندارد'})
        
    cancellation_request.status = 'Canceled'
    cancellation_request.save()

    if customer.is_from_pwa == True :
        add_static_report(request,f' {description} ',None, True, customer.req_user, get_ip(request))   
    else:
        add_static_report(request,f' {description} ')

    return JsonResponse({'type':'success', 'msg':'عملیات موردنظر شما با موفقیت انجام شد'})

