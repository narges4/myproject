from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.db import models
from requests import request
from exchange.models import Site_Settings
import jdatetime
import time
from master.models import Master
from datetime import datetime
from django.db.models import Sum

STATUSWALLETWITHDRAWIRT = [

    ('WaitingBankSend','در انتظار ارسال به بانک'),
    
    ('BankSend','ارسال به بانک'),
    ('Deposited','واریز شده'),
    ('Cancel','لغو شده'),
    ('CancelRequest','درخواست لغو'),
    ('Disconnect','خطا در ارسال'),
    ('UserCancel','درخواست لغو '),
]



class Wallet(models.Model):
    
    uname = models.ForeignKey('customer.Customer', on_delete=models.CASCADE)
    master = models.ForeignKey('master.Master', on_delete=models.CASCADE,null=True)
    wallet = models.CharField(max_length=50,default="-")
    amount = models.FloatField(default=0.0)
    desc = models.CharField(max_length=350,default="-")
    datetime = models.CharField(max_length=150,default="-")
    ip = models.CharField(max_length=100,default="-")
    reject_reson = models.CharField(max_length=350,default="-")
    confirmed_master = models.CharField(max_length=150,default="-")
    confirmed_datetime = models.CharField(max_length=150,default="-")
    is_verify = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=False)
    online_wallet_id = models.IntegerField(default=0)
    need_pending = models.BooleanField(default=False)
    proccess_time = models.FloatField(null=True, blank=True)
    withdraw_wallet_direct = models.IntegerField(default=0)

    #physical_delivery
    physical_delivery_pk = models.CharField(max_length=50,default="-")

    buysell_request_pk = models.CharField(max_length=50,default="-")
    refund_buysell_request_pk = models.CharField(max_length=50,default="-")

    deposit_with_id_pk = models.CharField(max_length=50,default="-")


    @property
    def ToshamsiDate(self):

        try : conf_date = jdatetime.datetime.fromtimestamp(int(self.confirmed_datetime))
        except : conf_date = 'در انتظار'

        return {
            'createDatetime':jdatetime.datetime.fromtimestamp(int(self.datetime)),
            'confirmedDatetime': conf_date,
            'ProccessTimeToshamsi':jdatetime.datetime.fromtimestamp(int(self.proccess_time)),
        }


    @property
    def ConfirmedDetail(self):

        try : return Master.objects.get(req_user=self.confirmed_master)
        except : return 'سیستم'


    def save(self,*args,**kwargs):

        if not self.pk and Wallet.objects.filter(uname=self.uname, wallet=self.wallet, amount=self.amount, desc=self.desc, datetime__gte=(time.time() - 3600)).count() != 0 :
            
            if self.desc.startswith('خرید طلای آب‌شده به شماره فاکتور') : return None
            elif self.desc.startswith('فروش طلای آب‌شده به شماره فاکتور') : return None
            elif self.desc.startswith('بابت برگشت خرید ناموفق فاکتور') : return None
            elif self.desc.startswith('بابت برگشت فروش ناموفق فاکتور') : return None
            elif self.desc.startswith('بابت تایید درخواست لغو برداشت') : return None
            elif self.desc.startswith('بابت ما به تفاوت درخواست خرید با تعیین قیمت به شناسه') : return None
            elif self.desc.startswith('بابت ما به تفاوت درخواست فروش با تعیین قیمت به شناسه') : return None
            elif self.desc.startswith('بابت لغو درخواست خرید با تعیین قیمت به شناسه') : return None
            elif self.desc.startswith('بابت لغو درخواست فروش با تعیین قیمت به شناسه') : return None
            elif self.desc.startswith('امتیاز دریافتی بابت فاکتور') : return None
            
        if self.proccess_time is None: self.proccess_time = time.time()

        return super().save(*args,**kwargs)
    
    def __str__(self):
        return str(self.id)
        

class WithdrawPaymentMethodIRT(models.Model):

    name = models.CharField(max_length=100,default="-")
    is_active = models.BooleanField(default=True)
    wage  = models.PositiveIntegerField(default=0)
    ceiling_daily = models.PositiveIntegerField(default=0)
    reseller_payment_method = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class WalletWithdrawIRT(models.Model):


  

    @property
    def ToshamsiDate(self):

        try : conf_date = jdatetime.datetime.fromtimestamp(int(self.confirmed_datetime))
        except : conf_date = 'در انتظار'

        return {
            'createDatetime':jdatetime.datetime.fromtimestamp(int(self.datetime)),
            'confirmedDatetime': conf_date
        }



    @staticmethod
    def sum_of_today_withdraw_of_user_in_today(payment_method):

        today = datetime.now()
        y = str(today.date()).split('-')
        daily = y[0] + '-' + y[1] + '-' + y[2] + ' 00:00:00'

        daily = int(datetime.strptime(daily,"%Y-%m-%d %H:%M:%S").timestamp())
        
        today_req = WalletWithdrawIRT.objects.filter(payment_method=WithdrawPaymentMethodIRT.objects.get(pk=payment_method),datetime__gte=str(daily)).exclude(is_verify=False).aggregate(Sum('amount'))
        today_req =  0 if not today_req["amount__sum"] else today_req["amount__sum"]

        res =  int(WithdrawPaymentMethodIRT.objects.get(pk=payment_method).ceiling_daily) - int(today_req)
        return  0  if res <  0 else res


class Online_Wallet(models.Model):


    @property
    def ToshamsiDate(self):

        try : conf_date = jdatetime.datetime.fromtimestamp(int(self.check_datetime))
        except : conf_date = 'در انتظار'

        return {
            'createDatetime':jdatetime.datetime.fromtimestamp(int(self.datetime)),
            'checkdDatetime': conf_date
        }


class WalletRepresentation(models.Model):
    
    @property
    def ToshamsiDate(self):

        try : conf_date = jdatetime.datetime.fromtimestamp(int(self.confirmed_datetime))
        except : conf_date = 'در انتظار'

        return {
            'createDatetime':jdatetime.datetime.fromtimestamp(int(self.datetime)),
            'confirmedDatetime': conf_date
        }


    @property
    def ConfirmedDetail(self):

        try : return Master.objects.get(req_user=self.confirmed_master)
        except : return 'سیستم'
        


class WalletOffice(models.Model):
    
    @property
    def ToshamsiDate(self):

        try : conf_date = jdatetime.datetime.fromtimestamp(int(self.confirmed_datetime))
        except : conf_date = 'در انتظار'

        return {
            'createDatetime':jdatetime.datetime.fromtimestamp(int(self.datetime)),
            'confirmedDatetime': conf_date
        }


    @property
    def ConfirmedDetail(self):

        try : return Master.objects.get(req_user=self.confirmed_master)
        except : return 'سیستم'       


class Cancel_Withdrawal_Request(models.Model):

    @property
    def ToshamsiDate(self):
        return jdatetime.datetime.fromtimestamp(int(self.datetime))
    


class Wallet_direct(models.Model):  

    @property
    def ToshamsiDate(self):
        return jdatetime.datetime.fromtimestamp(int(self.datetime))



class Wallet_Balance_log(models.Model):
    

    @property
    def ToshamsiDate(self):
        return jdatetime.datetime.fromtimestamp(int(self.date))
    


    
class DirectWallet_Detail_log(models.Model):
    
    @property
    def ToshamsiDate(self):
        return jdatetime.datetime.fromtimestamp(int(self.date))    





        