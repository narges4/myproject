from __future__ import unicode_literals
from datetime import datetime
import json
from django.db.models import Sum
from django.db import models
from django.contrib.auth.models import User
from django.db.models import Avg, Count, Min, Sum, F, Value, CharField
import jdatetime
from exchange.models import *
from wallet.models import *
from currency.models import *
import uuid
from django.core.validators import MaxValueValidator


CUSTOMERSTATUS = [ 
    ('Authenticated','Authenticated'),
    ('Suspended','Suspended'),
    ('PreRegister','PreRegister'),
]

USERTYPE = [
    ('Male','Male'),
    ('FeMale','FeMale'),
    ('Other','Other'),
]

USERLEVELING = [
    ('LowAttendance', 'کم مراجعه'),
    ('Normal', 'معمولی'),
    ('HighAttendance', 'پر مراجعه'),
]

CELINGTYPE = [
    ('sell','sell'),
    ('buy','buy'),
    ('trade','trade'),
    ('transfer','transfer'),
]

ERRORSREPORTSTATUS = [
    ('AwaitingReview','AwaitingReview'),
    ('CheckedOut','CheckedOut'),
]

PROMOTE = [

    ('BuySell','BuySell'),
    ('Introduce','Introduce'),
]

CERTIFICATE = [

    ('Pendding','Pendding'),
    ('Success','Success'),
    ('Rejected','Rejected'),
]

ORDER_STATUS_CHOICES = [
    ('Rejected', 'Rejected'),
    ('Not_received', 'Not_received'),
    ('Received', 'Received'),
    ('Pending_payment', 'Pending_payment'),
    ('Pending_delivery', 'Pending_delivery'),
    ('Canceled', 'Canceled'),
    ('Pending', 'Pending'),
    ('Connection_getway', 'Connection_getway'),

]



class Customer(models.Model):
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    unique_code = models.CharField(unique=True, null=True, blank=True)
    support = models.ForeignKey(Master, on_delete=models.CASCADE, blank=True, null=True, related_name='customer') 
    uuid_code = models.TextField(default="-")

    national_id = models.CharField(max_length=50, default="-")
    first_name = models.CharField(max_length=250, default="-")
    last_name = models.CharField(max_length=250, default="-")
    father_name = models.CharField(max_length=250, default="-")
    birth_date = models.CharField(max_length=50, default="-")
    sex = models.CharField(max_length=50,choices=USERTYPE,default="Other")
    country = models.CharField(max_length=50, default="-")
    state = models.CharField(max_length=50, default="-")
    city = models.CharField(max_length=50, default="-")
    mobile = models.CharField(max_length=50, default="-")
    address = models.TextField(default="-")
    reg_date = models.CharField(max_length=150, default="-")
    auth_date = models.CharField(max_length=150, default="-")
    last_ip = models.CharField(max_length=100, default="-")
    last_login = models.CharField(max_length=150, default="-")
    last_code = models.CharField(max_length=50, default="-")
    last_code_datetime = models.CharField(max_length=150,default="1649860168")
    referral_link = models.CharField(max_length=250, default="-")
    up_referral_link = models.CharField(max_length=250, default="-")
    req_user = models.CharField(max_length=50, default="-")
    profile_pic_name = models.CharField(max_length=250,default="defaultProfile.png")
    is_rulls = models.BooleanField(default=False)
    is_profile = models.BooleanField(default=False)
    is_mobile = models.BooleanField(default=False)
    is_auth = models.BooleanField(default=False)
    need_auth_check = models.BooleanField(default=False)
    is_representation_auth = models.BooleanField(default=False)
    is_suspended = models.BooleanField(default=False)
    is_force_to_change_pass = models.BooleanField(default=False)
    is_toverification = models.BooleanField(default=False)
    is_toverification_requird = models.BooleanField(default=False)
    
    is_mobile_ownership = models.BooleanField(default=True)
    mobile_ownership_counter = models.IntegerField(default=0)
    mobile_ownership_time = models.FloatField(default=0)
    mobile_ownership_description_reject = models.TextField(default='', null=True, blank=True)

    is_suspicious = models.BooleanField(default=False)
    is_suspicious_description = models.TextField(default='', null=True, blank=True)
    status = models.CharField(max_length=50,choices=CUSTOMERSTATUS, default="PreRegister")
    leveling = models.CharField(max_length=50,choices=USERLEVELING, default="LowAttendance")
    user_agent = models.TextField(default="-")
    change_mobile_datetime = models.CharField(max_length=150, null=True, blank=True)
    

    app_token = models.CharField(max_length=250, default="-")

    pyotp_hash = models.CharField(max_length=350, default="-")
    gateway_code = models.CharField(max_length=50,default="0")


    # Ceiling User

    sell = models.IntegerField(default=0)
    buy = models.IntegerField(default=0)
    trade = models.IntegerField(default=0)
    transfer = models.FloatField(default=0.0)
    classic_market_buy = models.IntegerField(default=0)
    classic_market_sell = models.IntegerField(default=0)

    # Sum Buy_Sell........... ---> irt 
    
    sell_price = models.FloatField(default=0.0)
    buy_price = models.FloatField(default=0.0)
    trade_price = models.FloatField(default=0.0)
    transfer_price = models.FloatField(default=0.0)
    classic_market_buy_price = models.FloatField(default=0.0)
    classic_market_sell_price = models.FloatField(default=0.0)


    # -------------------------------------


    welcome = models.BooleanField(default=False)
    attract_sales = models.BooleanField(default=False)


    get_gift = models.BooleanField(default=False)
    question_rate = models.FloatField(default=0.0)
    nick_name = models.CharField(max_length=250, default="-")
    Withdrawal_code = models.CharField(max_length=50,default="0")
    transfer_code = models.CharField(max_length=50,default="0")
    wallet_direct_transfer_code = models.CharField(max_length=50,default="0")
    delete_code =  models.CharField(max_length=50,default="0")

    check_survey = models.BooleanField(default=False)

    brith_year = models.CharField(max_length=10, default="-")
    brith_month = models.CharField(max_length=10, default="-")
    birth_day = models.CharField(max_length=10, default="-")
    send_birth_sms = models.CharField(max_length=10, default="-")
    send_sms_pk = models.IntegerField(default=0)
    is_vip = models.BooleanField(default=False)

    representation_register = models.BooleanField(default=False)
    sso_access = models.BooleanField(default=False)
    
    hour_to_pending = models.IntegerField(default=0)
    max_wallet_create_allow_trc20 = models.IntegerField(default=0)
    last_buysell_time = models.CharField(max_length=150,default="0")
    reseller_upper_link = models.CharField(max_length=250, default="-")

    block_date = models.CharField(max_length=150, default="-")

    is_investment = models.BooleanField(default=False)
    
    day_of_register = models.CharField(max_length=50, default="-")
    day_of_login = models.CharField(max_length=50, default="-")
 
    is_from_pwa = models.BooleanField(default=False)

    method_introduction = models.ForeignKey('exchange.Method_Introduction', on_delete=models.CASCADE, null=True, blank=True)
    is_bank = models.BooleanField(default=True)

    is_identity_check = models.BooleanField(default=False)
    identity_counter = models.IntegerField(default=0)
    identity_time = models.FloatField(default=0)
    is_alive = models.BooleanField(default=False)
    identificationSerial = models.CharField(max_length=250, default="-")
    identificationSeri = models.CharField(max_length=250, default="-")
    placeOfBirth = models.TextField(default="-")
    
    investment_show = models.BooleanField(default=False)
    new_investment_show = models.BooleanField(default=False)
    
    instant_increase = models.BooleanField(default=False)
    increase_link = models.CharField(max_length=12, default='-')
    unique_deposit_number = models.CharField(max_length=50, default='-')

    heirs_duration = models.ForeignKey('master.Heredity_Duration', on_delete=models.CASCADE, related_name='heirs_duration', null=True, blank=True)
    transferred_heir = models.ForeignKey('Customer_Heir', on_delete=models.CASCADE, null=True, blank=True)

    # -----------------
  
    points = models.FloatField(default=0.0)


    @property
    def RegisterFrom(self): 
        return f"representation" if not self.user.username.startswith('customer-') else f"main"
 
    @property
    def FullName(self):
        return self.first_name + " " + self.last_name

    @property
    def ToshamsiDate(self):

        try :
            return {
                'regDate':jdatetime.datetime.fromtimestamp(int(self.reg_date)),
                'lastLogin':jdatetime.datetime.fromtimestamp(int(self.last_login))
            }

        except : 

            return {
                'regDate':jdatetime.datetime.fromtimestamp(int(self.reg_date)),
                'lastLogin':"-"
            }


    @property
    def CustomerStatus(self):
        
        if self.need_auth_check == True : return {'status':'در انتظار تایید','color':'warning'}
        elif self.status == 'Authenticated' : return {'status':'احراز هویت شده','color':'success'}
        elif self.status == 'Suspended' : return {'status':'مسدود شده','color':'danger'}
        elif self.status == 'PreRegister' : return {'status':'پیش ثبت نام','color':'primary'}
        
        return {'status':'نامشخص','color':'primary'} 

    @property
    def CustomerToverificationAuthenticated(self):
        if self.is_toverification == True : return 'فعال'
        if self.is_toverification == False : return 'غیرفعال'

        return 'نامشخص'

    @property
    def CustomerType(self):

        if self.sex == 'Male' : return 'مرد'
        if self.sex == 'FeMale' : return 'زن'
        if self.sex == 'Other' : return 'دیگر'

        return 'نامشخص'

    @property
    def CustomerLevel(self):

        try :

            if Customer_Level.objects.filter(amount__gte=self.buy_price).first() :
                level = Customer_Level.objects.filter(amount__gte=self.buy_price).first()
                return level.title

            level = Customer_Level.objects.filter(amount__lte=self.buy_price).last()
            return level.title
                
        except :
            return 'بدون سطح'
        

    @property
    def month_to_timestamp(self):
        return (int(self.heirs_duration.month) * 30) * 86400



    @property
    def Referral(self):
        from currency.models import Currency_List
        
        ref_gift = Customer_refIncome_log.objects.filter(ref_link=self.referral_link, desc='Introduce').aggregate(Sum('amount'))['amount__sum']
       
        if str(ref_gift) == 'None' : ref_gift = 0  


        all_income = Customer_refIncome_log.objects.filter(ref_link=self.referral_link).aggregate(Sum('amount'))['amount__sum']
        if str(all_income) == 'None' : all_income = 0  
        all_income_to_grams = all_income / Currency_List.objects.get(symbol='XAU18').BuySellPrice['buy']

        date = datetime.now()
        x = str(date.date()).split('-')
        earlier = x[0] + '-' + x[1] + '-' + x[2] + ' 00:00:00'
        earlier = datetime.strptime(earlier,"%Y-%m-%d %H:%M:%S").timestamp()

        today = Customer_refIncome_log.objects.filter(ref_link=self.referral_link, datetime__gte=earlier).aggregate(Sum('amount'))['amount__sum']
        if str(today) == 'None' : today = 0  

        return {

            'All': Customer.objects.filter(up_referral_link=self.referral_link).count(),
            'Auth': Customer.objects.filter(up_referral_link=self.referral_link, status='Authenticated').count(),
            'Click': Customer_refLink_click.objects.filter(ref_link=self.referral_link).count(),
            'RefGift' : ref_gift,
            'Total':all_income,
            'Total_grams': all_income_to_grams,
            'Today':today,
            'Active' : Customer_gift.objects.filter(uname__up_referral_link=self.referral_link,get_uper_user=True).count()
        }


    @property
    def LastWalletTransaction(self):

        return {

            'deposite': Wallet.objects.filter(uname=self.pk, is_verify=True, amount__gt=0).order_by('-pk')[:7],
            'withdraw': Wallet.objects.filter(uname=self.pk, is_verify=True, amount__lt=0).order_by('-pk')[:7],
    
        }

    def __str__(self):
        return f'{self.first_name } {self.last_name}'



class Customer_Requests_Logs(models.Model):

    uname = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True, related_name='customer_requests_logs')
    identify = models.CharField(max_length=250)
    error = models.TextField()
    ip = models.CharField(max_length=150, null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    datetime = models.CharField(max_length=150)

    @property
    def ToshamsiDate(self):
        try: return jdatetime.datetime.fromtimestamp(int(self.datetime))
        except: return '-'

    class Meta:
        ordering = ['-id']
    

class Customer_Friend(models.Model):

    uname = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True, related_name='customer_friend')
    friend = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True, related_name='friend')
    datetime = models.CharField(max_length=150, default="-")

    @property
    def ToshamsiDate(self):
        try: return jdatetime.datetime.fromtimestamp(int(self.datetime))
        except: return '-'

class Customer_Communication(models.Model):

    CUSTOMER_COMMUNICATION_TYPE = [
        ('call', 'تماس تلفنی'),
        ('message', 'ارسال پیامک')
    ]

    uname = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True, related_name="customer_communication")
    master = models.ForeignKey(Master, on_delete=models.CASCADE, null=True, blank=True, related_name='customer_communication')
    type = models.CharField(max_length=50, choices=CUSTOMER_COMMUNICATION_TYPE, default=None, null=True, blank=True)
    time = models.IntegerField(default=0)
    desc = models.TextField(default="-")
    datetime = models.CharField(max_length=150, default="-")

    @property
    def ToshamsiDate(self):
        try: return jdatetime.datetime.fromtimestamp(int(self.datetime))
        except: return '-'

class Expert_Customer_Connection_Log(models.Model):

    uname = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True, related_name='expert_customer_connection_log')
    master = models.ForeignKey(Master, on_delete=models.CASCADE, null=True, blank=True, related_name='expert_customer_connection_log')
    chack = models.BooleanField(default=False) 
    datetime = models.CharField(max_length=150, default="-")

    @property
    def ToshamsiDate(self):
        try: return jdatetime.datetime.fromtimestamp(int(self.datetime))
        except: return '-'
    

class Customer_Note(models.Model):

    uname = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True, related_name="customer_note")
    master = models.ForeignKey(Master, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=250, null=True, blank=True)
    desc = models.TextField(default="-")
    datetime = models.CharField(max_length=150, default="-")

    @property
    def ToshamsiDate(self):
        try: return jdatetime.datetime.fromtimestamp(int(self.datetime))
        except: return '-'
    

class Customer_Redirect(models.Model):
    
    code = models.CharField(max_length=50, default="-")
    url = models.CharField(max_length=350, default="-")

    def __str__(self):
        return self.code + "  |  " + self.url


class Customer_uploads_Cat(models.Model):
    
    title = models.CharField(max_length=250, default="-")
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class Customer_uploads(models.Model):
    
    uname = models.ForeignKey('Customer', on_delete=models.CASCADE)
    file_type = models.CharField(max_length=350, default="-")
    file_name = models.CharField(max_length=350, default="-")
    file_url = models.CharField(max_length=350, default="-")
    datetime = models.CharField(max_length=150, default="-")

    @property
    def ToshamsiDate(self):
        return jdatetime.datetime.fromtimestamp(int(self.datetime))


class Customer_card(models.Model):
    
    uname = models.ForeignKey(Customer, on_delete=models.CASCADE)
    bank =  models.ForeignKey(Site_Banks,  on_delete=models.CASCADE)
    card_number = models.CharField(max_length=350, default="-")
    account_number = models.CharField(max_length=350, default="-")
    Shaba_number = models.CharField(max_length=350, default="-")
    is_verify = models.BooleanField(default=None,null=True)  # None : waiting / True : Accept / False : Reject
    desc_reject = models.TextField(default="-")
    confirmed_master = models.CharField(max_length=150, default="-")
    datetime = models.CharField(max_length=150, default="-")
    is_show = models.BooleanField(default=True)
    master = models.ForeignKey('master.Master', on_delete=models.CASCADE,null=True)
    card_ownership = models.BooleanField(default=False)
    complete_card_information = models.BooleanField(default=False)
    counter_check_ownership = models.IntegerField(default=0)
    counter_check = models.IntegerField(default=0)
    time_check = models.FloatField(default=0)
    
    @property
    def ToshamsiDate(self):
        return jdatetime.datetime.fromtimestamp(int(self.datetime))
 

    def __str__(self):
        return self.card_number


class Customer_Ceiling_List(models.Model):
    
    uname = models.ForeignKey(Customer, on_delete=models.CASCADE)
    amount = models.FloatField(default=0.0)
    ceiling = models.CharField(max_length=50,choices=CELINGTYPE, default="Other")
    is_verify = models.BooleanField(default=None,null=True)  # None : waiting / True : Accept / False : Reject
    confirmed_master = models.CharField(max_length=150, default="-")
    datetime = models.CharField(max_length=150, default="-")
    master = models.ForeignKey(Master, on_delete=models.CASCADE,null=True,blank=True)

    @property
    def ToshamsiDate(self):
        
        return jdatetime.datetime.fromtimestamp(int(self.datetime))


    @property
    def CeilingType(self):

        if self.ceiling == 'sell' : return 'فروش'
        if self.ceiling == 'buy' : return 'خرید'
        if self.ceiling == 'trade' : return 'تبدیل'
        if self.ceiling == 'transfer' : return 'انتقال'
        if self.ceiling == 'Other' : return 'دیگر'

        return 'نامشخص'


class Customer_errors_report(models.Model):

    uname = models.ForeignKey(Customer, on_delete=models.CASCADE)
    desc = models.TextField(default="-")
    file = models.TextField(default="-")
    datetime = models.CharField(max_length=20, default="-")
    status = models.CharField(max_length=100,choices=ERRORSREPORTSTATUS, default="AwaitingReview")

    @property
    def ToshamsiDate(self):
        return jdatetime.datetime.fromtimestamp(int(self.datetime))


class Customer_gift_check(models.Model):

    uname = models.CharField(max_length=150, default="-")
    datetime = models.CharField(max_length=20, default="-")
    game = models.CharField(max_length=20, default="-")
    gift = models.CharField(max_length=200, default="-")
    gift_symbol = models.CharField(max_length=200, default="-")
    gift_amount = models.IntegerField(default=0)
    is_winner = models.BooleanField(default=False)
    is_check = models.BooleanField(default=None,null=True)  # None : waiting / True : Accept / False : Reject

    @property
    def GetCustomerName(self):
        return Customer.objects.get(req_user=self.uname)

    @property
    def ToshamsiDate(self):
        return jdatetime.datetime.fromtimestamp(int(self.datetime))
        
class Customer_wallet_address(models.Model):
    
    uname = models.ForeignKey('Customer', on_delete=models.CASCADE)
    asset = models.CharField(max_length=150, default="-")
    network = models.CharField(max_length=150, default="-")
    address = models.CharField(max_length=350, default="-")
    

class Customer_certificate(models.Model):
    
    uname = models.ForeignKey('Customer', on_delete=models.CASCADE)
    bill_id = models.CharField(max_length=350, default="-")
    transactionId = models.CharField(max_length=350, default="-")
    token = models.CharField(max_length=350, default="-")
    serial = models.CharField(max_length=350, default="-")
    amount = models.CharField(max_length=5, default="-")
    datetime = models.CharField(max_length=20, default="-")
    status = models.CharField(max_length=100,choices=CERTIFICATE, default="Pendding")
    is_check = models.BooleanField(default=False)
    is_error = models.BooleanField(default=False)
    error = models.TextField(default="-")

    @property
    def ToshamsiDate(self):
        return jdatetime.datetime.fromtimestamp(int(self.datetime))

    @property
    def StatusShow(self):

        if self.status == 'Pendding' : return 'در انتظار صدور'
        if self.status == 'Rejected' : return 'رد شده'
        if self.status == 'Success' : return 'صادر شده'

        return 'نامشخص'




class Customer_gift(models.Model): 

    uname = models.ForeignKey('Customer', on_delete=models.CASCADE)
    is_check = models.BooleanField(default=False)
    amount_user = models.FloatField(default=0.0)
    wallet_user =  models.CharField(max_length=350, default="-")
    amount_interduce =  models.FloatField(default=0.0)
    wallet_interduce = models.CharField(max_length=350, default="-")
    min_buy = models.IntegerField(default=0)    
    up_referral_link =  models.CharField(max_length=250, default="-")   
    min_transaction_user = models.IntegerField(default=0)  
    get_user = models.BooleanField(default=False) 
    get_uper_user = models.BooleanField(default=False) 

class Customer_Representation_Request(models.Model): 

    uname = models.ForeignKey('customer.Customer', on_delete=models.CASCADE, null=True)
    txt = models.TextField(default="-")
    datetime = models.CharField(max_length=150, default="-")
    currency = models.CharField(max_length=150, default="-")
    currency_symbol = models.CharField(max_length=150, default="-")
    title = models.CharField(max_length=150, default="-")
    act = models.BooleanField(default=False)

    @property
    def ToshamsiDate(self):
        return jdatetime.datetime.fromtimestamp(int(self.datetime))


class Customer_Level(models.Model):
    
    title = models.CharField(max_length=500, default="-")
    amount = models.FloatField(default=0.0)
    datetime = models.CharField(max_length=150, default='-')

    @property
    def ToshamsiDate(self):
        return jdatetime.datetime.fromtimestamp(int(self.datetime))
    
    def __str__(self):
        return self.title


class Customer_Mission(models.Model):
    
    desc = models.TextField(default="-")
    status = models.BooleanField(default=None,null=True)  # None : waiting / True : Accept / False : Reject
    datetime = models.CharField(max_length=150, default='-')
    mission = models.ForeignKey(Site_Missions, on_delete=models.CASCADE)
    uname = models.ForeignKey(Customer, on_delete=models.CASCADE)

    @property
    def ToshamsiDate(self):
        return jdatetime.datetime.fromtimestamp(int(self.datetime))

class Customer_Course(models.Model):

    uname = models.ForeignKey(Customer, on_delete=models.CASCADE)
    status = models.BooleanField(default=None,null=True)  # None : waiting / True : Accept / False : Reject
    datetime = models.CharField(max_length=150, default='-')
    rate = models.IntegerField(default=0)

    @property
    def ToshamsiDate(self):
        return jdatetime.datetime.fromtimestamp(int(self.datetime))



class Customer_Gold_Order(models.Model):

    uname = models.ForeignKey(Customer, on_delete=models.CASCADE)
    datetime = models.CharField(max_length=150, default='-')
    city = models.ForeignKey(Site_Cities_With_Represent, on_delete=models.SET_NULL, null=True)
    branch = models.ForeignKey(Site_Branches_Each_Representative, on_delete=models.SET_NULL, null=True)
    delivery_date = models.ForeignKey(Site_Branch_Working_Days, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='Pending_payment')
    is_used = models.BooleanField(default=False)
    toman_total = models.IntegerField(default=0) #کل جمع تومانی
    gram_total = models.FloatField(default=0.0) #کل جمع گرمی
    reject_reason = models.TextField(null=True, blank=True)


    #new
    gram_remaining = models.FloatField(default=0.0) # مقدار گرم پرداخت شده از صندوق طلا
    toman_remaining = models.IntegerField(default=0) #مقدار تومان پرداخت شده از درگاه
    error_gateway = models.TextField(default="-")
    is_check = models.BooleanField(default=False)

    payment_status = models.IntegerField(default=-1)  # 0 : wallet / 1 : online / 2 : online & wallet
    gold_price = models.IntegerField(default=0)
    total_wages_toman = models.IntegerField(default=0)
    wages_coins_toman = models.IntegerField(default=0)
    wages_ingots_toman = models.IntegerField(default=0)
    gateway_buy_fee = models.IntegerField(default=0)

    reminder_sent = models.BooleanField(default=False)

    #deliverer
    deliverer_first_name = models.CharField(max_length=350, default="-")
    deliverer_last_name = models.CharField(max_length=350, default="-")
    deliverer_personal_code = models.CharField(max_length=5, default="-")
    deliverer_organizational_position = models.CharField(max_length=350, default="-")
    
    buyer_invoice = models.CharField(max_length=250, default="-")
    seller_invoice = models.CharField(max_length=250, default="-")

    @property
    def ToshamsiDate(self):

        return jdatetime.datetime.fromtimestamp(int(self.datetime))
        

    @property
    def OrderStatus(self):

        if self.status == 'Rejected' : return {'status':'رد شده','color':'[#FF4B3A]'}
        if self.status == 'Not_received' : return {'status':'تحویل نگرفته','color':'[#FF4B3A]'}
        if self.status == 'Received' : return {'status':'تحویل گرفته شده','color':'[#44BB1A]'}
        if self.status == 'Pending_payment' : return {'status':'در انتظار پرداخت','color':'orangeText'}
        if self.status == 'Pending_delivery' : return {'status':'در انتظار تحویل فیزیکی','color':'orangeText'}
        if self.status == 'Canceled' : return {'status':'انصراف داده شده','color':'[#FF4B3A]'}
        
        if self.status == 'Pending' : return {'status':'در انتظار بررسی','color':'orangeText'}
        if self.status == 'Connection_getway' : return {'status':'اتصال به درگاه','color':'orangeText'}

        return {'status':'نامشخص','color':'primary'} 

    @property
    def delivery_date_display(self):
        return self.delivery_date if self.delivery_date else 0
    
    def __str__(self):
        return f'{self.uname.first_name} {self.uname.last_name}'
    

class Customer_Cart_Products(models.Model):
    
    order = models.ForeignKey(Customer_Gold_Order, on_delete=models.CASCADE, related_name='order_products')
    product = models.ForeignKey(Site_Products, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)  # تعداد محصولات (برای سکه یا شمش)
    is_gold_melt = models.BooleanField(default=False)  # برای تعیین طلای آبشده

    title = models.CharField(max_length=400, default="-")
    cutie = models.IntegerField(default=0) # عیار
    grams = models.FloatField(default=0.0) # گرم
    fee = models.FloatField(default=0.0)
    type_gold = models.CharField(max_length=150, default="-")
    wages = models.FloatField(default=0.0,null=True, blank=True) # برای شمش و سکه، اجرت
    tracking_code = models.TextField(null=True, blank=True)  # برای آبشده
    desc = models.TextField(null=True, blank=True)  # برای آبشده
    price = models.FloatField(default=0.0)  # قیمت
    pure_grams = models.FloatField(default=0.0) # گرم خالص
    lab = models.CharField(max_length=350, default="-")

    @property
    def TypeOfGold(self):

        if self.type_gold == "gold1":
            return "آبشده"
        if self.type_gold == "gold2":
            return "سکه"
        if self.type_gold == "gold3":
            return "شمش"

        return "نامشخص"

class Customer_Heir(models.Model):

    uname = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='heirs')
    fname_lname = models.CharField(max_length=150, default="-")
    national_id = models.CharField(max_length=50, default="-")
    phone_number = models.CharField(max_length=50, default="-")
    assets_percentage = models.IntegerField(default=0, validators=[MaxValueValidator(100)])
    datetime = models.CharField(max_length=150, default='-')
    
    @property
    def ToshamsiDate(self):

        return jdatetime.datetime.fromtimestamp(int(self.datetime))

    def __str__(self):
        return self.fname_lname
        
        
class Customer_Heir_Log(models.Model):

    HEIR_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('checked', 'Checked'),
        ('rejected', 'Rejected'),
        ('transferred', 'Transferred')
    ]

    uname = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='heir_logs')
    master = models.ForeignKey(Master, on_delete=models.CASCADE, blank=True, null=True)
    status = models.CharField(max_length=11 ,choices=HEIR_STATUS_CHOICES, default=HEIR_STATUS_CHOICES[0])
    reject_reason = models.TextField(blank=True, null=True)
    process_datetime = models.CharField(max_length=150, default='0')
    datetime = models.CharField(max_length=150, default='-')

    def __str__(self):
        return f'{self.uname.first_name} {self.uname.last_name}'
    
    @property
    def ToshamsiDate(self):
        return jdatetime.datetime.fromtimestamp(int(self.datetime))
    
    @property
    def ProcessToshamsiDate(self):
        return jdatetime.datetime.fromtimestamp(int(self.process_datetime))
    
    @property
    def ten_days_leter(self):
        return int(self.process_datetime) + (86400 * 10)

    @property
    def log_status_to_farsi(self):
        if self.status == 'pending':
            return 'درانتظار'
        elif self.status == 'checked':
            return 'بررسی شده'
        elif self.status == 'rejected':
            return 'رد شده'
        elif self.status == 'transferred':
            return 'انتقال داده شده'
        else:
            return ''


