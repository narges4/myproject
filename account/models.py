from __future__ import unicode_literals
from locale import currency
from exchange.func.hash import *
from django.db import models
from master.models import *
import jdatetime

ACC = [

    ('handly','handly'),
]

TRCType = [

    ('Deposit','Deposit'),
    ('Withdraw','Withdraw'),
]


class Sms_Account_Pattern(models.Model):
    
    title = models.TextField(default="-")
    
    kavenegar_text = models.TextField(default="-")
    representation_text = models.TextField(default="-")
    kavenegar_pattern = models.TextField(default="-")

    smsir_text = models.TextField(default="-")
    smsir_pattern = models.TextField(default="-")

    farazsms_text = models.TextField(default="-")
    farazsms_pattern = models.TextField(default="-")

    act = models.BooleanField(default=False)
    


class Account_Price_log(models.Model):
    
    acc = models.CharField(max_length=50,choices=ACC,default="-")
    symbol = models.CharField(max_length=50,default="-")
    modify = models.CharField(max_length=50,default="robat")
    date = models.CharField(max_length=150, default='-')
    buy = models.IntegerField(default=0)
    sell = models.IntegerField(default=0)

    @property
    def ToshamsiDate(self):
        return jdatetime.datetime.fromtimestamp(int(self.date))

    @property
    def masterDefault(self):
        try: return Master.objects.get(req_user=self.modify)
        except: pass
        return 'ربات'


class Account_Balance_log(models.Model):
    
    acc = models.CharField(max_length=50,choices=ACC,default="-")
    symbol = models.CharField(max_length=50,default="-")
    modify = models.CharField(max_length=50,default="robat")
    date = models.CharField(max_length=150, default='-')
    active_balance = models.FloatField(default=0)
    locked_balance = models.FloatField(default=0)

    @property
    def ToshamsiDate(self):
        return jdatetime.datetime.fromtimestamp(int(self.date))

    @property
    def masterDefault(self):
        try: return Master.objects.get(req_user=self.modify)
        except: pass
        return 'ربات'
    

class Account_Mellipay(models.Model):
    
    mellipay_apikey = models.TextField(default="-")
    mellipay_secretkey = models.TextField(default="-")
    last_modify = models.CharField(max_length=150, default='-')
    uname = models.CharField(max_length=50,default="-")
    code = models.IntegerField(default=1000)

    @property
    def ToshamsiDate(self):
        return jdatetime.datetime.fromtimestamp(int(self.last_modify))

    @property
    def DecryptText(self):
        return {
            'username': decrypt_message(bytes(self.mellipay_apikey[2:].replace("'", ""),'utf-8')),
            'password': decrypt_message(bytes(self.mellipay_secretkey[2:].replace("'", ""),'utf-8')),
        }


class Account_Idpay(models.Model):
    
    idpay_apikey = models.TextField(default="-")
    last_modify = models.CharField(max_length=150, default='-')
    uname = models.CharField(max_length=50,default="-")
    code = models.IntegerField(default=1000)

    @property
    def ToshamsiDate(self):
        return jdatetime.datetime.fromtimestamp(int(self.last_modify))

    @property
    def DecryptText(self):
        return {
            'username': decrypt_message(bytes(self.idpay_apikey[2:].replace("'", ""),'utf-8')),
        }


class Account_Faraboom(models.Model):

    app_key = models.TextField(default="-")
    device_id = models.TextField(default="-")
    token = models.TextField(default="-")
    is_active = models.BooleanField(default=False)
    code = models.IntegerField(default=1000)




class Send_Sms_Queue(models.Model):

    phone = models.CharField(max_length=50,default="-")
    name = models.TextField(default="-")
    text = models.TextField(default="-")
    is_send = models.BooleanField(default=False)
    representation = models.BooleanField(default=None,null=True,blank=True)


class Log_Balance_check(models.Model):

    time_start = models.CharField(max_length=150, default='-')
    time_last  = models.CharField(max_length=150, default='-')
    currency = models.ForeignKey('currency.Currency_List', on_delete=models.CASCADE)
    amount = models.FloatField(default=0.0)

    @property
    def ToshamsiDate(self):
        return {"start":jdatetime.datetime.fromtimestamp(int(self.time_start)),"last":jdatetime.datetime.fromtimestamp(int(self.time_last))}


class Send_News_Sms(models.Model):

    phone_numnber = models.CharField(max_length=50,default="-")
    is_send = models.BooleanField(default=False,null=True,blank=True)
    date = models.CharField(max_length=150, default='-')
    type_sms =  models.CharField(max_length=50, default='-')
    text = models.CharField(max_length=500, default='-')

    @property
    def ToshamsiDate(self):
        return jdatetime.datetime.fromtimestamp(int(self.date))


class Account_Shahkar(models.Model):
    
    shahkar_apikey = models.TextField(default="-")
    shahkar_secretkey = models.TextField(default="-")
    shahkar_access_token = models.TextField(default="-")
    expire = models.CharField(max_length=150, default='0')
    last_modify = models.CharField(max_length=150, default='0')
    uname = models.CharField(max_length=50,default="-")
    code = models.IntegerField(default=1000)

    @property
    def ToshamsiDate(self):
        return jdatetime.datetime.fromtimestamp(int(self.last_modify))

    @property
    def DecryptText(self):
        return {
            'username': decrypt_message(bytes(self.shahkar_apikey[2:].replace("'", ""),'utf-8')),
            'password': decrypt_message(bytes(self.shahkar_secretkey[2:].replace("'", ""),'utf-8')),
        }


class Account_Vandar(models.Model):
    
    apikey = models.TextField(default="-")
    last_modify = models.CharField(max_length=150, default='0')
    uname = models.CharField(max_length=50,default="-")
    code = models.IntegerField(default=1000)

    @property
    def ToshamsiDate(self):
        return jdatetime.datetime.fromtimestamp(int(self.last_modify))

    @property
    def DecryptText(self):
        return {
            'vandar_apikey': decrypt_message(bytes(self.apikey[2:].replace("'", ""),'utf-8')),
        }


class Vandar_Automatic_Settlement_Token(models.Model):

    creation_date = models.CharField(max_length=150, default='0')
    expiration_date = models.CharField(max_length=150, default='0')
    access_token = models.TextField(default="-")
    refresh_token = models.TextField(default="-")

    @property
    def ToshamsiDate(self):

        return {
            'creation_date': jdatetime.datetime.fromtimestamp(int(self.creation_date)),
            'expiration_date' : jdatetime.datetime.fromtimestamp(int(self.expiration_date))
        }



class Vandar_Automatic_Settlement(models.Model):

    app_name = models.TextField(default="-")
    last_modify = models.CharField(max_length=150, default='-')
    code = models.IntegerField(default=1000)
    max_amount = models.IntegerField(default=0)
    divide_to = models.IntegerField(default=0)


    @property
    def ToshamsiDate(self):
        return jdatetime.datetime.fromtimestamp(int(self.last_modify))

    @property
    def DecryptText(self):
        return {
            'app_name': decrypt_message(bytes(self.app_name[2:].replace("'", ""),'utf-8')),
           
        }        



class Account_Balance_Vandar_log(models.Model):
    
    modify = models.CharField(max_length=50,default="robat")
    date = models.CharField(max_length=150, default='-')
    active_balance = models.FloatField(default=0)


    @property
    def ToshamsiDate(self):
        return jdatetime.datetime.fromtimestamp(int(self.date))

    