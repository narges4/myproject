# from operator import truediv
from django.shortcuts import render, get_object_or_404, redirect
from django.core.files.storage import FileSystemStorage
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group, Permission
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse, JsonResponse
from currency.models import *
from exchange.func.theme import *
from customer.models import *
from exchange.func.public import *
from ticket.models import Ticket
from exchange.models import *
from django.db import transaction 
import time
import datetime
from itertools import chain
from django.core import serializers
from django.core.serializers import serialize
from wallet.models import *
import django_urr
from django.urls import resolve
import jdatetime
from datetime import datetime
import khayyam

from django.db.models.functions import Coalesce, Cast
from ticket.models import *
import re
from django.db.models import Q
import urllib
from django.utils.dateparse import parse_date
from django.utils import timezone
from customer.func.public import *
from django.views.decorators.http import require_POST
from openpyxl import Workbook

from PIL import Image
import os

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.utils.dateparse import parse_datetime

from datetime import datetime


def master_login(request):

    logout(request)
    return render(request, get_master_theme() + "login.html", {"ip": get_ip(request)})


def master_login_submit(request):

    if request.method == "POST":

        uname = request.POST.get("uname")
        upass = request.POST.get("upass")

        if uname == "" or upass == "":
            return JsonResponse(
                {"type": "danger", "msg": "لطفا موارد خواسته شده را وارد نمایید"}
            )

        if Master.objects.filter(national_id=uname).count() != 1:
            return JsonResponse(
                {"type": "danger", "msg": "نام کاربری یا رمزعبور صحیح نیست"}
            )

        user = authenticate(username="master-" + uname, password=upass)

        if user != None:

            login(request, user)

            master = Master.objects.get(national_id=uname)
            # delete code
            master.save()

            add_static_report(request, "ورود به سایت")

            return JsonResponse(
                {"type": "success", "msg": "ورود با موفقیت انجام شد ..."}
            )

        else:
            return JsonResponse(
                {"type": "danger", "msg": "نام کاربری یا رمزعبور صحیح نیست"}
            )

    return JsonResponse({"type": "danger", "msg": "نام کاربری یا رمزعبور صحیح نیست"})


def master_code_verify(request):

    # Login Check Start
    if not request.user.is_authenticated:
        return redirect("master_login")
    # Login Check End

    master = Master.objects.get(req_user=request.user)

    if Site_Settings.objects.get(code=1001).is_customer_login == False:
        return redirect("master_login")

    return render(
        request, get_master_theme() + "code_verify.html", {"ip": get_ip(request)}
    )


def master_code_verify_request(request):

    # Login Check Start
    if not request.user.is_authenticated:
        return JsonResponse(
            {"type": "danger", "msg": "ورود شما منقضی شده لطفا مجددا وارد شوید"}
        )
    # Login Check End

    if request.method == "POST":

        master = Master.objects.get(req_user=request.user)

        if (int(master.last_code_datetime) + 60) > int(time.time()):
            return JsonResponse(
                {"type": "danger", "msg": "زمان دریافت کد جدید هر یک دقیقه است"}
            )

        code = code_generator(4)
        result = code_sender(master.mobile, "", code)

        if result[0] == True:

            master.last_code = code
            master.last_code_datetime = get_date_time()["timestamp"]
            master.save()

            add_static_report(request, "درخواست کد ورود")

            return JsonResponse({"type": "success", "msg": "کد با موفقیت ارسال شد"})

    return JsonResponse({"type": "danger", "msg": "در ارسال کد خطایی رخ داده"})


def master_code_verify_submit(request):

    # Login Check Start
    if not request.user.is_authenticated:
        return JsonResponse(
            {"type": "danger", "msg": "ورود شما منقضی شده لطفا مجددا وارد شوید"}
        )
    # Login Check End

    if request.method == "POST":

        code = request.POST.get("code")

        if code == "":
            return JsonResponse(
                {"type": "danger", "msg": "لطفا کد دریافتی خود را وارد نمایید"}
            )

        try:
            code = int(code)
        except:
            add_static_report(request, "وارد کردن کد نادرست برای ورود")
            return JsonResponse({"type": "danger", "msg": "کد وارد شده صحیح نیست"})

        master = Master.objects.get(req_user=request.user)

        if (int(master.last_code_datetime) + 60) < int(time.time()):
            return JsonResponse(
                {
                    "type": "danger",
                    "msg": "کد دریافتی منقضی شده. لطفا کد جدید دریافت نمایید",
                }
            )

        if int(master.last_code) == code:

            master.is_force_code_verify = False
            master.last_code_datetime = 0
            master.save()
            add_static_report(request, "تایید کد ورود")
            return JsonResponse(
                {"type": "success", "msg": "کد ورود با موفقیت تایید شد"}
            )

        else:

            master.is_force_code_verify = True
            master.last_code_datetime = 0
            master.save()
            add_static_report(request, "وارد کردن کد ورود اشتباه")

    return JsonResponse({"type": "danger", "msg": "کد وارد شده صحیح نیست"})


def master_panel(request):

    # master check start
    try:
        code = master_access_check(request)


        if code[0] != 100:
            return redirect(code[1])
    except:
        return redirect("master_login")
    # master check end 

    message = None

    if request.session.get("notification") != None:
        message = request.session.get("notification")
    request.session["notification"] = None 
  
    currency = Currency_List.objects.filter(is_sell=True).order_by("sort")

    tickets = Ticket.objects.filter(status="Waitting").count()
    auth_pendding = Customer.objects.filter(need_auth_check=True).count()
    bills = WalletWithdrawIRT.objects.filter(is_verify=None, is_check=True).count()
    error = Customer_errors_report.objects.filter(status="AwaitingReview").count()
    cards = Customer_card.objects.filter(is_verify=None,is_show=True).count()
    unread_contact = ContactForm.objects.filter(act=False).count()

    cancle_withdrawal = Cancel_Withdrawal_Request.objects.filter(is_verify=None).count()
    ceiling = Customer_Ceiling_List.objects.filter(is_verify=None).count()
    mission_waiting = Customer_Mission.objects.filter(status=None).count()
    exchange_req = Exchange_Request.objects.filter(act=False).count()

    call_req = Contact_Users.objects.filter(act=False).count()

   
    

    counter = {
        "unread_contact": unread_contact,
        "cards": cards,
        "errors": error,
        "tickets": tickets,
        "auth_pendding": auth_pendding,
        "bills": bills,
        "cancle_withdrawal": cancle_withdrawal,
        "ceiling": ceiling,
        "mission_waiting": mission_waiting,
        "exchange_req": exchange_req,
        "call_req": call_req,
    }

    
 
    return render(
        request,
        get_master_theme() + "panel.html",
        {"currency": currency, "counter": counter, "message": message, 'sett':Site_Settings.objects.get(code=1001)},
    )


def master_site_settings(request):

    # master check start
    try:
        code = master_access_check(request)
        if code[0] != 100:
            return redirect(code[1])
    except:
        return redirect("master_login")
    # master check end

    site_settings = Site_Settings.objects.get(code=1001)

    return render(
        request,
        get_master_theme() + "site_settings.html",
        {"site_settings": site_settings},
    )


def master_site_settings_submit(request):

    # master json check start
    try:
        code = master_access_check(request)
        if code[0] != 100:
            return JsonResponse({"type": "danger", "msg": code[2]})
    except:
        return JsonResponse(
            {"type": "danger", "msg": "ورود شما منقضی شده لطفا مجددا وارد شوید"}
        )
    # master json check end

    if request.method == "POST":

        title = request.POST.get("title")
        title_en = request.POST.get("title_en")
        desc = request.POST.get("desc")
        help_txt = request.POST.get("help")
        front_help_txt = request.POST.get("front_help")
        url = request.POST.get("url")
        show_address = request.POST.get("show_address")
        enamad = request.POST.get("enamad")

        if (
            title == ""
            or title_en == ""
            or desc == ""
            or url == ""
            or help_txt == ""
            or show_address == ""
            or front_help_txt == ""
            or enamad == ""
        ):
            return JsonResponse(
                {"type": "danger", "msg": "لطفا موارد خواسته شده را وارد نمایید"}
            )

        if not url.startswith("https://"):
            return JsonResponse(
                {"type": "danger", "msg": "آدرس سایت با https:// شروع میشود"}
            )

        setting = Site_Settings.objects.get(code=1001)
        setting.title = title
        setting.title_en = title_en
        setting.desc = desc
        setting.help_txt = help_txt
        setting.front_help_txt = front_help_txt
        setting.url = url
        setting.show_address = show_address
        setting.enamad = enamad
        setting.save()

        add_static_report(request, "ویرایش تنظیمات پایه سایت")

        return JsonResponse({"type": "success", "msg": "ویرایش با موفقیت انجام شد"})

    return JsonResponse(
        {"type": "danger", "msg": "پردازش مورد نظر با مشکل مواجه شده است"}
    )


def master_site_vector(request):

    # master check start
    try:
        code = master_access_check(request)
        if code[0] != 100:
            return redirect(code[1])
    except:
        return redirect("master_login")
    # master check end

    site_settings = Site_Settings.objects.get(code=1001)

    return render(
        request,
        get_master_theme() + "site_vectors.html",
        {"site_settings": site_settings, "type": "logo"},
    )


def master_site_vector_submit(request, type):

    # master json check start
    try:
        code = master_access_check(request)
        if code[0] != 100:
            return JsonResponse({"type": "danger", "msg": code[2]})
    except:
        return JsonResponse(
            {"type": "danger", "msg": "ورود شما منقضی شده لطفا مجددا وارد شوید"}
        )
    # master json check end

    if request.method == "POST":

        try:

            uploader = upload_file(request.FILES[type], "media", False)
            if uploader[0] != True:
                return JsonResponse({"type": "danger", "msg": uploader[1]})

        except:
            return JsonResponse(
                {"type": "danger", "msg": "در آپلود فایل خطایی رخ داده"}
            )

        setting = Site_Settings.objects.get(code=1001)

        if type == "login":

            oldfile = setting.vector_login_name
            setting.vector_login_name = uploader[2]

        elif type == "swap":

            oldfile = setting.vector_swap_name
            setting.vector_swap_name = uploader[2]

        elif type == "currency_deposite":

            oldfile = setting.vector_currency_deposite_name
            setting.vector_currency_deposite_name = uploader[2]

        elif type == "currency_withdraw":

            oldfile = setting.vector_currency_withdraw_name
            setting.vector_currency_withdraw_name = uploader[2]

        elif type == "irt_deposite":

            oldfile = setting.vector_irt_deposite_name
            setting.vector_irt_deposite_name = uploader[2]

        elif type == "irt_withdraw":

            oldfile = setting.vector_irt_withdraw_name
            setting.vector_irt_withdraw_name = uploader[2]

        elif type == "transfer":

            oldfile = setting.vector_transfer_name
            setting.vector_transfer_name = uploader[2]

        elif type == "inquiry":

            oldfile = setting.vector_inquiry_name
            setting.vector_inquiry_name = uploader[2]

        elif type == "password":

            oldfile = setting.vector_password_name
            setting.vector_password_name = uploader[2]

        elif type == "twostep":

            oldfile = setting.vector_twostep_name
            setting.vector_twostep_name = uploader[2]

        elif type == "error":

            oldfile = setting.vector_error_name
            setting.vector_error_name = uploader[2]

        elif type == "app":

            oldfile = setting.vector_app_name
            setting.vector_app_name = uploader[2]

        elif type == "awards":

            oldfile = setting.vector_awards_name
            setting.vector_awards_name = uploader[2]

        elif type == "uvoucher":

            oldfile = setting.vector_search_uv_name
            setting.vector_search_uv_name = uploader[2]

        setting.save()

        try:

            fs = FileSystemStorage(location="media")
            fs.delete(oldfile)

        except:
            pass

        add_static_report(request, "ویرایش وکتور سایت")
        return JsonResponse(
            {
                "type": "success",
                "msg": "آپلود با موفقیت انجام شد",
                "picture": setting.logo_name,
            }
        )

    return JsonResponse(
        {"type": "danger", "msg": "پردازش مورد نظر با مشکل مواجه شده است"}
    )


def master_site_logo(request):

    # master check start
    try:
        code = master_access_check(request)
        if code[0] != 100:
            return redirect(code[1])
    except:
        return redirect("master_login")
    # master check end

    site_settings = Site_Settings.objects.get(code=1001)

    return render(
        request,
        get_master_theme() + "site_logos.html",
        {"site_settings": site_settings, "type": "logo"},
    )


def master_site_icon(request):

    # master check start
    try:
        code = master_access_check(request)
        if code[0] != 100:
            return redirect(code[1])
    except:
        return redirect("master_login")
    # master check end

    site_settings = Site_Settings.objects.get(code=1001)

    return render(
        request,
        get_master_theme() + "site_logos.html",
        {"site_settings": site_settings, "type": "icon"},
    )


def master_site_favicon(request):

    # master check start
    try:
        code = master_access_check(request)
        if code[0] != 100:
            return redirect(code[1])
    except:
        return redirect("master_login")
    # master check end

    site_settings = Site_Settings.objects.get(code=1001)

    return render(
        request,
        get_master_theme() + "site_logos.html",
        {"site_settings": site_settings, "type": "favicon"},
    )

def master_customer_list(request):

    # master check start
    try:
        code = master_access_check(request)
        if code[0] != 100:
            return redirect(code[1])
    except:
        return redirect("master_login")
    # master check end

    paginator = Paginator(Customer.objects.filter(user__username__startswith='customer-').order_by("-pk"), 10)
    page = request.GET.get("page")

    try:
        querySet = paginator.page(page)
    except PageNotAnInteger:
        querySet = paginator.page(1)
    except EmptyPage:
        querySet = paginator.page(1)

    return render(
        request, get_master_theme() + "customer_list.html", {"querySet": querySet}
    )


def master_customer_search(request):

    # master check start
    try:
        code = master_access_check(request)
        if code[0] != 100:
            return redirect(code[1])
    except:
        return redirect("master_login")
    # master check end

    status = []
    customers = []
    txt = "-"

    if request.method == "POST":

        txt = request.POST.get("txt")
        status = request.POST.get("status")

        if txt != "" and status != "0":

            request.session["search"] = txt
            request.session["status"] = status

            if status == "need_auth_check":
                customer1 = Customer.objects.filter(
                    pk__contains=txt, need_auth_check=True
                )
                customer2 = Customer.objects.filter(
                    first_name__contains=txt, need_auth_check=True
                )
                customer3 = Customer.objects.filter(
                    last_name__contains=txt, need_auth_check=True
                )
                customer4 = Customer.objects.filter(
                    father_name__contains=txt, need_auth_check=True
                )
                customer5 = Customer.objects.filter(
                    birth_date__contains=txt, need_auth_check=True
                )
                customer6 = Customer.objects.filter(
                    sex__contains=txt, need_auth_check=True
                )
                customer7 = Customer.objects.filter(
                    country__contains=txt, need_auth_check=True
                )
                customer8 = Customer.objects.filter(
                    state__contains=txt, need_auth_check=True
                )
                customer9 = Customer.objects.filter(
                    city__contains=txt, need_auth_check=True
                )
                customer10 = Customer.objects.filter(
                    mobile__contains=txt, need_auth_check=True
                )
                customer11 = Customer.objects.filter(
                    address__contains=txt, need_auth_check=True
                )
                customer12 = Customer.objects.filter(
                    national_id__contains=txt, need_auth_check=True
                )

            else:
                customer1 = Customer.objects.filter(pk__contains=txt, status=status)
                customer2 = Customer.objects.filter(
                    first_name__contains=txt, status=status
                )
                customer3 = Customer.objects.filter(
                    last_name__contains=txt, status=status
                )
                customer4 = Customer.objects.filter(
                    father_name__contains=txt, status=status
                )
                customer5 = Customer.objects.filter(
                    birth_date__contains=txt, status=status
                )
                customer6 = Customer.objects.filter(sex__contains=txt, status=status)
                customer7 = Customer.objects.filter(
                    country__contains=txt, status=status
                )
                customer8 = Customer.objects.filter(state__contains=txt, status=status)
                customer9 = Customer.objects.filter(city__contains=txt, status=status)
                customer10 = Customer.objects.filter(
                    mobile__contains=txt, status=status
                )
                customer11 = Customer.objects.filter(
                    address__contains=txt, status=status
                )
                customer12 = Customer.objects.filter(
                    national_id__contains=txt, status=status
                )

            customers = list(
                chain(
                    customer1,
                    customer2,
                    customer3,
                    customer4,
                    customer5,
                    customer6,
                    customer7,
                    customer8,
                    customer9,
                    customer10,
                    customer11,
                    customer12,
                )
            )

            paginator = Paginator(list(dict.fromkeys(customers)), 10)
            page = request.GET.get("page")

            try:
                querySet = paginator.page(page)
            except PageNotAnInteger:
                querySet = paginator.page(1)
            except EmptyPage:
                querySet = paginator.page(1)

        elif txt != "" and status == "0":

            request.session["search"] = txt
            request.session["status"] = status

            customer1 = Customer.objects.filter(pk__contains=txt)
            customer2 = Customer.objects.filter(first_name__contains=txt)
            customer3 = Customer.objects.filter(last_name__contains=txt)
            customer4 = Customer.objects.filter(father_name__contains=txt)
            customer5 = Customer.objects.filter(birth_date__contains=txt)
            customer6 = Customer.objects.filter(sex__contains=txt)
            customer7 = Customer.objects.filter(country__contains=txt)
            customer8 = Customer.objects.filter(state__contains=txt)
            customer9 = Customer.objects.filter(city__contains=txt)
            customer10 = Customer.objects.filter(mobile__contains=txt)
            customer11 = Customer.objects.filter(address__contains=txt)
            customer12 = Customer.objects.filter(national_id__contains=txt)

            customers = list(
                chain(
                    customer1,
                    customer2,
                    customer3,
                    customer4,
                    customer5,
                    customer6,
                    customer7,
                    customer8,
                    customer9,
                    customer10,
                    customer11,
                    customer12,
                )
            )

            paginator = Paginator(list(dict.fromkeys(customers)), 10)
            page = request.GET.get("page")

            try:
                querySet = paginator.page(page)
            except PageNotAnInteger:
                querySet = paginator.page(1)
            except EmptyPage:
                querySet = paginator.page(1)

        elif txt == "" and status != "0":

            request.session["search"] = txt
            request.session["status"] = status

            if status == "need_auth_check":
                customers = Customer.objects.filter(need_auth_check=True)
            else:
                customers = Customer.objects.filter(status=status)
            paginator = Paginator(list(dict.fromkeys(customers)), 10)
            page = request.GET.get("page")

            try:
                querySet = paginator.page(page)
            except PageNotAnInteger:
                querySet = paginator.page(1)
            except EmptyPage:
                querySet = paginator.page(1)

        elif txt == "" and status == "0":

            request.session["search"] = txt
            request.session["status"] = status

            customers = customers
            paginator = Paginator(list(dict.fromkeys(customers)), 10)
            page = request.GET.get("page")

            try:
                querySet = paginator.page(page)
            except PageNotAnInteger:
                querySet = paginator.page(1)
            except EmptyPage:
                querySet = paginator.page(1)

    else:

        try:

            txt = request.session["search"]
            status = request.session["status"]

            if txt != "None" and status != "0":

                if status == "need_auth_check":
                    customer1 = Customer.objects.filter(
                        pk__contains=txt, need_auth_check=True
                    )
                    customer2 = Customer.objects.filter(
                        first_name__contains=txt, need_auth_check=True
                    )
                    customer3 = Customer.objects.filter(
                        last_name__contains=txt, need_auth_check=True
                    )
                    customer4 = Customer.objects.filter(
                        father_name__contains=txt, need_auth_check=True
                    )
                    customer5 = Customer.objects.filter(
                        birth_date__contains=txt, need_auth_check=True
                    )
                    customer6 = Customer.objects.filter(
                        sex__contains=txt, need_auth_check=True
                    )
                    customer7 = Customer.objects.filter(
                        country__contains=txt, need_auth_check=True
                    )
                    customer8 = Customer.objects.filter(
                        state__contains=txt, need_auth_check=True
                    )
                    customer9 = Customer.objects.filter(
                        city__contains=txt, need_auth_check=True
                    )
                    customer10 = Customer.objects.filter(
                        mobile__contains=txt, need_auth_check=True
                    )
                    customer11 = Customer.objects.filter(
                        address__contains=txt, need_auth_check=True
                    )
                    customer12 = Customer.objects.filter(
                        national_id__contains=txt, need_auth_check=True
                    )

                else:
                    customer1 = Customer.objects.filter(pk__contains=txt, status=status)
                    customer2 = Customer.objects.filter(
                        first_name__contains=txt, status=status
                    )
                    customer3 = Customer.objects.filter(
                        last_name__contains=txt, status=status
                    )
                    customer4 = Customer.objects.filter(
                        father_name__contains=txt, status=status
                    )
                    customer5 = Customer.objects.filter(
                        birth_date__contains=txt, status=status
                    )
                    customer6 = Customer.objects.filter(
                        sex__contains=txt, status=status
                    )
                    customer7 = Customer.objects.filter(
                        country__contains=txt, status=status
                    )
                    customer8 = Customer.objects.filter(
                        state__contains=txt, status=status
                    )
                    customer9 = Customer.objects.filter(
                        city__contains=txt, status=status
                    )
                    customer10 = Customer.objects.filter(
                        mobile__contains=txt, status=status
                    )
                    customer11 = Customer.objects.filter(
                        address__contains=txt, status=status
                    )
                    customer12 = Customer.objects.filter(
                        national_id__contains=txt, status=status
                    )

                customers = list(
                    chain(
                        customer1,
                        customer2,
                        customer3,
                        customer4,
                        customer5,
                        customer6,
                        customer7,
                        customer8,
                        customer9,
                        customer10,
                        customer11,
                        customer12,
                    )
                )

                paginator = Paginator(list(dict.fromkeys(customers)), 10)
                page = request.GET.get("page")

                try:
                    querySet = paginator.page(page)
                except PageNotAnInteger:
                    querySet = paginator.page(1)
                except EmptyPage:
                    querySet = paginator.page(1)

            elif txt != "None" and status == "0":

                customer1 = Customer.objects.filter(pk__contains=txt)
                customer2 = Customer.objects.filter(first_name__contains=txt)
                customer3 = Customer.objects.filter(last_name__contains=txt)
                customer4 = Customer.objects.filter(father_name__contains=txt)
                customer5 = Customer.objects.filter(birth_date__contains=txt)
                customer6 = Customer.objects.filter(sex__contains=txt)
                customer7 = Customer.objects.filter(country__contains=txt)
                customer8 = Customer.objects.filter(state__contains=txt)
                customer9 = Customer.objects.filter(city__contains=txt)
                customer10 = Customer.objects.filter(mobile__contains=txt)
                customer11 = Customer.objects.filter(address__contains=txt)
                customer12 = Customer.objects.filter(national_id__contains=txt)

                customers = list(
                    chain(
                        customer1,
                        customer2,
                        customer3,
                        customer4,
                        customer5,
                        customer6,
                        customer7,
                        customer8,
                        customer9,
                        customer10,
                        customer11,
                        customer12,
                    )
                )

                paginator = Paginator(list(dict.fromkeys(customers)), 10)
                page = request.GET.get("page")

                try:
                    querySet = paginator.page(page)
                except PageNotAnInteger:
                    querySet = paginator.page(1)
                except EmptyPage:
                    querySet = paginator.page(1)

            elif txt == "None" and status != "None":

                if status == "need_auth_check":
                    customers = Customer.objects.filter(need_auth_check=True)
                else:
                    customers = Customer.objects.filter(status=status)
                paginator = Paginator(list(dict.fromkeys(customers)), 10)
                page = request.GET.get("page")

                try:
                    querySet = paginator.page(page)
                except PageNotAnInteger:
                    querySet = paginator.page(1)
                except EmptyPage:
                    querySet = paginator.page(1)

            elif txt == "None" and status == "None":

                customers = customers
                paginator = Paginator(list(dict.fromkeys(customers)), 10)
                page = request.GET.get("page")

                try:
                    querySet = paginator.page(page)
                except PageNotAnInteger:
                    querySet = paginator.page(1)
                except EmptyPage:
                    querySet = paginator.page(1)

        except:
            pass

    return render(
        request, get_master_theme() + "customer_list.html", {"querySet": querySet}
    )


def master_customer_detail(request, pk):

    # master check start
    try:
        code = master_access_check(request)
        if code[0] != 100: return redirect(code[1])
    except: return redirect("master_login")
    # master check end

    message = None
    if request.session.get("notification") != None:
        message = request.session.get("notification")
    request.session["notification"] = None
    
    try: 
        customer = Customer.objects.get(pk=pk)
        if (not customer.user.username.startswith('customer-')) and customer.representation_register == False:
            return redirect("master_customer_list")
    except:
        return redirect("master_customer_list")
    activities = Site_Static_log.objects.values('desc').exclude(uname=None).distinct()
    wallet = Currency_List.objects.all().order_by("sort")
    ceilings = Customer_Ceiling_List.objects.filter(
        uname=Customer.objects.get(pk=pk)
    ).order_by("-pk")
    notes = Notes.objects.filter(customer=customer).order_by("-pk")
    auths = Auth.objects.filter(customer=customer).order_by("-pk")
    customerstatus = CUSTOMERSTATUS

    # withdrawal = WalletWithdrawIRT.objects.filter(uname=customer).order_by('-pk')
    log = Site_Static_log.objects.filter(uname=Customer.objects.get(pk=pk)).order_by(
        "-pk"
    )

    if customer.req_user.startswith("customer-"):

        referral = Customer.objects.filter(
            up_referral_link=customer.referral_link
        ).order_by("-pk")

    else:
        referral = Customer.objects.filter(
            reseller_upper_link=customer.referral_link
        ).order_by("-pk")

    notifications = Site_notifications.objects.filter(customer=customer).order_by("-pk")
    cards = Customer_card.objects.filter(uname=customer).order_by("-pk")
    factor = Currency_BuySell_List.objects.filter(
        uname=Customer.objects.get(pk=pk)
    ).order_by("-pk")

    dep_query = Currency_depositeWithdraw_List.objects.filter(uname=customer).order_by(
        "-pk"
    )

    deposit = dep_query.filter(bill_type="deposite", from_gateway=False).order_by("-pk")
    withdrawal = dep_query.filter(bill_type="withdraw").order_by("-pk")
    deposit_gateway = dep_query.filter(
        bill_type="deposite", from_gateway=True
    ).order_by("-pk")

    Withdraws = WalletWithdrawIRT.objects.filter(uname=customer).order_by("-pk")
    rial_deposit = Online_Wallet.objects.filter(
        owner=Customer.objects.get(pk=pk)
    ).order_by("-pk")
    bank = Site_Banks.objects.filter(act=True)
    tickets = Ticket.objects.filter(customer=customer).order_by("-pk")
    investment = CustomerInvestment.objects.filter(uname=customer).order_by("-pk")
    classic_market = Marker_PTOP.objects.filter(uname_request=customer).order_by("-pk")
    buy_sell_market = Market_Customer_PTOP.objects.filter(uname=customer).order_by(
        "-pk"
    )

    gateway = Geteway_Currency_request_personal.objects.filter(uname=customer).order_by(
        "-pk"
    )

    currency_direct = wallet.filter(is_direct=True, is_show=True, master_show=True)

    orders = Customer_Gold_Order.objects.filter(uname=customer).order_by("-pk")

    all_sms = Send_News_Sms.objects.filter(
        phone_numnber=customer.mobile, date__gte=customer.reg_date
    )
    friends = Customer_Friend.objects.filter(uname=customer)

    quick_purchase_packages = Quick_Purchase_Package.objects.filter(uname=customer).order_by("-pk")
    heirs = Customer_Heir.objects.filter(uname=customer)
    heirs_logs = Customer_Heir_Log.objects.filter(uname=customer)
    daily_buysells = Daily_Buysell.objects.filter(uname=customer).order_by("-pk")
    daily_bs_receipts = Currency_BuySell_List.objects.filter(uname=customer, is_daily_buysell=True).order_by('-pk')

    departments = TICKETDEPARTMENT

    paginator = Paginator(currency_direct, 10)
    page = request.GET.get("page")
    try:
        currency_direct = paginator.page(page)
    except PageNotAnInteger:
        currency_direct = paginator.page(1)
    except EmptyPage:
        currency_direct = paginator.page(1)

    paginator = Paginator(deposit_gateway, 10)
    page = request.GET.get("page")
    try:
        deposit_gateway = paginator.page(page)
    except PageNotAnInteger:
        deposit_gateway = paginator.page(1)
    except EmptyPage:
        deposit_gateway = paginator.page(1)

    paginator = Paginator(gateway, 10)
    page = request.GET.get("page")
    try:
        gateway = paginator.page(page)
    except PageNotAnInteger:
        gateway = paginator.page(1)
    except EmptyPage:
        gateway = paginator.page(1)

    paginator = Paginator(investment, 10)
    page = request.GET.get("page")
    try:
        investment = paginator.page(page)
    except PageNotAnInteger:
        investment = paginator.page(1)
    except EmptyPage:
        investment = paginator.page(1)

    paginator = Paginator(buy_sell_market, 10)
    page = request.GET.get("page")
    try:
        buy_sell_market = paginator.page(page)
    except PageNotAnInteger:
        buy_sell_market = paginator.page(1)
    except EmptyPage:
        buy_sell_market = paginator.page(1)

    paginator = Paginator(wallet, 10)
    page = request.GET.get("page")
    try:
        wallet = paginator.page(page)
    except PageNotAnInteger:
        wallet = paginator.page(1)
    except EmptyPage:
        wallet = paginator.page(1)

    paginator = Paginator(notifications, 10)
    page = request.GET.get("page")
    try:
        notifications = paginator.page(page)
    except PageNotAnInteger:
        notifications = paginator.page(1)
    except EmptyPage:
        notifications = paginator.page(1)

    paginator = Paginator(ceilings, 10)
    page = request.GET.get("page")
    try:
        ceilings = paginator.page(page)
    except PageNotAnInteger:
        ceilings = paginator.page(1)
    except EmptyPage:
        ceilings = paginator.page(1)

    paginator = Paginator(notes, 10)
    page = request.GET.get("page")
    try:
        notes = paginator.page(page)
    except PageNotAnInteger:
        notes = paginator.page(1)
    except EmptyPage:
        notes = paginator.page(1)

    paginator = Paginator(withdrawal, 10)
    page = request.GET.get("page")
    try:
        withdrawal = paginator.page(page)
    except PageNotAnInteger:
        withdrawal = paginator.page(1)
    except EmptyPage:
        withdrawal = paginator.page(1)

    paginator = Paginator(log, 10)
    page = request.GET.get("page")
    try:
        log = paginator.page(page)
    except PageNotAnInteger:
        log = paginator.page(1)
    except EmptyPage:
        log = paginator.page(1)

    paginator = Paginator(referral, 10)
    page = request.GET.get("page")
    try:
        referral = paginator.page(page)
    except PageNotAnInteger:
        referral = paginator.page(1)
    except EmptyPage:
        referral = paginator.page(1)

    paginator = Paginator(cards, 10)
    page = request.GET.get("page")
    try:
        cards = paginator.page(page)
    except PageNotAnInteger:
        cards = paginator.page(1)
    except EmptyPage:
        cards = paginator.page(1)

    paginator = Paginator(factor, 10)
    page = request.GET.get("page")
    try:
        factor = paginator.page(page)
    except PageNotAnInteger:
        factor = paginator.page(1)
    except EmptyPage:
        factor = paginator.page(1)

    paginator = Paginator(deposit, 10)
    page = request.GET.get("page")
    try:
        deposit = paginator.page(page)
    except PageNotAnInteger:
        deposit = paginator.page(1)
    except EmptyPage:
        deposit = paginator.page(1)

    paginator = Paginator(Withdraws, 10)
    page = request.GET.get("page")
    try:
        Withdraws = paginator.page(page)
    except PageNotAnInteger:
        Withdraws = paginator.page(1)
    except EmptyPage:
        Withdraws = paginator.page(1)

    paginator = Paginator(rial_deposit, 10)
    page = request.GET.get("page")
    try:
        rial_deposit = paginator.page(page)
    except PageNotAnInteger:
        rial_deposit = paginator.page(1)
    except EmptyPage:
        rial_deposit = paginator.page(1)

    paginator = Paginator(tickets, 10)
    page = request.GET.get("page")
    try:
        tickets = paginator.page(page)
    except PageNotAnInteger:
        tickets = paginator.page(1)
    except EmptyPage:
        tickets = paginator.page(1)

    paginator = Paginator(classic_market, 10)
    page = request.GET.get("page")
    try:
        classic_market = paginator.page(page)
    except PageNotAnInteger:
        classic_market = paginator.page(1)
    except EmptyPage:
        classic_market = paginator.page(1)

    paginator = Paginator(orders, 10)
    page = request.GET.get("page")
    try:
        orders = paginator.page(page)
    except PageNotAnInteger:
        orders = paginator.page(1)
    except EmptyPage:
        orders = paginator.page(1)

    paginator = Paginator(all_sms, 10)
    page = request.GET.get("page")
    try:
        all_sms = paginator.page(page)
    except PageNotAnInteger:
        all_sms = paginator.page(1)
    except EmptyPage:
        all_sms = paginator.page(1)

    paginator = Paginator(friends, 10)
    page = request.GET.get("page")
    try:
        friends = paginator.page(page)
    except PageNotAnInteger:
        friends = paginator.page(1)
    except EmptyPage:
        friends = paginator.page(1)


    paginator = Paginator(quick_purchase_packages, 10)
    page = request.GET.get("page")
    try:
        quick_purchase_packages = paginator.page(page)
    except PageNotAnInteger:
        quick_purchase_packages = paginator.page(1)
    except EmptyPage:
        quick_purchase_packages = paginator.page(1)


    paginator = Paginator(daily_buysells, 10)
    page = request.GET.get("page")
    try:
        daily_buysells = paginator.page(page)
    except PageNotAnInteger:
        daily_buysells = paginator.page(1)
    except EmptyPage:
        daily_buysells = paginator.page(1)

    Custom_Price = Currency_BuySell_Custom_Price.objects.filter(process_based_on='price',uname=customer).order_by('-pk')
    paginator = Paginator(Custom_Price, 10)
    page = request.GET.get("page")
    try:
        Customs_Price = paginator.page(page)
    except PageNotAnInteger:
        Customs_Price = paginator.page(1)
    except EmptyPage:
        Customs_Price = paginator.page(1)


    Custom_Datetime = Currency_BuySell_Custom_Price.objects.filter(process_based_on='datetime',uname=customer).order_by('-pk')
    paginator = Paginator(Custom_Datetime, 10)
    page = request.GET.get("page")
    try:
        Customs_Datetime = paginator.page(page)
    except PageNotAnInteger:
        Customs_Datetime = paginator.page(1)
    except EmptyPage:
        Customs_Datetime = paginator.page(1)

    paginator = Paginator(heirs, 10)
    page = request.GET.get("page")
    try:
        heirs = paginator.page(page)
    except PageNotAnInteger:
        heirs = paginator.page(1)
    except EmptyPage:
        heirs = paginator.page(1)

    paginator = Paginator(heirs_logs, 10)
    page = request.GET.get("page")
    try:
        heirs_logs = paginator.page(page)
    except PageNotAnInteger:
        heirs_logs = paginator.page(1)
    except EmptyPage:
        heirs_logs = paginator.page(1)

    paginator = Paginator(daily_bs_receipts, 10)
    page = request.GET.get("page")
    try:
        daily_bs_receipts = paginator.page(page)
    except PageNotAnInteger:
        daily_bs_receipts = paginator.page(1)
    except EmptyPage:
        daily_bs_receipts = paginator.page(1)
    
    banks = Site_Banks.objects.filter(act=True)
    today = int(get_date_time()["shamsi_date"][:4])

    return render(
        request,
        get_master_theme() + "customer_detail.html",
        {
            
            "querySet_ConnectionLogs": paginate(request, Expert_Customer_Connection_Log.objects.filter(uname=customer, goal__is_active=True
                                                                                                       ).annotate(is_chack=Subquery(Customer_Communication.objects.filter(
                                                                                                           uname=OuterRef('uname'), goal=OuterRef('goal')).values('id'
                                                                                                        ).annotate(count=Count('id')).values('count')[:1])).order_by("-pk")),
            "auth": Auth_Category.objects.filter(active=True),
            "currency_direct": currency_direct,
            "deposit_gateway": deposit_gateway,
            "gateway": gateway,
            "year": range((today - 81), today),
            "buy_sell_market": buy_sell_market,
            "month": range(1, 13),
            "classic_market": classic_market,
            "days": range(1, 32),
            "investment": investment,
            "departments": departments,
            "tickets": tickets,
            "rial_deposit": rial_deposit,
            "Withdraws": Withdraws,
            "deposit": deposit,
            "factor": factor,
            "cards": cards,
            "customer": customer,
            "wallet": wallet,
            "ceilings": ceilings,
            "notes": notes,
            "withdrawal": withdrawal,
            "log": log,
            "auths": auths,
            "customerstatus": customerstatus,
            "referral": referral,
            "notifications": notifications,
            "bank": bank,
            "customer_site_register": Customer.objects.filter(
                national_id=customer.national_id
            ),
            "orders": orders,
            "all_sms": all_sms,
            "friends": friends,
            "message": message,
            "quick_purchase_packages": quick_purchase_packages,
            "heirs": heirs,
            "heirs_logs": heirs_logs,
            "daily_buysells": daily_buysells,
            "Customs_Price": Customs_Price,
            "Customs_Datetime": Customs_Datetime,
            'daily_bs_receipts': daily_bs_receipts,
            "card_operation": Site_Settings.objects.get(code=1001).card_shakar_check,
            "banks": banks,
            "activities" : activities,
            "today": get_date_time()["shamsi_date"],
            
        },
    )


def master_customer_detail_reports_search(request, pk):
    # master check start
    try:
        code = master_access_check(request)
        if code[0] != 100:
            return redirect(code[1])
    except:
        return redirect("master_login")
    # master check end

    try:
        customer = Customer.objects.get(pk=pk)
        
        if (not customer.user.username.startswith('customer-')) and customer.representation_register == False:
            return redirect("master_customer_list")
        
    except Customer.DoesNotExist:
        return redirect("master_customer_list")

    message = None
    if request.session.get("notification") != None:
        message = request.session.get("notification")
    request.session["notification"] = None

    log = Site_Static_log.objects.filter(uname=customer).exclude(uname=None).distinct()

    if request.method == "POST":
        start_date = request.POST.get("date-picker-shamsi")  
        start_time = request.POST.get("start_time") 
        end_date = request.POST.get("date-picker-shamsii")  
        end_time = request.POST.get("end_time") 
        desc = request.POST.get("desc", "0")

        request.session["date-picker-shamsi"] = start_date
        request.session["start_time"] = start_time
        request.session["date-picker-shamsii"] = end_date
        request.session["end_time"] = end_time
        request.session["desc"] = desc


        if start_date == "" or start_date == None or start_date == "None":
            request.session["notification"] = ["وارد کردن اولین تاریخ جستجو الزامی است"]
            return redirect("master_customer_detail_reports_search", pk=pk)

        if start_time == "" or start_time == None or start_time == "None":
            request.session["notification"] = ["وارد کردن آخرین تاریخ جستجو الزامی است"]
            return redirect("master_customer_detail_reports_search", pk=pk)

        if desc == "0":
            request.session["notification"] = ["انتخاب کردن فعالیت مورد نظر الزامی است"]
            return redirect("master_customer_detail_reports_search", pk=pk)
        
    else:
        start_date = request.session.get("date-picker-shamsi", "0")
        start_time = request.session.get("start_time", "0")
        end_date = request.session.get("date-picker-shamsii", "0")
        end_time = request.session.get("end_time", "0")
        desc = request.session.get("desc", "0")

    try:
        sdata = start_date.split("/")
        newdata = khayyam.JalaliDate(sdata[0], sdata[1], sdata[2]).todate()
        newdata = str(newdata).split("-")

        earlier = (
            newdata[0] + "-" + newdata[1] + "-" + newdata[2] + f" {start_time}:00"
        )
        start_date = int(
            datetime.strptime(earlier, "%Y-%m-%d %H:%M:%S").timestamp()
        )

    except:
        request.session["notification"] = [" تاریخ وارد شده نامعتبر است"]
        return redirect("master_customer_detail_reports_search", pk=pk)

    try:
        if end_date == "" or end_date == None or end_date == "None":
            end_date = datetime.strptime(earlier, "%Y-%m-%d %H:%M:%S") + timedelta(days=(10))
            end_date = int(
                datetime.strptime(str(end_date), "%Y-%m-%d %H:%M:%S").timestamp()
            )
        else:
            if end_time == "" or end_time == None or end_time == "None":
                request.session["notification"] = ["وارد کردن اولین ساعت جستجو الزامی است"]
                return redirect("master_customer_detail_reports_search", pk=pk)


            sdata = end_date.split("/")
            newdata = khayyam.JalaliDate(sdata[0], sdata[1], sdata[2]).todate()
            newdata = str(newdata).split("-")
            last = (
                newdata[0] + "-" + newdata[1] + "-" + newdata[2] + f" {end_time}:00"
            )
            end_date = int(datetime.strptime(last, "%Y-%m-%d %H:%M:%S").timestamp())

            days_later = datetime.strptime(earlier, "%Y-%m-%d %H:%M:%S") + timedelta(days=(10))
            days_later = int(
                datetime.strptime(str(days_later), "%Y-%m-%d %H:%M:%S").timestamp()
            )

            if start_date > end_date:
                request.session["notification"] = [" تاریخ شروع نمیتواند بزرگتر از تاریخ پایان باشد "]
                return redirect("master_customer_detail_reports_search", pk=pk)


    except:
        request.session["notification"] = [" تاریخ وارد شده نامعتبر است"]
        return redirect("master_customer_detail_reports_search", pk=pk)

    if desc == "all":
        log = log.filter(date__gte=start_date,date__lte=end_date)
    else:
        log = log.filter(desc=desc,date__gte=start_date,date__lte=end_date)

    activities = Site_Static_log.objects.values('desc').exclude(uname=None).distinct()

    paginator = Paginator(log.order_by("-pk"), 10)
    page = request.GET.get("page")

    try:
        log = paginator.page(page)
    except PageNotAnInteger:
        log = paginator.page(1)
    except EmptyPage:
        log = paginator.page(1)

    return render(
        request, get_master_theme() + "customer_detail.html", {
            "log": log,
            "activities": activities,
            "today": get_date_time()["shamsi_date"],
            "customer": customer,
            "message" : message,
        }
    )


def master_customer_note_submit(request, pk):

    # master json check start
    try:
        code = master_access_check(request)
        if code[0] != 100:
            return JsonResponse({"type": "danger", "msg": code[2]})
    except:
        return JsonResponse(
            {"type": "danger", "msg": "ورود شما منقضی شده لطفا مجددا وارد شوید"}
        )
    # master json check end

    if request.method == "POST":

        desc = request.POST.get("desc")

        if desc == "":
            return JsonResponse(
                {"type": "danger", "msg": "لطفا موارد خواسته شده را وارد نمایید"}
            )

        manager = code[3]

        try:
            pic_note = upload_file(request.FILES["file_note"], "media/note", False)
            if pic_note[0] != True:
                return JsonResponse({"type": "danger", "msg": pic_note[1]})

        except:
            pic_note = ["", "-", "-"]

        date = get_date_time()["timestamp"]
        note = Notes(
            customer=Customer.objects.get(pk=pk),
            master=manager,
            desc=desc,
            date=date,
            file=pic_note[2],
        )
        note.save()

        add_static_report(request, "ثبت یادداشت جدید")

        return JsonResponse(
            {
                "type": "success",
                "msg": " یادداشت شما با موفقیت ثبت شد",
                "pk": note.pk,
                "date": str(note.ToshamsiDate["toshamsidate"]),
                "manager": f"{manager.first_name} {manager.last_name}",
                "desc": note.desc,
                "pic": f"/media/note/{pic_note[2]}",
            }
        )

    return JsonResponse(
        {"type": "danger", "msg": "ثبت یادداشت مورد نظر با مشکل مواجه شده است"}
    )


def master_about(request):

    # master check start
    try:
        code = master_access_check(request)
        if code[0] != 100:
            return redirect(code[1])
    except:
        return redirect("master_login")
    # master check end

    sett = AboutUs.objects.get(code=1001)

    return render(request, get_master_theme() + "about.html", {"sett": sett})


def master_about_submit(request):

    # master json check start
    try:
        code = master_access_check(request)
        if code[0] != 100:
            return JsonResponse({"type": "danger", "msg": code[2]})
    except:
        return JsonResponse(
            {"type": "danger", "msg": "ورود شما منقضی شده لطفا مجددا وارد شوید"}
        )
    # master json check end

    if request.method == "POST":

        txt = request.POST.get("txt")
        desc = request.POST.get("desc")

        if txt == "" or desc == "":
            return JsonResponse(
                {"type": "danger", "msg": "لطفا تمامی موارد را وارد نمایید"}
            )

        sett = AboutUs.objects.get(code=1001)

        try:

            uploader = upload_file(request.FILES["picture"], "media", False)
            if uploader[0] != True:
                return JsonResponse({"type": "danger", "msg": uploader[1]})

            fs = FileSystemStorage(location="media")
            fs.delete(sett.pic_name)
            sett.pic_name = uploader[2]

        except:
            pass

        sett.txt = txt
        sett.desc = desc
        sett.pic_name = sett.pic_name
        sett.save()

        add_static_report(request, "ویرایش درباره سایت")

        return JsonResponse(
            {
                "type": "success",
                "msg": "اطلاعات با موفقیت ثبت شد",
                "picture": sett.pic_name,
            }
        )

    return JsonResponse(
        {"type": "danger", "msg": "پردازش مورد نظر با مشکل مواجه شده است"}
    )






# delete code
# delete code
# delete code
# delete code
# delete code
# delete code
# delete code
# delete code
# delete code
# delete code
# delete code
# delete code
# delete code
# delete code
# delete code
# delete code
# delete code
# delete code
# delete code
# delete code
# delete code
# delete code
# delete code
# delete code
# delete code
# delete code
# delete code
# delete code
# delete code
# delete code
# delete code
# .
# .
# .


def master_site_cities_with_represent(request):

    # master check start
    try:
        code = master_access_check(request)
        if code[0] != 100:
            return redirect(code[1])
    except:
        return redirect("master_login")
    # master check end

    paginator = Paginator(Site_Cities_With_Represent.objects.all().order_by("sort"), 10)
    page = request.GET.get("page")

    try:
        querySet = paginator.page(page)
    except PageNotAnInteger:
        querySet = paginator.page(1)
    except EmptyPage:
        querySet = paginator.page(1)

    return render(
        request,
        get_master_theme() + "site_cities_with_represent.html",
        {"querySet": querySet},
    )


def master_site_cities_with_represent_submit(request):

    # master json check start
    try:
        code = master_access_check(request)
        if code[0] != 100:
            return JsonResponse({"type": "danger", "msg": code[2]})
    except:
        return JsonResponse(
            {"type": "danger", "msg": "ورود شما منقضی شده لطفا مجددا وارد شوید"}
        )
    # master json check end

    if request.method == "POST":

        name = request.POST.get("name")
        established = request.POST.get("established")
        sort = request.POST.get("sort")

        if name == "" or sort == "":
            return JsonResponse(
                {"type": "danger", "msg": "لطفا تمامی موارد خواسته شده را وارد نمایید"}
            )

        try:
            sort = int(sort)
        except:
            return JsonResponse(
                {"type": "danger", "msg": "لطفا ترتیب را به صورت عددی وارد نمایید"}
            )

        established = False if established != "on" else True

        if Site_Cities_With_Represent.objects.filter(name=name).count() != 0:
            return JsonResponse(
                {"type": "danger", "msg": "لطفا از نام تکراری استفاده نکنید"}
            )

        try:

            uploader = upload_file(request.FILES["logo"], "media", False)
            if uploader[0] != True:
                return JsonResponse({"type": "danger", "msg": uploader[1]})

        except:
            return JsonResponse(
                {"type": "danger", "msg": "در آپلود فایل خطایی رخ داده"}
            )

        city = Site_Cities_With_Represent(
            name=name, logo_name=uploader[2], established=established, sort=sort
        )
        city.save()

        add_static_report(request, "افزودن شهر دارای نمایندگی جدید")
        return JsonResponse(
            {
                "type": "success",
                "msg": " شهر جدید با موفقیت ثبت شد",
                "name": name,
                "pk": city.pk,
                "logo": uploader[1],
                "sort": sort,
            }
        )

    return JsonResponse(
        {"type": "danger", "msg": "پردازش مورد نظر با مشکل مواجه شده است"}
    )


def master_site_cities_with_represent_status_change(request, pk):

    # master json check start
    try:
        code = master_access_check(request)
        if code[0] != 100:
            return JsonResponse({"type": "danger", "msg": code[2]})
    except:
        return JsonResponse(
            {"type": "danger", "msg": "ورود شما منقضی شده لطفا مجددا وارد شوید"}
        )
    # master json check end

    city = Site_Cities_With_Represent.objects.get(pk=pk)

    if city.act == False:
        city.act = True
        city.save()
        add_static_report(request, "فعال سازی شهرهای دارای نمایندگی")
        return JsonResponse(
            {
                "type": "success",
                "msg": "شهر مورد نظر با موفقیت فعال شد",
                "status": city.act,
            }
        )

    elif city.act == True:
        city.act = False
        city.save()
        add_static_report(request, "غیرفعال سازی شهرهای دارای نمایندگی")
        return JsonResponse(
            {
                "type": "success",
                "msg": "شهر مورد نظر با موفقیت غیرفعال شد",
                "status": city.act,
            }
        )

    return JsonResponse(
        {"type": "danger", "msg": "تغییر وضعیت مورد نظر با مشکل مواجه شده است"}
    )


def master_site_cities_with_represent_edit_submit(request, pk):

    # master json check start
    try:
        code = master_access_check(request)
        if code[0] != 100:
            return JsonResponse({"type": "danger", "msg": code[2]})
    except:
        return JsonResponse(
            {"type": "danger", "msg": "ورود شما منقضی شده لطفا مجددا وارد شوید"}
        )
    # master json check end

    if request.method == "POST":

        name = request.POST.get("name_modal")
        sort = request.POST.get("sort_modal")

        city = Site_Cities_With_Represent.objects.get(pk=pk)
        established = request.POST.get("established_status")

        if name == "" or sort == "":
            return JsonResponse(
                {"type": "danger", "msg": "لطفا تمامی موارد خواسته شده را وارد نمایید"}
            )

        try:
            sort = int(sort)
        except:
            return JsonResponse(
                {"type": "danger", "msg": "لطفا ترتیب را به صورت عددی وارد نمایید"}
            )

        if (
            Site_Cities_With_Represent.objects.filter(name=name).exclude(pk=pk).count()
            != 0
        ):
            return JsonResponse(
                {"type": "danger", "msg": "لطفا از نام تکراری استفاده نکنید"}
            )

        established = False if established != "on" else True

        if len(name) > 200:
            return JsonResponse(
                {"type": "danger", "msg": "حداکثر کاراکتر نام 200 کاراکتر است"}
            )

        try:
            uploader = upload_file(request.FILES["logoo"], "media", False)
            if uploader[0] != True:
                return JsonResponse({"type": "danger", "msg": uploader[1]})

            fs = FileSystemStorage(location="media")
            fs.delete(city.logo_name)
            city.logo_name = uploader[2]

        except:
            pass

        city.name = name
        city.logo_name = city.logo_name
        city.established = established
        city.sort = sort
        city.save()

        add_static_report(request, "ویرایش اطلاعات شهرهای دارای نمایندگی ")
        return JsonResponse(
            {
                "type": "success",
                "msg": "شهر موردنظر با موفقیت ویرایش شد",
                "id": city.pk,
                "name": name,
                "logo": city.logo_name,
                "sort": sort,
            }
        )

    return JsonResponse({"type": "danger", "msg": "ویرایش شهر با مشکل مواجه شده است"})


def master_site_cities_with_represent_delete_submit(request, pk):

    # master json check start
    try:
        code = master_access_check(request)
        if code[0] != 100:
            return JsonResponse({"type": "danger", "msg": code[2]})
    except:
        return JsonResponse(
            {"type": "danger", "msg": "ورود شما منقضی شده لطفا مجددا وارد شوید"}
        )
    # master json check end

    if Site_Branches_Each_Representative.objects.filter(city=pk).count() != 0:
        return JsonResponse({"type": "danger", "msg": "حذف شهر امکان پذیر نیست."})

    if (
        Site_Products.objects.filter(
            city=Site_Cities_With_Represent.objects.get(pk=pk)
        ).count()
        != 0
    ):
        return JsonResponse({"type": "danger", "msg": "حذف شهر امکان پذیر نیست."})

    try:

        city = Site_Cities_With_Represent.objects.get(pk=pk)
        fs = FileSystemStorage(location="media")
        fs.delete(city.logo_name)
        city.delete()

        add_static_report(request, "حذف شهرهای دارای نمایندگی")
        return JsonResponse({"type": "success", "msg": "شهر با موفقیت حذف شد"})

    except:
        return JsonResponse({"type": "danger", "msg": "حذف شهر با مشکل مواجه شده است"})


def master_site_branches_each_representative(request, pk):

    # master check start
    try:
        code = master_access_check(request)
        if code[0] != 100:
            return redirect(code[1])
    except:
        return redirect("master_login")
    # master check end

    paginator = Paginator(
        Site_Branches_Each_Representative.objects.filter(
            city=Site_Cities_With_Represent.objects.get(pk=pk)
        ).order_by("-pk"),
        10,
    )
    page = request.GET.get("page")

    try:
        querySet = paginator.page(page)
    except PageNotAnInteger:
        querySet = paginator.page(1)
    except EmptyPage:
        querySet = paginator.page(1)

    return render(
        request,
        get_master_theme() + "site_branches_each_representative.html",
        {
            "querySet": querySet,
            "city_id": pk,
            "manager": Master.objects.filter(is_master=False).order_by("-pk"),
            "deliverer":Site_Branches_Deliverer.objects.filter(act=True)
        },
    )


def master_site_branches_each_representative_submit(request, pk):

    # master json check start
    try:
        code = master_access_check(request)
        if code[0] != 100:
            return JsonResponse({"type": "danger", "msg": code[2]})
    except:
        return JsonResponse(
            {"type": "danger", "msg": "ورود شما منقضی شده لطفا مجددا وارد شوید"}
        )
    # master json check end

    if request.method == "POST":

        name = request.POST.get("name")
        address = request.POST.get("address")
        working_time = request.POST.get("working_time")
        phone_numbers = request.POST.get("phone_numbers")
        manager = request.POST.getlist("category[]")
        deliverer = request.POST.get("deliverer")
        location = request.POST.get("location")

        if address == "" or working_time == "" or phone_numbers == "" or name == "" or deliverer == "0" or location == "" :

            return JsonResponse(
                {"type": "danger", "msg": "لطفا تمامی موارد را وارد نمایید"}
            )

        if manager == ["0"]:
            return JsonResponse(
                {"type": "danger", "msg": "لطفا مدیر شعبه را انتخاب نمایید"}
            )

        phone_list = phone_numbers.split(",")
        invalid_numbers = [
            number for number in phone_list if not re.fullmatch(r"09\d{9}", number)
        ]
        if invalid_numbers:
            return JsonResponse(
                {
                    "type": "danger",
                    "msg": 'شماره‌های وارد شده باید ۱۱ رقمی بوده و با "۰۹" شروع شوند.',
                }
            )

        try:
            city = Site_Cities_With_Represent.objects.get(pk=pk)
        except:
            return JsonResponse(
                {"type": "danger", "msg": "پردازش مورد نظر با مشکل مواجه شده است"}
            )

        if (
            Site_Branches_Each_Representative.objects.filter(
                city=city, address=address, working_time=working_time
            ).count()
            != 0
        ):
            return JsonResponse(
                {"type": "danger", "msg": "لطفا از آدرس تکراری استفاده نکنید"}
            )

        try:

            uploader = upload_file(request.FILES["logo"], "media", False)
            if uploader[0] != True:
                return JsonResponse({"type": "danger", "msg": uploader[1]})

        except:
            # return JsonResponse(
            #     {"type": "danger", "msg": "در آپلود فایل خطایی رخ داده"}
            # )
            pass
        branch = Site_Branches_Each_Representative(
            address=address,
            datetime=get_date_time()["datetime"],
            city=city,
            act=True,
            working_time=working_time,
            phone_numbers=phone_numbers,
            name=name,
            # picture=uploader[2],
            deliverer = Site_Branches_Deliverer.objects.get(pk=deliverer),
            location = location
            
        )
        branch.save()

        array = []
        for i in manager:
            if i != "0":
                mm = Master.objects.get(pk=i)
                branch.manager.add(mm)
                array.append(f"{mm.first_name} {mm.last_name}")

        manager = array

        add_static_report(request, "افزودن شعبه نمایندگی ")
        return JsonResponse(
            {
                "type": "success",
                "msg": " شعبه نمایندگی با موفقیت ثبت شد",
                "address": address,
                "pk": branch.pk,
                "name": name,
                "manager": manager,
            }
        )

    return JsonResponse(
        {"type": "danger", "msg": "پردازش مورد نظر با مشکل مواجه شده است"}
    )


def master_site_branches_each_representative_edit(request, pk):

    # master check start
    try:
        code = master_access_check(request)
        if code[0] != 100:
            return redirect(code[1])
    except:
        return redirect("master_login")
    # master check end

    branch = Site_Branches_Each_Representative.objects.get(pk=pk)
    branch_images = BranchImage.objects.filter(branch=branch).order_by("-pk")


    manager = Master.objects.filter(is_master=False).order_by("-pk")
    list_manager = []
    for i in manager:
        if next((j for j in branch.manager.all() if i == j), None) == None:
            list_manager.append(i)

    return render(
        request,
        get_master_theme() + "site_branches_each_representative_edit.html",
        {"branch": branch, "manager": list_manager,"deliverer":Site_Branches_Deliverer.objects.filter(act=True),'branch_images':branch_images},
    )


def master_site_branches_each_representative_edit_submit(request, pk):

    # master json check start
    try:
        code = master_access_check(request)
        if code[0] != 100:
            return JsonResponse({"type": "danger", "msg": code[2]})
    except:
        return JsonResponse(
            {"type": "danger", "msg": "ورود شما منقضی شده لطفا مجددا وارد شوید"}
        )
    # master json check end

    if request.method == "POST":

        address = request.POST.get("address")
        working_time = request.POST.get("working_time")
        phone_numbers = request.POST.get("phone_numbers")
        name = request.POST.get("name")
        manager = request.POST.getlist("category[]")
        deliverer = request.POST.get("deliverer")
        location = request.POST.get("location")

        if address == "" or working_time == "" or phone_numbers == "" or name == "" or deliverer == "0" or location == "" :
            return JsonResponse(
                {"type": "danger", "msg": "لطفا تمامی موارد را وارد نمایید"}
            )

        if manager == ["0"]:
            return JsonResponse({"type": "danger", "msg": "لطفا مدیر شعبه را انتخاب نمایید"})

        phone_list = phone_numbers.split(",")
        invalid_numbers = [number for number in phone_list if not re.fullmatch(r"09\d{9}", number)]
        if invalid_numbers:
            return JsonResponse({"type": "danger","msg": 'شماره‌های وارد شده باید ۱۱ رقمی بوده و با "۰۹" شروع شوند.'})

        try:
            branch = Site_Branches_Each_Representative.objects.get(pk=pk)
        except:
            return JsonResponse({"type": "danger", "msg": "پردازش مورد نظر با مشکل مواجه شده است"})

        if (Site_Branches_Each_Representative.objects.filter(city=branch.city, address=address).exclude(pk=pk).count()!= 0):
            return JsonResponse({"type": "danger", "msg": "لطفا از عنوان تکراری استفاده نکنید"})

        try:
            uploader = upload_file(request.FILES["logoo"], "media", False)
            if uploader[0] != True:
                return JsonResponse({"type": "danger", "msg": uploader[1]})

            fs = FileSystemStorage(location="media")
            fs.delete(branch.picture)
            branch.picture = uploader[2]

        except:
            pass

        branch.address = address
        branch.working_time = working_time
        branch.phone_numbers = phone_numbers
        branch.name = name
        branch.picture = branch.picture
        branch.deliverer = Site_Branches_Deliverer.objects.get(pk=deliverer)
        branch.location = location

        for j in branch.manager.all():
            branch.manager.remove(j)

        for i in manager:
            if i != "0":
                branch.manager.add(Master.objects.get(pk=i))

        branch.save()

        add_static_report(request, "ویرایش شعبه های نمایندگی ")
        return JsonResponse(
            {
                "type": "success",
                "msg": "شعبه نمایندگی موردنظر با موفقیت ویرایش شد",
                "id": branch.pk,
                "address": address,
                "working_time": working_time,
                "phone_numbers": phone_numbers,
                "name": name,
            }
        )

    return JsonResponse(
        {"type": "danger", "msg": "ویرایش شعبه نمایندگی با مشکل مواجه شده است"}
    )


def master_site_branches_each_representative_delete_submit(request, pk):

    # master json check start
    try:
        code = master_access_check(request)
        if code[0] != 100:
            return JsonResponse({"type": "danger", "msg": code[2]})
    except:
        return JsonResponse(
            {"type": "danger", "msg": "ورود شما منقضی شده لطفا مجددا وارد شوید"}
        )
    # master json check end

    if (
        Customer_Gold_Order.objects.filter(
            branch=Site_Branches_Each_Representative.objects.get(pk=pk)
        ).count()
        != 0
        or Site_Products.objects.filter(
            branch=Site_Branches_Each_Representative.objects.get(pk=pk)
        ).count()
        != 0
    ):
        return JsonResponse({"type": "danger", "msg": "حذف شعبه امکان پذیر نیست."})

    if Site_Branch_Working_Days.objects.filter(branch=pk).count() != 0:
        return JsonResponse({"type": "danger", "msg": "حذف شعبه امکان پذیر نیست."})

    try:
        branch = Site_Branches_Each_Representative.objects.get(pk=pk)
        fs = FileSystemStorage(location="media")
        fs.delete(branch.picture)
        branch.delete()

        add_static_report(request, "حذف شعبه های نمایندگی")
        return JsonResponse(
            {"type": "success", "msg": "شعبه نمایندگی با موفقیت حذف شد"}
        )

    except:
        return JsonResponse(
            {"type": "danger", "msg": "حذف شعبه نمایندگی با مشکل مواجه شده است"}
        )


def master_site_branches_each_representative_status_change(request, pk):

    # master json check start
    try:
        code = master_access_check(request)
        if code[0] != 100:
            return JsonResponse({"type": "danger", "msg": code[2]})
    except:
        return JsonResponse(
            {"type": "danger", "msg": "ورود شما منقضی شده لطفا مجددا وارد شوید"}
        )
    # master json check end

    branch = Site_Branches_Each_Representative.objects.get(pk=pk)

    if branch.act == False:

        branch.act = True
        branch.save()

        add_static_report(request, "فعال سازی شعبه های نمایندگی")

        return JsonResponse(
            {
                "type": "success",
                "msg": "شعبه نمایندگی مورد نظر با موفقیت فعال شد",
                "status": branch.act,
            }
        )

    elif branch.act == True:

        branch.act = False
        branch.save()

        products_with_positive_inventory = Site_Products.objects.filter(branch=branch, act=True)
        products_with_positive_inventory.update(act=False)

        add_static_report(request, "غیرفعال سازی شعبه های نمایندگی")

        return JsonResponse(
            {
                "type": "success",
                "msg": "شعبه نمایندگی مورد نظر با موفقیت غیرفعال شد",
                "status": branch.act,
            }
        )

    return JsonResponse(
        {"type": "danger", "msg": "تغییر وضعیت مورد نظر با مشکل مواجه شده است"}
    )


def master_site_branch_working_days(request, pk):

    # master check start
    try:
        code = master_access_check(request)
        if code[0] != 100:
            return redirect(code[1])
    except:
        return redirect("master_login")
    # master check end

    paginator = Paginator(
        Site_Branch_Working_Days.objects.filter(
            branch=Site_Branches_Each_Representative.objects.get(pk=pk)
        ).order_by("-working_date"),
        10,
    )
    page = request.GET.get("page")

    try:
        querySet = paginator.page(page)
    except PageNotAnInteger:
        querySet = paginator.page(1)
    except EmptyPage:
        querySet = paginator.page(1)

    return render(
        request,
        get_master_theme() + "site_branch_working_days.html",
        {"querySet": querySet, "branch_id": pk},
    )


def master_site_branch_working_days_submit(request, pk):

    # master json check start
    try:
        code = master_access_check(request)
        if code[0] != 100:
            return JsonResponse({"type": "danger", "msg": code[2]})
    except:
        return JsonResponse(
            {"type": "danger", "msg": "ورود شما منقضی شده لطفا مجددا وارد شوید"}
        )
    # master json check end

    if request.method == "POST":

        capacity = request.POST.get("capacity")
        dates_str = request.POST.get("dates", "")

        if capacity == "":
            return JsonResponse({"type": "danger", "msg": "لطفا ظرفیت را وارد نمایید"})

        try:
            capacity = int(capacity)
        except:
            return JsonResponse(
                {"type": "danger", "msg": "لطفا ظرفیت را به صورت عددی وارد نمایید"}
            )

        if capacity < 0:
            return JsonResponse(
                {"type": "danger", "msg": "لطفا ظرفیت را به صورت صحیح وارد نمایید"}
            )

        if dates_str == "":
            return JsonResponse({"type": "danger", "msg": "لطفا تاریخ را وارد نمایید"})

        try:
            branch = Site_Branches_Each_Representative.objects.get(pk=pk)
        except:
            return JsonResponse(
                {"type": "danger", "msg": "پردازش مورد نظر با مشکل مواجه شده است"}
            )

        today = khayyam.JalaliDate.today().todate()
        today_timestamp = int(
            datetime.strptime(str(today) + " 00:00:00", "%Y-%m-%d %H:%M:%S").timestamp()
        )

        date_list = [date.strip() for date in dates_str.split(",")]
        for date_str in date_list:
            sdata = date_str.split("/")
            newdata = khayyam.JalaliDate(sdata[0], sdata[1], sdata[2]).todate()
            earlier = str(newdata) + " 00:00:00"

            date_timestamp = int(
                datetime.strptime(earlier, "%Y-%m-%d %H:%M:%S").timestamp()
            )

            date_time = datetime.fromtimestamp(date_timestamp)
            jalali_date = jdatetime.datetime.fromgregorian(datetime=date_time).strftime('%Y/%m/%d') 
            weekday = jdatetime.datetime.fromgregorian(datetime=date_time).strftime('%A') 


            if date_timestamp < today_timestamp:
                return JsonResponse(
                    {
                        "type": "danger",
                        "msg": "لطفا تاریخ را به صورت صحیح انتخاب نمایید",
                    }
                )
            else:
                if (
                    Site_Branch_Working_Days.objects.filter(
                        branch=branch, working_date=date_timestamp
                    ).count()
                    == 0
                ):
                    Site_Branch_Working_Days(
                        working_date=date_timestamp, capacity=capacity, branch=branch,jalali_date=jalali_date, weekday=weekday
                    ).save()

            add_static_report(request, "افزودن روزهای کاری شعبه")
        return JsonResponse(
            {"type": "success", "msg": " روزهای کاری جدید با موفقیت ثبت شد"}
        )

    return JsonResponse(
        {"type": "danger", "msg": "پردازش مورد نظر با مشکل مواجه شده است"}
    )


def master_site_branch_working_days_edit_submit(request, pk):

    # master json check start
    try:
        code = master_access_check(request)
        if code[0] != 100:
            return JsonResponse({"type": "danger", "msg": code[2]})
    except:
        return JsonResponse(
            {"type": "danger", "msg": "ورود شما منقضی شده لطفا مجددا وارد شوید"}
        )
    # master json check end

    if request.method == "POST":

        capacity = request.POST.get("capacity_modal")

        if capacity == "":
            return JsonResponse({"type": "danger", "msg": "لطفا ظرفیت را وارد نمایید"})

        if int(capacity) < 0:
            return JsonResponse(
                {"type": "danger", "msg": "لطفا ظرفیت را به صورت صحیح وارد نمایید"}
            )

        try:
            capacity = int(capacity)
        except:
            return JsonResponse(
                {"type": "danger", "msg": "لطفا ظرفیت را به صورت عددی وارد نمایید"}
            )

        try:
            working_day = Site_Branch_Working_Days.objects.get(pk=pk)
        except:
            return JsonResponse(
                {"type": "danger", "msg": "پردازش مورد نظر با مشکل مواجه شده است"}
            )

        working_day.capacity = capacity
        working_day.save()

        add_static_report(request, "ویرایش ظرفیت روزهای کاری شعبه ")
        return JsonResponse(
            {
                "type": "success",
                "msg": "ظرفیت موردنظر با موفقیت ویرایش شد",
                "id": working_day.pk,
                "capacity": capacity,
            }
        )

    return JsonResponse(
        {"type": "danger", "msg": "ویرایش ظرفیت تاریخ موردنظر با مشکل مواجه شده است"}
    )


def master_site_branch_working_days_delete_submit(request, pk):

    # master json check start
    try:
        code = master_access_check(request)
        if code[0] != 100:
            return JsonResponse({"type": "danger", "msg": code[2]})
    except:
        return JsonResponse(
            {"type": "danger", "msg": "ورود شما منقضی شده لطفا مجددا وارد شوید"}
        )
    # master json check end

    if (
        Customer_Gold_Order.objects.filter(
            delivery_date=Site_Branch_Working_Days.objects.get(pk=pk)
        ).count()
        != 0
    ):
        return JsonResponse({"type": "danger", "msg": "حذف روز کاری امکان پذیر نیست."})

    try:
        working_days = Site_Branch_Working_Days.objects.get(pk=pk)
        working_days.delete()

        add_static_report(request, "حذف روزهای کاری شعبه")
        return JsonResponse(
            {"type": "success", "msg": "روز کاری موردنظر با موفقیت حذف شد"}
        )

    except:
        return JsonResponse(
            {"type": "danger", "msg": "حذف روز کاری با مشکل مواجه شده است"}
        )


def master_site_branch_working_days_status_change(request, pk):

    # master json check start
    try:
        code = master_access_check(request)
        if code[0] != 100:
            return JsonResponse({"type": "danger", "msg": code[2]})
    except:
        return JsonResponse(
            {"type": "danger", "msg": "ورود شما منقضی شده لطفا مجددا وارد شوید"}
        )
    # master json check end

    working_days = Site_Branch_Working_Days.objects.get(pk=pk)

    if working_days.act == False:

        working_days.act = True
        working_days.save()
        add_static_report(request, "فعال سازی روز کاری شعبه")

        return JsonResponse(
            {
                "type": "success",
                "msg": "روز کاری مورد نظر با موفقیت فعال شد",
                "status": working_days.act,
            }
        )

    elif working_days.act == True:

        working_days.act = False
        working_days.save()
        add_static_report(request, "غیرفعال سازی روز کاری شعبه")

        return JsonResponse(
            {
                "type": "success",
                "msg": "روز کاری مورد نظر با موفقیت غیرفعال شد",
                "status": working_days.act,
            }
        )

    return JsonResponse(
        {"type": "danger", "msg": "تغییر وضعیت مورد نظر با مشکل مواجه شده است"}
    )


def master_site_product_list(request):

    # master check start
    try:
        code = master_access_check(request)
        if code[0] != 100:
            return redirect(code[1])
    except:
        return redirect("master_login")
    # master check end

    molten_gold = Site_Products.objects.filter(type_gold="gold1").order_by("-pk")
    bullion_coin = Site_Products.objects.filter(
        type_gold__in=["gold2", "gold3"]
    ).order_by("-pk")

    paginator = Paginator(molten_gold, 10)
    page = request.GET.get("page")
    try:
        molten_gold = paginator.page(page)
    except PageNotAnInteger:
        molten_gold = paginator.page(1)
    except EmptyPage:
        molten_gold = paginator.page(1)

    paginator = Paginator(bullion_coin, 10)
    page = request.GET.get("page")
    try:
        bullion_coin = paginator.page(page)
    except PageNotAnInteger:
        bullion_coin = paginator.page(1)
    except EmptyPage:
        bullion_coin = paginator.page(1)

    categories = []
    for i in GOLDS:
        categories.append(i)
    return render(
        request,
        get_master_theme() + "site_products.html",
        {
            "molten_gold": molten_gold,
            "bullion_coin": bullion_coin,
            "categories": categories,
            "cities": Site_Cities_With_Represent.objects.filter(act=True).order_by("sort"),
            "last_gold_price": Currency_List.objects.get(symbol="XAU18").BuySellPrice[
                "buy"
            ],
            "branches": Site_Branches_Each_Representative.objects.filter(act=True).order_by("-pk"),
        },
    )


def master_site_product_add_submit(request):

    # master json check start
    try:
        code = master_access_check(request)
        if code[0] != 100:
            return JsonResponse({"type": "danger", "msg": code[2]})
    except:
        return JsonResponse(
            {"type": "danger", "msg": "ورود شما منقضی شده لطفا مجددا وارد شوید"}
        )
    # master json check end

    if request.method == "POST":

        title = request.POST.get("title")
        cutie = request.POST.get("cutie")
        grams = request.POST.get("grams")
        category = request.POST.get("category")
        fee = request.POST.get("fee")
        city = request.POST.get("city")
        branch = request.POST.get("branch")

        wages = request.POST.get("wages") or None
        tracking_code = request.POST.get("tracking_code") or None
        desc = request.POST.get("desc") or None
        lab_name = request.POST.get("lab_name")

        try : city = Site_Cities_With_Represent.objects.get(pk=city)
        except : return JsonResponse({"type": "danger", "msg": "پردازش مورد نظر با مشکل مواجه شده است"})

        try:
            branch = Site_Branches_Each_Representative.objects.get(pk=branch)
            if not (branch.manager.filter(id=Master.objects.get(req_user=request.user).pk).exists()):
                return JsonResponse({"type": "danger", "msg": "شما به این قسمت دسترسی ندارید"})
            
        except: return JsonResponse({"type": "danger", "msg": "شعبه مورد نظر یافت نشد"})


        if branch.city != city:
            return JsonResponse({"type": "danger", "msg": "شعبه انتخاب شده متعلق به این شهر نیست."})
        

        if (title == "" or cutie == "" or grams == "" or fee == "" or city in [0, "0"] or branch in [0, "0"] ):
            return JsonResponse({"type": "danger", "msg": "لطفا تمامی موارد خواسته شده را وارد نمایید"})

        try:
            float(grams)
        except:
            return JsonResponse(
                {
                    "type": "danger",
                    "msg": "میزان گرمی محصول موردنظر را به صورت صحیح وارد نمایید",
                }
            )

        try:
            float(fee)
        except:
            return JsonResponse(
                {
                    "type": "danger",
                    "msg": "میزان کارمزد محصول موردنظر را به صورت صحیح وارد نمایید",
                }
            )

        try:
            int(cutie)
        except:
            return JsonResponse(
                {
                    "type": "danger",
                    "msg": " عیار محصول موردنظر را به صورت صحیح وارد نمایید",
                }
            )

        if wages is not None:
            try:
                wages = float(wages)
            except:
                return JsonResponse(
                    {
                        "type": "danger",
                        "msg": " اجرت محصول موردنظر را به صورت صحیح وارد نمایید",
                    }
                )


        if category == "gold1":
            if tracking_code == None or desc == None or lab_name == "":
                return JsonResponse(
                    {
                        "type": "danger",
                        "msg": "لطفا تمامی موارد خواسته شده را وارد نمایید",
                    }
                )

        if category != "gold1":
            if wages == None:
                return JsonResponse(
                    {
                        "type": "danger",
                        "msg": "لطفا تمامی موارد خواسته شده را وارد نمایید",
                    }
                )



        if len(title) > 300:
            return JsonResponse(
                {"type": "danger", "msg": "حداکثر کاراکتر عنوان 300 کاراکتر است"}
            )

        try:

            uploader = upload_file(request.FILES["logo"], "media", False)
            if uploader[0] != True:
                return JsonResponse({"type": "danger", "msg": uploader[1]})

        except:
            return JsonResponse({"type": "danger", "msg": "لطفا تصویر را وارد نمایید"})
    

        aa = Site_Products(
            title=title,
            cutie=cutie,
            grams = (round(float(grams) * float(cutie) / 750, 4)) if category == "gold1"  else float(grams) ,
            fee=fee,
            logo_name=uploader[2],
            type_gold=category,
            wages=wages,
            desc=desc,
            pure_grams=grams,
            tracking_code=tracking_code,
            lab=lab_name,
            city=city,
            branch=branch,
        )
        aa.save()
        add_static_report(request, "افزودن محصولات سایت")

        return JsonResponse({"type": "success", "msg": "محصول با موفقیت ثبت شد"})

    return JsonResponse(
        {"type": "danger", "msg": "پردازش مورد نظر با مشکل مواجه شده است"}
    )


def master_site_product_status_change(request, pk):

    # master json check start
    try:
        code = master_access_check(request)
        if code[0] != 100:
            return JsonResponse({"type": "danger", "msg": code[2]})
    except:
        return JsonResponse({"type": "danger", "msg": "ورود شما منقضی شده لطفا مجددا وارد شوید"})
    # master json check end

    try:
        product = Site_Products.objects.get(pk=pk)
    except:
        return JsonResponse({"type": "danger", "msg": "تغییر وضعیت محصول با مشکل مواجه شده است"})


    if product.act == False:

        if (Permission.objects.filter(user=request.user,codename="master_site_physical_delivery_products").count()== 0):
            return JsonResponse({"type": "danger","msg": "شما دسترسی لازم برای تغییر وضعیت محصول را ندارید."})

        product.act = True
        product.save()

        add_static_report(request, "فعال سازی محصول")

        return JsonResponse({"type": "success","msg": "محصول مورد نظر با موفقیت فعال شد","status": product.act,})

    elif product.act == True:

        if not product.branch.manager.filter(id=Master.objects.get(req_user=request.user).pk).exists():
            return JsonResponse({"type": "danger", "msg": "شما به این قسمت دسترسی ندارید"})

        product.act = False
        product.save()

        add_static_report(request, "غیرفعال سازی محصول")

        return JsonResponse({"type": "success","msg": "محصول مورد نظر با موفقیت غیرفعال شد","status": product.act})

    return JsonResponse({"type": "danger", "msg": "تغییر وضعیت مورد نظر با مشکل مواجه شده است"})


def master_site_product_edit_submit(request, pk):

    # master json check start
    try:
        code = master_access_check(request)
        if code[0] != 100:
            return JsonResponse({"type": "danger", "msg": code[2]})
    except:
        return JsonResponse(
            {"type": "danger", "msg": "ورود شما منقضی شده لطفا مجددا وارد شوید"}
        )
    # master json check end

    try:
        product = Site_Products.objects.get(pk=pk)
        if not (
            product.branch.manager.filter(
                pk=Master.objects.get(req_user=request.user).pk
            ).exists()
        ):
            return JsonResponse(
                {"type": "danger", "msg": "شما به این قسمت دسترسی ندارید"}
            )
    except:
        return JsonResponse(
            {"type": "danger", "msg": "ویرایش محصول با مشکل موجه شده است"}
        )

    if request.method == "POST":

        title = request.POST.get("title_modal")
        cutie = request.POST.get("cutie_modal")
        grams = request.POST.get("grams_modal")
        fee = request.POST.get("fee_modal")
        city = request.POST.get("city")
        branch = request.POST.get("branch")
        lab_name = request.POST.get('lab_name_modal')
        
        wages = request.POST.get("wages_modal") or None
        desc = request.POST.get("desc_modal") or None
        tracking_code = request.POST.get("tracking_code_modal") or None

        

        if (title == "" or grams == "" or cutie == "" or fee == "" or city in [0, "0"] or branch in [0, "0"]):
            return JsonResponse({"type": "danger", "msg": "لطفا تمامی موارد خواسته شده را وارد نمایید"})
        branch = Site_Branches_Each_Representative.objects.get(pk=branch)
        if not branch.manager.filter(id=Master.objects.get(req_user=request.user).pk).exists():
            return JsonResponse(
                {
                    "type": "danger",
                    "msg": "شما مدیر این شعبه نیستید و اجازه ویرایش را ندارید",
                }
            )

        try: city = Site_Cities_With_Represent.objects.get(pk=city)
        except: return JsonResponse({"type": "danger", "msg": "پردازش مورد نظر با مشکل مواجه شده است"})

        if branch.city != city :
            return JsonResponse({"type": "danger", "msg": "شعبه انتخاب شده متعلق به این شهر نیست."})
        

        if len(title) > 300:
            return JsonResponse(
                {"type": "danger", "msg": "حداکثر کاراکتر عنوان 300 کاراکتر است"}
            )

        if product.type_gold == "gold1":
            if tracking_code == None or desc == None or lab_name == "":
                return JsonResponse(
                    {
                        "type": "danger",
                        "msg": "لطفا تمامی موارد خواسته شده را وارد نمایید",
                    }
                )
        
        if product.type_gold == "gold2" or product.type_gold == "gold3":
            if wages == None:
                return JsonResponse(
                    {
                        "type": "danger",
                        "msg": "لطفا تمامی موارد خواسته شده را وارد نمایید",
                    }
                )
        try:
            uploader = upload_file(request.FILES["logoo"], "media", False)
            if uploader[0] != True:
                return JsonResponse({"type": "danger", "msg": uploader[1]})

            fs = FileSystemStorage(location="media")
            fs.delete(product.logo_name)
            product.logo_name = uploader[2]

        except:
            pass

        product.title = title
        product.cutie = cutie
        product.grams = (round(float(grams) * float(cutie) / 750, 4)) if product.type_gold == "gold1"  else float(grams)
        product.pure_grams = grams
        product.fee = fee
        product.city = city
        product.wages = wages
        product.desc = desc
        product.tracking_code = tracking_code
        product.logo_name = product.logo_name
        product.branch = branch
        product.lab = lab_name
        product.save()

        add_static_report(request, "ویرایش محصول")

        return JsonResponse(
            {
                "type": "success",
                "msg": "محصول با موفقیت ویرایش شد",
                "id": product.pk,
                "title": title,
                "wages": wages,
                "cutie": cutie,
                "logo": product.logo_name,
                "fee": fee,
            }
        )

    return JsonResponse({"type": "danger", "msg": "ویرایش محصول با مشکل مواجه شده است"})


def master_site_product_delete_submit(request, pk):

    # master json check start
    try:
        code = master_access_check(request)
        if code[0] != 100:
            return JsonResponse({"type": "danger", "msg": code[2]})
    except:
        return JsonResponse(
            {"type": "danger", "msg": "ورود شما منقضی شده لطفا مجددا وارد شوید"}
        )
    # master json check end

    try:
        product = Site_Products.objects.get(pk=pk)
        if not (
            product.branch.manager.filter(
                id=Master.objects.get(req_user=request.user).pk
            ).exists()
        ):
            return JsonResponse(
                {"type": "danger", "msg": "شما به این قسمت دسترسی ندارید"}
            )
    except:
        return JsonResponse(
            {"type": "danger", "msg": "حذف محصول با مشکل مواجه شده است"}
        )

    if Customer_Cart_Products.objects.filter(product=product).count() != 0:
        return JsonResponse({"type": "danger", "msg": "حذف محصول امکان پذیر نیست."})

    try:
        Site_Product_Inventory.objects.filter(product=product).delete()
    except:
        return JsonResponse(
            {"type": "danger", "msg": "حذف محصول با مشکل مواجه شده است"}
        )

    product.delete()

    add_static_report(request, "حذف محصول")
    return JsonResponse({"type": "success", "msg": "محصول با موفقیت حذف شد"})


def master_site_product_melted_search(request):

    # master check start
    try:
        code = master_access_check(request)
        if code[0] != 100:
            return redirect(code[1])
    except:
        return redirect("master_login")
    # master check end

    city = Site_Cities_With_Represent.objects.filter(act=True).order_by("sort")
    branch = Site_Branches_Each_Representative.objects.filter(act=True).order_by("-pk")
    molten_gold = Site_Products.objects.filter(type_gold="gold1").order_by("-pk")
    bullion_coin = Site_Products.objects.filter(type_gold__in=["gold2", "gold3"]).order_by("-pk")

    categories = []
    for i in GOLDS:
        categories.append(i)


    if request.method == "POST":

        txt = request.POST.get("txt")
        request.session["txt"] = txt

    else:
        txt = request.session.get("txt", "")

    if txt != "":
        molten_gold = molten_gold.filter(
            Q(pk__contains=txt)
            | Q(title__contains=txt)
            | Q(city__name__contains=txt)
            | Q(cutie__contains=txt)
            | Q(grams__contains=txt)
            | Q(branch__name__contains=txt)
            | Q(lab__contains=txt)
          
        )

    paginator = Paginator(molten_gold.order_by("-pk"), 10)
    page = request.GET.get("page")

    try:
        molten_gold = paginator.page(page)
    except PageNotAnInteger:
        molten_gold = paginator.page(1)
    except EmptyPage:
        molten_gold = paginator.page(1)

    paginator = Paginator(bullion_coin, 10)
    page = request.GET.get("page")
    try:
        bullion_coin = paginator.page(page)
    except PageNotAnInteger:
        bullion_coin = paginator.page(1)
    except EmptyPage:
        bullion_coin = paginator.page(1)

    return render(
        request,
        get_master_theme() + "site_products.html",
        {"molten_gold": molten_gold, "cities": city, "branches":branch, "bullion_coin":bullion_coin, "categories": categories,},
    )


def master_site_product_bullion_coin_search(request):

    # master check start
    try:
        code = master_access_check(request)
        if code[0] != 100:
            return redirect(code[1])
    except:
        return redirect("master_login")
    # master check end

    city = Site_Cities_With_Represent.objects.filter(act=True).order_by("sort")
    branch = Site_Branches_Each_Representative.objects.filter(act=True).order_by("-pk")
    bullion_coin = Site_Products.objects.filter(type_gold__in=["gold2", "gold3"]).order_by("-pk")
    molten_gold = Site_Products.objects.filter(type_gold="gold1").order_by("-pk")

    categories = []
    for i in GOLDS:
        categories.append(i)
        
    

    if request.method == "POST":

        txt = request.POST.get("txt")
        request.session["txt"] = txt

    else:
        txt = request.session.get("txt", "")

    if txt != "":
        bullion_coin = bullion_coin.filter(
            Q(pk__contains=txt)
            | Q(title__contains=txt)
            | Q(city__name__contains=txt)
            | Q(cutie__contains=txt)
            | Q(grams__contains=txt)
            | Q(branch__name__contains=txt)
            | Q(lab__contains=txt)
          
        )

    paginator = Paginator(bullion_coin.order_by("-pk"), 10)
    page = request.GET.get("page")

    try:
        bullion_coin = paginator.page(page)
    except PageNotAnInteger:
        bullion_coin = paginator.page(1)
    except EmptyPage:
        bullion_coin = paginator.page(1)

    paginator = Paginator(molten_gold.order_by("-pk"), 10)
    page = request.GET.get("page")

    try:
        molten_gold = paginator.page(page)
    except PageNotAnInteger:
        molten_gold = paginator.page(1)
    except EmptyPage:
        molten_gold = paginator.page(1)

    return render(
        request,
        get_master_theme() + "site_products.html",{"molten_gold": molten_gold, "cities": city, "branches":branch, "bullion_coin":bullion_coin, "categories": categories,}, )
        
   


def master_site_product_inventory(request, pk):

    # master check start
    try:
        code = master_access_check(request)
        if code[0] != 100:
            return redirect(code[1])
    except:
        return redirect("master_login")
    # master check end

    try:
        product = Site_Products.objects.get(pk=pk)
    except:
        return JsonResponse(
            {"type": "danger", "msg": "پردازش مورد نظر با مشکل مواجه شده است"}
        )

    paginator = Paginator(
        Site_Product_Inventory.objects.filter(product=product).order_by("-pk"), 10
    )
    page = request.GET.get("page")

    try:
        querySet = paginator.page(page)
    except PageNotAnInteger:
        querySet = paginator.page(1)
    except EmptyPage:
        querySet = paginator.page(1)

    return render(
        request,
        get_master_theme() + "site_product_inventory.html",
        {"querySet": querySet, "product": product},
    )


def master_site_product_inventory_submit(request, pk):

    # master json check start
    try:
        code = master_access_check(request)
        if code[0] != 100:
            return JsonResponse({"type": "danger", "msg": code[2]})
    except:
        return JsonResponse(
            {"type": "danger", "msg": "ورود شما منقضی شده لطفا مجددا وارد شوید"}
        )
    # master json check end



    try:
        product = Site_Products.objects.get(pk=pk)
        if not (product.branch.manager.filter(id=Master.objects.get(req_user=request.user).pk).exists()):
            return JsonResponse({"type": "danger", "msg": "شما به این قسمت دسترسی ندارید"})
    except:
        return JsonResponse({"type": "danger", "msg": "پردازش مورد نظر با مشکل مواجه شده است"})


    if request.method == "POST":

        quantity = request.POST.get("quantity")

        if quantity == "":
            return JsonResponse({"type": "danger", "msg": "لطفا موجودی را وارد نمایید"})

        try:
            int(quantity)
        except:
            return JsonResponse(
                {
                    "type": "danger",
                    "msg": "موجودی محصول را یه صورت عدد صحیح وارد نمایید",
                }
            )


        if (calculate_product_inventory(pk)["product_inventory"] + int(quantity)) < 0:
            return JsonResponse(
                {
                    "type": "danger",
                    "msg": "تعداد موجودی محصولات نمی تواند کمتر از صفر باشد",
                }
            )

        inventory = Site_Product_Inventory(
            product=product, quantity=quantity, datetime=get_date_time()["timestamp"]
        )
        inventory.save()

        add_static_report(request, "ثبت موجودی محصول")

        return JsonResponse({"type": "success", "msg": "موجودی محصول با موفقیت ثبت شد"})

    return JsonResponse(
        {"type": "danger", "msg": "ثبت موجودی محصول با مشکل مواجه شده است"}
    )


def master_site_information_product_submit(request):

    # master check start
    try:
        code = master_access_check(request)
        if code[0] != 100:
            return redirect(code[1])
    except:
        return redirect("master_login")
    # master check end

    if request.method == "POST":

        title_product = request.POST.get("title_product")
        desc_product = request.POST.get("desc_product")

        if title_product == "" or desc_product == "":
            return JsonResponse(
                {"type": "danger", "msg": "لطفا موارد خواسته شده را وارد نمایید"}
            )

        if len(title_product) > 300:
            return JsonResponse(
                {"type": "danger", "msg": "حداکثر کاراکتر عنوان , 300 کاراکتر میباشد"}
            )

        setting = Site_Settings.objects.get(code=1001)
        setting.title_product = title_product
        setting.desc_product = desc_product
        setting.save()

        return JsonResponse({"type": "success", "msg": "ویرایش با موفقیت انجام شد"})

    return JsonResponse(
        {"type": "danger", "msg": "پردازش مورد نظر با مشکل مواجه شده است"}
    )


def master_rules_physical_delivery(request):

    # master check start
    try:
        code = master_access_check(request)
        if code[0] != 100:
            return redirect(code[1])
    except:
        return redirect("master_login")
    # master check end

    site_settings = Site_Settings.objects.get(code=1001)

    return render(
        request,
        get_master_theme() + "rules_physical_delivery.html",
        {"site_settings": site_settings},
    )


def master_rules_physical_delivery_submit(request):

    # master json check start
    try:
        code = master_access_check(request)
        if code[0] != 100:
            return JsonResponse({"type": "danger", "msg": code[2]})
    except:
        return JsonResponse(
            {"type": "danger", "msg": "ورود شما منقضی شده لطفا مجددا وارد شوید"}
        )
    # master json check end

    if request.method == "POST":

        rules_physical_delivery = request.POST.get("rules_physical_delivery")
        title_rules_physical_delivery = request.POST.get(
            "title_rules_physical_delivery"
        )

        if rules_physical_delivery == "" or title_rules_physical_delivery == "":
            return JsonResponse(
                {"type": "danger", "msg": "لطفا تمامی موارد را وارد نمایید"}
            )

        rules = Site_Settings.objects.get(code=1001)
        rules.rules_physical_delivery = rules_physical_delivery
        rules.title_rules_physical_delivery = title_rules_physical_delivery
        rules.save()

        add_static_report(request, "ویرایش قوانین تحویل فیزیکی طلا")
        return JsonResponse({"type": "success", "msg": "تغییرات با موفقیت ذخیره شد"})

    return JsonResponse(
        {"type": "danger", "msg": "پردازش مورد نظر با مشکل مواجه شده است"}
    )


def master_site_physical_delivery_information(request):

    # master check start
    try:
        code = master_access_check(request)
        if code[0] != 100:
            return redirect(code[1])
    except:
        return redirect("master_login")
    # master check end

    info = Site_Settings.objects.get(code=1001)

    return render(
        request, get_master_theme() + "site_physical_delivery.html", {"info": info}
    )


def master_site_physical_delivery_information_submit(request):

    # master json check start
    try:
        code = master_access_check(request)
        if code[0] != 100:
            return JsonResponse({"type": "danger", "msg": code[2]})
    except:
        return JsonResponse(
            {"type": "danger", "msg": "ورود شما منقضی شده لطفا مجددا وارد شوید"}
        )
    # master json check end

    if request.method == "POST":

        physical_delivery_title = request.POST.get("physical_delivery_title")
        physical_delivery_desc = request.POST.get("physical_delivery_desc")
        physical_delivery_text = request.POST.get("physical_delivery_text")
        # physical_delivery_title_btn = request.POST.get('physical_delivery_title_btn')
        # physical_delivery_link_btn = request.POST.get('physical_delivery_link_btn')

        if (
            physical_delivery_title == ""
            or physical_delivery_desc == ""
            or physical_delivery_text == ""
        ):
            return JsonResponse(
                {"type": "danger", "msg": "لطفا تمامی موارد را وارد نمایید"}
            )

        info = Site_Settings.objects.get(code=1001)

        try:
            uploader = upload_file(request.FILES["picture1"], "media", False)
            if uploader[0] != True:
                return JsonResponse({"type": "danger", "msg": uploader[1]})

            fs = FileSystemStorage(location="media")
            fs.delete(info.physical_delivery_pic1)
            info.physical_delivery_pic1 = uploader[2]
        except:
            pass

        info.physical_delivery_title = physical_delivery_title
        info.physical_delivery_desc = physical_delivery_desc
        info.physical_delivery_text = physical_delivery_text
        # info.physical_delivery_title_btn = physical_delivery_title_btn
        # info.physical_delivery_link_btn = physical_delivery_link_btn
        info.physical_delivery_pic1 = info.physical_delivery_pic1
        info.save()

        add_static_report(request, "ویرایش اطلاعات صفحه انتخاب شهر ")

        return JsonResponse(
            {
                "type": "success",
                "msg": "اطلاعات با موفقیت ثبت شد",
                "picture1": info.physical_delivery_pic1,
            }
        )

    return JsonResponse(
        {"type": "danger", "msg": "پردازش مورد نظر با مشکل مواجه شده است"}
    )


def master_site_product_list_information_submit(request):

    # master json check start
    try:
        code = master_access_check(request)
        if code[0] != 100:
            return JsonResponse({"type": "danger", "msg": code[2]})
    except:
        return JsonResponse(
            {"type": "danger", "msg": "ورود شما منقضی شده لطفا مجددا وارد شوید"}
        )
    # master json check end

    if request.method == "POST":

        product_desc = request.POST.get("product_desc")

        if product_desc == "":
            return JsonResponse(
                {"type": "danger", "msg": "لطفا توضیحات را وارد نمایید"}
            )

        info = Site_Settings.objects.get(code=1001)

        try:

            uploader = upload_file(request.FILES["picture"], "media", False)
            if uploader[0] != True:
                return JsonResponse({"type": "danger", "msg": uploader[1]})

            fs = FileSystemStorage(location="media")
            fs.delete(info.delivery_basket_icon)
            info.delivery_basket_icon = uploader[2]

        except:
            pass
        info.product_desc = product_desc
        info.delivery_basket_icon = info.delivery_basket_icon
        info.save()

        add_static_report(request, "ویرایش اطلاعات صفحه لیست محصولات ")

        return JsonResponse(
            {
                "type": "success",
                "msg": "اطلاعات با موفقیت ثبت شد",
                "picture": info.product_desc,
            }
        )

    return JsonResponse(
        {"type": "danger", "msg": "پردازش مورد نظر با مشکل مواجه شده است"}
    )


def master_site_physical_gold_invoice_information_submit(request):

    # master json check start
    try:
        code = master_access_check(request)
        if code[0] != 100:
            return JsonResponse({"type": "danger", "msg": code[2]})
    except:
        return JsonResponse(
            {"type": "danger", "msg": "ورود شما منقضی شده لطفا مجددا وارد شوید"}
        )
    # master json check end

    if request.method == "POST":

        title_delivery_basket_box = request.POST.get("title_delivery_basket_box")
        title_delivery_basket_invoice = request.POST.get(
            "title_delivery_basket_invoice"
        )
        delivery_cart_payment_description = request.POST.get(
            "delivery_cart_payment_description"
        )

        if (
            title_delivery_basket_box == ""
            or title_delivery_basket_invoice == ""
            or delivery_cart_payment_description == ""
        ):
            return JsonResponse(
                {"type": "danger", "msg": "لطفا تمامی موارد را وارد نمایید"}
            )

        info = Site_Settings.objects.get(code=1001)
        info.title_delivery_basket_box = title_delivery_basket_box
        info.title_delivery_basket_invoice = title_delivery_basket_invoice
        info.delivery_cart_payment_description = delivery_cart_payment_description
        info.save()

        add_static_report(request, "ویرایش اطلاعات صفحه سبد فاکتور تحویل فیزیکی")

        return JsonResponse({"type": "success", "msg": "اطلاعات با موفقیت ثبت شد"})

    return JsonResponse(
        {"type": "danger", "msg": "پردازش مورد نظر با مشکل مواجه شده است"}
    )


def master_site_edit_invoice_statuses_submit(request):

    # master json check start
    try:
        code = master_access_check(request)
        if code[0] != 100:
            return JsonResponse({"type": "danger", "msg": code[2]})
    except:
        return JsonResponse(
            {"type": "danger", "msg": "ورود شما منقضی شده لطفا مجددا وارد شوید"}
        )
    # master json check end

    if request.method == "POST":

        text_rejected = request.POST.get("text_rejected")
        text_not_received = request.POST.get("text_not_received")
        text_canceled = request.POST.get("text_canceled")
        text_pending_delivery = request.POST.get("text_pending_delivery")
        text_received = request.POST.get("text_received")
        delivery_conditions = request.POST.get("delivery_conditions")
        delivery_documents = request.POST.get("delivery_documents")
        desc_received = request.POST.get("desc_received")

        if (
            text_rejected == ""
            or text_not_received == ""
            or text_canceled == ""
            or text_pending_delivery == ""
            or text_received == ""
            or delivery_conditions == ""
            or delivery_documents == ""
            or desc_received == ""
        ):
            return JsonResponse(
                {"type": "danger", "msg": "لطفا تمامی موارد را وارد نمایید"}
            )

        info = Site_Settings.objects.get(code=1001)

        try:
            uploader = upload_file(request.FILES["picture1"], "media", False)
            if uploader[0] != True:
                return JsonResponse({"type": "danger", "msg": uploader[1]})

            fs = FileSystemStorage(location="media")
            fs.delete(info.picture_rejected)
            info.picture_rejected = uploader[2]
        except:
            pass

        try:
            uploader = upload_file(request.FILES["picture2"], "media", False)
            if uploader[0] != True:
                return JsonResponse({"type": "danger", "msg": uploader[1]})

            fs = FileSystemStorage(location="media")
            fs.delete(info.picture_not_received)
            info.picture_not_received = uploader[2]
        except:
            pass

        try:
            uploader = upload_file(request.FILES["picture3"], "media", False)
            if uploader[0] != True:
                return JsonResponse({"type": "danger", "msg": uploader[1]})

            fs = FileSystemStorage(location="media")
            fs.delete(info.picture_canceled)
            info.picture_canceled = uploader[2]
        except:
            pass

        try:
            uploader = upload_file(request.FILES["picture4"], "media", False)
            if uploader[0] != True:
                return JsonResponse({"type": "danger", "msg": uploader[1]})

            fs = FileSystemStorage(location="media")
            fs.delete(info.picture_pending_delivery)
            info.picture_pending_delivery = uploader[2]
        except:
            pass

        try:
            uploader = upload_file(request.FILES["picture5"], "media", False)
            if uploader[0] != True:
                return JsonResponse({"type": "danger", "msg": uploader[1]})

            fs = FileSystemStorage(location="media")
            fs.delete(info.picture_received)
            info.picture_received = uploader[2]
        except:
            pass

        info.text_rejected = text_rejected
        info.text_not_received = text_not_received
        info.text_canceled = text_canceled
        info.text_pending_delivery = text_pending_delivery
        info.text_received = text_received
        info.delivery_conditions = delivery_conditions
        info.delivery_documents = delivery_documents
        info.desc_received = desc_received
        info.picture_rejected = info.picture_rejected
        info.picture_not_received = info.picture_not_received
        info.picture_canceled = info.picture_canceled
        info.picture_pending_delivery = info.picture_pending_delivery
        info.picture_received = info.picture_received
        info.save()

        add_static_report(request, "ویرایش اطلاعات صفحه انتخاب شهر ")

        return JsonResponse(
            {
                "type": "success",
                "msg": "اطلاعات با موفقیت ثبت شد",
                "picture1": info.picture_rejected,
                "picture2": info.picture_not_received,
                "picture3": info.picture_canceled,
                "picture4": info.picture_pending_delivery,
                "picture5": info.picture_received,
            }
        )

    return JsonResponse(
        {"type": "danger", "msg": "پردازش مورد نظر با مشکل مواجه شده است"}
    )


def master_site_customer_order_list(request, type):

    # master check start
    try:
        code = master_access_check(request)
        if code[0] != 100:
            return redirect(code[1])
    except:
        return redirect("master_login")
    # master check end

    if type == "Rejected":
        orders = Customer_Gold_Order.objects.filter(
            status__in=["Rejected", "Canceled"]
        ).order_by("-pk")

    elif type == "Not_received":
        orders = Customer_Gold_Order.objects.filter(status="Not_received").order_by(
            "-pk"
        )

    elif type == "Received":
        orders = Customer_Gold_Order.objects.filter(status="Received").order_by("-pk")

    elif type == "Pending_delivery":
        orders = Customer_Gold_Order.objects.filter(status="Pending_delivery").order_by(
            "-pk"
        )

    else:
        orders = Customer_Gold_Order.objects.all().order_by("-pk")

    paginator = Paginator(orders, 10)
    page = request.GET.get("page")

    try:
        querySet = paginator.page(page)
    except PageNotAnInteger:
        querySet = paginator.page(1)
    except EmptyPage:
        querySet = paginator.page(1)

    return render(
        request,
        get_master_theme() + "customer_order_list.html",
        {"querySet": querySet, "type": type},
    )

def master_site_customer_order_status_change(request, pk):

    # master check start
    try:
        code = master_access_check(request)
        if code[0] != 100:
            return redirect(code[1])
    except:
        return redirect("master_login")
    # master check end

    if request.method == "POST":

        status = request.POST.get("status")

        try:
            order = Customer_Gold_Order.objects.get(pk=pk, status="Pending_delivery")
        except:
            return JsonResponse(
                {"type": "success", "msg": "امکان تغییر وضعیت وجود ندارد"}
            )

        if status == "Received":

            try:
                uploader = upload_file(request.FILES["buyer_invoice"], "media", False)
                if uploader[0] != True:
                    return JsonResponse({"type": "danger", "msg": uploader[1]})

                fs = FileSystemStorage(location="media")
                fs.delete(order.buyer_invoice)
                order.buyer_invoice = uploader[2]
            except:
                return JsonResponse({"type": "danger", "msg": "لطفا فاکتور خریدار را آپلود نمایید"})
    
            try:
                uploader = upload_file(request.FILES["seller_invoice"], "media", False)
                if uploader[0] != True:
                    return JsonResponse({"type": "danger", "msg": uploader[1]})

                fs = FileSystemStorage(location="media")
                fs.delete(order.seller_invoice)
                order.seller_invoice = uploader[2]
            except:
                return JsonResponse({"type": "danger", "msg": "لطفا فاکتور فروشنده را آپلود نمایید"})

            order.status = "Received"
            order.reject_reason = None
            order.buyer_invoice = order.buyer_invoice
            order.seller_invoice = order.seller_invoice
            order.save()
            
            add_static_report(
                request, "تغییر وضعیت فاکتور محصول کاربر به تحویل داده شده"
            )
            return JsonResponse(
                {
                    "type": "success",
                    "msg": "وضعیت فاکتور به وضعیت تحویل داده شده تغییر یافت",
                }
            )

        elif status == "Rejected":

            reject_reason = request.POST.get("reject_reason")

            if reject_reason:

                order.status = "Rejected"
                order.reject_reason = reject_reason
                order.save()

                try:
                    working_day = order.delivery_date
                    working_day.capacity = working_day.capacity + 1
                    working_day.save()
                except:
                    pass

                for cart_product in Customer_Cart_Products.objects.filter(order=order):
                    inventory = Site_Product_Inventory(
                        product=cart_product.product,
                        quantity=cart_product.quantity,
                        datetime=get_date_time()["timestamp"],
                    )
                    inventory.save()

                if order.payment_status == 0:

                    w = Wallet(
                        uname=order.uname,
                        wallet="XAU18",
                        desc=f"بابت لغو تحویل فیزیکی  : {order.pk}",
                        amount=order.gram_total,
                        datetime=get_date_time()["timestamp"],
                        confirmed_datetime=get_date_time()["timestamp"],
                        ip=get_ip(request),
                        is_verify=False,
                        physical_delivery_pk=order.pk,
                    )
                    w.save()

                elif order.payment_status == 2:

                    w = Wallet(
                        uname=order.uname,
                        wallet="XAU18",
                        desc=f"بابت لغو تحویل فیزیکی  : {order.pk}",
                        amount=order.gram_remaining,
                        datetime=get_date_time()["timestamp"],
                        confirmed_datetime=get_date_time()["timestamp"],
                        ip=get_ip(request),
                        is_verify=False,
                        physical_delivery_pk=order.pk,
                    )
                    w.save()

                    Wallet(
                        uname=order.uname,
                        wallet="IRT",
                        desc=f"بابت لغو تحویل فیزیکی : {order.pk}",
                        amount=order.toman_remaining,
                        datetime=get_date_time()["timestamp"],
                        confirmed_datetime=get_date_time()["timestamp"],
                        ip="0.0.0.0",
                        is_verify=False,
                    ).save()

                elif order.payment_status == 1:

                    try :
                        wO = Online_Wallet.objects.get(order=order,is_physical_delivery=True,owner=order.uname)
                        wallet_amount = int(int(wO.transactionAmount) / 10) 

                        Wallet(
                            uname=order.uname,
                            wallet="IRT",
                            desc=f"بابت لغو تحویل فیزیکی : {order.pk}",
                            amount=wallet_amount,
                            datetime=get_date_time()["timestamp"],
                            confirmed_datetime=get_date_time()["timestamp"],
                            ip="0.0.0.0",
                            is_verify=False,
                        ).save()
                    except : pass    

                add_static_report(request, "تغییر وضعیت فاکتور محصول کاربر به رد شده")
                return JsonResponse(
                    {
                        "type": "success",
                        "msg": "وضعیت فاکتور به وضعیت رد شده تغییر یافت",
                    }
                )
            else:
                return JsonResponse(
                    {"type": "danger", "msg": "لطفا دلیل رد فاکتور را وارد نمایید"}
                )

        elif status == "Not_received":
            reject_reason = request.POST.get("reject_reason")
            if reject_reason:
                order.status = "Not_received"
                order.reject_reason = reject_reason
                order.save()
                return JsonResponse(
                    {
                        "type": "success",
                        "msg": "وضعیت فاکتور به وضعیت تحویل گرفته نشده تغییر یافت",
                    }
                )
            else:
                return JsonResponse(
                    {"type": "danger", "msg": "لطفا دلیل عدم تحویل را وارد نمایید"}
                )

        return JsonResponse({"type": "danger", "msg": "امکان تغییر وضعیت وجود ندارد"})


def master_site_customer_order_detail(request, pk):

    # master json check start
    try:
        code = master_access_check(request)
        if code[0] != 100:
            return JsonResponse({"type": "danger", "msg": code[2]})
    except:
        return JsonResponse(
            {"type": "danger", "msg": "ورود شما منقضی شده لطفا مجددا وارد شوید"}
        )
    # master json check end

    order = Customer_Gold_Order.objects.get(pk=pk)
    customer_cart = Customer_Cart_Products.objects.filter(order=order)

    return render(
        request,
        get_master_theme() + "customer_order_detail.html",
        {
            "order": order,
            "customer_cart": customer_cart,
            "last_gold_price": Currency_List.objects.get(symbol="XAU18").BuySellPrice[
                "buy"
            ],
            "set": ContactUs.objects.get(code=1001),
        },
    )


def master_physical_delivery_settings(request):

    # master json check start
    try:
        code = master_access_check(request)
        if code[0] != 100:
            return JsonResponse({"type": "danger", "msg": code[2]})
    except:
        return JsonResponse(
            {"type": "danger", "msg": "ورود شما منقضی شده لطفا مجددا وارد شوید"}
        )
    # master json check end

    if request.method == "POST":

        physical_delivery_show = request.POST.get("physical_delivery_show")

        physical_delivery_show = False if physical_delivery_show != "on" else True

        deposit = Site_Settings.objects.get(code=1001)
        deposit.physical_delivery_show = physical_delivery_show
        deposit.save()

        add_static_report(request, "ویرایش تنظیمات نمایش تحویل فیزیکی طلا")

        return JsonResponse({"type": "success", "msg": "اطلاعات با موفقیت ثبت شد"})

    return JsonResponse(
        {"type": "danger", "msg": "پردازش مورد نظر با مشکل مواجه شده است"}
    )


def master_physical_delivery_submit(request):

    # master json check start
    try:
        code = master_access_check(request)
        if code[0] != 100:
            return JsonResponse({"type": "danger", "msg": code[2]})
    except:
        return JsonResponse(
            {"type": "danger", "msg": "ورود شما منقضی شده لطفا مجددا وارد شوید"}
        )
    # master json check end

    if request.method == "POST":

        physical_delivery_page_title = request.POST.get("physical_delivery_page_title")
        physical_delivery_page_desc = request.POST.get("physical_delivery_page_desc")

        if physical_delivery_page_title == "" or physical_delivery_page_desc == "":
            return JsonResponse(
                {"type": "danger", "msg": "لطفا تمامی موارد را وارد نمایید"}
            )

        info = Site_Settings.objects.get(code=1001)

        try:
            uploader = upload_file(request.FILES["picture"], "media", False)
            if uploader[0] != True:
                return JsonResponse({"type": "danger", "msg": uploader[1]})

            fs = FileSystemStorage(location="media")
            fs.delete(info.physical_delivery_page_pic)
            info.physical_delivery_page_pic = uploader[2]
        except:
            pass

        info.physical_delivery_page_title = physical_delivery_page_title
        info.physical_delivery_page_desc = physical_delivery_page_desc
        info.physical_delivery_page_pic = info.physical_delivery_page_pic
        info.save()

        add_static_report(request, "ویرایش اطلاعات صفحه تحویل فیزیکی ")

        return JsonResponse(
            {
                "type": "success",
                "msg": "اطلاعات با موفقیت ثبت شد",
                "picture": info.physical_delivery_page_pic,
            }
        )

    return JsonResponse(
        {"type": "danger", "msg": "پردازش مورد نظر با مشکل مواجه شده است"}
    )


def master_physical_delivery_counter_submit(request):

    # master json check start
    try:
        code = master_access_check(request)
        if code[0] != 100:
            return JsonResponse({"type": "danger", "msg": code[2]})
    except:
        return JsonResponse(
            {"type": "danger", "msg": "ورود شما منقضی شده لطفا مجددا وارد شوید"}
        )
    # master json check end

    if request.method == "POST":

        physical_delivery_counter_title1 = request.POST.get(
            "physical_delivery_counter_title1"
        )
        physical_delivery_counter1 = request.POST.get("physical_delivery_counter1")
        physical_delivery_counter_title2 = request.POST.get(
            "physical_delivery_counter_title2"
        )
        physical_delivery_counter2 = request.POST.get("physical_delivery_counter2")
        physical_delivery_counter_title3 = request.POST.get(
            "physical_delivery_counter_title3"
        )
        physical_delivery_counter3 = request.POST.get("physical_delivery_counter3")
        physical_delivery_counter_title4 = request.POST.get(
            "physical_delivery_counter_title4"
        )
        physical_delivery_counter4 = request.POST.get("physical_delivery_counter4")

        if (
            physical_delivery_counter_title1 == ""
            or physical_delivery_counter1 == ""
            or physical_delivery_counter_title2 == ""
            or physical_delivery_counter2 == ""
            or physical_delivery_counter_title3 == ""
            or physical_delivery_counter3 == ""
            or physical_delivery_counter_title4 == ""
            or physical_delivery_counter4 == ""
        ):
            return JsonResponse(
                {"type": "danger", "msg": "لطفا تمامی موارد را وارد نمایید"}
            )

        info = Site_Settings.objects.get(code=1001)

        try:
            uploader = upload_file(request.FILES["picture1"], "media", False)
            if uploader[0] != True:
                return JsonResponse({"type": "danger", "msg": uploader[1]})

            fs = FileSystemStorage(location="media")
            fs.delete(info.physical_delivery_counter_picture1)
            info.physical_delivery_counter_picture1 = uploader[2]
        except:
            pass

        try:
            uploader = upload_file(request.FILES["picture2"], "media", False)
            if uploader[0] != True:
                return JsonResponse({"type": "danger", "msg": uploader[1]})

            fs = FileSystemStorage(location="media")
            fs.delete(info.physical_delivery_counter_picture2)
            info.physical_delivery_counter_picture2 = uploader[2]
        except:
            pass

        try:
            uploader = upload_file(request.FILES["picture3"], "media", False)
            if uploader[0] != True:
                return JsonResponse({"type": "danger", "msg": uploader[1]})

            fs = FileSystemStorage(location="media")
            fs.delete(info.physical_delivery_counter_picture3)
            info.physical_delivery_counter_picture3 = uploader[2]
        except:
            pass

        try:
            uploader = upload_file(request.FILES["picture4"], "media", False)
            if uploader[0] != True:
                return JsonResponse({"type": "danger", "msg": uploader[1]})

            fs = FileSystemStorage(location="media")
            fs.delete(info.physical_delivery_counter_picture4)
            info.physical_delivery_counter_picture4 = uploader[2]
        except:
            pass

        info.physical_delivery_counter_title1 = physical_delivery_counter_title1
        info.physical_delivery_counter1 = physical_delivery_counter1
        info.physical_delivery_counter_title2 = physical_delivery_counter_title2
        info.physical_delivery_counter2 = physical_delivery_counter2
        info.physical_delivery_counter_title3 = physical_delivery_counter_title3
        info.physical_delivery_counter3 = physical_delivery_counter3
        info.physical_delivery_counter_title4 = physical_delivery_counter_title4
        info.physical_delivery_counter4 = physical_delivery_counter4
        info.physical_delivery_counter_picture1 = (
            info.physical_delivery_counter_picture1
        )
        info.physical_delivery_counter_picture2 = (
            info.physical_delivery_counter_picture2
        )
        info.physical_delivery_counter_picture3 = (
            info.physical_delivery_counter_picture3
        )
        info.physical_delivery_counter_picture4 = (
            info.physical_delivery_counter_picture4
        )
        info.save()

        add_static_report(request, "ویرایش شمارنده های تحویل فیزیکی ")

        return JsonResponse(
            {
                "type": "success",
                "msg": "اطلاعات با موفقیت ثبت شد",
                "picture1": info.physical_delivery_counter_picture1,
                "picture2": info.physical_delivery_counter_picture2,
                "picture3": info.physical_delivery_counter_picture3,
                "picture4": info.physical_delivery_counter_picture4,
            }
        )

    return JsonResponse(
        {"type": "danger", "msg": "پردازش مورد نظر با مشکل مواجه شده است"}
    )


def master_physical_delivery_deliverers_list(request):

    
    # master check start
    try:
        code = master_access_check(request)
        if code[0] != 100: return redirect(code[1])
    except: return redirect("master_login")
    # master check end

    deliverers = Site_Branches_Deliverer.objects.all()

    paginator = Paginator(deliverers.order_by("-pk"), 10)
    page = request.GET.get("page")

    try:
        querySet = paginator.page(page)
    except PageNotAnInteger:
        querySet = paginator.page(1)
    except EmptyPage:
        querySet = paginator.page(1)

    return render(request, get_master_theme() + 'master_deliverers_list.html', {'deliverers': querySet, 'deliverers_count': deliverers.count()})



def master_cancle_deposite_withdrawal(request,pk):

    # master json check start
    try : 
        code=master_access_check(request)
        if code[0] != 100 : return JsonResponse({'type':'danger', 'msg':code[2]})
    except: return JsonResponse({'type':'danger', 'msg':'ورود شما منقضی شده لطفا مجددا وارد شوید'})
    # master json check end

    try :

        wallet = WalletWithdrawIRT.objects.get(pk=pk,bank_send=True,check_inquery=False,status='BankSend')

        wallet_settlment = Settlement_Vandar_APi()    
        send_req_bank = wallet_settlment.cancel_settlement(wallet.trans_id)

        add_static_report(request, 'لغو برداشت')

        if send_req_bank['success'] == True :

    
            wallet.status = 'Cancel'
            wallet.is_verify = False
            wallet.reject_reson = 'عدم تایید برداشت'
            wallet.confirmed_datetime = get_date_time()['timestamp']
            wallet.save()   


            w = Wallet(

                uname = wallet.uname, 
                master = code[3], 
                wallet = wallet.wallet.wallet, 
                amount = (wallet.wallet.amount) * (-1), 
                desc = f'بابت لغو برداشت به شناسه : {wallet.pk}', 
                datetime = get_date_time()['timestamp'],
                is_verify = False,
            )
            w.save()

            return JsonResponse({'type':'success', 'msg':'لغو برداشت با موفقیت انجام شد'})

        else :

            return JsonResponse({'type':'danger', 'msg':'در حال حاضر امکان لغو برداشت مورد نظر وجود ندارد'})    

    except : return JsonResponse({'type':'danger', 'msg':'در حال حاضر امکان لغو برداشت مورد نظر وجود ندارد'})   


def master_physical_delivery_deliverers_add_submit(request):

    # master check start
    try:
        code = master_access_check(request)
        if code[0] != 100:
            return redirect(code[1])
    except:
        return redirect("master_login")
    # master check end

    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        personal_code = request.POST.get('personal_code')
        organizational_position = request.POST.get('organizational_position')

        if first_name == "" or last_name == "" or personal_code == "" or organizational_position == "":
            return JsonResponse(
                {"type": "danger", "msg": "لطفا فیلد های خواسته شده را تکمیل نمایید"}
            )

 
        
        deliverer = Site_Branches_Deliverer()

        deliverer.first_name = first_name
        deliverer.last_name = last_name
        deliverer.personal_code = personal_code
        deliverer.organizational_position = organizational_position
        deliverer.save()

        add_static_report(request, "اضافه کردن تحویل دهنده")

        return JsonResponse(
            {
                "type": "success",
                "msg": "تحویل دهنده با موفقیت ثبت شد",
                "first_name": deliverer.first_name,
                "last_name": deliverer.last_name,
                "personal_code": deliverer.personal_code,
                "organizational_position": deliverer.organizational_position,
            }
        )

    return JsonResponse({"type": "danger", "msg": "ثبت تحویل دهنده با مشکل مواجه شد"})


def master_physical_delivery_deliverers_edit(request, pk):
    # master check start
    try:
        code = master_access_check(request)
        if code[0] != 100:
            return redirect(code[1])
    except:
        return redirect("master_login")
    # master check end

    try:
        deliverer = Site_Branches_Deliverer.objects.get(pk=pk)
    except:
        return JsonResponse({"type": "danger", "msg": "ویرایش تحویل دهنده با مشکل مواجه شده است"})

    return render(
        request,
        get_master_theme() + "master_deliverers_edit.html",
        {"querySet": deliverer},
    )


def master_physical_delivery_deliverers_edit_submit(request, pk):

    # master check start
    try:
        code = master_access_check(request)
        if code[0] != 100:
            return redirect(code[1])
    except:
        return redirect("master_login")
    # master check end

    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        personal_code = request.POST.get('personal_code')
        organizational_position = request.POST.get('organizational_position')

        if first_name == "" or last_name == "" or personal_code == "" or organizational_position == "":
            return JsonResponse(
                {"type": "danger", "msg": "لطفا فیلد های خواسته شده را تکمیل نمایید"}
            )
 
        try:
            deliverer = Site_Branches_Deliverer.objects.get(pk=pk)
        except:
            return JsonResponse({"type": "danger", "msg": "ویرایش تحویل دهنده با مشکل مواجه شده است"})

        deliverer.first_name = first_name
        deliverer.last_name = last_name
        deliverer.personal_code = personal_code
        deliverer.organizational_position = organizational_position
        deliverer.save()

        add_static_report(request, "ویرایش تحویل دهنده")

        return JsonResponse(
            {
                "type": "success",
                "msg": "تحویل دهنده با موفقیت ویرایش شد",
                "first_name": deliverer.first_name,
                "last_name": deliverer.last_name,
                "personal_code": deliverer.personal_code,
                "organizational_position": deliverer.organizational_position,
            }
        )

    return JsonResponse({"type": "danger", "msg": "ویرایش تحویل دهنده با مشکل مواجه شد"})


def master_physical_delivery_deliverers_delete_submit(request, pk):
    # master check start
    try:
        code = master_access_check(request)
        if code[0] != 100:
            return redirect(code[1])
    except:
        return redirect("master_login")
    # master check end

    try:
        deliverer = Site_Branches_Deliverer.objects.get(pk=pk)
    except:
        return JsonResponse({"type": "danger", "msg": "حذف تحویل دهنده با مشکل مواجه شده است"})

    deliverer.delete()

    add_static_report(request, "حذف تحویل دهنده")

    return JsonResponse({"type": "success", "msg": "تحویل دهنده با موفقیت حذف شد"})


def master_physical_delivery_deliverers_change_status(request, pk):

    # master json check start
    try:
        code = master_access_check(request)
        if code[0] != 100:
            return JsonResponse({"type": "danger", "msg": code[2]})
    except:
        return JsonResponse(
            {"type": "danger", "msg": "ورود شما منقضی شده لطفا مجددا وارد شوید"}
        )
    # master json check end

    deliverers = Site_Branches_Deliverer.objects.get(pk=pk)
    deliverers.act = False if deliverers.act == True else True
    deliverers.save()

    add_static_report(request, f" تغییر وضعیت تحویل گیرنده {deliverers.first_name}  {deliverers.last_name}")
    return JsonResponse(
        {
            "type": "success",
            "msg": "وضعیت با موفقیت ویرایش  شد",
            "id": pk,
            "status": deliverers.act,
        }
    )


# delete code
# .
# .
# .
