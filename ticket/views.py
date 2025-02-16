from django.shortcuts import render

# Create your views here.
from django.shortcuts import render

# Create your views here.
from csv import excel_tab
from pprint import pprint
from webbrowser import get
from django.shortcuts import render, get_object_or_404, redirect
from django.core.files.storage import FileSystemStorage
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User , Group , Permission
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse, JsonResponse
from currency.models import *
from exchange.func.theme import *
from master.func.access import master_access_check
from .models import *
from exchange.func.public import *
import time
from customer.func.access import *

from khayyam import *
import jdatetime
from itertools import chain, count
import datetime
from datetime import datetime
from django.http import QueryDict
from django.db.models import Q
from django.utils.html import escape

# Create your views here.

def customer_ticket(request):

    # customer check start
    try :
        pattern_url = customer_access_check(request)
        if pattern_url[0] != 100 : return redirect(pattern_url[1])
    except: return redirect('account')
    # customer check end

    customer = pattern_url[2]
    waitting_count = Ticket.objects.filter(customer=customer,status="Waitting").count()
    answered_count = Ticket.objects.filter(customer=customer,status="Answered").count()
    closed_count = Ticket.objects.filter(customer=customer,status="Closed").count()
    tickets = Ticket.objects.filter(customer=customer).order_by('-pk')
    all_count = tickets.count()
    departments = TICKETDEPARTMENT


    paginator = Paginator(tickets,10)
    page = request.GET.get('page')

    try:
        ticket = paginator.page(page)
    except PageNotAnInteger:
        ticket = paginator.page(1)
    except EmptyPage:
        ticket = paginator.page(paginator.num_page) 



    return render(request, get_customer_theme(pattern_url[2]) + 'ticket.html', {'ticket':ticket, 'departments':departments, 'all_count':all_count, 'waitting_count':waitting_count, 'answered_count':answered_count, 'closed_count':closed_count,'ticket_count':tickets.count()})


def customer_ticket_modify_submit(request):

    # customer check start
    try :
        pattern_url = customer_access_check(request)
        if pattern_url[0] != 100 : return redirect(pattern_url[1])
    except: return redirect('account')
    # customer check end
    
    if request.method == 'POST' :

        title = request.POST.get('title')
        department = request.POST.get('department')
        desc = request.POST.get('desc')
        file_ticket = request.POST.get('file_ticket')
        customer = pattern_url[2]

        if title == "" or desc == "":
            return JsonResponse({'type':'danger', 'msg':'لطفا موارد خواسته شده را وارد نمایید'})
        
        if len(title) > 50 :
            return JsonResponse({'type':'danger', 'msg':'عنوان تیکت نمیتواند بیشتر از ۵۰ کاراکتر باشد'})


        if department == "select" :
            return JsonResponse({'type':'danger', 'msg':'لطفا دپارتمان تیکت را انتحاب نمایید'})

        if Ticket.objects.filter(customer=customer, status='Waitting', department=department).count() != 0 or  Ticket.objects.filter(customer=customer, status='Answered', department=department).count() != 0 :
            return JsonResponse({'type':'danger', 'msg':'شما یک تیکت در انتظار پیگیری دارید لطفا شکیبا باشید.'})
            
        if file_ticket != "":
            try :
                uploader = upload_file(request.FILES['file_ticket'],'usermedia/tickets', False)
                if uploader[0] != True : return JsonResponse({'type':'danger', 'msg':uploader[1]})

            except : return JsonResponse({'type':'danger', 'msg':'در آپلود فایل خطایی رخ داده'})
        else:
            uploader=['','-', '-']

        desc = escape(desc)

        title = escape(title)
    
        date = get_date_time()['timestamp']
        
        ticket = Ticket(customer=customer, title=title, date=date, last_update=date, department=department, count=1)
        ticket.save()
        ticket_answer = Ticket_answer(ticket=ticket, customer=customer, desc=desc, date=date, file_name=uploader[2], file_url=uploader[1])
        ticket_answer.save()

        if ticket.department == 'dep1' : ticket_department = 'پشتیبانی مشتریان' 
        elif ticket.department == 'dep2' : ticket_department = 'امور مالی' 
        elif ticket.department == 'dep3' : ticket_department = 'آموزش و مشاوره تخصصی' 
        elif ticket.department == 'dep4' : ticket_department = 'انتقادات و پیشنهادات' 
        elif ticket.department == 'dep5' : ticket_department = 'ارسال شکایات به واحد نظارت' 
        elif ticket.department == 'dep6' : ticket_department = 'دفتر مدیرعامل' 
        elif ticket.department == 'dep7' : ticket_department = 'پشتیبانی مشتریان' 
        elif ticket.department == 'dep8' : ticket_department = 'مشارکت'
        elif ticket.department == 'dep9' : ticket_department = 'شکایت ,انتقادات و پیشنهادات' 
        elif ticket.department == 'dep10' : ticket_department = 'دفتر مدیرعامل' 
        else : ticket_department = 'نامشخص' 


        shamsi_date = ticket.ToshamsiDate['dateinnum']  # دسترسی به تاریخ
        formatted_date = f"{shamsi_date[0]}/{shamsi_date[1]}/{shamsi_date[2]}"  # فرمت تاریخ

        
        if customer.is_from_pwa == True :
            add_static_report(request, 'ثبت تیکت جدید', None, True, customer.req_user, get_ip(request))  
        else:
            add_static_report(request, 'ثبت تیکت جدید')

        return JsonResponse({'type':'success', 'msg':' تیکت شما با موفقیت ثبت شد','ticket_pk':ticket.pk,'ticket_title':ticket.title,'ticket_department':ticket_department,'ticket_date':formatted_date,'ticket_status':'در انتظار بررسی'})

    return JsonResponse({'type':'danger', 'msg':'ثبت تیکت مورد نظر با مشکل مواجه شده است'})


def customer_ticket_detail(request, pk):

    # customer check start
    try :

        pattern_url = customer_access_check(request)
        if pattern_url[0] != 100 : return redirect(pattern_url[1])

    except: return redirect('account')
    # customer check end

    customer = pattern_url[2]
    try : ticket = Ticket.objects.get(pk=pk, customer=customer)
    except : return redirect('customer_panel')
    answer = Ticket_answer.objects.filter(ticket=ticket).order_by('pk')
    sticker = Sticker.objects.filter(active=True).order_by('pk')[:6]
    tickets = Ticket.objects.filter(customer=customer).exclude(pk=pk).order_by('-pk')[:6]

    all_count = Ticket.objects.filter(customer=customer).count()
    waitting_count = Ticket.objects.filter(customer=customer,status="Waitting").count()
    answered_count = Ticket.objects.filter(customer=customer,status="Answered").count()
    closed_count = Ticket.objects.filter(customer=customer,status="Closed").count()

    return render(request, get_customer_theme(pattern_url[2]) + 'ticket_detail.html', {'ticket':ticket, 'answer':answer, 'sticker':sticker,'tickets':tickets , 'all_count':all_count, 'waitting_count':waitting_count, 'answered_count':answered_count, 'closed_count':closed_count})


def customer_ticket_answer_submit(request, pk):

    # customer check start
    try :

        pattern_url = customer_access_check(request)
        if pattern_url[0] != 100 : return redirect(pattern_url[1])

    except: return redirect('account')
    # customer check end

    customer = pattern_url[2]
    date = get_date_time()['timestamp']
    try : ticket = Ticket.objects.get(pk=pk, customer=customer)
    except : return redirect('customer_panel')

    last_ticket_answer = Ticket_answer.objects.filter(ticket=ticket, customer=customer).last()
    if last_ticket_answer and (int(last_ticket_answer.date) + 60) > date:
        return JsonResponse({'type':'danger', 'msg':'لطفاً یک دقیقه صبر کنید و سپس درخواست جدید ارسال کنید.'})

    if request.method == 'POST' :

        desc = request.POST.get('desc')
        sticker = request.POST.get('sticker')

        if sticker == '':

            if desc == "": 
                return JsonResponse({'type':'danger', 'msg':'لطفا موارد خواسته شده را وارد نمایید'})

            try :

                uploader = upload_file(request.FILES['file_ticket'],'usermedia/tickets', False)
                if uploader[0] != True : return JsonResponse({'type':'danger', 'msg':uploader[1]})
                file_name = uploader[2] 
                file_url = uploader[1]

            except : 

                file_name = '-'
                file_url = '-'
        
            
            
            ticket.status = "Waitting"
            ticket.is_show = True
            ticket.count += 1
            ticket.last_update = date
            ticket.save() 
            Ticket_answer(ticket=ticket, customer=customer, desc=desc, date=date, file_name=file_name, file_url=file_url).save() 
            date =  jdatetime.datetime.fromtimestamp(int(date))

            dateinnum = str(date).split()[0].split('-')
            time = str(date).split()[1]
            dateinletter = JalaliDate(dateinnum[0], dateinnum[1], dateinnum[2]).strftime('%A %D %B %N')

            if customer.is_from_pwa == True :
                add_static_report(request, 'ارسال تیکت پاسخ',None, True, customer.req_user, get_ip(request))   
            else:
                add_static_report(request, 'ارسال تیکت پاسخ')
            return JsonResponse({'type':'success', 'msg':' پیام شما با موفقیت ثبت شد', 'text':desc,'file': file_url,'date': dateinletter,'time':time, 'icon':customer.profile_pic_name , 'name':customer.first_name , 'family':customer.last_name })

        else:

            desc  = ""

            date = get_date_time()['timestamp']
            stickr = Sticker.objects.get(pk=sticker, active=True)
            try : ticket = Ticket.objects.get(pk=pk, customer=customer)
            except : return redirect('customer_panel')
            ticket.status = "Waitting"
            ticket.count += 1
            ticket.last_update = date
            ticket.save() 

        
            Ticket_answer(ticket=ticket, customer=customer, sticker=stickr, date=date,desc=desc).save() 

            date =  jdatetime.datetime.fromtimestamp(int(date))

            dateinnum = str(date).split()[0].split('-')
            time = str(date).split()[1]
            dateinletter = JalaliDate(dateinnum[0], dateinnum[1], dateinnum[2]).strftime('%A %D %B %N')
            if customer.is_from_pwa == True :
                add_static_report(request, 'ارسال تیکت پاسخ',None, True, customer.req_user, get_ip(request))   
            else:
                add_static_report(request, 'ارسال تیکت پاسخ')
            return JsonResponse({'type':'success', 'msg':' پیام شما با موفقیت ثبت شد', 'text':desc, 'date': dateinletter , 'time':time, 'icon':customer.profile_pic_name })

    return JsonResponse({'type':'danger', 'msg':'ثبت پیام مورد نظر با مشکل مواجه شده است'})


def customer_ticket_rate_submit(request, pk):

    # customer check start
    try :

        pattern_url = customer_access_check(request)
        if pattern_url[0] != 100 : return redirect(pattern_url[1])

    except: return redirect('account')
    # customer check end

    if request.method == 'POST' :

        rate = request.POST.get('rate_ticket') 
        descriptipn = request.POST.get('descriptipn')

        ticket = Ticket.objects.get(pk=pk)
        if ticket.rate == None:
            if rate == "": 
                return JsonResponse({'type':'danger', 'msg':'لطفا موارد خواسته شده را وارد نمایید'})
            if ticket.status != "Closed":
                return JsonResponse({'type':'danger', 'msg':' ثبت امتیاز برای تیکت مورد نظر فقط پس از بسته شدن تیکت امکان پذیر است.'})
            ticket.rate = rate
            ticket.descriptipn = descriptipn
            ticket.save() 
            add_static_report(request, 'ثبت امتیاز برای تیکت')
            return JsonResponse({'type':'success', 'msg':' امتیاز تیکت شما با موفقیت ثبت شد',})
        else:
            return JsonResponse({'type':'danger', 'msg':'امتیاز برای تیکت مورد نظر قبلا ثبت شده است'})

    return JsonResponse({'type':'danger', 'msg':'ثبت امتیاز تیکت مورد نظر با مشکل مواجه شده است'})


def master_ticket(request):

    
    # master check start
    try :
        code = master_access_check(request)
        if code[0] != 100 : return redirect(code[1])
    except: return redirect('master_login')
    # master check end
    
    ticket1 = Ticket.objects.filter(status="Waitting").order_by('-pk')[:10]
    ticket2 = Ticket.objects.filter(status="Ckecking").order_by('-pk')[:10]

    ticket = list(chain(ticket1,ticket2))
    ticket = list(dict.fromkeys(ticket))

    departments = TICKETDEPARTMENT

    paginator = Paginator(ticket,10)
    page = request.GET.get('page')

    try:
        ticket = paginator.page(page)
    except PageNotAnInteger: ticket = paginator.page(1)
    except EmptyPage: ticket = paginator.page(paginator.num_page) 

    return render(request, get_master_theme() + 'ticket.html', {'tickets':ticket, "departments":departments,'user_type':Token_Check.objects.all()})


def master_ticket_archive(request):

    
    # master check start
    try :
        code = master_access_check(request)
        if code[0] != 100 : return redirect(code[1])
    except: return redirect('master_login')
    # master check end
    
    try: crm_query = Master.objects.get(req_user=request.user)
    except: return redirect('master_login')


    departments = TICKETDEPARTMENT 
    tickets = Ticket.objects.filter((Q(status='Waitting') & 
                                     (Q(crm=crm_query) | Q(crm__isnull=True) | Q(is_show=True))
                                     ) | Q(status__in=['Closed', 'Ckecking', 'Answered', 'FromMaster'])).order_by('-pk')[:1000]

    paginator = Paginator(tickets, 10)
    page = request.GET.get('page')

    try: querySet = paginator.page(page)
    except PageNotAnInteger: querySet = paginator.page(1)
    except EmptyPage: querySet = paginator.page(paginator.num_page) 

    return render(request, get_master_theme() + 'tickets_archive.html', {'querySet':querySet, "departments":departments, })


def master_ticket_modify_submit(request):


    # master json check start
    try : 
        code=master_access_check(request)
        if code[0] != 100 : return JsonResponse({'type':'danger', 'msg':code[2]})
    except: return JsonResponse({'type':'danger', 'msg':'ورود شما منقضی شده لطفا مجددا وارد شوید'})
    # master json check end
    

    if request.method == 'POST' :

        title = request.POST.get('title')
        customerNationalId = request.POST.get('customerNationalId')
        department = request.POST.get('department')
        desc = request.POST.get('desc')
        file_ticket = request.POST.get('file_ticket')
        prefix = request.POST.get('prefix')

        if prefix == "0" : return JsonResponse({'type':'danger', 'msg':'لطفا نوع کاربر را  وارد نمایید'})


        try:
            customer = Customer.objects.get(req_user=f'{prefix}{customerNationalId}')
            master = code[3]
        except:
            return JsonResponse({'type':'danger', 'msg':'کاربر مورد نظر یافت نشد'})
        
        if title == "" or desc == "":
            return JsonResponse({'type':'danger', 'msg':'لطفا موارد خواسته شده را وارد نمایید'})

        if Ticket.objects.filter(master=master, customer=customer, title=title,).count() != 0:
            return JsonResponse({'type':'danger', 'msg':'شما قبلا تیکت با عنوان مشابه برای کاربر ارسال کرده اید'})

        if department == "select" :
            return JsonResponse({'type':'danger', 'msg':'لطفا دپارتمان تیکت را انتحاب نمایید'})

        if file_ticket != "":
            try :
                uploader = upload_file(request.FILES['file_ticket'],'usermedia/tickets', False)
                if uploader[0] != True : return JsonResponse({'type':'danger', 'msg':uploader[1]})

            except : return JsonResponse({'type':'danger', 'msg':'در آپلود فایل خطایی رخ داده'})
        else:
            uploader=['','-', '-']
    
        date = get_date_time()['timestamp']
        ticket = Ticket(master=master, customer=customer, title=title, date=date, last_update=date, department=department, from_master=True, status="FromMaster")
        ticket.save()
        Ticket_answer(ticket=ticket, customer=customer, master=master, desc=desc, date=date, file_name=uploader[2], file_url=uploader[1]).save()
        Site_notifications(title=title,customer=customer,type='Private', desc=desc, link='#',master=master, date=date,icon_name=uploader[1], department="Ticket").save()

        add_static_report(request, 'ثبت تیکت جدید')
        return JsonResponse({'type':'success', 'msg':' تیکت شما با موفقیت ثبت شد',})

    return JsonResponse({'type':'danger', 'msg':'ثبت تیکت مورد نظر با مشکل مواجه شده است'})


def master_ticket_detail(request, pk):
     
    # master check start
    try :
        code = master_access_check(request)
        if code[0] != 100 : return redirect(code[1])
    except: return redirect('master_login')
    # master check end
    
    try: crm_query = Master.objects.get(req_user=request.user)
    except: return redirect('master_login')

    tickets = Ticket.objects.filter((Q(status='Waitting') & (Q(crm=crm_query) | Q(crm__isnull=True) | Q(is_show=True))) | Q(status='Ckecking')).order_by('-pk')[:20]

    try : ticket = Ticket.objects.get(pk=pk)
    except : return redirect('master_ticket')

    ticket.count = 0
    ticket.save()

    answer = Ticket_answer.objects.filter(ticket=ticket).order_by('-pk')
    stickers = Sticker.objects.filter(active=True).order_by('-pk')[:6]

    departments = TICKETDEPARTMENT

    return render(request, get_master_theme() + 'ticket_detail.html', {'ticket':ticket, 'answer':answer, 'tickets':tickets, 'stickers':stickers, 'departments':departments, 'pk':pk})


def master_ticket_answer_submit(request, pk):
     
    # master json check start
    try : 
        code=master_access_check(request)
        if code[0] != 100 : return JsonResponse({'type':'danger', 'msg':code[2]})
    except: return JsonResponse({'type':'danger', 'msg':'ورود شما منقضی شده لطفا مجددا وارد شوید'})
    # master json check end

    if request.method == 'POST' :

        desc = request.POST.get('desc')
        file_ticket = request.POST.get('file_ticket')
        sticker = request.POST.get('sticker') 
        master = code[3]

        if sticker == '':

            if desc == "": 
                return JsonResponse({'type':'danger', 'msg':'لطفا موارد خواسته شده را وارد نمایید'})
                
            try :
                uploader = upload_file(request.FILES['file_ticket'],'usermedia/tickets', False)
                if uploader[0] != True : return JsonResponse({'type':'danger', 'msg':uploader[1]})

                file_name = uploader[2]
                file_url = uploader[1]

            except : 

                file_name = '-'
                file_url = '-'
            
                
            date = get_date_time()['timestamp']
            ticket = Ticket.objects.get(pk=pk)
            if ticket.status != "FromMaster":
                ticket.status = "Answered"
            ticket.last_update = date
            ticket.is_show = True
            ticket.save() 

            Ticket_answer(ticket=ticket, master=master, desc=desc, date=date, file_name=file_name, file_url=file_url).save() 
            
            date =  jdatetime.datetime.fromtimestamp(int(date))

            dateinnum = str(date).split()[0].split('-')
            time = str(date).split()[1]
            dateinletter = JalaliDate(dateinnum[0], dateinnum[1], dateinnum[2]).strftime('%A %D %B %N')

            if ticket.customer.req_user.startswith('customer-'):
                Send_Sms_Queue(phone=ticket.customer.mobile,name ='MelliGoldTicketAnswered',text=ticket.title).save()
            else : Send_Sms_Queue(phone=ticket.customer.mobile,name ='MelliGoldTicketAnswered',text=ticket.title,representation=True).save()    

            add_static_report(request, 'ارسال جواب تیکت')
            return JsonResponse({'type':'success', 'msg':' پیام شما با موفقیت ثبت شد', 'text':desc ,'file': file_url , 'file_name': file_name ,  'date': dateinletter , 'time':time,})
        
        else:

            date = get_date_time()['timestamp']
            stickr = Sticker.objects.get(pk=sticker, active=True)
            ticket = Ticket.objects.get(pk=pk)
            if ticket.status != "FromMaster":
                ticket.status = "Answered"
            ticket.last_update = date
            ticket.save() 

            Ticket_answer(ticket=ticket, master=master, sticker=stickr, date=date).save() 

            date =  jdatetime.datetime.fromtimestamp(int(date))

            dateinnum = str(date).split()[0].split('-')
            time = str(date).split()[1]
            dateinletter = JalaliDate(dateinnum[0], dateinnum[1], dateinnum[2]).strftime('%A %D %B %N')


            if ticket.customer.req_user.startswith('customer-'):
                Send_Sms_Queue(phone=ticket.customer.mobile,name ='MelliGoldTicketAnswered',text=ticket.title).save()
            else : Send_Sms_Queue(phone=ticket.customer.mobile,name ='MelliGoldTicketAnswered',text=ticket.title,representation=True).save()

            add_static_report(request, 'ارسال جواب تیکت')
            return JsonResponse({'type':'success', 'msg':' پیام شما با موفقیت ثبت شد', 'date': dateinletter , 'time':time, })

    return JsonResponse({'type':'danger', 'msg':'ثبت پیام مورد نظر با مشکل مواجه شده است'})


def master_ticket_ckecking_submit(request, pk, crm=None):
    
    
    # master json check start
    try : 
        code=master_access_check(request)
        if code[0] != 100 : return JsonResponse({'type':'danger', 'msg':code[2]})
    except: return JsonResponse({'type':'danger', 'msg':'ورود شما منقضی شده لطفا مجددا وارد شوید'})
    # master json check end
    date = get_date_time()['timestamp']
    ticket = Ticket.objects.get(pk=pk)
    if crm:
        desc = 'کارشناسی تیکت مورد نظر به شما اختصاص یافت.'
        try: crm_query = Master.objects.get(req_user=request.user)
        except: return redirect('master_login') 
        ticket.crm = crm_query
        ticket.is_show = False
    else:
        desc = 'تیکت مورد نظر در وضعیت در حال پیگیری قرار گرفت.'
        ticket.status = "Ckecking"
        ticket.is_show = True
    ticket.last_update = date
    ticket.save() 
    add_static_report(request, 'تغییر وضعیت تیکت به در حال پیگیری')
    return JsonResponse({'type':'success', 'msg':desc})


def master_ticket_closed_submit(request, pk):
     
    # master json check start
    try : 
        code=master_access_check(request)
        if code[0] != 100 : return JsonResponse({'type':'danger', 'msg':code[2]})
    except: return JsonResponse({'type':'danger', 'msg':'ورود شما منقضی شده لطفا مجددا وارد شوید'})
    # master json check end

    date = get_date_time()['timestamp']
    ticket = Ticket.objects.get(pk=pk)
    ticket.status = "Closed"
    ticket.last_update = date
    ticket.is_show = True
    ticket.save()

    # Send_Sms_Queue(phone=ticket.customer.mobile,name ='MellichangeWinner',text=str(pk)).save()

    add_static_report(request, 'تغییر وضعیت تیکت به بسته شده')
    return JsonResponse({'type':'success', 'msg':' تیکت مورد نظر بسته شد.'})


def master_sticker(request):

    # master check start
    try :
        code = master_access_check(request)
        if code[0] != 100 : return redirect(code[1])
    except: return redirect('master_login')
    # master check end
    
    stickers = Sticker.objects.all().order_by('-pk')

    paginator = Paginator(stickers,10)
    page = request.GET.get('page')

    try:
        stickers = paginator.page(page)
    except PageNotAnInteger:
        stickers = paginator.page(1)
    except EmptyPage:
        stickers = paginator.page(paginator.num_page) 

    return render(request, get_master_theme() + 'stickers.html', {'stickers':stickers, })


def master_sticker_modify_submit(request):

    
    # master json check start
    try : 
        code=master_access_check(request)
        if code[0] != 100 : return JsonResponse({'type':'danger', 'msg':code[2]})
    except: return JsonResponse({'type':'danger', 'msg':'ورود شما منقضی شده لطفا مجددا وارد شوید'})
    # master json check end
    
    
    if request.method == 'POST' :

        try :
            uploader = upload_file(request.FILES['file_sticker'],'media/stickers', False)
            if uploader[0] != True : return JsonResponse({'type':'danger', 'msg':uploader[1]})

        except : return JsonResponse({'type':'danger', 'msg':'در آپلود فایل خطایی رخ داده'})
    
        date = get_date_time()['timestamp']
        sticker = Sticker(file_name=uploader[2])
        sticker.save()
        add_static_report(request, 'ثبت استیکر جدید')
        return JsonResponse({'type':'success', 'msg':' استیکر شما با موفقیت ثبت شد', 'pk':sticker.pk, 'filename':uploader[2]})

    return JsonResponse({'type':'danger', 'msg':'ثبت استیکر مورد نظر با مشکل مواجه شده است'})


def master_sticker_active_submit(request, pk):
     
    
    # master json check start
    try : 
        code=master_access_check(request)
        if code[0] != 100 : return JsonResponse({'type':'danger', 'msg':code[2]})
    except: return JsonResponse({'type':'danger', 'msg':'ورود شما منقضی شده لطفا مجددا وارد شوید'})
    # master json check end

    date = get_date_time()['timestamp']
    sticker = Sticker.objects.get(pk=pk)
    if sticker.active == True:
        sticker.active = False
        sticker.save()
        add_static_report(request, 'ویرایش وضعیت استیکرها')
        return JsonResponse({'type':'success', 'msg':'استیکر مورد نظر به وضعیت عدم نمایش درآمد.', 'status':sticker.active})
    elif sticker.active == False:
        sticker.active = True
        sticker.save() 

        add_static_report(request, 'ویرایش وضعیت استیکرها')
        return JsonResponse({'type':'success', 'msg':'استیکر مورد نظر به وضعیت نمایش درآمد.', 'status':sticker.active})
    

def master_sticker_delete_submit(request,pk):

    # master json check start
    try : 
        code=master_access_check(request)
        if code[0] != 100 : return JsonResponse({'type':'danger', 'msg':code[2]})
    except: return JsonResponse({'type':'danger', 'msg':'ورود شما منقضی شده لطفا مجددا وارد شوید'})
    # master json check end
    
    try :

        sticker = Sticker.objects.get(pk=pk)
        fs = FileSystemStorage(location='media/stickers')  
        fs.delete(sticker.file_name)
        sticker.delete()
        add_static_report(request, 'حذف استیکر')
        
        return JsonResponse({'type':'success', 'msg':'استیکر با موفقیت حذف شد'})

    except : return JsonResponse({'type':'danger', 'msg':'حذف استیکر با مشکل مواجه شده است'})

def master_ticket_answer_edit_submit(request, pk):
     
    # master json check start
    try : 
        code=master_access_check(request)
        if code[0] != 100 : return JsonResponse({'type':'danger', 'msg':code[2]})
    except: return JsonResponse({'type':'danger', 'msg':'ورود شما منقضی شده لطفا مجددا وارد شوید'})
    # master json check end

    if request.method == 'POST' :

        desc = request.POST.get('desc')
        

        if desc == "": 
            return JsonResponse({'type':'danger', 'msg':'لطفا موارد خواسته شده را وارد نمایید'})
            
        try :
            uploader = upload_file(request.FILES['file_ticket_answer'],'usermedia/tickets', False)
            if uploader[0] != True : return JsonResponse({'type':'danger', 'msg':uploader[1]})

            file_name = uploader[2]
            file_url = uploader[1]

        except : 

            file_name = '-'
            file_url = '-'
        
        ticketanswer = Ticket_answer.objects.get(pk=pk)
        ticketanswer.desc = desc
        if file_name != '-' and file_url != '-' :
            ticketanswer.file_name=file_name
            ticketanswer.file_url=file_url
        ticketanswer.save() 


        add_static_report(request, 'ویرایش جواب تیکت')
        return JsonResponse({'type':'success', 'msg':' پیام شما با موفقیت ویرایش شد', 'text':desc ,'file': file_url , 'file_name': file_name})
        
    return JsonResponse({'type':'danger', 'msg':'ویرایش پیام مورد نظر با مشکل مواجه شده است'})





def master_ticket_search(request):

    # master check start
    try :
        code = master_access_check(request)
        if code[0] != 100 : return redirect(code[1])
    except: return redirect('master_login')
    # master check end

    try: crm_query = Master.objects.get(req_user=request.user)
    except: return redirect('master_login')

    departments = TICKETDEPARTMENT
    # querySet = Ticket.objects.all()

    if request.method == 'POST':
        txt = request.POST.get('txt')
        status = request.POST.get('status')

        request.session['txt'] = txt
        request.session['status'] = status
  
    else:
        txt = request.session.get('txt', "")
        status = request.session.get('status', "all")


    query = Q()

    if txt:
        query &= (Q(pk__icontains=txt) | 
                  Q(customer__national_id__icontains=txt) | 
                  Q(customer__first_name__icontains=txt) | 
                  Q(customer__last_name__icontains=txt))


    if status != "0":
        if status == "Waitting": query &= (Q(status=status) & (Q(crm=crm_query) | Q(crm__isnull=True) | Q(is_show=True)))
        else: query &= Q(status=status)

    querySet = Ticket.objects.filter(query).distinct().order_by('-date')
    count_querySet = querySet.count()

    paginator = Paginator(querySet, 10)
    page = request.GET.get('page')

    try:
        querySet = paginator.page(page)
    except PageNotAnInteger:
        querySet = paginator.page(1)
    except EmptyPage:
        querySet = paginator.page(paginator.num_pages)
    
    return render(request, get_master_theme() + 'tickets_archive.html', {'querySet': querySet,'departments':departments, 'count_querySet': count_querySet})


