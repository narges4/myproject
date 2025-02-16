from django.shortcuts import render, get_object_or_404, redirect
from django.core.files.storage import FileSystemStorage
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User , Group , Permission
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse, JsonResponse
from currency.models import *
# from exchange.func.theme import *
from customer.models import *
from exchange.func.public import *
# from note.models import Notes
# from representation.models import *
from master.func.access import *
from .models import *
from exchange.models import *
import time
import datetime
from itertools import chain
from wallet.models import *
import khayyam
from django.db.models import Q




def master_buySell_list(request, type):

    # master check start
    try :
        code = master_access_check(request)
        if code[0] != 100 : return redirect(code[1])
    except: return redirect('master_login')
    # master check end

    if type == 'Success': bill = Currency_BuySell_List.objects.filter(status='Success').order_by('-pk')
    elif type == 'UnSuccess': bill = Currency_BuySell_List.objects.filter(status='Rejected').order_by('-pk')
    elif type == 'Pendding': bill = Currency_BuySell_List.objects.filter(status='Pendding').order_by('-pk')
    else: bill = Currency_BuySell_List.objects.all().order_by('-pk')

    paginator = Paginator(bill,10)
    page = request.GET.get('page')
    try: querySet = paginator.page(page)
    except PageNotAnInteger: querySet = paginator.page(1)
    except EmptyPage: querySet = paginator.page(1)

    return render(request, get_master_theme() + 'buySel_list.html', {'querySet':querySet,'type':type})

def master_buySell_search(request, type):

    # master check start
    try:
        code = master_access_check(request)
        if code[0] != 100:
            return redirect(code[1])
    except:
        return redirect('master_login')
    # master check end

    txt = "-"
    buysells = []
    querySet = [] 

    if request.method == 'POST':
        txt = request.POST.get('txt', '').strip() 
        request.session['search'] = txt
    else:
        txt = request.session.get('search', '').strip() 

   
    if txt:
        if type == 'Success':
            status_filter = ['Success']
        elif type == 'UnSuccess':
            status_filter = ['Rejected']
        elif type == 'Pendding':
            status_filter = ['Pendding']
        else:
            status_filter = [] 

        query = Q(pk__contains=txt) | \
                Q(pk__contains=txt) | \
                Q(acc__contains=txt) | \
                Q(currency__symbol__contains=txt) | \
                Q(currency__fa_title__contains=txt) |  \
                Q(currency__en_title__contains=txt) | \
                Q(uname__first_name__contains=txt) | \
                Q(uname__last_name__contains=txt) | \
                Q(amount__contains=txt) | \
                Q(fee_amount__contains=txt) 

        if status_filter:
            buysells = Currency_BuySell_List.objects.filter(query, status__in=status_filter).distinct()
        else:

            buysells = Currency_BuySell_List.objects.filter(query).distinct()

        paginator = Paginator(buysells, 10)
        page = request.GET.get('page')

        try:
            querySet = paginator.page(page)
        except PageNotAnInteger:
            querySet = paginator.page(1)
        except EmptyPage:
            querySet = paginator.page(1)

    return render(request, get_master_theme() + 'buySel_list.html', {'querySet':querySet,'type':type})


def master_swap_list(request, type):

    # master check start
    try :
        code = master_access_check(request)
        if code[0] != 100 : return redirect(code[1])
    except: return redirect('master_login')
    # master check end


    if type == 'Success' :
        bill = Currency_Swap_List.objects.filter(status='Success').order_by('-pk')

    elif type == 'UnSuccess' :
        bill = Currency_Swap_List.objects.filter(status='Rejected').order_by('-pk')

    elif type == 'Pendding' :
        bill = Currency_Swap_List.objects.filter(status='Pendding').order_by('-pk')

    else :
        bill = Currency_Swap_List.objects.all().order_by('-pk')


    paginator = Paginator(bill,10)
    page = request.GET.get('page')

    try:
        querySet = paginator.page(page)
    except PageNotAnInteger:
        querySet = paginator.page(1)
    except EmptyPage:
        querySet = paginator.page(1)


    return render(request, get_master_theme() + 'swap_list.html', {'querySet':querySet,'type':type})

def master_swap_search(request,type):

    bills = []
    txt = "-"

    if type == 'Success' :

        if request.method == 'POST':
            
            txt = request.POST.get('txt')

            request.session['search'] = txt

            bill1 = Currency_Swap_List.objects.filter(pk__contains=txt,status='Success')
            
            bill3 = Currency_Swap_List.objects.filter(first_currency__symbol__contains=txt,status='Success')
            bill4 = Currency_Swap_List.objects.filter(first_currency__fa_title__contains=txt,status='Success')
            bill5 = Currency_Swap_List.objects.filter(first_currency__en_title__contains=txt,status='Success')
            bill6 = Currency_Swap_List.objects.filter(uname__first_name__contains=txt,status='Success')
            bill7 = Currency_Swap_List.objects.filter(uname__last_name__contains=txt,status='Success')
            bill8 = Currency_Swap_List.objects.filter(second_currency__contains=txt,status='Success')
            bill9 = Currency_Swap_List.objects.filter(sell_price__contains=txt,status='Success')

            bills = list(chain(bill1,bill3,bill4,bill5,bill6,bill7,bill8,bill9))

            paginator = Paginator(list(dict.fromkeys(bills)),10)
            page = request.GET.get('page')

            try:
                querySet = paginator.page(page)
            except PageNotAnInteger:
                querySet = paginator.page(1)
            except EmptyPage:
                querySet = paginator.page(1) 

        else:

            txt = request.session['search']
        
            bill1 = Currency_Swap_List.objects.filter(pk__contains=txt,status='Success')
            
            bill3 = Currency_Swap_List.objects.filter(first_currency__symbol__contains=txt,status='Success')
            bill4 = Currency_Swap_List.objects.filter(first_currency__fa_title__contains=txt,status='Success')
            bill5 = Currency_Swap_List.objects.filter(first_currency__en_title__contains=txt,status='Success')
            bill6 = Currency_Swap_List.objects.filter(uname__first_name__contains=txt,status='Success')
            bill7 = Currency_Swap_List.objects.filter(uname__last_name__contains=txt,status='Success')
            bill8 = Currency_Swap_List.objects.filter(second_currency__contains=txt,status='Success')
            bill9 = Currency_Swap_List.objects.filter(sell_price__contains=txt,status='Success')

            bills = list(chain(bill1,bill3,bill4,bill5,bill6,bill7,bill8,bill9))

            paginator = Paginator(list(dict.fromkeys(bills)),10)
            page = request.GET.get('page')

            try:
                querySet = paginator.page(page)
            except PageNotAnInteger:
                querySet = paginator.page(1)
            except EmptyPage:
                querySet = paginator.page(1)    

    elif type == 'UnSuccess' :

        if request.method == 'POST':
            
            txt = request.POST.get('txt')

            request.session['search'] = txt

            bill1 = Currency_Swap_List.objects.filter(pk__contains=txt,status='Rejected')
            
            bill3 = Currency_Swap_List.objects.filter(first_currency__symbol__contains=txt,status='Rejected')
            bill4 = Currency_Swap_List.objects.filter(first_currency__fa_title__contains=txt,status='Rejected')
            bill5 = Currency_Swap_List.objects.filter(first_currency__en_title__contains=txt,status='Rejected')
            bill6 = Currency_Swap_List.objects.filter(uname__first_name__contains=txt,status='Rejected')
            bill7 = Currency_Swap_List.objects.filter(uname__last_name__contains=txt,status='Rejected')
            bill8 = Currency_Swap_List.objects.filter(second_currency__contains=txt,status='Rejected')
            bill9 = Currency_Swap_List.objects.filter(sell_price__contains=txt,status='Rejected')

            bills = list(chain(bill1,bill3,bill4,bill5,bill6,bill7,bill8,bill9))

            paginator = Paginator(list(dict.fromkeys(bills)),10)
            page = request.GET.get('page')

            try:
                querySet = paginator.page(page)
            except PageNotAnInteger:
                querySet = paginator.page(1)
            except EmptyPage:
                querySet = paginator.page(1) 

        else:

            txt = request.session['search']
        
            bill1 = Currency_Swap_List.objects.filter(pk__contains=txt,status='Rejected')
            
            bill3 = Currency_Swap_List.objects.filter(first_currency__symbol__contains=txt,status='Rejected')
            bill4 = Currency_Swap_List.objects.filter(first_currency__fa_title__contains=txt,status='Rejected')
            bill5 = Currency_Swap_List.objects.filter(first_currency__en_title__contains=txt,status='Rejected')
            bill6 = Currency_Swap_List.objects.filter(uname__first_name__contains=txt,status='Rejected')
            bill7 = Currency_Swap_List.objects.filter(uname__last_name__contains=txt,status='Rejected')
            bill8 = Currency_Swap_List.objects.filter(second_currency__contains=txt,status='Rejected')
            bill9 = Currency_Swap_List.objects.filter(sell_price__contains=txt,status='Rejected')

            bills = list(chain(bill1,bill3,bill4,bill5,bill6,bill7,bill8,bill9))

            paginator = Paginator(list(dict.fromkeys(bills)),10)
            page = request.GET.get('page')

            try:
                querySet = paginator.page(page)
            except PageNotAnInteger:
                querySet = paginator.page(1)
            except EmptyPage:
                querySet = paginator.page(1)  

    elif type == 'Pendding' :  

        if request.method == 'POST':
            
            txt = request.POST.get('txt')

            request.session['search'] = txt

            bill1 = Currency_Swap_List.objects.filter(pk__contains=txt,status='Pendding')
            
            bill3 = Currency_Swap_List.objects.filter(first_currency__symbol__contains=txt,status='Pendding')
            bill4 = Currency_Swap_List.objects.filter(first_currency__fa_title__contains=txt,status='Pendding')
            bill5 = Currency_Swap_List.objects.filter(first_currency__en_title__contains=txt,status='Pendding')
            bill6 = Currency_Swap_List.objects.filter(uname__first_name__contains=txt,status='Pendding')
            bill7 = Currency_Swap_List.objects.filter(uname__last_name__contains=txt,status='Pendding')
            bill8 = Currency_Swap_List.objects.filter(second_currency__contains=txt,status='Pendding')
            bill9 = Currency_Swap_List.objects.filter(sell_price__contains=txt,status='Pendding')

            bills = list(chain(bill1,bill3,bill4,bill5,bill6,bill7,bill8,bill9))

            paginator = Paginator(list(dict.fromkeys(bills)),10)
            page = request.GET.get('page')

            try:
                querySet = paginator.page(page)
            except PageNotAnInteger:
                querySet = paginator.page(1)
            except EmptyPage:
                querySet = paginator.page(1) 

        else:

            txt = request.session['search']
        
            bill1 = Currency_Swap_List.objects.filter(pk__contains=txt,status='Pendding')
            
            bill3 = Currency_Swap_List.objects.filter(first_currency__symbol__contains=txt,status='Pendding')
            bill4 = Currency_Swap_List.objects.filter(first_currency__fa_title__contains=txt,status='Pendding')
            bill5 = Currency_Swap_List.objects.filter(first_currency__en_title__contains=txt,status='Pendding')
            bill6 = Currency_Swap_List.objects.filter(uname__first_name__contains=txt,status='Pendding')
            bill7 = Currency_Swap_List.objects.filter(uname__last_name__contains=txt,status='Pendding')
            bill8 = Currency_Swap_List.objects.filter(second_currency__contains=txt,status='Pendding')
            bill9 = Currency_Swap_List.objects.filter(sell_price__contains=txt,status='Pendding')

            bills = list(chain(bill1,bill3,bill4,bill5,bill6,bill7,bill8,bill9))

            paginator = Paginator(list(dict.fromkeys(bills)),10)
            page = request.GET.get('page')

            try:
                querySet = paginator.page(page)
            except PageNotAnInteger:
                querySet = paginator.page(1)
            except EmptyPage:
                querySet = paginator.page(1)  

    else :
        if request.method == 'POST':
            
            txt = request.POST.get('txt')

            request.session['search'] = txt

            bill1 = Currency_Swap_List.objects.filter(pk__contains=txt)
            
            bill3 = Currency_Swap_List.objects.filter(first_currency__symbol__contains=txt)
            bill4 = Currency_Swap_List.objects.filter(first_currency__fa_title__contains=txt)
            bill5 = Currency_Swap_List.objects.filter(first_currency__en_title__contains=txt)
            bill6 = Currency_Swap_List.objects.filter(uname__first_name__contains=txt)
            bill7 = Currency_Swap_List.objects.filter(uname__last_name__contains=txt)
            bill8 = Currency_Swap_List.objects.filter(second_currency__contains=txt)
            bill9 = Currency_Swap_List.objects.filter(sell_price__contains=txt)

            bills = list(chain(bill1,bill3,bill4,bill5,bill6,bill7,bill8,bill9))

            paginator = Paginator(list(dict.fromkeys(bills)),10)
            page = request.GET.get('page')

            try:
                querySet = paginator.page(page)
            except PageNotAnInteger:
                querySet = paginator.page(1)
            except EmptyPage:
                querySet = paginator.page(1) 

        else:

            txt = request.session['search']
        
            bill1 = Currency_Swap_List.objects.filter(pk__contains=txt)
             
            bill3 = Currency_Swap_List.objects.filter(first_currency__symbol__contains=txt)
            bill4 = Currency_Swap_List.objects.filter(first_currency__fa_title__contains=txt)
            bill5 = Currency_Swap_List.objects.filter(first_currency__en_title__contains=txt)
            bill6 = Currency_Swap_List.objects.filter(uname__first_name__contains=txt)
            bill7 = Currency_Swap_List.objects.filter(uname__last_name__contains=txt)
            bill8 = Currency_Swap_List.objects.filter(second_currency__contains=txt)
            bill9 = Currency_Swap_List.objects.filter(sell_price__contains=txt)

            bills = list(chain(bill1,bill3,bill4,bill5,bill6,bill7,bill8,bill9))

            paginator = Paginator(list(dict.fromkeys(bills)),10)
            page = request.GET.get('page')

            try:
                querySet = paginator.page(page)
            except PageNotAnInteger:
                querySet = paginator.page(1)
            except EmptyPage:
                querySet = paginator.page(1)  

    return render(request, get_master_theme() + 'swap_list.html', {'querySet':querySet,'type':type})


def master_currency_withdrawal_handly(request, type):

    # master check start
    try :
        code = master_access_check(request)
        if code[0] != 100 : return redirect(code[1])
    except: return redirect('master_login')
    # master check end

    message = None

    if request.session.get('notification') != None :
        message = request.session.get('notification')
    request.session['notification'] = None

    if type == 'Success' :
        bill = Currency_depositeWithdraw_List.objects.filter(status='Success',bill_type="withdraw").order_by('-pk')

    elif type == 'UnSuccess' :
        bill = Currency_depositeWithdraw_List.objects.filter(status='Rejected',bill_type="withdraw").order_by('-pk')

    elif type == 'Pendding' :
        bill = Currency_depositeWithdraw_List.objects.filter(status='Pendding',bill_type="withdraw").order_by('-pk')

    else :
        bill = Currency_depositeWithdraw_List.objects.filter(bill_type="withdraw").order_by('-pk')

    paginator = Paginator(bill,10)
    page = request.GET.get('page')

    try:
        querySet = paginator.page(page)
    except PageNotAnInteger:
        querySet = paginator.page(1)
    except EmptyPage:
        querySet = paginator.page(1)

    return render(request, get_master_theme() + 'currency_withdrawal_list.html', {'querySet':querySet,'type':type, 'message':message})




def master_currency_withdrawal_handly_search(request,type):

    bills = []
    txt = "-"

    if type == 'Success' :

        if request.method == 'POST':
            
            txt = request.POST.get('txt')

            request.session['search'] = txt

            bill1 = Currency_depositeWithdraw_List.objects.filter(pk__contains=txt,status='Success',bill_type="withdraw")
            bill2 = Currency_depositeWithdraw_List.objects.filter(currency__symbol__contains=txt,status='Success',bill_type="withdraw")
            bill3 = Currency_depositeWithdraw_List.objects.filter(currency__fa_title__contains=txt,status='Success',bill_type="withdraw")
            bill4 = Currency_depositeWithdraw_List.objects.filter(currency__en_title__contains=txt,status='Success',bill_type="withdraw")
            bill5 = Currency_depositeWithdraw_List.objects.filter(uname__first_name__contains=txt,status='Success',bill_type="withdraw")
            bill6 = Currency_depositeWithdraw_List.objects.filter(uname__last_name__contains=txt,status='Success',bill_type="withdraw")
            bill7 = Currency_depositeWithdraw_List.objects.filter(fee_amount__contains=txt,status='Success',bill_type="withdraw")
            bill8 = Currency_depositeWithdraw_List.objects.filter(amount__contains=txt,status='Success',bill_type="withdraw")

            bills = list(chain(bill1,bill2,bill3,bill4,bill5,bill6,bill7,bill8))

            paginator = Paginator(list(dict.fromkeys(bills)),10)
            page = request.GET.get('page')

            try:
                querySet = paginator.page(page)
            except PageNotAnInteger:
                querySet = paginator.page(1)
            except EmptyPage:
                querySet = paginator.page(1) 

        else:

            txt = request.session['search']
        
            bill1 = Currency_depositeWithdraw_List.objects.filter(pk__contains=txt,status='Success',bill_type="withdraw")
            bill2 = Currency_depositeWithdraw_List.objects.filter(currency__symbol__contains=txt,status='Success',bill_type="withdraw")
            bill3 = Currency_depositeWithdraw_List.objects.filter(currency__fa_title__contains=txt,status='Success',bill_type="withdraw")
            bill4 = Currency_depositeWithdraw_List.objects.filter(currency__en_title__contains=txt,status='Success',bill_type="withdraw")
            bill5 = Currency_depositeWithdraw_List.objects.filter(uname__first_name__contains=txt,status='Success',bill_type="withdraw")
            bill6 = Currency_depositeWithdraw_List.objects.filter(uname__last_name__contains=txt,status='Success',bill_type="withdraw")
            bill7 = Currency_depositeWithdraw_List.objects.filter(fee_amount__contains=txt,status='Success',bill_type="withdraw")
            bill8 = Currency_depositeWithdraw_List.objects.filter(amount__contains=txt,status='Success',bill_type="withdraw")

            bills = list(chain(bill1,bill2,bill3,bill4,bill5,bill6,bill7,bill8))

            paginator = Paginator(list(dict.fromkeys(bills)),10)
            page = request.GET.get('page')

            try:
                querySet = paginator.page(page)
            except PageNotAnInteger:
                querySet = paginator.page(1)
            except EmptyPage:
                querySet = paginator.page(1)    

    elif type == 'UnSuccess' :

        if request.method == 'POST':
            
            txt = request.POST.get('txt')

            request.session['search'] = txt

            bill1 = Currency_depositeWithdraw_List.objects.filter(pk__contains=txt,status='Rejected',bill_type="withdraw")
            bill2 = Currency_depositeWithdraw_List.objects.filter(amount__contains=txt,status='Rejected',bill_type="withdraw")
            bill3 = Currency_depositeWithdraw_List.objects.filter(currency__symbol__contains=txt,status='Rejected',bill_type="withdraw")
            bill4 = Currency_depositeWithdraw_List.objects.filter(currency__fa_title__contains=txt,status='Rejected',bill_type="withdraw")
            bill5 = Currency_depositeWithdraw_List.objects.filter(currency__en_title__contains=txt,status='Rejected',bill_type="withdraw")
            bill6 = Currency_depositeWithdraw_List.objects.filter(uname__first_name__contains=txt,status='Rejected',bill_type="withdraw")
            bill7 = Currency_depositeWithdraw_List.objects.filter(uname__last_name__contains=txt,status='Rejected',bill_type="withdraw")
            bill8 = Currency_depositeWithdraw_List.objects.filter(fee_amount__contains=txt,status='Rejected',bill_type="withdraw")

            bills = list(chain(bill1,bill2,bill3,bill4,bill5,bill6,bill7,bill8))

            paginator = Paginator(list(dict.fromkeys(bills)),10)
            page = request.GET.get('page')

            try:
                querySet = paginator.page(page)
            except PageNotAnInteger:
                querySet = paginator.page(1)
            except EmptyPage:
                querySet = paginator.page(1) 

        else:

            txt = request.session['search']
        
            bill1 = Currency_depositeWithdraw_List.objects.filter(pk__contains=txt,status='Rejected',bill_type="withdraw")
            bill2 = Currency_depositeWithdraw_List.objects.filter(amount__contains=txt,status='Rejected',bill_type="withdraw")
            bill3 = Currency_depositeWithdraw_List.objects.filter(currency__symbol__contains=txt,status='Rejected',bill_type="withdraw")
            bill4 = Currency_depositeWithdraw_List.objects.filter(currency__fa_title__contains=txt,status='Rejected',bill_type="withdraw")
            bill5 = Currency_depositeWithdraw_List.objects.filter(currency__en_title__contains=txt,status='Rejected',bill_type="withdraw")
            bill6 = Currency_depositeWithdraw_List.objects.filter(uname__first_name__contains=txt,status='Rejected',bill_type="withdraw")
            bill7 = Currency_depositeWithdraw_List.objects.filter(uname__last_name__contains=txt,status='Rejected',bill_type="withdraw")
            bill8 = Currency_depositeWithdraw_List.objects.filter(fee_amount__contains=txt,status='Rejected',bill_type="withdraw")

            bills = list(chain(bill1,bill2,bill3,bill4,bill5,bill6,bill7,bill8))

            paginator = Paginator(list(dict.fromkeys(bills)),10)
            page = request.GET.get('page')

            try:
                querySet = paginator.page(page)
            except PageNotAnInteger:
                querySet = paginator.page(1)
            except EmptyPage:
                querySet = paginator.page(1)  

    elif type == 'Pendding' :  

        if request.method == 'POST':
            
            txt = request.POST.get('txt')

            request.session['search'] = txt

            bill1 = Currency_depositeWithdraw_List.objects.filter(pk__contains=txt,status='Pendding',bill_type="withdraw")
            bill2 = Currency_depositeWithdraw_List.objects.filter(amount__contains=txt,status='Pendding',bill_type="withdraw")
            bill3 = Currency_depositeWithdraw_List.objects.filter(currency__symbol__contains=txt,status='Pendding',bill_type="withdraw")
            bill4 = Currency_depositeWithdraw_List.objects.filter(currency__fa_title__contains=txt,status='Pendding',bill_type="withdraw")
            bill5 = Currency_depositeWithdraw_List.objects.filter(currency__en_title__contains=txt,status='Pendding',bill_type="withdraw")
            bill6 = Currency_depositeWithdraw_List.objects.filter(uname__first_name__contains=txt,status='Pendding',bill_type="withdraw")
            bill7 = Currency_depositeWithdraw_List.objects.filter(uname__last_name__contains=txt,status='Pendding',bill_type="withdraw")
            bill8 = Currency_depositeWithdraw_List.objects.filter(fee_amount__contains=txt,status='Pendding',bill_type="withdraw")

            bills = list(chain(bill1,bill2,bill3,bill4,bill5,bill6,bill7,bill8))

            paginator = Paginator(list(dict.fromkeys(bills)),10)
            page = request.GET.get('page')

            try:
                querySet = paginator.page(page)
            except PageNotAnInteger:
                querySet = paginator.page(1)
            except EmptyPage:
                querySet = paginator.page(1) 

        else:

            txt = request.session['search']
        
            bill1 = Currency_depositeWithdraw_List.objects.filter(pk__contains=txt,status='Pendding',bill_type="withdraw")
            bill2 = Currency_depositeWithdraw_List.objects.filter(amount__contains=txt,status='Pendding',bill_type="withdraw")
            bill3 = Currency_depositeWithdraw_List.objects.filter(currency__symbol__contains=txt,status='Pendding',bill_type="withdraw")
            bill4 = Currency_depositeWithdraw_List.objects.filter(currency__fa_title__contains=txt,status='Pendding',bill_type="withdraw")
            bill5 = Currency_depositeWithdraw_List.objects.filter(currency__en_title__contains=txt,status='Pendding',bill_type="withdraw")
            bill6 = Currency_depositeWithdraw_List.objects.filter(uname__first_name__contains=txt,status='Pendding',bill_type="withdraw")
            bill7 = Currency_depositeWithdraw_List.objects.filter(uname__last_name__contains=txt,status='Pendding',bill_type="withdraw")
            bill8 = Currency_depositeWithdraw_List.objects.filter(fee_amount__contains=txt,status='Pendding',bill_type="withdraw")

            bills = list(chain(bill1,bill2,bill3,bill4,bill5,bill6,bill7,bill8))

            paginator = Paginator(list(dict.fromkeys(bills)),10)
            page = request.GET.get('page')

            try:
                querySet = paginator.page(page)
            except PageNotAnInteger:
                querySet = paginator.page(1)
            except EmptyPage:
                querySet = paginator.page(1)  

    else :
        if request.method == 'POST':
            
            txt = request.POST.get('txt')

            request.session['search'] = txt

            bill1 = Currency_depositeWithdraw_List.objects.filter(pk__contains=txt,bill_type="withdraw")
            bill2 = Currency_depositeWithdraw_List.objects.filter(amount__contains=txt,bill_type="withdraw")
            bill3 = Currency_depositeWithdraw_List.objects.filter(currency__symbol__contains=txt,bill_type="withdraw")
            bill4 = Currency_depositeWithdraw_List.objects.filter(currency__fa_title__contains=txt,bill_type="withdraw")
            bill5 = Currency_depositeWithdraw_List.objects.filter(currency__en_title__contains=txt,bill_type="withdraw")
            bill6 = Currency_depositeWithdraw_List.objects.filter(uname__first_name__contains=txt,bill_type="withdraw")
            bill7 = Currency_depositeWithdraw_List.objects.filter(uname__last_name__contains=txt,bill_type="withdraw")
            bill8 = Currency_depositeWithdraw_List.objects.filter(fee_amount__contains=txt,bill_type="withdraw")

            bills = list(chain(bill1,bill2,bill3,bill4,bill5,bill6,bill7,bill8))

            paginator = Paginator(list(dict.fromkeys(bills)),10)
            page = request.GET.get('page')

            try:
                querySet = paginator.page(page)
            except PageNotAnInteger:
                querySet = paginator.page(1)
            except EmptyPage:
                querySet = paginator.page(1) 

        else:

            txt = request.session['search']
        
            bill1 = Currency_depositeWithdraw_List.objects.filter(pk__contains=txt,bill_type="withdraw")
            bill2 = Currency_depositeWithdraw_List.objects.filter(amount__contains=txt,bill_type="withdraw")
            bill3 = Currency_depositeWithdraw_List.objects.filter(currency__symbol__contains=txt,bill_type="withdraw")
            bill4 = Currency_depositeWithdraw_List.objects.filter(currency__fa_title__contains=txt,bill_type="withdraw")
            bill5 = Currency_depositeWithdraw_List.objects.filter(currency__en_title__contains=txt,bill_type="withdraw")
            bill6 = Currency_depositeWithdraw_List.objects.filter(uname__first_name__contains=txt,bill_type="withdraw")
            bill7 = Currency_depositeWithdraw_List.objects.filter(uname__last_name__contains=txt,bill_type="withdraw")
            bill8 = Currency_depositeWithdraw_List.objects.filter(fee_amount__contains=txt,bill_type="withdraw")

            bills = list(chain(bill1,bill2,bill3,bill4,bill5,bill6,bill7,bill8))

            paginator = Paginator(list(dict.fromkeys(bills)),10)
            page = request.GET.get('page')

            try:
                querySet = paginator.page(page)
            except PageNotAnInteger:
                querySet = paginator.page(1)
            except EmptyPage:
                querySet = paginator.page(1)  

    return render(request, get_master_theme() + 'currency_withdrawal_list.html', {'querySet':querySet,'type':type})


def master_currency_withdrawal_handly_edit(request,pk):

    # master json check start
    try : 
        code=master_access_check(request)
        if code[0] != 100 : return JsonResponse({'type':'danger', 'msg':code[2]})
    except: return JsonResponse({'type':'danger', 'msg':'ورود شما منقضی شده لطفا مجددا وارد شوید'})
    # master json check end

    if request.method == "POST":

        status = request.POST.get('status')
        TranacrionId = request.POST.get('TranacrionId')

        if status == "None"  :
            return JsonResponse({'type':'danger', 'msg':'وارد کردن وضعیت الزامی است'})

        currency_handly_withdrawl = Currency_depositeWithdraw_List.objects.get(pk=pk)
        if status == "Success" : # success

            if  TranacrionId == "" or TranacrionId == "-" :
                return JsonResponse({'type':'danger', 'msg':'وارد کردن کد پیگیری '})

            translation_id =  TranacrionId.replace(' ', '')

            if  Currency_depositeWithdraw_List.objects.filter(bill_type="withdraw",hash_id = translation_id).exclude(pk=pk).count() != 0 :
                return JsonResponse({'type':'danger', 'msg':'کد پیگیری وارد شده معتبر نیست'})

            currency_handly_withdrawl.hash_id = TranacrionId.replace(' ', '')
            currency_handly_withdrawl.status = "Success"
            currency_handly_withdrawl.is_checked = True
            currency_handly_withdrawl.save()

        elif  status == "Rejected" :# reject

            currency_handly_withdrawl.status = "Rejected"
            currency_handly_withdrawl.is_checked = True
            currency_handly_withdrawl.save()

        elif  status == "Rejectedd" : # reject with return currency

            currency_handly_withdrawl.status = "Rejected"
            currency_handly_withdrawl.wallet_return = True
            currency_handly_withdrawl.is_checked = True
            currency_handly_withdrawl.save()

            currency_handly_withdrawl = Currency_depositeWithdraw_List.objects.get(pk=pk)

            time = get_date_time()['timestamp']

            wallet_back = Wallet.objects.get(pk=currency_handly_withdrawl.wallet_id)

            w = Wallet(

                uname = currency_handly_withdrawl.uname,
                wallet = currency_handly_withdrawl.currency.symbol,
                desc = f'بابت عدم تایید برداشت از کیف پول : {currency_handly_withdrawl.currency.fa_title}',
                amount = (wallet_back.amount) * (-1) ,
                datetime = time,
                confirmed_datetime = time,
                ip = get_ip(request),
                is_verify = True,

            )
            w.save()


        return JsonResponse({'type':'success', 'msg':' با موفقیت ویرایش  شد','hash':TranacrionId,'status':status})

    return JsonResponse({'type':'danger', 'msg':'پردازش مورد نظر با مشکل مواجه شده است'})


def master_currency_deposit_handly(request, type):

    # master check start
    try :
        code = master_access_check(request)
        if code[0] != 100 : return redirect(code[1])
    except: return redirect('master_login')
    # master check end


    if type == 'Success' :
        bill = Currency_depositeWithdraw_List.objects.filter(status='Success',bill_type="deposite",from_gateway=False).order_by('-pk')

    elif type == 'UnSuccess' :
        bill = Currency_depositeWithdraw_List.objects.filter(status='Rejected',bill_type="deposite",from_gateway=False).order_by('-pk')

    elif type == 'Pendding' :
        bill = Currency_depositeWithdraw_List.objects.filter(status='Pendding',bill_type="deposite",from_gateway=False).order_by('-pk')

    else :
        bill = Currency_depositeWithdraw_List.objects.filter(bill_type="deposite",from_gateway=False).order_by('-pk')

    paginator = Paginator(bill,10)
    page = request.GET.get('page')

    try:
        querySet = paginator.page(page)
    except PageNotAnInteger:
        querySet = paginator.page(1)
    except EmptyPage:
        querySet = paginator.page(1)


    return render(request, get_master_theme() + 'currency_deposite_list.html', {'querySet':querySet,'type':type})


def master_rial_deposit_handly(request, type):

    # master check start
    try :
        code = master_access_check(request)
        if code[0] != 100 : return redirect(code[1])
    except: return redirect('master_login')
    # master check end

    if type == 'Success' :
        bill = Online_Wallet.objects.filter(is_completed=True).order_by('-pk')[:500]

    elif type == 'UnSuccess' :
        bill = Online_Wallet.objects.filter(is_completed=False).exclude(error_mellipay="-").order_by('-pk')[:500]

    elif type == 'Pendding' :
        bill = Online_Wallet.objects.filter(is_completed=False,error_mellipay="-").order_by('-pk')[:500]

    else :
        bill = Online_Wallet.objects.all().order_by('-pk')[:500]

    paginator = Paginator(bill,10)
    page = request.GET.get('page')

    try:
        querySet = paginator.page(page)
    except PageNotAnInteger:
        querySet = paginator.page(1)
    except EmptyPage:
        querySet = paginator.page(1)


    return render(request, get_master_theme() + 'rial_deposite_list.html', {'querySet':querySet,'type':type})

def master_rial_deposit_handly_search(request, type):

    # master check start
    try:
        code = master_access_check(request)
        if code[0] != 100:
            return redirect(code[1])
    except:
        return redirect('master_login')
    # master check end

    txt = request.POST.get('txt', '').strip() if request.method == 'POST' else request.session.get('search', '').strip()
    request.session['search'] = txt  # Update session regardless of POST/GET

    bills = []

    # Define status filter based on the type
    status_filter = {
        'Success': True,
        'UnSuccess': False,
        'Pendding': 0
    }.get(type, None)

    # Build the query using Q objects
    query = Q()
    if txt:
        query |= Q(pk__contains=txt) | \
                 Q(amount__contains=txt) | \
                 Q(currency__symbol__contains=txt) | \
                 Q(currency__fa_title__contains=txt) | \
                 Q(currency__en_title__contains=txt) | \
                 Q(owner__first_name__contains=txt) | \
                 Q(owner__last_name__contains=txt)

    # Filter bills based on the constructed query and status
    if status_filter is not None:
        bills = Online_Wallet.objects.filter(query, is_completed=status_filter).distinct()
    else:
        bills = Online_Wallet.objects.filter(query).distinct()

    # Paginate the results
    paginator = Paginator(bills, 10)
    page = request.GET.get('page')

    try:
        querySet = paginator.page(page)
    except PageNotAnInteger:
        querySet = paginator.page(1)
    except EmptyPage:
        querySet = paginator.page(paginator.num_pages)  # Show last page if out of range

    return render(request, get_master_theme() + 'rial_deposite_list.html', {'querySet': querySet, 'type': type}) 

def master_currency_deposit_handly_edit(request,pk):

    # master json check start
    try : 
        code=master_access_check(request)
        if code[0] != 100 : return JsonResponse({'type':'danger', 'msg':code[2]})
    except: return JsonResponse({'type':'danger', 'msg':'ورود شما منقضی شده لطفا مجددا وارد شوید'})
    # master json check end

    if request.method == "POST":

        amount = request.POST.get('amount')
        TranacrionId = request.POST.get('TranacrionId')
        status = request.POST.get('status')

        if status == "None"  :
            return JsonResponse({'type':'danger', 'msg':'وارد کردن وضعیت الزامی است'})

        currency_handly_withdrawl = Currency_depositeWithdraw_List.objects.get(pk=pk)
        if status == "Success" : # success

            if TranacrionId == "":
                return JsonResponse({'type':'danger', 'msg':'وارد کردن کد پیگیری الزامی است'})

            try :
                amount = float(amount)
            except:
                return JsonResponse({'type':'danger', 'msg':'تعداد وارد شده صحیح نیست'})

            translation_id =  TranacrionId.replace(' ', '')

            if  Currency_depositeWithdraw_List.objects.filter(bill_type="deposite",hash_id = translation_id,status='Pendding').exclude(pk=pk).count() != 0   or Currency_depositeWithdraw_List.objects.filter(bill_type="deposite",hash_id = TranacrionId,status='Success').count() != 0   :
                return JsonResponse({'type':'danger', 'msg':'کد پیگیری وارد شده معتبر نیست'})

            currency_handly_withdrawl.amount = amount
            currency_handly_withdrawl.status = "Success"
            currency_handly_withdrawl.save()

            time = get_date_time()['timestamp']

            w = Wallet(

                uname = currency_handly_withdrawl.uname,
                wallet = currency_handly_withdrawl.currency.symbol,
                desc = f'بابت تایید درخواست واریز طلا : {currency_handly_withdrawl.currency.fa_title}',
                amount = amount ,
                datetime = time,
                confirmed_datetime = time,
                ip = get_ip(request),
                is_verify = True,

            )
            w.save()


        elif  status == "Rejected" :

            currency_handly_withdrawl.status = "Rejected"
            currency_handly_withdrawl.save()


        return JsonResponse({'type':'success', 'msg':' با موفقیت ویرایش  شد','hash':TranacrionId,'status':status})

    return JsonResponse({'type':'danger', 'msg':'پردازش  مورد نظر با مشکل مواجه شده است'})



def master_all_currency_balance(request):

    # master check start
    try :
        code = master_access_check(request)
        if code[0] != 100 : return redirect(code[1])
    except: return redirect('master_login')
    # master check end


    paginator = Paginator(Account_Balance_log.objects.all().order_by('-pk')[:14400],15)
    page = request.GET.get('page')

    try:
        querySet = paginator.page(page)
    except PageNotAnInteger:
        querySet = paginator.page(1)
    except EmptyPage:
        querySet = paginator.page(1)

    return render(request, get_master_theme() + 'all_currency_balance.html', {'today':get_date_time()['shamsi_date'],'querySet':querySet,'currency':Currency_List.objects.all()})



def master_all_currency_price(request):

    # master check start
    try :
        code = master_access_check(request)
        if code[0] != 100 : return redirect(code[1])
    except: return redirect('master_login')
    # master check end


    paginator = Paginator(Account_Price_log.objects.all().order_by('-pk')[:14400],15)
    page = request.GET.get('page')

    try:
        querySet = paginator.page(page)
    except PageNotAnInteger:
        querySet = paginator.page(1)
    except EmptyPage:
        querySet = paginator.page(1)


    return render(request, get_master_theme() + 'all_currency_price.html', {'querySet':querySet})
    
def master_all_currency_price_search(request):

    # master check start
    try :
        code = master_access_check(request)
        if code[0] != 100 : return redirect(code[1])
    except: return redirect('master_login')
    # master check end

    currencys = []
    txt = "-"

    if request.method == 'POST':

        txt = request.POST.get('txt')

        request.session['search'] = txt

        currency1 = Account_Price_log.objects.filter(pk__contains=txt).order_by('-pk')
        currency2 = Account_Price_log.objects.filter(symbol__contains=txt).order_by('-pk')
        currency3 = Account_Price_log.objects.filter(acc__contains=txt).order_by('-pk')
        currency4 = Account_Price_log.objects.filter(buy__contains=txt).order_by('-pk')
        currency5 = Account_Price_log.objects.filter(sell__contains=txt).order_by('-pk')

        currencys = list(chain(currency1,currency2,currency3,currency4,currency5))

        paginator = Paginator(list(dict.fromkeys(currencys)),10)
        page = request.GET.get('page')

        try:
            querySet = paginator.page(page)
        except PageNotAnInteger:
            querySet = paginator.page(1)
        except EmptyPage:
            querySet = paginator.page(1)

    else:

        txt = request.session['search']

        currency1 = Account_Price_log.objects.filter(pk__contains=txt).order_by('-pk')
        currency2 = Account_Price_log.objects.filter(symbol__contains=txt).order_by('-pk')
        currency3 = Account_Price_log.objects.filter(acc__contains=txt).order_by('-pk')
        currency4 = Account_Price_log.objects.filter(buy__contains=txt).order_by('-pk')
        currency5 = Account_Price_log.objects.filter(sell__contains=txt).order_by('-pk')

        currencys = list(chain(currency1,currency2,currency3,currency4,currency5))

        paginator = Paginator(list(dict.fromkeys(currencys)),10)
        page = request.GET.get('page')

        try:
            querySet = paginator.page(page)
        except PageNotAnInteger:
            querySet = paginator.page(1)
        except EmptyPage:
            querySet = paginator.page(1)

    return render(request, get_master_theme() + 'all_currency_price.html', {'querySet':querySet})

def master_all_currency_balance_search(request):

    # master json check start
    try : 
        code=master_access_check(request)
        if code[0] != 100 : return JsonResponse({'type':'danger', 'msg':code[2]})
    except: return JsonResponse({'type':'danger', 'msg':'ورود شما منقضی شده لطفا مجددا وارد شوید'})
    # master json check end

    querySet = []

    if request.method == "POST":

        start_date = request.POST.get('date-picker-shamsi')
        start_time = request.POST.get('start_time')
        end_date = request.POST.get('date-picker-shamsi-1')
        end_time = request.POST.get('end_time')
        arz = request.POST.get('currency')

        if start_date == "" or start_date == None or  start_date == "None" :
            return JsonResponse({'type':'danger', 'msg':'وارد کردن اولین تاریخ جستجو الزامی است'})

        if start_time == "" or start_time == None or  start_time == "None" :
            return JsonResponse({'type':'danger', 'msg':'وارد کردن اولین ساعت جستجو الزامی است'})

        try :
            sdata = start_date.split('/')
            newdata = khayyam.JalaliDate(sdata[0], sdata[1], sdata[2]).todate()
            newdata = str(newdata).split('-')

            earlier = newdata[0] + '-' + newdata[1] + '-' + newdata[2] + f' {start_time}:00'
            start_date = int(datetime.strptime(earlier,"%Y-%m-%d %H:%M:%S").timestamp())

        except:
            return JsonResponse({'type':'danger', 'msg':'تاریخ وارد شده نامعتبر است'})

        try :

            if end_date == "" or end_date == None or  end_date == "None" :

                end_date = datetime.strptime(earlier,"%Y-%m-%d %H:%M:%S") +  timedelta(days=(31))
                end_date = int(datetime.strptime(str(end_date),"%Y-%m-%d %H:%M:%S").timestamp())

            else :

                if  end_time == "" or end_time == None or  end_time == "None" :
                    return JsonResponse({'type':'danger', 'msg':'وارد کردن  ساعت جستجو الزامی است'})

                sdata = end_date.split('/')
                newdata = khayyam.JalaliDate(sdata[0], sdata[1], sdata[2]).todate()
                newdata = str(newdata).split('-')
                last = newdata[0] + '-' + newdata[1] + '-' + newdata[2] + f' {end_time}:00'
                end_date = int(datetime.strptime(last,"%Y-%m-%d %H:%M:%S").timestamp())

                days_later = datetime.strptime(earlier,"%Y-%m-%d %H:%M:%S") +  timedelta(days=(31))
                days_later = int(datetime.strptime(str(days_later),"%Y-%m-%d %H:%M:%S").timestamp())

                if end_date >  days_later :
                    return JsonResponse({'type':'danger', 'msg':'حداکثر فاصله زمانی جستجو یک ماه است'})

        except:  return JsonResponse({'type':'danger', 'msg':'خطایی رخ داده است'})
       
        
        request.session['date-picker-shamsi'] = start_date
        request.session['start_time'] = start_time
        request.session['date-picker-shamsii'] = end_date
        request.session['end_time'] = end_time
        request.session['currency'] = arz
        

        if arz == "0" :
            balance = Account_Balance_log.objects.filter(date__gte=start_date,date__lte=end_date).order_by('-pk')
        else :
            balance = Account_Balance_log.objects.filter(date__gte=start_date,date__lte=end_date,symbol=arz).order_by('-pk')

        request.session['balance'] = balance    

        paginator = Paginator(balance,10)
        page = request.GET.get('page')

        try:
            querySet = paginator.page(page)
        except PageNotAnInteger:
            querySet = paginator.page(1)
        except EmptyPage:
            querySet = paginator.page(1)

    
    else:


        balance = request.session['balance'] 

        paginator = Paginator(balance,10)
        page = request.GET.get('page')

        try:
            querySet = paginator.page(page)
        except PageNotAnInteger:
            querySet = paginator.page(1)
        except EmptyPage:
            querySet = paginator.page(1)


    return JsonResponse({'type':'success','today':get_date_time()['shamsi_date'],'querySet' : querySet})
    
 
def master_currency_deposite_search(request):
    
    # master check start
    try :
        code = master_access_check(request)
        if code[0] != 100 : return redirect(code[1])
    except: return redirect('master_login')
    # master check end

    querySet = []
    txt = "-"

    if request.method == 'POST':
        
        txt = request.POST.get('txt')
        status = request.POST.get('status')

        if txt != "" and status != "0" :

            request.session['search'] = txt
            request.session['status'] = status

            querySet3 = Currency_depositeWithdraw_List.objects.filter(hash_id__contains=txt,status=status,bill_type="deposite")
            
            paginator = Paginator(querySet3,10)
            page = request.GET.get('page')

            try:
                querySet = paginator.page(page)
            except PageNotAnInteger:
                querySet = paginator.page(1)
            except EmptyPage:
                querySet = paginator.page(1) 
        
        elif txt != "" and status == "0" :

            request.session['search'] = txt
            request.session['status'] = status

            querySet3 = Currency_depositeWithdraw_List.objects.filter(hash_id__contains=txt,bill_type="deposite")
            
            
            paginator = Paginator(querySet3,10)
            page = request.GET.get('page')

            try:
                querySet = paginator.page(page)
            except PageNotAnInteger:
                querySet = paginator.page(1)
            except EmptyPage:
                querySet = paginator.page(1) 
        
        elif txt == "" and status != "0" :

            request.session['search'] = "None"
            request.session['status'] = status

            querySet3 = Currency_depositeWithdraw_List.objects.filter(status=status,bill_type="deposite")
            
            
            paginator = Paginator(querySet3,10)
            page = request.GET.get('page')

            try:
                querySet = paginator.page(page)
            except PageNotAnInteger:
                querySet = paginator.page(1)
            except EmptyPage:
                querySet = paginator.page(1) 


    else:

        try:

            txt = request.session['search']
            status = request.session['status'] 

            if txt != "None" and status != "0" :

                querySet3 = Currency_depositeWithdraw_List.objects.filter(hash_id__contains=txt,status=status,bill_type="deposite")
                
                
                paginator = Paginator(querySet3,10)
                page = request.GET.get('page')

                try:
                    querySet = paginator.page(page)
                except PageNotAnInteger:
                    querySet = paginator.page(1)
                except EmptyPage:
                    querySet = paginator.page(1)   

            elif txt != "None" and status == "0":  

                querySet3 = Currency_depositeWithdraw_List.objects.filter(hash_id__contains=txt,bill_type="deposite")
                
                
                paginator = Paginator(querySet3,10)
                page = request.GET.get('page')

                try:
                    querySet = paginator.page(page)
                except PageNotAnInteger:
                    querySet = paginator.page(1)
                except EmptyPage:
                    querySet = paginator.page(1) 

            elif txt == "None" and status != "0":

                querySet3 = Currency_depositeWithdraw_List.objects.filter(status=status,bill_type="deposite")
                
                
                paginator = Paginator(querySet3,10)
                page = request.GET.get('page')

                try:
                    querySet = paginator.page(page)
                except PageNotAnInteger:
                    querySet = paginator.page(1)
                except EmptyPage:
                    querySet = paginator.page(1) 


        except:  
            pass

    return render(request, get_master_theme() + 'deposite_search.html', {'querySet':querySet})
    
    
  
  
def master_currency_deposit_gateway(request, type):

    # master check start
    try :
        code = master_access_check(request)
        if code[0] != 100 : return redirect(code[1])
    except: return redirect('master_login')
    # master check end


    if type == 'Success' :
        bill = Currency_depositeWithdraw_List.objects.filter(status='Success',bill_type="deposite",from_gateway=True).order_by('-pk')

    elif type == 'UnSuccess' :
        bill = Currency_depositeWithdraw_List.objects.filter(status='Rejected',bill_type="deposite",from_gateway=True).order_by('-pk')

    elif type == 'Pendding' :
        bill = Currency_depositeWithdraw_List.objects.filter(status='Pendding',bill_type="deposite",from_gateway=True).order_by('-pk')

    else :
        bill = Currency_depositeWithdraw_List.objects.filter(bill_type="deposite",from_gateway=True).order_by('-pk')

    paginator = Paginator(bill,10)
    page = request.GET.get('page')

    try:
        querySet = paginator.page(page)
    except PageNotAnInteger:
        querySet = paginator.page(1)
    except EmptyPage:
        querySet = paginator.page(1)


    return render(request, get_master_theme() + 'currency_deposite_list_gateway.html', {'querySet':querySet,'type':type})     



def master_currency_direct_wallet(request,wid,pk):

    # master check start
    try :
        code = master_access_check(request)
        if code[0] != 100 : return redirect(code[1])
    except: return redirect('master_login')
    # master check end

    currency = Currency_List.objects.get(pk=wid)

    list_chain_currency = list(set(Currency_Chain.objects.filter(symbol=currency).values_list('chain', flat=True)))

    direct_wallet = Wallet_direct.objects.filter(uname=Customer.objects.get(pk=pk),chain__in=list_chain_currency).order_by('pk')

    paginator = Paginator(direct_wallet,10)
    page = request.GET.get('page')

    try:
        direct_wallet = paginator.page(page)
    except PageNotAnInteger:
        direct_wallet = paginator.page(1)
    except EmptyPage:
        direct_wallet = paginator.page(1)

    return render(request, get_master_theme() + 'currency_wallet_direct.html',{'querySet':direct_wallet,'currency':currency,'customer':pk})   




    
    
    
    
    
    
    
    

def master_transfer_list(request, type):

    # master check start
    try :
        code = master_access_check(request)
        if code[0] != 100 : return redirect(code[1])
    except: return redirect('master_login')
    # master check end


    if type == 'Success' :
        bill = Currency_Transfer_List.objects.filter(status='Success').order_by('-pk')

    elif type == 'UnSuccess' :
        bill = Currency_Transfer_List.objects.filter(status='Rejected').order_by('-pk')

    elif type == 'Pendding' :
        bill = Currency_Transfer_List.objects.filter(status='Pendding').order_by('-pk')

    else :
        bill = Currency_Transfer_List.objects.all().order_by('-pk')


    paginator = Paginator(bill,10)
    page = request.GET.get('page')

    try:
        querySet = paginator.page(page)
    except PageNotAnInteger:
        querySet = paginator.page(1)
    except EmptyPage:
        querySet = paginator.page(1)


    return render(request, get_master_theme() + 'transfer_list.html', {'querySet':querySet,'type':type})

def master_transfer_search(request,type):

    bills = []
    txt = "-"

    if type == 'Success' :

        if request.method == 'POST':
            
            txt = request.POST.get('txt')

            request.session['search'] = txt

            bill1 = Currency_Transfer_List.objects.filter(pk__contains=txt,status='Success')
            bill2 = Currency_Transfer_List.objects.filter(currency__symbol__contains=txt,status='Success')
            bill3 = Currency_Transfer_List.objects.filter(currency__fa_title__contains=txt,status='Success')
            bill4 = Currency_Transfer_List.objects.filter(currency__en_title__contains=txt,status='Success')
            bill5 = Currency_Transfer_List.objects.filter(uname__first_name__contains=txt,status='Success')
            bill6 = Currency_Transfer_List.objects.filter(uname__last_name__contains=txt,status='Success')
            bill7 = Currency_Transfer_List.objects.filter(fee_amount__contains=txt,status='Success')
            bill8 = Currency_Transfer_List.objects.filter(amount__contains=txt,status='Success')
            bill9 = Currency_Transfer_List.objects.filter(reciever_id__contains=txt,status='Success')

            bills = list(chain(bill1,bill2,bill3,bill4,bill5,bill6,bill7,bill8,bill9))

            paginator = Paginator(list(dict.fromkeys(bills)),10)
            page = request.GET.get('page')

            try:
                querySet = paginator.page(page)
            except PageNotAnInteger:
                querySet = paginator.page(1)
            except EmptyPage:
                querySet = paginator.page(1) 

        else:

            txt = request.session['search']
        
            bill1 = Currency_Transfer_List.objects.filter(pk__contains=txt,status='Success')
            bill2 = Currency_Transfer_List.objects.filter(amount__contains=txt,status='Success')
            bill3 = Currency_Transfer_List.objects.filter(currency__symbol__contains=txt,status='Success')
            bill4 = Currency_Transfer_List.objects.filter(currency__fa_title__contains=txt,status='Success')
            bill5 = Currency_Transfer_List.objects.filter(currency__en_title__contains=txt,status='Success')
            bill6 = Currency_Transfer_List.objects.filter(uname__first_name__contains=txt,status='Success')
            bill7 = Currency_Transfer_List.objects.filter(uname__last_name__contains=txt,status='Success')
            bill8 = Currency_Transfer_List.objects.filter(fee_amount__contains=txt,status='Success')
            bill9 = Currency_Transfer_List.objects.filter(reciever_id__contains=txt,status='Success')

            bills = list(chain(bill1,bill2,bill3,bill4,bill5,bill6,bill7,bill8,bill9))

            paginator = Paginator(list(dict.fromkeys(bills)),10)
            page = request.GET.get('page')

            try:
                querySet = paginator.page(page)
            except PageNotAnInteger:
                querySet = paginator.page(1)
            except EmptyPage:
                querySet = paginator.page(1)    

    elif type == 'UnSuccess' :

        if request.method == 'POST':
            
            txt = request.POST.get('txt')

            request.session['search'] = txt

            bill1 = Currency_Transfer_List.objects.filter(pk__contains=txt,status='Rejected')
            bill2 = Currency_Transfer_List.objects.filter(amount__contains=txt,status='Rejected')
            bill3 = Currency_Transfer_List.objects.filter(currency__symbol__contains=txt,status='Rejected')
            bill4 = Currency_Transfer_List.objects.filter(currency__fa_title__contains=txt,status='Rejected')
            bill5 = Currency_Transfer_List.objects.filter(currency__en_title__contains=txt,status='Rejected')
            bill6 = Currency_Transfer_List.objects.filter(uname__first_name__contains=txt,status='Rejected')
            bill7 = Currency_Transfer_List.objects.filter(uname__last_name__contains=txt,status='Rejected')
            bill8 = Currency_Transfer_List.objects.filter(fee_amount__contains=txt,status='Rejected')
            bill9 = Currency_Transfer_List.objects.filter(reciever_id__contains=txt,status='Rejected')

            bills = list(chain(bill1,bill2,bill3,bill4,bill5,bill6,bill7,bill8,bill9))

            paginator = Paginator(list(dict.fromkeys(bills)),10)
            page = request.GET.get('page')

            try:
                querySet = paginator.page(page)
            except PageNotAnInteger:
                querySet = paginator.page(1)
            except EmptyPage:
                querySet = paginator.page(1) 

        else:

            txt = request.session['search']
        
            bill1 = Currency_Transfer_List.objects.filter(pk__contains=txt,status='Rejected')
            bill2 = Currency_Transfer_List.objects.filter(amount__contains=txt,status='Rejected')
            bill3 = Currency_Transfer_List.objects.filter(currency__symbol__contains=txt,status='Rejected')
            bill4 = Currency_Transfer_List.objects.filter(currency__fa_title__contains=txt,status='Rejected')
            bill5 = Currency_Transfer_List.objects.filter(currency__en_title__contains=txt,status='Rejected')
            bill6 = Currency_Transfer_List.objects.filter(uname__first_name__contains=txt,status='Rejected')
            bill7 = Currency_Transfer_List.objects.filter(uname__last_name__contains=txt,status='Rejected')
            bill8 = Currency_Transfer_List.objects.filter(fee_amount__contains=txt,status='Rejected')
            bill9 = Currency_Transfer_List.objects.filter(reciever_id__contains=txt,status='Rejected')

            bills = list(chain(bill1,bill2,bill3,bill4,bill5,bill6,bill7,bill8,bill9))

            paginator = Paginator(list(dict.fromkeys(bills)),10)
            page = request.GET.get('page')

            try:
                querySet = paginator.page(page)
            except PageNotAnInteger:
                querySet = paginator.page(1)
            except EmptyPage:
                querySet = paginator.page(1)  

    elif type == 'Pendding' :  

        if request.method == 'POST':
            
            txt = request.POST.get('txt')

            request.session['search'] = txt

            bill1 = Currency_Transfer_List.objects.filter(pk__contains=txt,status='Pendding')
            bill2 = Currency_Transfer_List.objects.filter(amount__contains=txt,status='Pendding')
            bill3 = Currency_Transfer_List.objects.filter(currency__symbol__contains=txt,status='Pendding')
            bill4 = Currency_Transfer_List.objects.filter(currency__fa_title__contains=txt,status='Pendding')
            bill5 = Currency_Transfer_List.objects.filter(currency__en_title__contains=txt,status='Pendding')
            bill6 = Currency_Transfer_List.objects.filter(uname__first_name__contains=txt,status='Pendding')
            bill7 = Currency_Transfer_List.objects.filter(uname__last_name__contains=txt,status='Pendding')
            bill8 = Currency_Transfer_List.objects.filter(fee_amount__contains=txt,status='Pendding')
            bill9 = Currency_Transfer_List.objects.filter(reciever_id__contains=txt,status='Pendding')

            bills = list(chain(bill1,bill2,bill3,bill4,bill5,bill6,bill7,bill8,bill9))

            paginator = Paginator(list(dict.fromkeys(bills)),10)
            page = request.GET.get('page')

            try:
                querySet = paginator.page(page)
            except PageNotAnInteger:
                querySet = paginator.page(1)
            except EmptyPage:
                querySet = paginator.page(1) 

        else:

            txt = request.session['search']
        
            bill1 = Currency_Transfer_List.objects.filter(pk__contains=txt,status='Pendding')
            bill2 = Currency_Transfer_List.objects.filter(amount__contains=txt,status='Pendding')
            bill3 = Currency_Transfer_List.objects.filter(currency__symbol__contains=txt,status='Pendding')
            bill4 = Currency_Transfer_List.objects.filter(currency__fa_title__contains=txt,status='Pendding')
            bill5 = Currency_Transfer_List.objects.filter(currency__en_title__contains=txt,status='Pendding')
            bill6 = Currency_Transfer_List.objects.filter(uname__first_name__contains=txt,status='Pendding')
            bill7 = Currency_Transfer_List.objects.filter(uname__last_name__contains=txt,status='Pendding')
            bill8 = Currency_Transfer_List.objects.filter(fee_amount__contains=txt,status='Pendding')
            bill9 = Currency_Transfer_List.objects.filter(reciever_id__contains=txt,status='Pendding')

            bills = list(chain(bill1,bill2,bill3,bill4,bill5,bill6,bill7,bill8,bill9))

            paginator = Paginator(list(dict.fromkeys(bills)),10)
            page = request.GET.get('page')

            try:
                querySet = paginator.page(page)
            except PageNotAnInteger:
                querySet = paginator.page(1)
            except EmptyPage:
                querySet = paginator.page(1)  

    else :
        if request.method == 'POST':
            
            txt = request.POST.get('txt')

            request.session['search'] = txt

            bill1 = Currency_Transfer_List.objects.filter(pk__contains=txt)
            bill2 = Currency_Transfer_List.objects.filter(amount__contains=txt)
            bill3 = Currency_Transfer_List.objects.filter(currency__symbol__contains=txt)
            bill4 = Currency_Transfer_List.objects.filter(currency__fa_title__contains=txt)
            bill5 = Currency_Transfer_List.objects.filter(currency__en_title__contains=txt)
            bill6 = Currency_Transfer_List.objects.filter(uname__first_name__contains=txt)
            bill7 = Currency_Transfer_List.objects.filter(uname__last_name__contains=txt)
            bill8 = Currency_Transfer_List.objects.filter(fee_amount__contains=txt)
            bill9 = Currency_Transfer_List.objects.filter(reciever_id__contains=txt)

            bills = list(chain(bill1,bill2,bill3,bill4,bill5,bill6,bill7,bill8,bill9))

            paginator = Paginator(list(dict.fromkeys(bills)),10)
            page = request.GET.get('page')

            try:
                querySet = paginator.page(page)
            except PageNotAnInteger:
                querySet = paginator.page(1)
            except EmptyPage:
                querySet = paginator.page(1) 

        else:

            txt = request.session['search']
        
            bill1 = Currency_Transfer_List.objects.filter(pk__contains=txt)
            bill2 = Currency_Transfer_List.objects.filter(amount__contains=txt)
            bill3 = Currency_Transfer_List.objects.filter(currency__symbol__contains=txt)
            bill4 = Currency_Transfer_List.objects.filter(currency__fa_title__contains=txt)
            bill5 = Currency_Transfer_List.objects.filter(currency__en_title__contains=txt)
            bill6 = Currency_Transfer_List.objects.filter(uname__first_name__contains=txt)
            bill7 = Currency_Transfer_List.objects.filter(uname__last_name__contains=txt)
            bill8 = Currency_Transfer_List.objects.filter(fee_amount__contains=txt)
            bill9 = Currency_Transfer_List.objects.filter(reciever_id__contains=txt)

            bills = list(chain(bill1,bill3,bill4,bill5,bill6,bill7,bill8,bill9))

            paginator = Paginator(list(dict.fromkeys(bills)),10)
            page = request.GET.get('page')

            try:
                querySet = paginator.page(page)
            except PageNotAnInteger:
                querySet = paginator.page(1)
            except EmptyPage:
                querySet = paginator.page(1)  

    return render(request, get_master_theme() + 'transfer_list.html', {'querySet':querySet,'type':type})




def master_buySell_custom_price_list(request, type):

    # master check start
    try :
        code = master_access_check(request)
        if code[0] != 100 : return redirect(code[1])
    except: return redirect('master_login')
    # master check end

    if type == 'Pendding': bill = Currency_BuySell_Custom_Price.objects.filter(status='Pendding',process_based_on='price').order_by('-pk')
    elif type == 'Success': bill = Currency_BuySell_Custom_Price.objects.filter(status='Success',process_based_on='price').order_by('-pk')
    elif type == 'UnSuccess': bill = Currency_BuySell_Custom_Price.objects.filter(status='Rejected',process_based_on='price').order_by('-pk')
    elif type == 'Canceled': bill = Currency_BuySell_Custom_Price.objects.filter(status='Canceled',process_based_on='price').order_by('-pk')
    else: bill = Currency_BuySell_Custom_Price.objects.filter(process_based_on='price').order_by('-pk')

    paginator = Paginator(bill,10)
    page = request.GET.get('page')
    try: querySet = paginator.page(page)
    except PageNotAnInteger: querySet = paginator.page(1)
    except EmptyPage: querySet = paginator.page(1)

    return render(request, get_master_theme() + 'buySel_custom_price_list.html', {'querySet':querySet,'type':type})




def master_buySell_custom_price_search(request, type):

    # master check start
    try:
        code = master_access_check(request)
        if code[0] != 100:
            return redirect(code[1])
    except:
        return redirect('master_login')
    # master check end

    txt = "-"
    buysells = []
    querySet = [] 

    if request.method == 'POST':
        txt = request.POST.get('txt', '').strip() 
        request.session['search'] = txt
    else:
        txt = request.session.get('search', '').strip() 

   
    if txt:
        if type == 'Success':
            status_filter = ['Success']
        elif type == 'UnSuccess':
            status_filter = ['Rejected']
        elif type == 'Pendding':
            status_filter = ['Pendding']
        elif type == 'Canceled':
            status_filter = ['Canceled']
        else:
            status_filter = [] 

        query = Q(pk__contains=txt) | \
                Q(acc__contains=txt) | \
                Q(currency__symbol__contains=txt) | \
                Q(currency__fa_title__contains=txt) |  \
                Q(currency__en_title__contains=txt) | \
                Q(uname__first_name__contains=txt) | \
                Q(uname__last_name__contains=txt) | \
                Q(amount__contains=txt) | \
                Q(fee_amount__contains=txt) 

        if status_filter:
            buysells = Currency_BuySell_Custom_Price.objects.filter(query, status__in=status_filter,process_based_on='price').distinct()
        else:

            buysells = Currency_BuySell_Custom_Price.objects.filter(query,process_based_on='price').distinct()

        paginator = Paginator(buysells, 10)
        page = request.GET.get('page')

        try:
            querySet = paginator.page(page)
        except PageNotAnInteger:
            querySet = paginator.page(1)
        except EmptyPage:
            querySet = paginator.page(1)

    return render(request, get_master_theme() + 'buySel_custom_price_list.html', {'querySet':querySet,'type':type})





def master_buySell_custom_datetime_list(request, type):

    # master check start
    try :
        code = master_access_check(request)
        if code[0] != 100 : return redirect(code[1])
    except: return redirect('master_login')
    # master check end

    if type == 'Pendding': bill = Currency_BuySell_Custom_Price.objects.filter(status='Pendding',process_based_on='datetime').order_by('-pk')
    elif type == 'Success': bill = Currency_BuySell_Custom_Price.objects.filter(status='Success',process_based_on='datetime').order_by('-pk')
    elif type == 'UnSuccess': bill = Currency_BuySell_Custom_Price.objects.filter(status='Rejected',process_based_on='datetime').order_by('-pk')
    elif type == 'Canceled': bill = Currency_BuySell_Custom_Price.objects.filter(status='Canceled',process_based_on='datetime').order_by('-pk')
    else: bill = Currency_BuySell_Custom_Price.objects.filter(process_based_on='datetime').order_by('-pk')

    paginator = Paginator(bill,10)
    page = request.GET.get('page')
    try: querySet = paginator.page(page)
    except PageNotAnInteger: querySet = paginator.page(1)
    except EmptyPage: querySet = paginator.page(1)

    return render(request, get_master_theme() + 'buySel_custom_datetime_list.html', {'querySet':querySet,'type':type})




def master_buySell_custom_datetime_search(request, type):

    # master check start
    try:
        code = master_access_check(request)
        if code[0] != 100:
            return redirect(code[1])
    except:
        return redirect('master_login')
    # master check end

    txt = "-"
    buysells = []
    querySet = [] 

    if request.method == 'POST':
        txt = request.POST.get('txt', '').strip() 
        request.session['search'] = txt
    else:
        txt = request.session.get('search', '').strip() 

   
    if txt:
        if type == 'Success':
            status_filter = ['Success']
        elif type == 'UnSuccess':
            status_filter = ['Rejected']
        elif type == 'Pendding':
            status_filter = ['Pendding']
        elif type == 'Canceled':
            status_filter = ['Canceled']
        else:
            status_filter = [] 

        query = Q(pk__contains=txt) | \
                Q(acc__contains=txt) | \
                Q(currency__symbol__contains=txt) | \
                Q(currency__fa_title__contains=txt) |  \
                Q(currency__en_title__contains=txt) | \
                Q(uname__first_name__contains=txt) | \
                Q(uname__last_name__contains=txt) | \
                Q(amount__contains=txt) | \
                Q(fee_amount__contains=txt) 

        if status_filter:
            buysells = Currency_BuySell_Custom_Price.objects.filter(query, status__in=status_filter,process_based_on='datetime').distinct()
        else:

            buysells = Currency_BuySell_Custom_Price.objects.filter(query,process_based_on='datetime').distinct()

        paginator = Paginator(buysells, 10)
        page = request.GET.get('page')

        try:
            querySet = paginator.page(page)
        except PageNotAnInteger:
            querySet = paginator.page(1)
        except EmptyPage:
            querySet = paginator.page(1)

    return render(request, get_master_theme() + 'buySel_custom_datetime_list.html', {'querySet':querySet,'type':type})


def master_daily_buysell_list(request, bills_type):

    # master check start
    try :
        code = master_access_check(request)
        if code[0] != 100 : return redirect(code[1])
    except: return redirect('master_login')
    # master check end

    quary = Currency_BuySell_List.objects.filter(is_daily_buysell=True)

    if bills_type == 'Pendding': 
        bills = quary.filter(status='Pendding').order_by('-pk')

    elif bills_type == 'Success': 
        bills = quary.filter(status='Success').order_by('-pk')

    elif bills_type == 'Rejected': 
        bills = quary.filter(status='Rejected').order_by('-pk')

    else: 
        bills = quary.order_by('-pk')

    paginator = Paginator(bills,10)
    page = request.GET.get('page')
    try: querySet = paginator.page(page)
    except PageNotAnInteger: querySet = paginator.page(1)
    except EmptyPage: querySet = paginator.page(1)

    return render(
        request, get_master_theme() + 'buySel_daily_list.html', 
        {
            'querySet':querySet, 
            'type':bills_type,
        }
    )

def master_daily_buysell_search(request, bills_type):

    # master check start
    try:
        code = master_access_check(request)
        if code[0] != 100:
            return redirect(code[1])
    except:
        return redirect('master_login')
    # master check end


    txt = "-"
    buysells = []
    querySet = []


    if request.method == 'POST':
        txt = request.POST.get('txt', '').strip() 
        request.session['search'] = txt
        
    else:
        txt = request.session.get('search', '').strip() 

    
    if txt:
        if bills_type == 'Success':
            status_filter = ['Success']
        elif bills_type == 'UnSuccess':
            status_filter = ['Rejected']
        elif bills_type == 'Pendding':
            status_filter = ['Pendding']
        elif bills_type == 'Canceled':
            status_filter = ['Canceled']
        else:
            status_filter = [] 

        query = Q(pk__contains=txt) | \
                Q(acc__contains=txt) | \
                Q(currency__symbol__contains=txt) | \
                Q(currency__fa_title__contains=txt) |  \
                Q(currency__en_title__contains=txt) | \
                Q(uname__first_name__contains=txt) | \
                Q(uname__last_name__contains=txt) | \
                Q(amount__contains=txt) | \
                Q(fee_amount__contains=txt) 

        if status_filter:
            buysells = Currency_BuySell_List.objects.filter(query,is_daily_buysell=True,status__in=status_filter).distinct().order_by('-pk')
            
        else:
            buysells = Currency_BuySell_List.objects.filter(query,is_daily_buysell=True).distinct().order_by('-pk')


        paginator = Paginator(buysells, 10)
        page = request.GET.get('page')

        try:
            querySet = paginator.page(page)
        except PageNotAnInteger:
            querySet = paginator.page(1)
        except EmptyPage:
            querySet = paginator.page(1)

    return render(request, get_master_theme() + 'buySel_daily_list.html', {'querySet':querySet,'type':bills_type})
            


