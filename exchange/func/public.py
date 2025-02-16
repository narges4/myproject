import os
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from customer.models import Customer , Customer_Gold_Order , Customer_Cart_Products
from account.models import *
from exchange.models import *
import random
import string
import time
from django.http import HttpResponse
import pandas as pd
import jdatetime
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from PIL import Image
from django.db.models import F
from django.db.models import Avg, Count, Min, Sum, F, Value, CharField
from currency.models import *
from datetime import datetime, date, timedelta
from wallet.models import *
import urllib

import logging 

def get_ip(r):

    x_forwarded_for = r.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for: ip = x_forwarded_for.split(',')[0]
    else: ip = r.META.get('REMOTE_ADDR')

    ip = urllib.parse.unquote(ip)

    try :

        ip_check = ip.split('.')
        if len(ip_check) != 4 :
            return "-.-.-.-"
        
    except : return "-.-.-.-"
    
    return ip 


def get_date_time() :
    
    now = datetime.now()

    year = now.year
    month = now.month
    day = now.day
    hour = now.hour
    minute = now.minute

    if len(str(day)) == 1 :
        day = "0" + str(day)
    if len(str(month)) == 1 :
        month = "0" + str(month)

    
    if len(str(hour)) == 1 :
        hour = "0" + str(hour)
    if len(str(minute)) == 1 :
        minute = "0" + str(minute)    

    showtime = str(hour) + ":" + str(minute)   
                    
    stoday = shamsiDate(int(year),int(month),int(day))

    today =  (str(year) + "/" + str(month) + "/" + str(day))
    
    return {'shamsi_date':stoday,'time':showtime,'miladi_date':today,'datetime':now, 'timestamp':int(time.time()), 'hour': hour}


def shamsiDate(gyear, gmonth, gday):

    _gl = [0, 31, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335]
    _g = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]

    deydiffjan = 10
    if gLeapYear(gyear - 1):
        deydiffjan = 11
    if gLeapYear(gyear):
        gd = _gl[gmonth - 1] + gday
    else:
        gd = _g[gmonth - 1] + gday

    if gd > 79:
        sy = gyear - 621
        gd = gd - 79
        if gd <= 186:
            gmod = gd % 31
            if gmod == 0:
                sd = 31
                sm = int(gd / 31)
            else:
                sd = gmod
                sm = int(gd / 31) + 1
        else:
            gd = gd - 186
            gmod = gd % 30
            if gmod == 0:
                sd = 30
                sm = int(gd / 30) + 6
            else:
                sd = gmod
                sm = int(gd / 30) + 7
    else:
        sy = gyear - 622
        gd = gd + deydiffjan
        gmod = gd % 30
        if gmod == 0:
            sd = 30
            sm = int(gd / 30) + 9
        else:
            sd = gmod;
            sm = int(gd / 30) + 10

    if len(str(sd)) == 1 :
        p = "0" + str(sd)
    else:
        p = str(sd)

    if len(str(sm)) == 1 :
        n = "0" + str(sm)
    else:
        n = str(sm)

    result = str(sy) + '/' + n + '/' + p
    return result    


def gLeapYear(y):

    if (y % 4 == 0) and ((y % 100 != 0) or (y % 400 == 0)): return True
    else: return False


def miladiDate(jy, jm, jd):

    jy = int(jy)
    jm = int(jm)
    jd = int(jd)

    jy += 1595
    days = -355668 + (365 * jy) + ((jy // 33) * 8) + (((jy % 33) + 3) // 4) + jd
    if (jm < 7):
        days += (jm - 1) * 31
    else:
        days += ((jm - 7) * 30) + 186
    gy = 400 * (days // 146097)
    days %= 146097
    if (days > 36524):
        days -= 1
        gy += 100 * (days // 36524)
        days %= 36524
        if (days >= 365):
            days += 1
    gy += 4 * (days // 1461)
    days %= 1461
    if (days > 365):
        gy += ((days - 1) // 365)
        days = (days - 1) % 365
    gd = days + 1
    if ((gy % 4 == 0 and gy % 100 != 0) or (gy % 400 == 0)):
        kab = 29
    else:
        kab = 28
    sal_a = [0, 31, kab, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    gm = 0
    while (gm < 13 and gd > sal_a[gm]):
        gd -= sal_a[gm]
        gm += 1

    return str(gy) + '/' + str(gm) + '/' + str(gd)


def mobile_check(txt):

    isascii = lambda s: len(s) == len(s.encode())
    if str(isascii(txt)) == 'False' :
        return [False, 'شماره وارد شده صحیح نیست']
    
    if len(txt) != 11 :
        return [False, 'شماره وارد شده صحیح نیست']  

    if not txt.isdigit() :
        return [False, 'شماره وارد شده صحیح نیست']

    if not txt.startswith('0') :
        return [False, 'شماره وارد شده صحیح نیست']

    return [True, '']  


def national_id_check(txt):

    isascii = lambda s: len(s) == len(s.encode())
    if str(isascii(txt)) == 'False' :
        return [False, 'کد ملی را به انگلیسی وارد نمایید']

    if len(txt) != 10 :
        return [False, 'کد ملی وارد شده صحیح نیست']

    if not txt.isdigit() :
       return [False, 'کد ملی وارد شده صحیح نیست']

    if  txt == "1234567891": return [False, 'کد ملی وارد شده صحیح نیست'] 

    x = txt[0]
    c = 0

    for i in txt : 
        if int(i) == int(x) : c += 1

    if c == 10 : return [False, 'کد ملی وارد شده صحیح نیست']

    num = int(txt[9:])

    count = 0
    counter = 1

    for i in txt :

        if counter == 1 : count = count + (int(i) * 10)
        if counter == 2 : count = count + (int(i) * 9)
        if counter == 3 : count = count + (int(i) * 8)
        if counter == 4 : count = count + (int(i) * 7)
        if counter == 5 : count = count + (int(i) * 6)
        if counter == 6 : count = count + (int(i) * 5)
        if counter == 7 : count = count + (int(i) * 4)
        if counter == 8 : count = count + (int(i) * 3)
        if counter == 9 : count = count + (int(i) * 2)
        counter += 1
            
    if count % 11 >= 2 :

        c = 11 - (count % 11)

    else :

        c = (count % 11)

    if c != num : return [False, 'کد ملی وارد شده صحیح نیست']

    return [True, '']   



def code_generator(rng):

    secret_key = settings.SUB_KEY

    now = int(time.time())
    delta = random.randint(1000000,9999999)
    num = totp(key=secret_key, step=10, digits=rng, t0=(now-delta))

    while int(len(str(num))) != int(rng) :

        now = int(time.time())
        delta = random.randint(1000000,9999999)
        num = totp(key=secret_key, step=10, digits=rng, t0=(now-delta))
    
    return num


def pass_generator(rng):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(rng))


def passwordValidator(text):

    counter = 0

    if len(text) >= 8:
        for i in text:
            if i in string.ascii_lowercase:
                counter += 1
                break
        for i in text:
            if i in string.ascii_uppercase:
                counter += 1
                break
        for i in text:
            if i in string.digits:
                counter += 1
                break
        for i in text:
            if i in string.punctuation:
                counter += 1
                break
                
    return counter


def upload_file(myfile,loc, is_webp=True):

    bucket_name = settings.MEDIA_BUCKET_NAME

    dir = f"{settings.BASE_DIR}/{loc}"
    if not os.path.exists(dir):
        os.makedirs(dir)
    fs = FileSystemStorage(location=dir)

    x = myfile.name.find('.')
    tt = ''.join(random.choice(string.ascii_letters) for x in range(8))
    
    myname = tt + myfile.name[x:] if loc != 'icon' else f'favicon{myfile.name[x:]}'

    filename = fs.save(myname, myfile)
    url = "/" + loc + "/" + filename
    
    if not str(myfile.content_type).startswith("image"):

        fs = FileSystemStorage(location=dir)
        fs.delete(filename)
        error = "فایل انتخابی تصویر نیست"
        return [False,error]

    if myfile.size > 10000000 :
                
        fs = FileSystemStorage(location=dir)
        fs.delete(filename)
        error = "حجم تصویر بیشتر از 10 مگابایت است"
        return [False,error]

    if not myfile.content_type in ['image/png', 'image/jpg', 'image/jpeg'] :

        fs = FileSystemStorage(location=dir)
        fs.delete(filename)
        error = "فایل انتخابی تصویر نیست"
        return [False,error]

    try :

        image = Image.open(f"{dir}/{filename}")
        verify_img = image.verify()
        
        if not verify_img in [None, True] :

            fs = FileSystemStorage(location=dir)
            fs.delete(filename)
            error = "فایل انتخابی تصویر نیست"
            return [False,error]

    except Exception as e:
        fs = FileSystemStorage(location=dir)
        fs.delete(filename)
        error = "فایل انتخابی تصویر نیست"
        return [False,error]

    
    if is_webp == True :

        try :

            image = Image.open(f"{dir}/{filename}")
            image = image.convert('RGB')
            image.save(dir + '/' + tt + '.webp', format="webp")

            fs = FileSystemStorage(location=dir)
            fs.delete(filename)

            P_url = "/" + loc + '/' + tt + '.webp'
            P_filename = tt + '.webp'

            return [True,P_url,P_filename]

        except : 

            error = "در آپلود فایل خطایی رخ داده لطفا مجددا تلاش نمایید"
            return [False,error]

    else : 
        

        return [True,url,filename]


def app_image_check(name, loc):

    # fs = FileSystemStorage(location=loc)
    url = "/" + loc + "/" + name

    try :

        image = Image.open(url[1:])
        verify_img = image.verify()
        
        if not verify_img in [None, True] :

            fs = FileSystemStorage(location=loc)
            fs.delete(name)
            return False

    except :

        fs = FileSystemStorage(location=loc)
        fs.delete(name)
        return False

    return True

def datetime_converter(value):
    return str(jdatetime.datetime.fromtimestamp(int(value)))


def add_static_report(req, desc, status=None, is_app=None, uname=None, ip='0.0.0.0'):
    
    if is_app == None : is_app = False
    if status == None : status = "primary"
    if ip_check(ip) == False : ip = "-.-.-.-"
 
    if Customer.objects.filter(req_user=req.user).count() == 1:
        Site_Static_log(uname=Customer.objects.get(req_user=req.user),desc=desc, status=status, date=get_date_time()['timestamp'], ip=get_ip(req), is_app=is_app).save()
        
    elif Master.objects.filter(req_user=req.user).count() == 1:
        Site_Static_log(master = Master.objects.get(req_user=req.user),desc=desc, status=status, date=get_date_time()['timestamp'], ip=get_ip(req), is_app=is_app).save()
        
    if is_app == True and Customer.objects.get(req_user=uname).is_from_pwa == False:

        if uname.startswith('customer-'):
            Site_Static_log(uname=Customer.objects.get(req_user=uname),desc=desc, status=status, date=get_date_time()['timestamp'], ip=ip, is_app=is_app).save()
        else :  
            Site_Static_log(uname=Customer.objects.get(req_user=uname),desc=desc, status=status, date=get_date_time()['timestamp'], ip=ip, is_reseller=True).save()
            
    return True



def CustomerDailyCeilingRemain(customer):

    daily = get_date_time()['timestamp']

    # ToDo
    ceiling = Customer_Ceiling.objects.get(code=1001)
    buy =  (ceiling.purchase_ceiling + customer.buy) 
    sell =  (ceiling.sales_ceiling + customer.sell) 
    trade = (ceiling.conversion_ceiling + customer.trade)
    transfer = (ceiling.transmission_ceiling + customer.transfer)   
    increase  =  (ceiling.increase_ceiling)     

    return {"buy":buy,"sell":sell,"trade":trade,"transfer":transfer,"increase":increase}    



def order_info(pk):

    order = Customer_Gold_Order.objects.get(pk=pk)
    cart_products = Customer_Cart_Products.objects.filter(order=order)

    total_grams = cart_products.aggregate(total_grams=Sum(F('quantity') * F('product__grams')))['total_grams'] or 0
    total_grams_saved = cart_products.aggregate(total_grams=Sum(F('quantity') * F('grams')))['total_grams'] or 0

    # مجموع اجرت پرداختی 
    total_wages = cart_products.aggregate(total_wages=Sum(F('quantity') * F('product__wages')))['total_wages'] or 0
    total_fee = cart_products.aggregate(total_fee=Sum(F('quantity') * F('product__fee')))['total_fee'] or 0
    total_fee_saved = cart_products.aggregate(total_fee=Sum(F('quantity') * F('fee')))['total_fee'] or 0
    total_wages_saved = cart_products.aggregate(total_wages=Sum(F('quantity') * F('wages')))['total_wages'] or 0

    gold_dict = dict(GOLDS) 
    categories_str = ', '.join(list(map(lambda x: gold_dict.get(x, 'نامشخص'), list(cart_products.values_list('product__type_gold', flat=True).distinct()) )))

    total_products = cart_products.aggregate(total_quantity=Sum('quantity'))['total_quantity']
    total_products = total_products or 0

    #start information melted
    melted = Customer_Cart_Products.objects.filter(order=order,is_gold_melt=True)
    weight_melted = melted.aggregate(total_grams=Sum(F('quantity') * F('product__grams')))['total_grams'] or 0
    weight_melted_saved = melted.aggregate(total_grams=Sum(F('quantity') * F('grams')))['total_grams'] or 0
    count_melted = melted.aggregate(total_quantity=Sum('quantity'))['total_quantity']
    count_melted = count_melted or 0
    #end information melted

    #start information coin
    coins = Customer_Cart_Products.objects.filter(order=order,product__type_gold="gold2")
    # وزن سکه های دریافتی 
    Weight_coins = coins.aggregate(total_grams=Sum(F('quantity') * F('product__grams')))['total_grams'] or 0
    Weight_coins_saved = coins.aggregate(total_grams=Sum(F('quantity') * F('grams')))['total_grams'] or 0
    # تعداد سکه های دریافتی 
    count_coins = coins.aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
    count_coins = count_coins or 0
    # مجموع اجرت سکه
    wages_coins = coins.aggregate(total_wages=Sum(F('quantity') * F('product__wages')))['total_wages'] or 0
    #end information coin

    #start information ingots
    ingots = Customer_Cart_Products.objects.filter(order=order,product__type_gold="gold3")
    #وزن شمش های دریافتی 
    Weight_ingots = ingots.aggregate(total_grams=Sum(F('quantity') * F('product__grams')))['total_grams'] or 0
    Weight_ingots_saved = ingots.aggregate(total_grams=Sum(F('quantity') * F('grams')))['total_grams'] or 0
    #تعداد شمش های دریافتی 
    count_ingots = ingots.aggregate(total_quantity=Sum('quantity'))['total_quantity']
    count_ingots = count_ingots or 0
    # مجموع اجرت شمش
    wages_ingots = ingots.aggregate(total_wages=Sum(F('quantity') * F('product__wages')))['total_wages'] or 0
    #end information ingots


    gold_price = Currency_List.objects.get(symbol='XAU18').BuySellPrice['buy']
    wages_coins_toman = 0
    wages_ingots_toman = 0

    for product in cart_products:

        product_weight = product.product.grams if product.product.grams is not None else 0
        product_wages = product.product.wages if product.product.wages is not None else 0

        product_price_in_toman = product_weight * gold_price
        wages_in_toman = (product_wages * product_price_in_toman) / 100
        wages_in_toman = product.quantity * wages_in_toman
 

        if product.product.type_gold == "gold2":
            wages_coins_toman += wages_in_toman
        elif product.product.type_gold == "gold3":
            wages_ingots_toman += wages_in_toman

    total_wages_toman = round(wages_coins_toman) + round(wages_ingots_toman)


    return {"total_grams":total_grams,'titles':categories_str,'total_products':total_products,'weight_melted':weight_melted,'Weight_coins':Weight_coins,'Weight_ingots':Weight_ingots,'count_melted':count_melted,'count_coins':count_coins,'count_ingots':count_ingots,'wages_coins':wages_coins,'wages_ingots':wages_ingots,'total_wages':total_wages,'total_fee':total_fee,'wages_coins_toman':round(wages_coins_toman),'count_ingots_toman':round(wages_ingots_toman),'total_wages_toman':total_wages_toman,'total_grams_saved':total_grams_saved,'Weight_coins_saved':Weight_coins_saved,'Weight_ingots_saved':Weight_ingots_saved,'weight_melted_saved':weight_melted_saved,'total_fee_saved':total_fee_saved,'total_wages_saved':total_wages_saved}
    


def upload_audio(myfile, loc):

    dir = f"{settings.BASE_DIR}/{loc}"
    if not os.path.exists(dir):
        os.makedirs(dir)

    fs = FileSystemStorage(location=dir)

    ext = os.path.splitext(myfile.name)[1] 
    tt = ''.join(random.choice(string.ascii_letters) for _ in range(8))
    filename = tt + ext

    if myfile.content_type not in ['audio/mpeg', 'audio/wav', 'audio/mp3']:
        return [False, "فرمت فایل صوتی معتبر نیست"]

    max_audio_size = 30 * 1024 * 1024  # 30 مگابایت
    if myfile.size > max_audio_size:
        return [False, "حجم فایل صوتی باید کمتر از 30 مگابایت باشد"]

    try:
        saved_filename = fs.save(filename, myfile)
        audio_path = fs.path(saved_filename)

        audio = MP3(audio_path)
        duration = audio.info.length
        time_formatted = f"{int(duration // 60)}:{int(duration % 60):02d}"

        url = f"{settings.PODCAST_URL}{saved_filename}"

        return [True, url, saved_filename, time_formatted]

    except :
        return [False, "در آپلود فایل صوتی خطایی وجود دارد"]
    



def custom_float_format(value, decimal_places=4):

    try:
        formatted_number = ('{:.{dp}f}'.format(float(value), dp=decimal_places)).rstrip('0').rstrip('.')
        return formatted_number
    except (ValueError, TypeError):
        return value

def none_round_custom_float_format(value, decimal_places=4):

    try:
        value_str = str(value)
        if '.' in value_str:
            integer_part, decimal_part = value_str.split('.')
            formatted_number = f"{integer_part}.{decimal_part[:decimal_places]}"
            return formatted_number.rstrip('0').rstrip('.')
        return value_str
    except (ValueError, TypeError):
        return value
    

def paginate(request, queryset, per_page=10):
    page = request.GET.get("page")  
    paginator = Paginator(queryset, per_page)
    try: 
        return paginator.page(page)
    except (PageNotAnInteger, EmptyPage): 
        return paginator.page(1)
    


def convert_irt_xau18(irt_amount,gold,Unitprice):

    currency = Currency_List.objects.get(symbol=gold)

    gram = irt_amount / Unitprice

    p = 1 + (currency.buy_fee / 100)

    amount_grm = gram / p
    f = (currency.buy_fee * amount_grm) / 100

    if f < currency.buy_fee_lower : fee = currency.buy_fee_lower
    elif f > currency.buy_fee_upper : fee = currency.buy_fee_upper
    else : fee = f

    amount_grm = gram - fee

    maintenance_cost = amount_grm * currency.maintenance_cost

    return {"fee":fee , "pure_amount":round(amount_grm , 4), 'unit_price':Unitprice ,"fee_price":round(fee * Unitprice , 0),'maintenance_cost':int(maintenance_cost)}


def convert_sell_irt_xau18(irt_amount,gold,Unitprice):

    currency = Currency_List.objects.get(symbol=gold)

    gram = irt_amount / Unitprice

    p = 1 - (currency.sell_fee / 100)

    amount_grm = gram / p
    f = (currency.sell_fee * amount_grm) / 100

    if f < currency.sell_fee_lower : fee = currency.sell_fee_lower
    elif f > currency.sell_fee_upper : fee = currency.sell_fee_upper
    else : fee = f

    amount_grm = gram + fee


    return {"fee":fee , "pure_amount":amount_grm , 'unit_price':Unitprice ,"fee_price": fee  * Unitprice}


def calculate_lower_amount_irt(u_price):

    currency = Currency_List.objects.get(symbol='XAU18')
    lower_amount = currency.lower_amount

    if float(currency.buy_fee) != float(0) :

        f = ((currency.buy_fee * lower_amount) / 100)
        if f < currency.buy_fee_lower : fee = currency.buy_fee_lower
        elif f > currency.buy_fee_upper : fee = currency.buy_fee_upper
        else : fee = f
        fee_price = round(fee * u_price, 0)

    else:

        fee = 0
        fee_price = 0 

    
    return round((lower_amount * u_price) + int(lower_amount * currency.maintenance_cost) + (fee * u_price ))

