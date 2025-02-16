from doctest import FAIL_FAST
from math import ceil
from django.shortcuts import render, get_object_or_404, redirect
from django.core.files.storage import FileSystemStorage
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User , Group , Permission
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse, JsonResponse
from exchange.func.theme import *
from customer.models import *
from exchange.func.public import *
from master.func.access import *
from currency.models import *
from .models import *
import time
from itertools import chain
from customer.func.access import *
from customer.func.public import *
from openpyxl import Workbook
from django.db.models import Q
from django.db.models import Q , Exists , OuterRef

def master_wallet_dpwt(request, wallet, pk):

    # master check start
    try :
        code = master_access_check(request)
        if code[0] != 100 : return redirect(code[1])
    except: return redirect('master_login')
    # master check end

    try : customer = Customer.objects.get(pk=pk)
    except : return redirect('master_customer_list')

    if wallet == 'IRT' :

        querySet = Wallet.objects.filter(wallet='IRT', uname=customer).order_by('-pk')
    
    elif Currency_List.objects.filter(symbol=wallet).count() == 1 :

        try : 
            
            if Currency_List.objects.get(symbol=wallet).is_wallet == True :
                querySet = Wallet.objects.filter(wallet=wallet, uname=customer).order_by('-pk')

            else : return redirect('master_customer_detail', pk=pk)

        except : return redirect('master_customer_detail', pk=pk)


    else: return redirect('master_customer_detail', pk=pk)

    paginator = Paginator(querySet,10)
    page = request.GET.get('page')

    try:
        querySet = paginator.page(page)
    except PageNotAnInteger:
        querySet = paginator.page(1)
    except EmptyPage:
        querySet = paginator.page(1) 
        
    return render(request, get_master_theme() + 'wallet_dpwt.html', {'customer':customer, 'wallet':wallet, 'querySet':querySet})


def master_wallet_dpwt_submit(request):

    # master json check start
    try : 
        code=master_access_check(request)
        if code[0] != 100 : return JsonResponse({'type':'danger', 'msg':code[2]})
    except: return JsonResponse({'type':'danger', 'msg':'ورود شما منقضی شده لطفا مجددا وارد شوید'})
    # master json check end
    
    if request.method == 'POST' :

        amount = request.POST.get('amount')
        desc = request.POST.get('desc')
        wallet = request.POST.get('wallet')
        customer_id = request.POST.get('customer')

        amount = amount.replace(',','')

        if amount == "" or desc == "" or wallet == "" or customer_id == "" :
            return JsonResponse({'type':'danger', 'msg':'لطفا موارد خواسته شده را وارد نمایید'})
        
        if Customer.objects.filter(pk=customer_id).count() != 1 :
            return JsonResponse({'type':'danger', 'msg':'کاربر مورد نظر یافت نشد'})

        if wallet == 'IRT' :

            try : amount = float(int(amount))
            except : return JsonResponse({'type':'danger', 'msg':'لطفا مبلغ خود را به صورت عددی وارد نمایید'})

        elif Currency_List.objects.filter(symbol=wallet).count() == 1 :

            try : amount = float(amount)
            except : return JsonResponse({'type':'danger', 'msg':'لطفا مبلغ خود را به صورت اعشاری وارد نمایید'})


            if amount > float(0) :

                currency  = Currency_List.objects.get(symbol=wallet)

                
                # delete code

        else: return JsonResponse({'type':'danger', 'msg':'کیف پول مورد نظر یافت نشد'})
        
        customer = Customer.objects.get(pk=customer_id)
        master = code[3]

        if Wallet.objects.filter(datetime__range=(int(time.time()) - 10 , int(time.time()) + 50), amount=amount, wallet=wallet, uname=customer).count() != 0 :
            return JsonResponse({'type':'danger', 'msg':'به دلیل وجود تراکنش مشابه تا 60 ثانیه امکان ثبت تراکنش وجود ندارد'})

        if amount < float(0) : is_verify_set = True
        else : is_verify_set = False
        
        if amount < float(0) : color = 'danger'
        else : color = 'success'
        datetime_now = get_date_time()['timestamp']
        if str(amount).endswith('.0') : amount_show = abs(int(amount))
        else: amount_show = abs(amount)
        

        w = Wallet(
    
            uname = customer, 
            master = master, 
            wallet = wallet, 
            amount = amount, 
            desc = desc, 
            datetime = datetime_now,
            ip = get_ip(request), 
            is_verify = is_verify_set,
        )
        w.save()

        if amount < float(0) : 
            add_static_report(request, 'برداشت از کیف پول کاربر')
            return JsonResponse({'type':'success', 'msg':'برداشت با موفقیت انجام شد', 'code':w.pk, 'master':master.nick_name, 'amount':f'{amount_show:,}', 'date':datetime_converter(datetime_now), 'desc':desc, 'color':color})

        else : 
            add_static_report(request, 'واریز به کیف پول کاربر')
            return JsonResponse({'type':'success', 'msg':'واریز با موفقیت انجام شد', 'code':w.pk, 'master':master.nick_name, 'amount':f'{amount_show:,}', 'date':datetime_converter(datetime_now), 'desc':desc, 'color':color})


    return JsonResponse({'type':'danger', 'msg':'پردازش مورد نظر با مشکل مواجه شده است'})


def master_transaction_all(request):

    # master check start
    try :
        code = master_access_check(request)
        if code[0] != 100 : return redirect(code[1])
    except: return redirect('master_login')
    # master check end

    paginator = Paginator(Wallet.objects.all().order_by('-pk')[:1000],10)
    page = request.GET.get('page')

    try:
        querySet = paginator.page(page)
    except PageNotAnInteger:
        querySet = paginator.page(1)
    except EmptyPage:
        querySet = paginator.page(1) 

    return render(request, get_master_theme() + 'wallet_transaction_all.html', {'querySet':querySet})


def master_transaction_all_search(request):
 
    # master check start
    try :
        code = master_access_check(request)
        if code[0] != 100 : return redirect(code[1])
    except: return redirect('master_login')
    # master check end

    querySet = Wallet.objects.all()

    if request.method == 'POST':

        txt = request.POST.get('txt')  
        request.session['txt'] = txt
        

    else:
        txt = request.session.get('txt', '')  
     
    
    if txt != "":
        querySet = querySet.filter(
            Q(pk__contains=txt) |
            Q(uname__first_name__contains=txt) |
            Q(uname__last_name__contains=txt) |
            Q(master__nick_name__contains=txt) | 
            Q(wallet__contains=txt) |
            Q(desc__contains=txt) | 
            Q(amount__contains=txt) 
        )


    paginator = Paginator(querySet.order_by('-pk'),10)
    page = request.GET.get('page')

    try:
        querySet = paginator.page(page)
    except PageNotAnInteger:
        querySet = paginator.page(1)
    except EmptyPage:
        querySet = paginator.page(1) 




    return render(request, get_master_theme() + 'wallet_transaction_all.html', {'querySet':querySet})
           
def master_transaction_waiting(request):

    # master check start
    try :
        code = master_access_check(request)
        if code[0] != 100 : return redirect(code[1])
    except: return redirect('master_login')
    # master check end

    paginator = Paginator(Wallet.objects.filter(is_verify=False,is_rejected=False,is_locked=False).order_by('-pk'),10)
    page = request.GET.get('page')

    try:
        querySet = paginator.page(page)
    except PageNotAnInteger:
        querySet = paginator.page(1)
    except EmptyPage:
        querySet = paginator.page(1) 

    return render(request, get_master_theme() + 'wallet_transaction_waiting.html', {'querySet':querySet})

def master_transaction_waiting_search(request):
 
    # master check start
    try :
        code = master_access_check(request)
        if code[0] != 100 : return redirect(code[1])
    except: return redirect('master_login')
    # master check end

    querySet = Wallet.objects.filter(is_verify=False,is_rejected=False,is_locked=False)

    if request.method == 'POST':

        txt = request.POST.get('txt')  
        request.session['txt'] = txt
        

    else:
        txt = request.session.get('txt', '')  
     
    
    if txt != "":
        querySet = querySet.filter(
            Q(pk__contains=txt) |
            Q(uname__first_name__contains=txt) |
            Q(uname__last_name__contains=txt) |
            Q(master__nick_name__contains=txt) | 
            Q(wallet__contains=txt) |
            Q(desc__contains=txt) | 
            Q(amount__contains=txt) 
        )


    paginator = Paginator(querySet.order_by('-pk'),10)
    page = request.GET.get('page')

    try:
        querySet = paginator.page(page)
    except PageNotAnInteger:
        querySet = paginator.page(1)
    except EmptyPage:
        querySet = paginator.page(1) 

    return render(request, get_master_theme() + 'wallet_transaction_waiting.html', {'querySet':querySet})
           

def master_confirm_transaction(request,pk):

    # master json check start
    try : 
        code=master_access_check(request)
        if code[0] != 100 : return JsonResponse({'type':'danger', 'msg':code[2]})
    except: return JsonResponse({'type':'danger', 'msg':'ورود شما منقضی شده لطفا مجددا وارد شوید'})
    # master json check end

    wallet = Wallet.objects.get(pk=pk)

    if wallet.master != None :
        if str(request.user.username) == str(wallet.master.req_user) :
            return JsonResponse({'type':'danger', 'msg':'واریز و تایید نمیتواند توسط یک مدیر انجام شود'})
    
    if wallet.proccess_time > get_date_time()['timestamp'] :
        return JsonResponse({'type':'danger', 'msg':'در حال حاضر امکان تایید تراکنش وجود ندارد'})
    
    wallet.is_verify = True
    wallet.confirmed_master = request.user.username
    wallet.confirmed_datetime = get_date_time()['timestamp']
    wallet.save()

    add_static_report(request, 'تایید تراکنش')

    return JsonResponse({'type':'success', 'msg':'تراکنش با موفقیت تایید شد'})


def master_reject_transaction(request,pk):

    # master json check start
    try : 
        code=master_access_check(request)
        if code[0] != 100 : return JsonResponse({'type':'danger', 'msg':code[2]})
    except: return JsonResponse({'type':'danger', 'msg':'ورود شما منقضی شده لطفا مجددا وارد شوید'})
    # master json check end

    if request.method == 'POST' :

        reject_reson = request.POST.get('reject_reson')

        if reject_reson == "" :
            return JsonResponse({'type':'danger', 'msg':'لطفا دلیل عدم تایید تراکنش را وارد نمایید'})

        wallet = Wallet.objects.get(pk=pk)

        if wallet.master != None :
            if str(request.user.username) == str(wallet.master.req_user) :
                return JsonResponse({'type':'danger', 'msg':'واریز و رد نمیتواند توسط یک مدیر انجام شود'})
    
        wallet.is_rejected = True
        wallet.reject_reson = reject_reson
        wallet.confirmed_master = request.user.username
        wallet.confirmed_datetime = get_date_time()['timestamp']
        wallet.save()

        add_static_report(request, 'عدم تایید تراکنش')

        return JsonResponse({'type':'success', 'msg':'تراکنش مورد نظر رد شد'})

    return JsonResponse({'type':'danger', 'msg':'پردازش مورد نظر با مشکل مواجه شده است'})


def customer_harvest(request):

    # customer check start
    try :
        pattern_url = customer_access_check(request)
        if pattern_url[0] != 100 : return redirect(pattern_url[1])
    except: return redirect('account')
    # customer check end
    trans_irt = WalletWithdrawIRT.objects.filter(uname=pattern_url[2]).order_by('-pk')

    paginator = Paginator(trans_irt,10)
    page = request.GET.get('page')

    try:
        querySet = paginator.page(page)
    except PageNotAnInteger:
        querySet = paginator.page(1)
    except EmptyPage:
        querySet = paginator.page(paginator.num_page) 

    cards = Customer_card.objects.filter(is_verify=True,uname=pattern_url[2],is_show=True)
    payment_method = WithdrawPaymentMethodIRT.objects.filter(is_active= True)

    gram_equivalent_of_Toman_balance = get_customer_balance(request.user,'IRT')["balance"] / Currency_List.objects.get(symbol='XAU18').BuySellPrice['buy']


    return render(request, get_customer_theme(pattern_url[2]) + 'harvest.html',{'cards':cards,'payment_method':payment_method, 'trans_irt': querySet, 'trans_irt_count': trans_irt.count(), 'gram_equivalent': gram_equivalent_of_Toman_balance})


def master_all_WalletWithdrawIRT(request):

    # master check start
    try :
        code = master_access_check(request)
        if code[0] != 100 : return redirect(code[1])
    except: return redirect('master_login')
    # master check end

    paginator = Paginator(WalletWithdrawIRT.objects.all().order_by('-pk')[:2000],10)
    page = request.GET.get('page')

    try:
        querySet = paginator.page(page)
    except PageNotAnInteger:
        querySet = paginator.page(1)
    except EmptyPage:
        querySet = paginator.page(paginator.num_page) 

    return render(request, get_master_theme() + 'all_withdraw.html', {'querySet':querySet})    


def master_all_WalletWithdrawIRT_search(request):
 
    # master check start
    try :
        code = master_access_check(request)
        if code[0] != 100 : return redirect(code[1])
    except: return redirect('master_login')
    # master check end

    querySet = WalletWithdrawIRT.objects.all()

    if request.method == 'POST':

        txt = request.POST.get('txt')  
        request.session['txt'] = txt
        

    else:
        txt = request.session.get('txt', '')  
     
    
    if txt != "":
        querySet = querySet.filter(
            Q(pk__contains=txt) |
            Q(uname__first_name__contains=txt) |
            Q(uname__last_name__contains=txt) |
            Q(reject_reson__contains=txt) | 
            Q(amount__contains=txt) 
        )


    paginator = Paginator(querySet.order_by('-pk'),10)
    page = request.GET.get('page')

    try:
        querySet = paginator.page(page)
    except PageNotAnInteger:
        querySet = paginator.page(1)
    except EmptyPage:
        querySet = paginator.page(1) 

    return render(request, get_master_theme() + 'all_withdraw.html', {'querySet':querySet})


def master_accept_WalletWithdrawIRT(request):

    # master check start
    try :
        code = master_access_check(request)
        if code[0] != 100 : return redirect(code[1])
    except: return redirect('master_login')
    # master check end

    paginator = Paginator(WalletWithdrawIRT.objects.filter(is_verify=True).order_by('-pk')[:1000],10)
    page = request.GET.get('page')

    try:
        querySet = paginator.page(page)
    except PageNotAnInteger:
        querySet = paginator.page(1)
    except EmptyPage:
        querySet = paginator.page(paginator.num_page) 

    return render(request, get_master_theme() + 'accept_withdraw.html', {'querySet':querySet})    

def master_accept_WalletWithdrawIRT_search(request):
 
    # master check start
    try :
        code = master_access_check(request)
        if code[0] != 100 : return redirect(code[1])
    except: return redirect('master_login')
    # master check end

    querySet = WalletWithdrawIRT.objects.filter(is_verify=True)

    if request.method == 'POST':

        txt = request.POST.get('txt')  
        request.session['txt'] = txt
        

    else:
        txt = request.session.get('txt', '')  
     
    
    if txt != "":
        querySet = querySet.filter(
            Q(pk__contains=txt) |
            Q(uname__first_name__contains=txt) |
            Q(uname__last_name__contains=txt) |
            Q(reject_reson__contains=txt) | 
            Q(amount__contains=txt) 
        )


    paginator = Paginator(querySet.order_by('-pk'),10)
    page = request.GET.get('page')

    try:
        querySet = paginator.page(page)
    except PageNotAnInteger:
        querySet = paginator.page(1)
    except EmptyPage:
        querySet = paginator.page(1) 

    return render(request, get_master_theme() + 'accept_withdraw.html', {'querySet':querySet})

def master_reject_WalletWithdrawIRT(request):

    # master check start
    try :
        code = master_access_check(request)
        if code[0] != 100 : return redirect(code[1])
    except: return redirect('master_login')
    # master check end

    paginator = Paginator(WalletWithdrawIRT.objects.filter(is_verify=False).order_by('-pk')[:1000],10)
    page = request.GET.get('page')

    try:
        querySet = paginator.page(page)
    except PageNotAnInteger:
        querySet = paginator.page(1)
    except EmptyPage:
        querySet = paginator.page(paginator.num_page) 

    return render(request, get_master_theme() + 'reject_withdraw.html', {'querySet':querySet})    

def master_reject_WalletWithdrawIRT_search(request):
 
    # master check start
    try :
        code = master_access_check(request)
        if code[0] != 100 : return redirect(code[1])
    except: return redirect('master_login')
    # master check end

    querySet = WalletWithdrawIRT.objects.filter(is_verify=False)

    if request.method == 'POST':

        txt = request.POST.get('txt')  
        request.session['txt'] = txt
        

    else:
        txt = request.session.get('txt', '')  
     
    
    if txt != "":
        querySet = querySet.filter(
            Q(pk__contains=txt) |
            Q(uname__first_name__contains=txt) |
            Q(uname__last_name__contains=txt) |
            Q(reject_reson__contains=txt) | 
            Q(amount__contains=txt) 
        )


    paginator = Paginator(querySet.order_by('-pk'),10)
    page = request.GET.get('page')

    try:
        querySet = paginator.page(page)
    except PageNotAnInteger:
        querySet = paginator.page(1)
    except EmptyPage:
        querySet = paginator.page(1) 

    return render(request, get_master_theme() + 'reject_withdraw.html', {'querySet':querySet})

def master_waiting_WalletWithdrawIRT(request):

    # master check start
    try :
        code = master_access_check(request)
        if code[0] != 100 : return redirect(code[1])
    except: return redirect('master_login')
    # master check end


    if Site_Settings.objects.get(code=1001).automatic_deposit == True :

    
        wallet = WalletWithdrawIRT.objects.filter(
            Q(
                Exists(
                    Cancel_Withdrawal_Request.objects.filter(withdrawal=OuterRef('pk'))
                ),
                is_verify=None,
                is_check=True
            ) | Q(
                payment_method__pk=4,
                is_verify=None,
                is_check=True
            )
        )

    else :
        
        wallet = WalletWithdrawIRT.objects.filter(is_verify=None,is_check=True).exclude(bank_send=True).order_by('-pk')

    paginator = Paginator(wallet,10)
    page = request.GET.get('page')

    try:
        querySet = paginator.page(page)
    except PageNotAnInteger:
        querySet = paginator.page(1)
    except EmptyPage:
        querySet = paginator.page(paginator.num_page) 

    return render(request, get_master_theme() + 'waiting_withdraw.html', {'querySet':querySet})    

def master_waiting_WalletWithdrawIRT_search(request):
 
    # master check start
    try :
        code = master_access_check(request)
        if code[0] != 100 : return redirect(code[1])
    except: return redirect('master_login')
    # master check end

    querySet = WalletWithdrawIRT.objects.filter(is_verify=None,is_check=True)

    if request.method == 'POST':

        txt = request.POST.get('txt')  
        request.session['txt'] = txt
        

    else:
        txt = request.session.get('txt', '')  
     
    
    if txt != "":
        querySet = querySet.filter(
            Q(pk__contains=txt) |
            Q(uname__first_name__contains=txt) |
            Q(uname__last_name__contains=txt) |
            Q(reject_reson__contains=txt) | 
            Q(amount__contains=txt) 
        )


    paginator = Paginator(querySet.order_by('-pk'),10)
    page = request.GET.get('page')

    try:
        querySet = paginator.page(page)
    except PageNotAnInteger:
        querySet = paginator.page(1)
    except EmptyPage:
        querySet = paginator.page(1) 

    return render(request, get_master_theme() + 'waiting_withdraw.html', {'querySet':querySet})    



    # delete views    
    # delete views    
    # delete views
    # .
    # .
    # .