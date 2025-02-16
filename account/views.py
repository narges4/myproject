

from django.shortcuts import render, get_object_or_404, redirect
from django.core.files.storage import FileSystemStorage
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User , Group , Permission
from django.http import HttpResponse, JsonResponse
from account.defaultclass.utopia import Utopia_APi
from master.func.access import *
from exchange.func.public import *
from currency.models import *
from exchange.func.theme import *
import time
from .models import *
from master.models import *
from exchange.models import *
from exchange.func.hash import *
import datetime
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from itertools import chain
from currency.func.public import *
import khayyam
from account.defaultclass.kucoin import *




def master_currency_list(request):
    
    # master check start
    try :
        code = master_access_check(request)
        if code[0] != 100 : return redirect(code[1])
    except: return redirect('master_login')
    # master check end

    
    paginator = Paginator(Currency_List.objects.filter(master_show=True).order_by("sort"),10)
    page = request.GET.get('page')

    try:
        querySet = paginator.page(page)
    except PageNotAnInteger:
        querySet = paginator.page(1)
    except EmptyPage:
        querySet = paginator.page(1) 

    return render(request, get_master_theme() + 'currency_list.html', {'querySet':querySet})


def master_currency_search(request):

    currencies = []
    txt = "-"

    if request.method == 'POST':
        
        txt = request.POST.get('txt')

        request.session['search'] = txt

        currency1 = Currency_List.objects.filter(acc__contains=txt)
        currency2 = Currency_List.objects.filter(symbol__contains=txt)
        currency3 = Currency_List.objects.filter(fa_title__contains=txt)
        currency4 = Currency_List.objects.filter(en_title__contains=txt)
        currency5 = Currency_List.objects.filter(about_txt__contains=txt)
        currency6 = Currency_List.objects.filter(buy_extera_price__contains=txt)
        currency7 = Currency_List.objects.filter(sell_extera_price__contains=txt)
        currency8 = Currency_List.objects.filter(buy_lower_price__contains=txt)
        currency9 = Currency_List.objects.filter(sell_upper_price__contains=txt)
        currency10 = Currency_List.objects.filter(pk__contains=txt)

        currencies = list(chain(currency1,currency2,currency3,currency4,currency5,currency6,currency7,currency8,currency9,currency10))

        paginator = Paginator(list(dict.fromkeys(currencies)),10)
        page = request.GET.get('page')

        try:
            querySet = paginator.page(page)
        except PageNotAnInteger:
            querySet = paginator.page(1)
        except EmptyPage:
            querySet = paginator.page(1) 

    else:

        txt = request.session['search']
       
        currency1 = Currency_List.objects.filter(acc__contains=txt)
        currency2 = Currency_List.objects.filter(symbol__contains=txt)
        currency3 = Currency_List.objects.filter(fa_title__contains=txt)
        currency4 = Currency_List.objects.filter(en_title__contains=txt)
        currency5 = Currency_List.objects.filter(about_txt__contains=txt)
        currency6 = Currency_List.objects.filter(buy_extera_price__contains=txt)
        currency7 = Currency_List.objects.filter(sell_extera_price__contains=txt)
        currency8 = Currency_List.objects.filter(buy_lower_price__contains=txt)
        currency9 = Currency_List.objects.filter(sell_upper_price__contains=txt)
        currency10 = Currency_List.objects.filter(pk__contains=txt)

        currencies = list(chain(currency1,currency2,currency3,currency4,currency5,currency6,currency7,currency8,currency9,currency10))

        paginator = Paginator(list(dict.fromkeys(currencies)),10)
        page = request.GET.get('page')

        try:
            querySet = paginator.page(page)
        except PageNotAnInteger:
            querySet = paginator.page(1)
        except EmptyPage:
            querySet = paginator.page(1)    

    return render(request, get_master_theme() + 'currency_list.html', {'querySet':querySet})


def master_currency_guide(request,pk):

    # master json check start
    try : 
        code=master_access_check(request)
        if code[0] != 100 : return JsonResponse({'type':'danger', 'msg':code[2]})
    except: return JsonResponse({'type':'danger', 'msg':'ورود شما منقضی شده لطفا مجددا وارد شوید'})
    # master json check end

    if request.method == 'POST':

        rules_buy = request.POST.get('rules_buy')
        rules_sale = request.POST.get('rules_sale')
        rules_transfer = request.POST.get('rules_transfer')
        rules_trade = request.POST.get('rules_trade')
        rules_deposit = request.POST.get('rules_deposit')
        rules_harvest = request.POST.get('rules_harvest')
        rules_airdrop = request.POST.get('rules_airdrop')
        rules_reservation = request.POST.get('rules_reservation')
        rules_buy_title = request.POST.get('rules_buy_title')
        rules_transfer_title = request.POST.get('rules_transfer_title')
        rules_sell_title = request.POST.get('rules_sell_title')
        
        if rules_buy == "" or rules_sale == "" or rules_transfer == "" or rules_trade == "" or rules_deposit == "" or rules_harvest == "" or rules_airdrop == "" or  rules_reservation == "" or rules_buy_title == "" or  rules_sell_title == "":
            return JsonResponse({'type':'danger', 'msg':'لطفا تمامی قوانین را وارد نمایید'})

        sett = Currency_List.objects.get(pk=pk)

        try :
            uploader = upload_file(request.FILES['picture1'],'media',False)
            if uploader[0] != True : return JsonResponse({'type':'danger', 'msg':uploader[1]})

            fs = FileSystemStorage(location='media')  
            fs.delete(sett.rules_buy_pic)
            sett.rules_buy_pic = uploader[2]
        except : pass

        try :
            uploader = upload_file(request.FILES['picture2'],'media',False)
            if uploader[0] != True : return JsonResponse({'type':'danger', 'msg':uploader[1]})

            fs = FileSystemStorage(location='media')  
            fs.delete(sett.rules_sell_pic)
            sett.rules_sell_pic = uploader[2]
        except : pass

        sett.rules_buy = rules_buy
        sett.rules_sale = rules_sale
        sett.rules_transfer = rules_transfer
        sett.rules_trade = rules_trade
        sett.rules_deposit = rules_deposit
        sett.rules_reservation = rules_reservation
        sett.rules_harvest = rules_harvest
        sett.rules_buy_title = rules_buy_title
        sett.rules_transfer_title = rules_transfer_title
        sett.rules_sell_title = rules_sell_title
        sett.rules_buy_pic = sett.rules_buy_pic
        sett.rules_sell_pic = sett.rules_sell_pic
        sett.save()

        add_static_report(request, 'ویرایش اطلاعات قوانین طلا')
        
        return JsonResponse({'type':'success', 'msg':'اطلاعات با موفقیت ثبت شد'})

    return JsonResponse({'type':'danger', 'msg':'پردازش مورد نظر با مشکل مواجه شده است'})

 
def master_currency_about(request,pk):

    # master json check start
    try : 
        code=master_access_check(request)
        if code[0] != 100 : return JsonResponse({'type':'danger', 'msg':code[2]})
    except: return JsonResponse({'type':'danger', 'msg':'ورود شما منقضی شده لطفا مجددا وارد شوید'})
    # master json check end

    if request.method == 'POST':

        fa_title = request.POST.get('fa_title')
        en_title = request.POST.get('en_title')
        about_txt = request.POST.get('about_txt')

        if fa_title == "" or en_title == "" or about_txt == "" :
            return JsonResponse({'type':'danger', 'msg':'لطفا تمامی موارد را وارد نمایید'})

        sett = Currency_List.objects.get(pk=pk)
        try :
            uploader = upload_file(request.FILES['logo'],'media',False)
            if uploader[0] != True : return JsonResponse({'type':'danger', 'msg':uploader[1]})

            fs = FileSystemStorage(location='media')  
            fs.delete(sett.logo_name)
            sett.logo_name = uploader[2]
            
        except : pass

        sett.fa_title = fa_title
        sett.en_title = en_title
        sett.about_txt = about_txt
        sett.logo_name = sett.logo_name
        sett.save()

        add_static_report(request, 'ویرایش درباره طلا')
        
        return JsonResponse({'type':'success', 'msg':'اطلاعات با موفقیت ثبت شد','picture': '/media/' + sett.logo_name})

    return JsonResponse({'type':'danger', 'msg':'پردازش مورد نظر با مشکل مواجه شده است'})

def master_currency_pricing(request,pk):

    # master json check start
    try : 
        code=master_access_check(request)
        if code[0] != 100 : return JsonResponse({'type':'danger', 'msg':code[2]})
    except: return JsonResponse({'type':'danger', 'msg':'ورود شما منقضی شده لطفا مجددا وارد شوید'})
    # master json check end

    if request.method == 'POST':

        buy_extera_price = request.POST.get('buy_extera_price')
        sell_extera_price = request.POST.get('sell_extera_price')
        buy_lower_price = request.POST.get('buy_lower_price')
        sell_upper_price = request.POST.get('sell_upper_price')
        lower_amount = request.POST.get('lower_amount')
        buy_fee = request.POST.get('buy_fee')
        buy_fee_lower = request.POST.get('buy_fee_lower')
        buy_fee_upper = request.POST.get('buy_fee_upper')
        sell_fee = request.POST.get('sell_fee')
        sell_fee_lower = request.POST.get('sell_fee_lower')
        sell_fee_upper = request.POST.get('sell_fee_upper')
        transfer_fee = request.POST.get('transfer_fee')
        acc_fee = request.POST.get('acc_fee')
        profit_percent = request.POST.get('profit_percent')
        profit_percent_sell = request.POST.get('profit_percent_sell')
        max_buy_user = request.POST.get('max_buy_user')
        quick_ceiling = request.POST.get('quick_ceiling')
        


        present_mcm_buy = request.POST.get('present_mcm_buy')
        present_mcm_sell = request.POST.get('present_mcm_sell')
        maintenance_cost = request.POST.get('maintenance_cost')

        buy_extera_price = buy_extera_price.replace(',','')
        sell_extera_price = sell_extera_price.replace(',','')
        buy_lower_price = buy_lower_price.replace(',','')
        sell_upper_price = sell_upper_price.replace(',','')
        lower_amount = lower_amount.replace(',','')
        buy_fee = buy_fee.replace(',','')
        buy_fee_lower = buy_fee_lower.replace(',','')
        buy_fee_upper = buy_fee_upper.replace(',','')
        sell_fee = sell_fee.replace(',','')
        sell_fee_lower = sell_fee_lower.replace(',','')
        sell_fee_upper = sell_fee_upper.replace(',','')
        acc_fee = acc_fee.replace(',','')
        profit_percent = profit_percent.replace(',','')
        profit_percent_sell = profit_percent_sell.replace(',','')

        present_mcm_buy = present_mcm_buy.replace(',','')
        present_mcm_sell = present_mcm_sell.replace(',','')
        max_buy_user = max_buy_user.replace(',','')
        maintenance_cost = maintenance_cost.replace(',','')
        quick_ceiling = quick_ceiling.replace(',','')
 
        if buy_extera_price == "" or sell_extera_price == "" or buy_lower_price == "" or sell_upper_price == "" or lower_amount == "" or buy_fee == "" or acc_fee == "" or profit_percent == "" or buy_fee_lower == "" or buy_fee_upper == "" or sell_fee == "" or sell_fee_lower == "" or sell_fee_upper == "" or profit_percent_sell == "" or maintenance_cost == ""  or quick_ceiling == "":
            return JsonResponse({'type':'danger', 'msg':'لطفا تمامی موارد را وارد نمایید'})

        try: 
            
            buy_extera_price = int(buy_extera_price)
            sell_extera_price = int(sell_extera_price)
            buy_lower_price = int(buy_lower_price)
            sell_upper_price = int(sell_upper_price)
            lower_amount = float(lower_amount)
            buy_fee = float(buy_fee)
            buy_fee_lower = float(buy_fee_lower)
            buy_fee_upper = float(buy_fee_upper)
            sell_fee = float(sell_fee)
            sell_fee_lower = float(sell_fee_lower)
            sell_fee_upper = float(sell_fee_upper)
            acc_fee = float(acc_fee)
            profit_percent = float(profit_percent)
            profit_percent_sell = float(profit_percent_sell)

            present_mcm_buy = float(present_mcm_buy)
            present_mcm_sell = float(present_mcm_sell)
            max_buy_user = float(max_buy_user)
            maintenance_cost = float(maintenance_cost)
            quick_ceiling = float(quick_ceiling)

        except : return JsonResponse({'type':'danger', 'msg':'لطفا مبالغ را به صورت عددی وارد نمایید'})

        if buy_fee < 0 or buy_fee > 100 or sell_fee < 0 or sell_fee > 100 :
            return JsonResponse({'type':'danger', 'msg':'لطفا درصد کارمزدها را به درستی وارد نمایید'})
        
        if buy_fee_lower < 0 or sell_fee_lower < 0 :
            return JsonResponse({'type':'danger', 'msg':'حداقل میزان کارمزدها نمیتواند کمتر از صفر باشد'})

        if maintenance_cost < 0 :
            return JsonResponse({'type':'danger', 'msg':'هزینه نگهداری نمیتواند کمتر از صفر باشد'})

        if quick_ceiling < 0:
            return JsonResponse({'type':'danger', 'msg':'سقف مقدار پکیج خرید سریع نمیتواند کمتر از صفر باشد'})
        
        sett = Currency_List.objects.get(pk=pk)
        sett.buy_extera_price = buy_extera_price
        sett.sell_extera_price = sell_extera_price
        sett.buy_lower_price = buy_lower_price
        sett.sell_upper_price = sell_upper_price
        sett.lower_amount = lower_amount
        sett.buy_fee = buy_fee
        sett.buy_fee_lower = buy_fee_lower
        sett.buy_fee_upper = buy_fee_upper
        sett.sell_fee = sell_fee
        sett.sell_fee_lower = sell_fee_lower
        sett.sell_fee_upper = sell_fee_upper
        sett.transfer_fee = transfer_fee
        sett.acc_fee = acc_fee
        sett.profit_percent = profit_percent
        sett.profit_percent_sell = profit_percent_sell

        sett.present_mcm_buy = present_mcm_buy
        sett.present_mcm_sell = present_mcm_sell
        sett.max_buy_user = max_buy_user
        sett.maintenance_cost = maintenance_cost
        sett.quick_purchase_packages_ceiling = quick_ceiling
        sett.save()

        add_static_report(request, 'ویرایش قیمت گذاری طلا')
        
        return JsonResponse({'type':'success', 'msg':'اطلاعات با موفقیت ثبت شد', 'buy_extera_price':f'{buy_extera_price:,}','sell_extera_price':f'{sell_extera_price:,}', 'buy_lower_price':f'{buy_lower_price:,}','sell_upper_price':f'{sell_upper_price:,}'})

    return JsonResponse({'type':'danger', 'msg':'پردازش مورد نظر با مشکل مواجه شده است'})

def master_currency_access(request,pk):

    # master json check start
    try : 
        code=master_access_check(request)
        if code[0] != 100 : return JsonResponse({'type':'danger', 'msg':code[2]})
    except: return JsonResponse({'type':'danger', 'msg':'ورود شما منقضی شده لطفا مجددا وارد شوید'})
    # master json check end
    
    if request.method == 'POST' :
        
        is_buy = request.POST.get('is_buy')
        is_sell = request.POST.get('is_sell')
        is_trade_to = request.POST.get('is_trade_to')
        is_trade_from = request.POST.get('is_trade_from')
        is_transfer = request.POST.get('is_transfer')
        is_price_update = request.POST.get('is_price_update')
        is_papular = request.POST.get('is_papular')
        is_deposite = request.POST.get('is_deposite')
        is_withdraw = request.POST.get('is_withdraw')
        bazar = request.POST.get('bazar')
        currency_gateway = request.POST.get('currency_gateway')
        reservation = request.POST.get('reservation')
        is_first_page = request.POST.get('is_first_page')

        b = Currency_List.objects.get(pk=pk)

        if is_buy == 'on' :
            if b.symbol == 'HotV' : return JsonResponse({'type':'danger', 'msg':' فعال کردن خرید از کاربر امکانپذیر نیست'})
            b.is_buy = True
        else :
            b.is_buy = False

        if is_sell == 'on' :
            b.is_sell = True
        else :
            b.is_sell = False

        if is_trade_to == 'on' :
            b.is_trade_to = True
        else :
            b.is_trade_to = False

        if is_trade_from == 'on' :
            b.is_trade_from = True
        else :
            b.is_trade_from = False

        if is_transfer == 'on' :
            b.is_transfer = True
        else :
            b.is_transfer = False

        if is_price_update == 'on' :
            if b.symbol == 'HotV' : return JsonResponse({'type':'danger', 'msg':' فعال کردن بروزرسانی قیمت امکانپذیر نیست'})
            b.is_price_update = True
        else :
            b.is_price_update = False

        if is_papular == 'on' :
            b.is_papular = True
        else :
            b.is_papular = False

        if is_deposite == 'on' :

            if b.symbol == "MCR" :
                return JsonResponse({'type':'danger', 'msg':'امکان فعال کردن واریز طلا یاقوت وجود ندارد'})
            b.is_deposite = True
             
        else :
            b.is_deposite = False

        if is_withdraw == 'on' :

            if b.symbol == "MCR" :
                return JsonResponse({'type':'danger', 'msg':'امکان فعال کردن برداشت طلا یاقوت وجود ندارد'})
            b.is_withdraw =  True
            
        else :
            b.is_withdraw = False

        if bazar == 'on' :
            b.classic_market = True
        else :
            b.classic_market = False    
            
            
        if currency_gateway == 'on' :
            if b.symbol == 'HotV' : return JsonResponse({'type':'danger', 'msg':' فعال کردن درگاه ارزی امکانپذیر نیست'})
            b.is_currency_gateway = True
        else :
            b.is_currency_gateway = False        
            
        if is_first_page == 'on' :
            b.is_first_page = True
        else :
            b.is_first_page = False

        if reservation == 'on' :
            b.reservation = True
        else :
            b.reservation = False            

        b.save()

        add_static_report(request, 'ویرایش دسترسی طلا')
        return JsonResponse({'type':'success', 'msg':'اطلاعات با موفقیت ثبت شد'})

    return JsonResponse({'type':'danger', 'msg':'پردازش مورد نظر با مشکل مواجه شده است'})



def master_account_handly(request):
    
    # master check start
    try :
        code = master_access_check(request)
        if code[0] != 100 : return redirect(code[1])
    except: return redirect('master_login')
    # master check end


    handly_symbol = Currency_List.objects.filter(acc='handly')

    return render(request, get_master_theme() + 'account_handly.html', {'handly_symbol':handly_symbol})



def master_account_handly_price_submit(request):

    # master json check start
    try : 
        code=master_access_check(request)
        if code[0] != 100 : return JsonResponse({'type':'danger', 'msg':code[2]})
    except: return JsonResponse({'type':'danger', 'msg':'ورود شما منقضی شده لطفا مجددا وارد شوید'})
    # master json check end
    
    if request.method == 'POST' :

        symbol = request.POST.get('symbol')
        buy = request.POST.get('buy')
        sell = request.POST.get('sell')

        buy = buy.replace(',','')
        sell = sell.replace(',','')

        if symbol == "select" :
            return JsonResponse({'type':'danger', 'msg':'لطفا طلا خود را انتخاب نمایید'})

        if buy == "" or sell == "" :
            return JsonResponse({'type':'danger', 'msg':'لطفا قیمت های مورد نظر را وارد نمایید'})

        try : buy = int(buy)
        except : return JsonResponse({'type':'danger', 'msg':'لطفا قیمت خرید را به درستی وارد نمایید'})

        try : sell = int(sell)
        except : return JsonResponse({'type':'danger', 'msg':'لطفا قیمت فروش را به درستی وارد نمایید'})

        handly = Currency_List.objects.get(acc='handly', symbol=symbol)

        if handly.buy_lower_price > buy :
            return JsonResponse({'type':'danger', 'msg':f'قیمت فروش نمیتواند کمتر از {handly.buy_lower_price:,} تومان باشد'})

        if handly.sell_upper_price < sell :
            return JsonResponse({'type':'danger', 'msg':f'قیمت خرید نمیتواند بیشتر از {handly.sell_upper_price:,} تومان باشد'})

        date = get_date_time()['timestamp']
        Account_Price_log(acc='handly', symbol=symbol, modify=request.user, date=date, buy=buy, sell=sell).save()

        manager = code[3].nick_name
        
        add_static_report(request, 'بروزرسانی قیمت طلا ' + handly.symbol)
        return JsonResponse({'type':'success', 'msg':'قیمت طلا با موفقیت بروز شد', 'modify':str(manager), 'buy':f'{sell:,}','sell':f'{buy:,}','date':datetime_converter(date)})


    return JsonResponse({'type':'danger', 'msg':'پردازش مورد نظر با مشکل مواجه شده است'})


def master_account_handly_balance_submit(request):

    # master json check start
    try : 
        code=master_access_check(request)
        if code[0] != 100 : return JsonResponse({'type':'danger', 'msg':code[2]})
    except: return JsonResponse({'type':'danger', 'msg':'ورود شما منقضی شده لطفا مجددا وارد شوید'})
    # master json check end
    
    if request.method == 'POST' :

        symbol = request.POST.get('symbol')
        amount = request.POST.get('amount')

        if symbol == "select" :
            return JsonResponse({'type':'danger', 'msg':'لطفا طلا خود را انتخاب نمایید'})

        if amount == "" :
            return JsonResponse({'type':'danger', 'msg':'لطفا میزان موجودی خود را وارد نمایید'})

        try : amount = float(amount)
        except : return JsonResponse({'type':'danger', 'msg':'لطفا قیمت خرید را به درستی وارد نمایید'})

        reserved = get_asset_wallet_reserved(symbol)['reserved'] + get_asset_bill_reserved(symbol)['pendding']

        if amount < float(reserved) :
            return JsonResponse({'type':'danger', 'msg':f'حداقل میزان موجودی فعال {reserved} است'})

        date = get_date_time()['timestamp']
        Account_Balance_log(acc='handly', symbol=symbol, modify=request.user, date=date, active_balance=amount).save()

        manager = code[3].nick_name
        
        add_static_report(request, 'بروزرسانی موجودی طلا ' + symbol)
        return JsonResponse({'type':'success', 'msg':'موجودی طلا با موفقیت بروز شد', 'modify':str(manager),'amount':amount,'date':datetime_converter(date)})


    return JsonResponse({'type':'danger', 'msg':'پردازش مورد نظر با مشکل مواجه شده است'})


def master_balance_report(request):

    # master check start
    try :
        code = master_access_check(request)
        if code[0] != 100 : return redirect(code[1])
    except: return redirect('master_login')
    # master check end


    paginator = Paginator(Log_Balance_check.objects.all().order_by('-pk'),10)
    page = request.GET.get('page')

    try:
        querySet = paginator.page(page)
    except PageNotAnInteger:
        querySet = paginator.page(1)
    except EmptyPage:
        querySet = paginator.page(1) 

    return render(request, get_master_theme() + 'balance_report.html', {'querySet':querySet})




def master_direct_wallet_submit(request):

    # master json check start
    try : 
        code=master_access_check(request)
        if code[0] != 100 : return JsonResponse({'type':'danger', 'msg':code[2]})
    except: return JsonResponse({'type':'danger', 'msg':'ورود شما منقضی شده لطفا مجددا وارد شوید'})
    # master json check end
    
    if request.method == 'POST' :

        time.sleep(1)

        apikey = request.POST.get('apikey')
        secretkey = request.POST.get('secretkey')
        wallet_trc20_count = request.POST.get('wallet_trc20_count')
        wallet_erc20_count = request.POST.get('wallet_erc20_count')
        wallet_polygon_count = request.POST.get('wallet_polygon_count')
        wallet_bsc_count = request.POST.get('wallet_bsc_count')
        
        if apikey == "" :
            return JsonResponse({'type':'danger', 'msg':'لطفا نام کلید را وارد نمایید'})

        if secretkey == "" :
            return JsonResponse({'type':'danger', 'msg':'لطفا رمز کلید را وارد نمایید'})
        
        try:
            int(wallet_trc20_count)
            int(wallet_erc20_count)
            int(wallet_polygon_count)
            int(wallet_bsc_count)
        except:   return JsonResponse({'type':'danger', 'msg':'لطفا تعداد را به صورت عددی وارد نمایید'})  
        

        sett = Site_Settings.objects.get(code=1001)
        sett.max_wallet_create_allow_trc20 = wallet_trc20_count
        sett.max_wallet_create_allow_erc20 = wallet_erc20_count
        sett.max_wallet_create_allow_polygon = wallet_polygon_count
        sett.max_wallet_create_allow_bsc = wallet_bsc_count
        sett.save()

    
        ku = Account_Kucooin_Direct_Wallet.objects.get(code=1000)
        ku.apikey = encrypt_message(apikey)
        ku.secretkey = encrypt_message(secretkey)
        ku.last_modify = get_date_time()['timestamp']
        ku.save()

        add_static_report(request, 'ویرایش کیف پول ارزی')
        return JsonResponse({'type':'success', 'msg':'ویرایش با موفقیت انجام شد'})


    return JsonResponse({'type':'danger', 'msg':'پردازش مورد نظر با مشکل مواجه شده است'})



