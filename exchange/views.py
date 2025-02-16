from django.shortcuts import render

# Create your views here.

from collections import defaultdict
from dataclasses import dataclass
import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
import pytz
from requests import Session
from django.views.decorators.cache import cache_page
from account.func.currency_buySell import check_buysell_cancel_requests, handly_sell
from .models import *
from exchange.func.theme import *
from .func.access import *
from django.http import HttpResponse, JsonResponse
from exchange.func.public import *
from currency.models import Currency_List
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import requests
from django.contrib.auth.models import User , Group , Permission
from currency.models import Currency_List, Currency_Chain 
import urllib
from itertools import chain
from openpyxl import Workbook
from account.func.price_check import *
from django.db.models import Exists, OuterRef
from django.db.models import F
from django.db.models import F, Value
import khayyam
from customer.func.access import *
from django.db.models import Q
from master.models import UTM, UTMLog
from django.utils.html import escape
from account.func.currency_buySell import *


def under_update(request):

    if site_access_check() == False :
        return redirect('home')

    return render(request, get_front_theme() + 'under_update.html')




def home(request):


    currency = Currency_List.objects.filter(is_show=True, is_first_page=True).order_by('sort')

    currencies = Currency_List.objects.filter(is_show=True,is_papular=True)

    set = ContactUs.objects.get(code=1001)
    setting = Site_Settings.objects.get(code=1001)
    banner = SiteBanner.objects.all().order_by('-pk')

    academy = Academy.objects.filter(act=True,publish_date__lte=get_date_time()['timestamp']).order_by("-publish_date")[:8]

    active_categories_with_subcategories = Faq_Categories.objects.annotate(num_faqs=Count('faq', filter=Q(faq__act=True))).filter(num_faqs__gt=0, act=True)
    active_faqs = Faq.objects.filter(category__in=active_categories_with_subcategories, act=True).order_by('-pk')[:4]

    features = SiteFeatures.objects.all().order_by('-pk')[:10]
    evidences = SiteEvidence.objects.filter(act=True).order_by("-pk")[:10]
    comments = UserOpinion.objects.filter(act=True).order_by("-pk")[:10]
    partners = SitePartner.objects.filter(act=True).order_by("-pk")[:10]
    paths = Site_Path.objects.filter(act=True).order_by("-pk")[:6]
    piggy1 = Melligold_Saving_Box.objects.get(code=1001)
    newspaper = Newspaper.objects.filter(act=True)


   

    message = None

    if request.session.get('notification') != None :
        message = request.session.get('notification')
    request.session['notification'] = None

    package = InvestmentList.objects.filter(act=True)
   
    goldPackages = {}
    for package in package:
        if package.currency not in goldPackages:
            goldPackages[package.currency] = []

        goldPackages[package.currency].append({
            'name': package.currency,
            'time': package.period_time,
            'profit': package.profit_loss,
            'insurance': package.insurance
        })


    currencies_without_investment = Currency_List.objects.annotate(
        has_investment=Exists(
            InvestmentList.objects.filter(currency=OuterRef('symbol'),act=True)
        )
    )

    set = ContactUs.objects.get(code=1001)

    product = Site_Products.objects.annotate(total_quantity=Sum('site_product_inventory__quantity'))


    molten_gold = product.filter(
        Q(city__site_branches_each_representative__site_branch_working_days__act=True) & 
        Q(city__site_branches_each_representative__site_branch_working_days__jalali_date__gte=jdatetime.datetime.now().strftime('%Y/%m/%d')),
        Q(city__site_branches_each_representative__site_branch_working_days__capacity__gt=0),
        type_gold="gold1",
        total_quantity__gt=0,
        act=True,
        city__act=True
    ).order_by("-pk")[:8]

    count_molten_gold_with_zero_inventory = molten_gold.count()

    bullion_coin = product.filter(
        Q(city__site_branches_each_representative__site_branch_working_days__act=True) & 
        Q(city__site_branches_each_representative__site_branch_working_days__jalali_date__gte=jdatetime.datetime.now().strftime('%Y/%m/%d')),
        Q(city__site_branches_each_representative__site_branch_working_days__capacity__gt=0),
        type_gold__in=["gold2", "gold3"],
        total_quantity__gt=0,
        act=True,
        city__act=True
    ).order_by("-pk")[:8]

    count_bullion_coin_with_zero_inventory = bullion_coin.count()

    return render(request, get_front_theme() + 'home.html', {'banner':banner,'set':set,'piggy1':piggy1,'currency':currency,'setting':setting,'message':message, 'academy':academy, 'faq':active_faqs, 'features':features,'evidences':evidences, 'comments':comments,'partners':partners,'paths':paths,'currencies':currencies,'deposit':goldPackages,'package':InvestmentList.objects.filter(act=True),'currencies_2':currencies_without_investment,'molten_gold':molten_gold,'bullion_coin':bullion_coin,'last_gold_price':Currency_List.objects.get(symbol='XAU18').BuySellPrice['buy'],'newspaper':newspaper,'last_gold_price': Currency_List.objects.get(symbol='XAU18').BuySellPrice['buy'],'count_molten_gold_with_zero_inventory':count_molten_gold_with_zero_inventory,'count_bullion_coin_with_zero_inventory':count_bullion_coin_with_zero_inventory,'cc':Currency_List.objects.get(symbol='XAU18')})



def account(request):

    logout(request)

    # Update Check Start
    if site_access_check() == True :
        return redirect('under_update')
    # Update Check End
    set = ContactUs.objects.get(code=1001)

   
    return render(request, get_customer_theme() + 'account.html',{'settings':Site_Settings.objects.get(code=1001),'set':set})


def account_ref_code(request,code):

    if Customer.objects.filter(referral_link=code).count() == 0 :
        return redirect('account')

    try : Customer_refLink_click(ref_link=code, datetime=get_date_time()['timestamp'], ip=get_ip(request)).save()
    except: pass
    set = ContactUs.objects.get(code=1001)

    return render(request, get_front_theme() + 'account_ref.html',{'code':code,'set':set})


# @cache_page(60 * 60)
def about_us(request):

    sett = AboutUs.objects.get(code=1001)
    set = ContactUs.objects.get(code=1001)

    evidences = SiteEvidence.objects.all().order_by("-pk")[:10]
    comments = UserOpinion.objects.all().order_by("-pk")[:10]
    academy = Academy.objects.filter(act=True,publish_date__lte=get_date_time()['timestamp']).order_by("-publish_date")

    data = {}

    categories = Members_Categories.objects.filter(act=True).order_by("sort")

    for category in categories:
        department_name = category.title
        department_data = []

        isCat = list(Members_Subcategories.objects.filter(category=category, act=True).order_by('sort').values("pk", "title"))
        if isCat: department_data.append({"isCat": isCat})


        isMember = []
        isMember = list(Site_Managers_Subset.objects.filter(subcategory__category=category, act=True).order_by('sort').annotate(pk_cat=F('subcategory__pk'),position=F('side'),image=F('logo_name'),about=F('desc')).values("pk_cat", "name", "position", "image", "about"))


        members = Site_Board_Of_Directors.objects.filter(category=category, act=True).exclude(is_ceo=True).order_by('sort')
        if members.exists():
            for member in members:
                isMember.append({
                    "pk_cat": "-",
                    "name": member.name,
                    "position": member.side,
                    "image": member.logo_name,
                    "about": member.desc
                })

        if isMember:
            department_data.append({"isMember": isMember})



        isAdmin = list(Site_Managers.objects.filter(category=category, act=True).order_by('sort').annotate(position=F('side'),image=F('logo_name'),about=F('desc')).values("name", "position", "image", "about"))
        if isAdmin: department_data.append({"isAdmin": isAdmin})


        if department_data:
            data[department_name] = department_data

    return render(request, get_front_theme() + 'about_us.html',{'sett':sett,'set':set,'evidences':evidences, 'comments':comments, 'academy':academy, 'teams_member':data, 'ceo':Site_Board_Of_Directors.objects.filter(is_ceo=True,act=True)})

# @cache_page(60 * 60)
def contact_us(request):

    set = ContactUs.objects.get(code=1001)
    departments = Site_Department.objects.all()
    evidences = SiteEvidence.objects.all().order_by("-pk")[:10]

    return render(request, get_front_theme() + 'contact_us.html',{'set':set,'departments':departments,'category':support_Category.objects.all().exclude(title="بدون دسته"),'manager':Master.objects.filter(is_master=False),'evidences':evidences})


def contact_us_form(request):  

    user_agent = request.META.get('HTTP_USER_AGENT', '')
    user_ip = get_ip(request)
    datetime_now = get_date_time()['timestamp']
    
    last_query = ContactForm.objects.filter(ip=user_ip, user_agent=user_agent)
    if last_query.exists():
        if (int(last_query.last().datetime) + 300) > datetime_now:
            return JsonResponse({'type':'danger', 'msg':'برای ثبت درخواست مجدد لطفا کمی صبر کنید و سپس دوباره تلاش کنید.'})


    if request.method == "POST":

        name = request.POST.get('name')
        number = request.POST.get('number')
        txt = request.POST.get('txt')

        if name == "" or number == "" or txt == "" :
            return JsonResponse({'type':'danger', 'msg':'لطفا تمامی موارد را وارد نمایید'})

        m_check = mobile_check(number)
        if m_check[0] == False :
            return JsonResponse({'type':'danger', 'msg':m_check[1]})

        

        ContactForm(name=name,number=number,txt=txt, ip=user_ip, user_agent=user_agent,datetime=datetime_now).save()    

        return JsonResponse({'type':'success', 'msg':'پیام شما با موفقیت ارسال شد'})

    return JsonResponse({'type':'danger', 'msg':'پردازش مورد نظر با مشکل مواجه شده است'})


@cache_page(60 * 60)
def faq(request):

    categories_with_subcategories = Faq_Categories.objects.annotate(num_subcategories=Count('faq', filter=Q(faq__act=True))).filter(num_subcategories__gt=0)
    categories_with_active_subcategories = categories_with_subcategories.filter(act=True).order_by('-pk')

    return render(request, get_front_theme() + 'faq.html',{'faq': Faq.objects.filter(act=True).order_by("pk"),'set': ContactUs.objects.get(code=1001),'category':categories_with_active_subcategories})


def academy(request,title):

    try: academy = Academy_Categories.objects.get(act=True,title=urllib.parse.unquote(title))
    except : return render(request,"404.html")

    popular_academy = Academy.objects.filter(act=True,publish_date__lte=get_date_time()['timestamp']).order_by('-view', '-publish_date')
    paginator = Paginator(Academy.objects.filter(act=True,category__title=urllib.parse.unquote(title),publish_date__lte=get_date_time()['timestamp']).order_by("-publish_date"),6)
    page = request.GET.get('page')

    try:
        academy = paginator.page(page)
    except PageNotAnInteger:
        academy = paginator.page(1)
    except EmptyPage:
        academy = paginator.page(1) 

    return render(request, get_front_theme() + 'academy.html',{'set':ContactUs.objects.get(code=1001),'category':Academy_Categories.objects.filter(act=True,main_category__title=urllib.parse.unquote(title)).order_by("-pk"), 'academy':academy, 'visited_academy':Academy.objects.filter(publish_date__lte=get_date_time()['timestamp']).order_by("-view")[:5],'category_all':Academy_Categories.objects.filter(act=True).order_by("-pk"),'title_academy':title,'popular_academy':popular_academy})


def academy_category(request,title,category):

    paginator = Paginator(Academy.objects.filter(act=True,category__title=urllib.parse.unquote(title),category__main_category__title=urllib.parse.unquote(category),publish_date__lte=get_date_time()['timestamp']).order_by("-pk"),12)
    page = request.GET.get('page')

    try:
        academy = paginator.page(page)
    except PageNotAnInteger:
        academy = paginator.page(1)
    except EmptyPage:
        academy = paginator.page(1) 

    return render(request, get_front_theme() + 'academy_category.html',{'set':ContactUs.objects.get(code=1001),'category':Academy_Categories.objects.filter(act=True,main_category__title=urllib.parse.unquote(category)).order_by("-pk"), 'academy':academy, 'visited_academy':Academy.objects.filter(publish_date__lte=get_date_time()['timestamp']).order_by("-view")[:5],'all_category':Academy_Categories.objects.filter(act=True), 'curect_category':title})


def academy_search_submit(request):
    
    category = []
    txt = "-"    

    if request.method == 'POST'  :

        txt = request.POST.get('txt')
        category = request.POST.get('category')

        if txt != "" and category != "0" :

            request.session['search'] = txt
            request.session['category'] = category

            academy1 = Academy.objects.filter(act=True,title__contains=txt,category__title__contains = category,publish_date__lte=get_date_time()['timestamp'])
            academy2 = Academy.objects.filter(act=True,short_text__contains=txt,category__title__contains = category,publish_date__lte=get_date_time()['timestamp'])
            academy3 = Academy.objects.filter(act=True,long_text__contains=txt,category__title__contains = category,publish_date__lte=get_date_time()['timestamp'])
            academy4 = Academy.objects.filter(act=True,manager__contains=txt,category__title__contains = category,publish_date__lte=get_date_time()['timestamp'])
            academy5 = Academy.objects.filter(act=True,pk__contains=txt,category__title__contains = category,publish_date__lte=get_date_time()['timestamp'])
            academies = list(chain(academy1,academy2,academy3,academy4,academy5))

            paginator = Paginator(list(dict.fromkeys(academies)),12)
            page = request.GET.get('page')

            try:
                querySet = paginator.page(page)
            except PageNotAnInteger:
                querySet = paginator.page(1)
            except EmptyPage:
                querySet = paginator.page(1) 

        elif txt != "" and category == "0" :

            request.session['search'] = txt
            request.session['category'] = "None"

            academy1 = Academy.objects.filter(act=True,title__contains=txt,publish_date__lte=get_date_time()['timestamp'])
            academy2 = Academy.objects.filter(act=True,short_text__contains=txt,publish_date__lte=get_date_time()['timestamp'])
            academy3 = Academy.objects.filter(act=True,long_text__contains=txt,publish_date__lte=get_date_time()['timestamp'])
            academy4 = Academy.objects.filter(act=True,manager__contains=txt,publish_date__lte=get_date_time()['timestamp'])
            academy5 = Academy.objects.filter(act=True,pk__contains=txt,publish_date__lte=get_date_time()['timestamp'])
            academy6 = Academy.objects.filter(act=True,category__title__contains=txt,publish_date__lte=get_date_time()['timestamp'])

            academies = list(chain(academy1,academy2,academy3,academy4,academy5,academy6))
            paginator = Paginator(list(dict.fromkeys(academies)),12)
            page = request.GET.get('page')

            try:
                querySet = paginator.page(page)
            except PageNotAnInteger:
                querySet = paginator.page(1)
            except EmptyPage:
                querySet = paginator.page(1) 

        elif txt == "" and category != "0" :
  
            request.session['category'] = category
            request.session['search'] = "None"

            academies = Academy.objects.filter(act=True,category__title__contains = category,publish_date__lte=get_date_time()['timestamp'])
            paginator = Paginator(academies,12)
            page = request.GET.get('page')

            try:
                querySet = paginator.page(page)
            except PageNotAnInteger:
                querySet = paginator.page(1)
            except EmptyPage:
                querySet = paginator.page(1) 

        elif txt == "" and category == "0" :
  
            request.session['category'] = "None"
            request.session['search'] = "None"

            academies = Academy.objects.filter(act=None,publish_date__lte=get_date_time()['timestamp'])
            paginator = Paginator(academies,12)
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
            category = request.session['category'] 

            if txt != "None" and category != "None" :

                academy1 = Academy.objects.filter(act=True,title__contains=txt,category__title__contains = category,publish_date__lte=get_date_time()['timestamp'])
                academy2 = Academy.objects.filter(act=True,short_text__contains=txt,category__title__contains = category,publish_date__lte=get_date_time()['timestamp'])
                academy3 = Academy.objects.filter(act=True,long_text__contains=txt,category__title__contains = category,publish_date__lte=get_date_time()['timestamp'])
                academy4 = Academy.objects.filter(act=True,manager__contains=txt,category__title__contains = category,publish_date__lte=get_date_time()['timestamp'])
                academy5 = Academy.objects.filter(act=True,pk__contains=txt,category__title__contains = category,publish_date__lte=get_date_time()['timestamp'])
                academies = list(chain(academy1,academy2,academy3,academy4,academy5))

                paginator = Paginator(list(dict.fromkeys(academies)),12)
                page = request.GET.get('page')

                try:
                    querySet = paginator.page(page)
                except PageNotAnInteger:
                    querySet = paginator.page(1)
                except EmptyPage:
                    querySet = paginator.page(1) 

            elif txt != "None" and category == "None": 

                academy1 = Academy.objects.filter(act=True,title__contains=txt,publish_date__lte=get_date_time()['timestamp'])
                academy2 = Academy.objects.filter(act=True,short_text__contains=txt,publish_date__lte=get_date_time()['timestamp'])
                academy3 = Academy.objects.filter(act=True,long_text__contains=txt,publish_date__lte=get_date_time()['timestamp'])
                academy4 = Academy.objects.filter(act=True,manager__contains=txt,publish_date__lte=get_date_time()['timestamp'])
                academy5 = Academy.objects.filter(act=True,pk__contains=txt,publish_date__lte=get_date_time()['timestamp'])
                academy6 = Academy.objects.filter(act=True,category__title__contains=txt,publish_date__lte=get_date_time()['timestamp'])
                academies = list(chain(academy1,academy2,academy3,academy4,academy5,academy6))

                paginator = Paginator(list(dict.fromkeys(academies)),12)
                page = request.GET.get('page')

                try:
                    querySet = paginator.page(page)
                except PageNotAnInteger:
                    querySet = paginator.page(1)
                except EmptyPage:
                    querySet = paginator.page(1) 

            elif txt == "None" and category != "None":
                
                academies = Academy.objects.filter(act=True,category__title__contains = category,publish_date__lte=get_date_time()['timestamp'])
                paginator = Paginator(list(dict.fromkeys(academies)),12)
                page = request.GET.get('page')

                try:
                    querySet = paginator.page(page)
                except PageNotAnInteger:
                    querySet = paginator.page(1)
                except EmptyPage:
                    querySet = paginator.page(1) 

            elif txt == "None" and category == "None": 

                academies = Academy.objects.filter(act=None,publish_date__lte=get_date_time()['timestamp'])
                paginator = Paginator(list(dict.fromkeys(academies)),12)
                page = request.GET.get('page')

                try:
                    querySet = paginator.page(page)
                except PageNotAnInteger:
                    querySet = paginator.page(1)
                except EmptyPage:
                    querySet = paginator.page(1) 

        except:  
            pass
  
    return render(request, get_front_theme() + 'academy_search.html',{'set':ContactUs.objects.get(code=1001),'category':Academy_Categories.objects.filter(act=True).order_by("-pk"), 'querySet':querySet, 'visited_academy':Academy.objects.filter(publish_date__lte=get_date_time()['timestamp']).order_by("-view")[:5]})


def melligold_path(request):

    return render(request, get_front_theme() + 'mellichange_path.html',{'paths':Site_Path.objects.filter(act=True).order_by("pk"), "set" :ContactUs.objects.get(code=1001)})


def application(request):

    return render(request, get_front_theme() + 'app.html',{'set': ContactUs.objects.get(code=1001)})


def user_question(request):  

    if request.method == "POST":

        number = request.POST.get('number')
        txt = request.POST.get('txt')

        if number == "" or txt == "" :
            return JsonResponse({'type':'danger', 'msg':'لطفا تمامی موارد را وارد نمایید'})

        m_check = mobile_check(number)
        if m_check[0] == False :
            return JsonResponse({'type':'danger', 'msg':m_check[1]})

        datetime_now = get_date_time()['timestamp']

        Customer_Question(number=number,txt=txt,datetime=datetime_now).save()    

        return JsonResponse({'type':'success', 'msg':'سوال شما با موفقیت ارسال شد'})

    return JsonResponse({'type':'danger', 'msg':'پردازش مورد نظر با مشکل مواجه شده است'})


def courses(request):

    return render(request, get_front_theme() + 'courses.html',{'courses':Course.objects.filter(act=True).order_by("-pk")})


def courses_detail(request,title):

    course = Course.objects.get(title=urllib.parse.unquote(title))

    if Customer.objects.filter(req_user=request.user).count() == 0 : customer = 0
    else : customer = 1

    try : 
        uname=Customer.objects.get(req_user=request.user)
        if Customer_Course.objects.filter(course=course,uname=uname).count() == 0 : customer_course = 0
        else : customer_course = 1
    except : customer_course = 0

    return render(request, get_front_theme() + 'courses_detail.html',{'course':course, 'sessions':Session.objects.filter(course=course,act=True), 'customer':customer, 'first_comment':Comment_Course.objects.filter(course=course,is_first=True,act=True).order_by("-pk"), 'customer_course':customer_course})
       

def contact_user_registered(request):
    
    if request.method == 'POST':
        
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        
        if name == ""  or phone == "" :
            return JsonResponse({'type':'danger', 'msg':'وارد کردن تمام فیلد ها الزامی است'})
        

        try:
            int(phone)
        except:  return JsonResponse({'type':'danger', 'msg':'شماره تماس وارد شده نامعتبر است'})  
        
        Contact_Users(name=name,mobile=phone,datetime=get_date_time()['timestamp']).save()
        
        return JsonResponse({'type':'success', 'msg':'با موفقیت ثبت شد'})

    return JsonResponse({'type':'danger', 'msg':'پردازش مورد نظر با مشکل مواجه شده است'})
     
        
def currency_detail(request,symbol):

    try : currency = Currency_List.objects.get(symbol=symbol)
    except : 
        
        request.session['notification'] = ['طلا مورد نظر یافت نشد']
        return redirect('home')

    return render(request, get_customer_theme() + 'currency_detail.html',{'currency':currency,'set':ContactUs.objects.get(code=1001)})


def site_awards(request):
    return render(request, get_customer_theme() + 'awards.html',{"product":Product.objects.filter(act=True).order_by("-pk"),'mcr':Site_Ruby_Award.objects.get(code=1001),'set':ContactUs.objects.get(code=1001)}) 
        
               
def academies(request):
     
    popular_academy = Academy.objects.filter(act=True,publish_date__lte=get_date_time()['timestamp']).order_by('-view', '-publish_date')
    paginator = Paginator(Academy.objects.filter(act=True,publish_date__lte=get_date_time()['timestamp']).order_by("-publish_date"),6)
    page = request.GET.get('page')

    try:
        academy = paginator.page(page)
    except PageNotAnInteger:
        academy = paginator.page(1)
    except EmptyPage:
        academy = paginator.page(1) 

    return render(request, get_front_theme() + 'academies.html',{'set':ContactUs.objects.get(code=1001),'category':Academy_Categories.objects.filter(act=True).order_by("-pk"), 'academy':academy, 'visited_academy':Academy.objects.filter(publish_date__lte=get_date_time()['timestamp']).order_by("-view")[:5],'all_category':Academy_Categories.objects.filter(act=True),'category_all':Academy_Categories.objects.filter(act=True).order_by("-pk"),'popular_academy':popular_academy})

    
# @cache_page(60 * 60)
def melligold_media(request):

    media = Melligold_Media_Titles.objects.get(code=1001)
    media_newspaper = Media_Newspaper.objects.filter(act=True)[:6]
    cat = Melligold_Media_Episode_Category.objects.filter(act=True).order_by("-pk")
    sub = Melligold_Media_Episode_Subcategory.objects.filter(act=True).order_by("-pk")[:6]
    episode = Melligold_Media_Episode.objects.filter(act=True)
    logo = Melligold_Media_Logo.objects.filter(act=True)

    categories = Melligold_Media_Podcast_Category.objects.filter(act=True).order_by('-pk')


    output = []

    for category in categories:
       
        podcasts = (Melligold_Media_Podcast.objects
                    .filter(pod_category=category,act=True)
                    .order_by('-pod_date')[:4])  

        if podcasts.exists():
            podcast_items = []
            for podcast in podcasts:
                podcast_items.append({
                    'title': podcast.pod_title,
                    'image': f"/media/{podcast.pod_pic}",
                    'time': podcast.time,
                    # 'url': podcast.pod_audio.url if podcast.pod_audio else ""
                    'url': f"/podcast/{podcast.pod_audio}" 
                })

            output.append({
                'pk': category.pk,  
                'category': category.name,
                'podcast_item': podcast_items
            })

    eposide_chosen = episode.filter(is_chosen=True).order_by('-pk')[:5]

    return render(request, get_front_theme() + 'melligold_media.html',{'set':ContactUs.objects.get(code=1001),'media':media,'media_newspaper':media_newspaper,'cat':cat,'sub':sub,'episode':episode,'podcast':output,'logo':logo,'chosen_episode':eposide_chosen,'eposide_active':eposide_chosen.first(),'podcast_category':categories})


def category_media(request,title):


    episode_category = Melligold_Media_Episode_Subcategory.objects.get(act=True, name_url=urllib.parse.unquote(title))
    episode = Melligold_Media_Episode.objects.filter(act=True, episode_category=episode_category).order_by('pk')
    similar_episode = Melligold_Media_Episode.objects.filter(act=True, episode_category__category=episode_category.category).exclude(episode_category=episode_category).order_by('-pk')[:3]

    if episode.count() == 1:

        episode = Melligold_Media_Episode.objects.get(act=True, episode_category=episode_category)
        return redirect('episode_category',episode.episode_name_url)
    
    return render(request, get_front_theme() + 'category_media.html',{'set':ContactUs.objects.get(code=1001),'episode':episode,'episode_category':episode_category,'similar_episode':similar_episode})


def episode_category(request, title):

    
    episode = Melligold_Media_Episode.objects.get(act=True, episode_name_url=urllib.parse.unquote(title))
    other_episode = Melligold_Media_Episode.objects.filter(act=True,episode_category=episode.episode_category).exclude(episode_name_url=urllib.parse.unquote(title))

    episode.episode_views = episode.episode_views + 1
    episode.save()

    return render(request, get_front_theme() + 'episode_category.html',{'set':ContactUs.objects.get(code=1001),'episode':episode, 'other_episode':other_episode})


def melligold_podcast(request):
     
    media = Melligold_Media_Titles.objects.get(code=1001)
    podcast = Melligold_Media_Podcast.objects.filter(act=True)
    pod_category = Melligold_Media_Podcast_Category.objects.filter(act=True).order_by('-pk')


    output = []
    for category in  pod_category:
       
        podcasts = (Melligold_Media_Podcast.objects
                    .filter(pod_category=category,act=True)
                    .order_by('-pod_date')[:4])  

        if podcasts.exists():
            podcast_items = []
            for podcast in podcasts:
                podcast_items.append({
                    'title': podcast.pod_title,
                    'image': f"/media/{podcast.pod_pic}",
                    'time': podcast.time,
                    'chosen' : str(podcast.is_chosen),
                    # 'url': podcast.pod_audio.url if podcast.pod_audio else ""
                    'url': f"/podcast/{podcast.pod_audio}" 
                })

            output.append({
                'pk': category.pk,  
                'category': category.name,
                'podcast_item': podcast_items
            })

    return render(request, get_front_theme() + 'melligold_podcast.html',{'set':ContactUs.objects.get(code=1001),'podcast':podcast,'pod_category':pod_category,'media':media,'output':output})


def melligold_newspaper(request):

    media = Melligold_Media_Titles.objects.get(code=1001)
    newspaper = Newspaper.objects.filter(act=True)
    media_newspaper = Media_Newspaper.objects.filter(act=True)[:3]
     
    return render(request, get_front_theme() + 'melligold_newspaper.html',{'set':ContactUs.objects.get(code=1001),'newspaper':newspaper,'media_newspaper':media_newspaper,'media':media})

    
def physical_delivery(request):

    set = ContactUs.objects.get(code=1001)

    products = Site_Products.objects.annotate(total_quantity=Sum('site_product_inventory__quantity'))
    molten_gold_with_zero_inventory = products.filter(
        Q(city__site_branches_each_representative__site_branch_working_days__act=True) & 
        Q(city__site_branches_each_representative__site_branch_working_days__jalali_date__gte=jdatetime.datetime.now().strftime('%Y/%m/%d')),
        Q(city__site_branches_each_representative__site_branch_working_days__capacity__gt=0),
        total_quantity__gt=0,
        type_gold="gold1",
        act=True,
        city__act=True
    ).order_by('-pk')

    count_molten_gold_with_zero_inventory = molten_gold_with_zero_inventory.count()

    molten_gold_page = request.GET.get('molten_gold_page', 1)
    paginator_molten_gold = Paginator(molten_gold_with_zero_inventory, 12)
    try:
        molten_gold = paginator_molten_gold.page(molten_gold_page)
    except PageNotAnInteger:
        molten_gold = paginator_molten_gold.page(1)
    except EmptyPage:
        molten_gold = paginator_molten_gold.page(paginator_molten_gold.num_pages)


    bullion_coin_with_zero_inventory = products.filter(
        Q(city__site_branches_each_representative__site_branch_working_days__act=True) & 
        Q(city__site_branches_each_representative__site_branch_working_days__jalali_date__gte=jdatetime.datetime.now().strftime('%Y/%m/%d')),
        Q(city__site_branches_each_representative__site_branch_working_days__capacity__gt=0),
        total_quantity__gt=0,
        type_gold__in=["gold2", "gold3"],
        act=True,
        city__act=True
        ).order_by('-pk')
    count_bullion_coin_with_zero_inventory = bullion_coin_with_zero_inventory.count()

    paginator = Paginator(bullion_coin_with_zero_inventory,12)
    page = request.GET.get('page')
    try:
        bullion_coin = paginator.page(page)
    except PageNotAnInteger:
        bullion_coin = paginator.page(1)
    except EmptyPage:
        bullion_coin = paginator.page(1)


    return render(request, get_front_theme() + 'physical_delivery.html',{'set':set,'molten_gold':molten_gold,'bullion_coin':bullion_coin,'last_gold_price':Currency_List.objects.get(symbol='XAU18').BuySellPrice['buy'],'count_molten_gold_with_zero_inventory':count_molten_gold_with_zero_inventory,'count_bullion_coin_with_zero_inventory':count_bullion_coin_with_zero_inventory})

#account for theme 02
def register_theme02(request):

    logout(request)

    # Update Check Start
    if site_access_check() == True :
        return redirect('under_update')
    # Update Check End
   

    return render(request, get_customer_theme() + 'register.html',{'settings':Site_Settings.objects.get(code=1001),'set':ContactUs.objects.get(code=1001)})

#account ref for theme 02
def register_theme02_ref_code(request,code):

    # if Customer.objects.filter(referral_link=code).count() == 0 :
    #     return redirect('register_theme02')
    set = ContactUs.objects.get(code=1001)
    try : Customer_refLink_click(ref_link=code, datetime=get_date_time()['timestamp'], ip=get_ip(request)).save()
    except: pass

    return render(request, get_customer_theme() + 'register_ref.html',{'code':code,'set':set})


def forget_password_theme02(request):

    logout(request)

    # Update Check Start
    if site_access_check() == True :
        return redirect('under_update')
    # Update Check End
    set = ContactUs.objects.get(code=1001)

    return render(request, get_customer_theme() + 'forget_password.html',{'settings':Site_Settings.objects.get(code=1001),'set':set})



def get_detail_episode(request,pk):


    try :
        eposite = Melligold_Media_Episode.objects.get(pk=pk)
    except :  return JsonResponse({'type':'danger'})    


    return JsonResponse({'type':'success','eposite_link':eposite.episode_link,'episode_description':eposite.episode_description,'episode_title':eposite.episode_title,'time':eposite.ToshamsiDate['dateinnum'],'picture':f"/media/{eposite.episode_pic}",'category':eposite.episode_category.category.name,'episode_category':eposite.episode_category.name})


def licenses(request):

    evidences = SiteEvidence.objects.all().order_by("-pk")

    return render(request, get_front_theme() + 'licenses.html',{'set':ContactUs.objects.get(code=1001),'evidences':evidences})


def transmission(request):
    
    boxes = Transmission_Box.objects.all().order_by("-pk")
    steps = Transmission_Steps.objects.all()
     
    return render(request, get_front_theme() + 'transmission.html',{'set':ContactUs.objects.get(code=1001),'faq': Faq.objects.filter(act=True).order_by("pk")[:6],'boxes':boxes,'steps':steps})


@cache_page(60 * 60)
def generate_price_chart(request,asset,range_type):  

    current_time = datetime.now()
    current_hour = current_time.hour
    tehran_tz = pytz.timezone('Asia/Tehran')

    def calculate_aggregated_data(start_timestamp, end_timestamp, time_interval):
        all_logs = Account_Price_log.objects.filter(
            symbol=asset,
            date__gte=start_timestamp,
            date__lte=end_timestamp
        )
        logs = all_logs.values('date', 'buy')

        if not logs.exists(): return JsonResponse({'type': 'danger', 'msg': 'اطلاعات یافت نشد'})

        logs_df = pd.DataFrame(list(logs))
        logs_df['date'] = pd.to_numeric(logs_df['date'], errors='coerce')

        if logs_df['date'].isnull().any():
            return JsonResponse({'type': 'danger', 'msg': 'اطلاعات یافت نشد'})

        logs_df['rounded_time'] = (logs_df['date'] // time_interval) * time_interval

        aggregated_data = (
            logs_df.sort_values('date')
            .drop_duplicates('rounded_time', keep='first')
            .sort_values('rounded_time', ascending=True)[['rounded_time', 'buy']] 
        ) 
        values_only = [entry for entry in list(all_logs.values_list('buy', flat=True)) if entry > 0]
        max_price = max(values_only) if values_only else 0
        min_price = min(values_only) if values_only else 0

        return aggregated_data, max_price, min_price, values_only
    
    if range_type == '24': 
        start_timestamp = (current_time - timedelta(minutes=1440)).timestamp()
        end_timestamp = current_time.timestamp()
        time_interval = 15 * 60  

    elif range_type == '7': 
        start_timestamp = (current_time - timedelta(weeks=1)).timestamp()
        end_timestamp = current_time.timestamp()
        time_interval = 2 * 60 * 60

    elif range_type == '30': 
        start_timestamp = (current_time - timedelta(days=30)).timestamp()
        end_timestamp = current_time.timestamp()
        time_interval = 8 * 60 * 60 

    aggregated_data, max_price, min_price, values_only = calculate_aggregated_data(start_timestamp, end_timestamp, time_interval)

    data_array = [
        [f"{time}", int(avg_price)]
        for time, avg_price in zip(aggregated_data['rounded_time'], aggregated_data['buy'])
    ] 

    if len(aggregated_data) >= 2:  
        last_percentage_change = round(
            ((aggregated_data.iloc[-1]['buy'] - aggregated_data.iloc[-2]['buy'])
            / aggregated_data.iloc[-2]['buy']) * 100, 2
        ) 
    avg_price = (max_price + min_price) / 2 if values_only else 0
    price_now = Currency_List.objects.get(symbol='XAU18').BuySellPrice['buy']
    
    try : last_percentage_change  = round((((price_now - avg_price) * 100) / price_now), 2)
    except: last_percentage_change = 0


    data = {'chart_data':data_array, 'min_price':int(min_price), 'max_price':int(max_price),'last_percentage_change':last_percentage_change}


    return JsonResponse({'type':'success', 'msg':'پیام شما با موفقیت ارسال شد',"Chart_data":data})






def report_discrepancy_physical_delivery(request, pk):

    try: bill_gold = Customer_Gold_Order.objects.get(pk=pk, status='Received')
    except:  return render(request,"404.html")

    return render(request, get_front_theme() + 'report_discrepancy.html', {"bill":bill_gold, "pk":pk})


def bank_resources(request):

    paginator = Paginator(Bank_Resources_Receipt.objects.all().order_by("-date"), 12)
    page = request.GET.get('page')

    try:
        receipts = paginator.page(page)
    except PageNotAnInteger:
        receipts = paginator.page(1)
    except EmptyPage:
        receipts = paginator.page(1)

    count_receipts = Bank_Resources_Receipt.objects.all().count()

    return render(request, get_front_theme() + 'bank_resources.html',{'receipts':receipts,'count_receipts':count_receipts,'set':ContactUs.objects.get(code=1001)})
