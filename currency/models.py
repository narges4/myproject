from __future__ import unicode_literals
import time
# from os import symlink
# from symtable import Symbol
from django.db import models
from requests import request
from account.models import Account_Price_log, Account_Balance_log

# from exchange.func.public import get_date_time
import jdatetime
from exchange.models import Site_Dollar_log,Site_Settings
from customer.models import Customer
from datetime import datetime
from khayyam import *
from account.models import Account_Kucoin_Trans_withdraw_list
from reseller.models import AppKey
from wallet.models import Online_Wallet,Wallet_Balance_log
import json
from django.conf import settings

ACC = [

    ('handly','handly'),
]

TYPE = [
    ('buy','buy'),
    ('sell','sell'),
    ('swap','swap'),
    ('transfer','transfer'),
    ('deposite','deposite'),
    ('withdraw','withdraw'),

]

class Currency_List(models.Model):
    
    acc = models.CharField(max_length=50,choices=ACC,default="-")
    symbol = models.CharField(max_length=50,default="-")
    fa_title = models.CharField(max_length=50,default="-")
    en_title = models.CharField(max_length=50,default="-")
    about_txt = models.TextField(default="-")
    logo_name = models.TextField(default="-")
    
    buy_extera_price = models.IntegerField(default=0)
    sell_extera_price = models.IntegerField(default=0)

    buy_lower_price = models.IntegerField(default=0)
    sell_upper_price = models.IntegerField(default=0)

    lower_amount = models.FloatField(default=0.0)
    transfer_fee = models.FloatField(default=0.0)
    trade_fee = models.FloatField(default=0.0)
    acc_fee = models.FloatField(default=0.0)
    withdraw_fee = models.FloatField(default=0.0)
    profit_percent = models.FloatField(default=0.0)
    profit_percent_sell = models.FloatField(default=0.0)

    buy_fee = models.FloatField(default=0.0)
    buy_fee_lower = models.FloatField(default=0.0)
    buy_fee_upper = models.FloatField(default=0.0)

    sell_fee = models.FloatField(default=0.0)
    sell_fee_lower = models.FloatField(default=0.0)
    sell_fee_upper = models.FloatField(default=0.0)

    is_sell = models.BooleanField(default=False)
    is_buy = models.BooleanField(default=False)
    is_deposite = models.BooleanField(default=False)
    is_withdraw = models.BooleanField(default=False)
    is_trade_to = models.BooleanField(default=False)
    is_trade_from = models.BooleanField(default=False)
    is_transfer = models.BooleanField(default=False)
    is_wallet = models.BooleanField(default=False)
    is_price_update = models.BooleanField(default=False)
    is_papular = models.BooleanField(default=False)
    is_detail_update = models.BooleanField(default=False)
    is_chain = models.BooleanField(default=False)
    is_memo = models.BooleanField(default=False)
    is_investment = models.BooleanField(default=False)
    is_first_page = models.BooleanField(default=False)

    rules_buy = models.TextField(default="-")
    rules_sale = models.TextField(default="-")
    rules_transfer = models.TextField(default="-")
    rules_trade = models.TextField(default="-")
    rules_deposit = models.TextField(default="-")
    rules_harvest = models.TextField(default="-")
    is_show = models.BooleanField(default=True)

    rules_buy_reps = models.TextField(default="-")
    rules_sale_reps = models.TextField(default="-")
    rules_transfer_reps = models.TextField(default="-")
    rules_trade_reps = models.TextField(default="-")
    rules_deposit_reps = models.TextField(default="-")
    rules_harvest_reps = models.TextField(default="-")
    rules_reservation_reps = models.TextField(default="-")

    sell = models.FloatField(default=0.0)
    buy = models.FloatField(default=0.0)
    trade = models.FloatField(default=0.0)
    transfer = models.FloatField(default=0.0)
    balance_controler = models.BooleanField(default=False)
    classic_market = models.BooleanField(default=False)
    is_pack = models.BooleanField(default=False)
    pack_range = models.BooleanField(default=False)
    min_market  = models.FloatField(default=0.0)
    max_market  = models.FloatField(default=0.0)
    fee_market = models.FloatField(default=0.0)
    is_currency_gateway = models.BooleanField(default=False)
    
    # Reservation
    reservation = models.BooleanField(default=False)
    min_reservation = models.FloatField(default=0.0)
    max_reservation = models.FloatField(default=0.0)
    rules_reservation = models.TextField(default="-")
    sort = models.IntegerField(default=1000)
    is_direct = models.BooleanField(default=False)

    master_show = models.BooleanField(default=True)
    present_mcm_buy =  models.FloatField(default=0.0)
    present_mcm_sell =  models.FloatField(default=0.0)
    present_mcm_transfer =  models.FloatField(default=0.0)
    present_mcm_swap =  models.FloatField(default=0.0)
    max_buy_user =  models.FloatField(default=0.0)

    is_instant_price_default = models.BooleanField(default=False)

    rules_buy_pic = models.TextField(default="-")
    rules_sell_pic = models.TextField(default="-")
    rules_buy_title = models.CharField(max_length=300,default="-")
    rules_sell_title = models.CharField(max_length=300,default="-")
    rules_transfer_title = models.CharField(max_length=300,default="-")

    rules_buy_pic_reps = models.TextField(default="-")
    rules_sell_pic_reps = models.TextField(default="-") 
    rules_buy_title_reps = models.CharField(max_length=300,default="-")
    rules_sell_title_reps = models.CharField(max_length=300,default="-")
    rules_transfer_title_reps = models.CharField(max_length=300,default="-")

    maintenance_cost = models.FloatField(default=0)

    quick_purchase_packages_ceiling = models.FloatField(default=0)

    def __str__(self):
        return self.symbol

    @property
    def UpdateAt(self):

        try :

            last = Account_Price_log.objects.filter(symbol=self.symbol).last()
            return str(last.ToshamsiDate)

        except : return '-'


    @property
    def BuySellPrice(self):

        try :

            last = Account_Price_log.objects.filter(symbol=self.symbol).last()
            return {'buy':last.buy, 'sell':last.sell,'last_price_query':last.date}

        except : return {'buy':0, 'sell':0}

    
    @property
    def BuySellDollarPrice(self):

        try :

            last = Account_Price_log.objects.filter(symbol=self.symbol).last()
            dollar = Site_Dollar_log.objects.last().dollar_price_new
            return {'buy':round(last.buy / dollar , 2), 'sell':round(last.sell / dollar , 2)}

        except : return {'buy':0.0, 'sell':0.0}


    @property
    def Balance(self):

        try : return Account_Balance_log.objects.filter(symbol=self.symbol).last().active_balance
        except : return 0.0


    @property
    def WalletAddress(self):

        if self.is_deposite == False : return "واریز به این کیف پول غیرفعال است"

    
    @property
    def RemainBalanceCost(self):

        dollar = Site_Dollar_log.objects.last().dollar_price_new
        return {'toman':int(self.Balance * self.BuySellPrice['buy']), 'dollar':round(int(self.Balance * self.BuySellPrice['buy']) / dollar, 2)}



class Currency_Chain(models.Model):
    
    symbol = models.ForeignKey('Currency_List', on_delete=models.CASCADE)

    chain = models.CharField(max_length=50,default="-")
    wallet = models.CharField(max_length=150,default="-")
    fee = models.FloatField(default=0.0)

    is_active = models.BooleanField(default=False)
    is_default = models.BooleanField(default=False)
    minimum_amount = models.FloatField(default=0.0)
    is_direct = models.BooleanField(default=False)

    first_need_fee = models.FloatField(default=0.0)
    need_fee = models.FloatField(default=0.0)



class Currency_BuySell_List(models.Model):
    
    uname = models.ForeignKey('customer.Customer', on_delete=models.CASCADE)
    acc = models.CharField(max_length=50,choices=ACC,default="-")
    currency = models.ForeignKey('currency.Currency_List', on_delete=models.CASCADE)

    wallet_id = models.CharField(max_length=150,default="-")

    amount = models.FloatField(default=0.0)
    fee_amount = models.FloatField(default=0.0)

    fee_price = models.IntegerField(default=0)
    unit_price = models.IntegerField(default=0)
    total_price = models.IntegerField(default=0)
    total_price_difference = models.IntegerField(default=0)

    datetime = models.CharField(max_length=150,default="-")
    ip = models.CharField(max_length=100,default="-")

    bill_type = models.CharField(max_length=50,choices=TYPE,default="buy")
    status = models.CharField(max_length=50,default="Pendding")

    is_gate = models.BooleanField(default=False)
    deposite_on_wallet = models.BooleanField(default=False)

    is_checked = models.BooleanField(default=False)

    error = models.TextField(default="-")
    online_wallet_id = models.CharField(max_length=150,default="-")
    text = models.TextField(default="")
    is_reservation = models.BooleanField(default=False)



    # Direct Wallet 
    is_wallet_direct = models.BooleanField(default=False)
    wallet_address =  models.TextField(default="-")
    wallet_chain = models.CharField(max_length=50,default="-")
    wallet_direct_pk = models.IntegerField(default=0)

    need_pending = models.BooleanField(default=False)
    proccess_time = models.FloatField(null=True, blank=True)


    myproject_wallet_address = models.TextField(default="-")
    sell_payment_method = models.TextField(default="IrtWallet")
    card_withdrawal_sell = models.IntegerField(default=0)
    payment_method_withdrawal = models.IntegerField(default=0)
    day_of_week = models.CharField(default='-', max_length=150)

    maintenance_cost = models.IntegerField(default=0)

    is_daily_buysell = models.BooleanField(default=False)
    daily_buysell_type = models.CharField(max_length=150, default="-")

    is_instant_exchange = models.BooleanField(default=False)

    is_timer_buysell = models.BooleanField(default=False)
    timer_buysell_id = models.CharField(max_length=150,default="-")

    amount_gram_difference = models.FloatField(default=0.0)
    amount_irt_difference = models.FloatField(default=0.0)
    amount_type = models.CharField(max_length=50,default="gram")

    process_based_on = models.CharField(max_length=150,default="-")
    send_to_polce =  models.BooleanField(default=False)

    @property
    def ToshamsiDate(self):
        return jdatetime.datetime.fromtimestamp(int(self.datetime))

    @property
    def ProccessTimeToshamsi(self):
        return jdatetime.datetime.fromtimestamp(int(self.proccess_time))

    @property
    def ToTypeShow(self):

        if self.bill_type == 'buy' : return 'خرید از ما'
        if self.bill_type == 'sell' : return 'فروش به ما'
 

    @property
    def ToStatusShow(self):

        if self.status == 'Pendding' : return 'در انتظار'
        if self.status == 'Success' : return 'موفق'
        if self.status == 'Rejected' : return 'ناموفق'

    @property
    def TrackingOnlineWallet(self):

        try : 
            return  Online_Wallet.objects.get(pk=self.online_wallet_id).CustomerRefNum
        except : return "نامشخص"    


    @property
    def GetTransAction(self):
        try :
            trans = Account_Kucoin_Trans_withdraw_list.objects.get(kucoinId=self.hash_id).transId 
            return trans  if trans != "-" else self.hash_id      
        except : 
            return self.hash_id 
     

    def __str__(self):
        return str(self.pk)

    def save(self,*args,**kwargs):

        if not self.pk and self.bill_type == 'buy' and Currency_BuySell_List.objects.filter(uname=self.uname, online_wallet_id=self.online_wallet_id, amount=self.amount, total_price=self.total_price, bill_type='buy', datetime__gte=(time.time() - 3600)).count() != 0 :
            return None
        
        elif not self.pk and self.bill_type == 'sell' and Currency_BuySell_List.objects.filter(uname=self.uname, amount=self.amount, total_price=self.total_price, bill_type='sell', datetime__gte=(time.time() - 60)).count() != 0 :
            return None
            
        if self.proccess_time is None : self.proccess_time = time.time()

        return super().save(*args,**kwargs)

    @property
    def json_bill_list(self):
        ToshamsiDate = jdatetime.datetime.fromtimestamp(int(self.datetime))
        site_setting = Site_Settings.objects.get(code=1001)

        if self.bill_type == 'buy':
            ToTypeShow = 'خرید از ما'
            buyer = self.uname.FullName
            seller = site_setting.title
        elif self.bill_type == 'sell':
            ToTypeShow = 'فروش به ما'
            buyer = site_setting.title
            seller = self.uname.FullName
        else:
            ToTypeShow = 'نامشخص'
            buyer = None
            seller = None

        ProccessTimeToshamsi = f'فاکتور شما در {self.ProccessTimeToshamsi}  توسط ربات مورد بررسی قرار خواهد گرفت' if self.need_pending else 'در انتظار'

        return {
            'pk': self.pk,
            'uname': str(self.uname),
            'status': self.status,
            'ToTypeShow': ToTypeShow,
            'bill_type': self.bill_type,
            'ToshamsiDate': ToshamsiDate.strftime('%Y-%m-%d %H:%M:%S'),
            'ProccessTimeToshamsi': ProccessTimeToshamsi,
            'fa_title':  self.currency.fa_title,
            'amount': ('{:.{dp}f}'.format(float(self.amount), dp=4)).rstrip('0').rstrip('.') ,
            'fee_amount': ('{:.{dp}f}'.format(float(self.fee_amount), dp=4)).rstrip('0').rstrip('.') ,
            'unit_price': self.unit_price,
            'total_price': self.total_price,
            'text': "" if self.text == "-"  or  self.text == "" or self.text ==  None else self.text,
            'buyer': buyer,  
            'seller': seller,
            'fee_irt': f'{self.fee_price:,}',
            'ip': self.ip,
            'maintenance_cost': f'{int(self.maintenance_cost):,}',
            'signature':f'{settings.STATIC_URL}master/theme-01/assets/media/image/emza.png'
            
        }


class Currency_Swap_List(models.Model):

    uname = models.ForeignKey('customer.Customer', on_delete=models.CASCADE)

    first_currency = models.ForeignKey('currency.Currency_List', on_delete=models.CASCADE)
    second_currency = models.CharField(max_length=50, default="-")

    wallet_id = models.CharField(max_length=150,default="-")

    amount = models.FloatField(default=0.0)
    fee_amount = models.FloatField(default=0.0)
    recieve_amount = models.FloatField(default=0.0)

    sell_price = models.IntegerField(default=0)
    buy_price = models.IntegerField(default=0)

    datetime = models.CharField(max_length=150,default="-")
    ip = models.CharField(max_length=100,default="-")

    bill_type = models.CharField(max_length=50,choices=TYPE,default="swap")
    status = models.CharField(max_length=50,default="Pendding")

    is_checked = models.BooleanField(default=False)
    irt_price = models.IntegerField(default=0)

    error = models.TextField(default="-")
    

    @property
    def ToshamsiDate(self):
        return jdatetime.datetime.fromtimestamp(int(self.datetime))

    @property
    def SwapAsset(self):
        return Currency_List.objects.get(symbol=self.second_currency)

    @property
    def ToTypeShow(self):
        return 'تبدیل'

    @property
    def ToStatusShow(self):

        if self.status == 'Pendding' : return 'در انتظار'
        if self.status == 'Success' : return 'موفق'
        if self.status == 'Rejected' : return 'ناموفق'

    def __str__(self):
        return str(self.pk)



class Currency_Transfer_List(models.Model):

    uname = models.ForeignKey('customer.Customer', on_delete=models.CASCADE,null=True, related_name="currency_transfer")
    uname_transfer = models.ForeignKey('customer.Customer', on_delete=models.CASCADE,null=True, related_name="user_transfer")
    reciever_id = models.CharField(max_length=150,default="-")

    currency = models.ForeignKey('currency.Currency_List', on_delete=models.CASCADE)

    wallet_id = models.CharField(max_length=150,default="-")

    amount = models.FloatField(default=0.0)
    fee_amount = models.FloatField(default=0.0)

    datetime = models.CharField(max_length=150,default="-")
    ip = models.CharField(max_length=100,default="-")

    bill_type = models.CharField(max_length=50,choices=TYPE,default="transfer")
    status = models.CharField(max_length=50,default="Pendding")

    is_checked = models.BooleanField(default=False)
    irt_price = models.IntegerField(default=0)
    
    error = models.TextField(default="-")
    

    @property
    def ToshamsiDate(self):
        try :return jdatetime.datetime.fromtimestamp(int(self.datetime))
        except : return '-'

    @property
    def ReciverDetail(self):
        try : return Customer.objects.get(uuid_code=self.reciever_id)
        except : pass

    @property
    def ToTypeShow(self):
        return 'انتقال'

    @property
    def ToStatusShow(self):

        if self.status == 'Pendding' : return 'در انتظار'
        if self.status == 'Success' : return 'موفق'
        if self.status == 'Rejected' : return 'ناموفق'

    def __str__(self):
        return str(self.pk)


class Currency_depositeWithdraw_List(models.Model):

    uname = models.ForeignKey('customer.Customer', on_delete=models.CASCADE)
    acc = models.CharField(max_length=50,choices=ACC,default="-")
    currency = models.ForeignKey('currency.Currency_List', on_delete=models.CASCADE)
    gateway = models.ForeignKey('exchange.Geteway_Currency_request_personal', on_delete=models.CASCADE,null=True,blank=True)

    wallet_id = models.CharField(max_length=150,default="-")

    amount = models.FloatField(default=0.0)
    fee_amount = models.FloatField(default=0.0)

    datetime = models.CharField(max_length=150,default="-")
    ip = models.CharField(max_length=100,default="-")

    bill_type = models.CharField(max_length=50,choices=TYPE,default="withdraw")
    status = models.CharField(max_length=50,default="Pendding")

    deposite_on_wallet = models.BooleanField(default=False)
    from_gateway = models.BooleanField(default=False)

    is_checked = models.BooleanField(default=False)

    error = models.TextField(default="-")
    wallet_return = models.BooleanField(default=False)
    
    name_deposite = models.CharField(max_length=50,default="-")
    phone_number_deposite = models.CharField(max_length=50,default="-")
    text_deposite = models.TextField(default="-",null=True)
    total_price = models.IntegerField(default=0)
    wallet_direct = models.ForeignKey('wallet.Wallet_direct', on_delete=models.CASCADE,null=True,blank=True)
    transaction_id = models.IntegerField(default=0)

    @property
    def ToshamsiDate(self):
        return jdatetime.datetime.fromtimestamp(int(self.datetime))

    @property
    def ToTypeShow(self):

        if self.bill_type == 'withdraw' : return 'برداشت'
        if self.bill_type == 'deposite' : return 'واریز'

    @property
    def ToStatusShow(self):

        if self.status == 'Pendding' : return 'در انتظار'
        if self.status == 'Success' : return 'موفق'
        if self.status == 'Rejected' : return 'ناموفق'
        if self.status == 'GateWay' : return 'معلق'


    def __str__(self):
        return str(self.pk)


class Account_Wallet_Access(models.Model):

    uname = models.ForeignKey('customer.Customer', on_delete=models.CASCADE)
    title = models.CharField(max_length=100, default='-')
    currency = models.ForeignKey('Currency_List', on_delete=models.CASCADE)
    address_wallet =  models.TextField(default="-")


class Quick_Purchase_Package(models.Model):
    UNIT_CHOICES = [
        ('gram', 'گرم'),
        ('sot', 'سوت'),
    ]

    uname = models.ForeignKey('customer.Customer', on_delete=models.CASCADE)
    show_amount = models.FloatField(default=0.0)
    amount = models.FloatField(default=0.0)
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES)
    sort = models.IntegerField(default=0)
    act = models.BooleanField(default=False)
    datetime = models.CharField(max_length=150,default="-")

    def __str__(self):
        return f'{self.amount} {self.unit}'
    
    @property
    def ToshamsiDate(self):
        return jdatetime.datetime.fromtimestamp(int(self.datetime))
    

    @property
    def to_farsi_unit(self):
        if self.unit == 'gram':
            return 'گرم'
        else:
            return 'سوت'
        




class Currency_BuySell_Custom_Price(models.Model):
    
    uname = models.ForeignKey('customer.Customer', on_delete=models.CASCADE)
    acc = models.CharField(max_length=50,choices=ACC,default="-")
    currency = models.ForeignKey('currency.Currency_List', on_delete=models.CASCADE)

    wallet_id = models.CharField(max_length=150,default="-")

    amount = models.FloatField(default=0.0)
    fee_amount = models.FloatField(default=0.0)
    maintenance_cost = models.FloatField(default=0)


    fee_price = models.FloatField(default=0.0)
    unit_price = models.IntegerField(default=0)
    total_price = models.FloatField(default=0.0)
    orginal_total_price = models.FloatField(default=0.0)

    datetime = models.CharField(max_length=150,default="-")
    ip = models.CharField(max_length=100,default="-")

    bill_type = models.CharField(max_length=50,choices=TYPE,default="buy")
    status = models.CharField(max_length=50,default="Pendding")

    is_checked = models.BooleanField(default=False)

    error = models.TextField(default="-")

    proccess_time = models.IntegerField(default=0)
    sell_payment_method = models.TextField(default="IrtWallet")

    desired_price = models.IntegerField(default=0)
    desired_time = models.CharField(max_length=150,default="-")
    process_based_on = models.CharField(max_length=150,default="-")
    is_canceled = models.BooleanField(default=False)
    
    amount_type = models.CharField(max_length=50,default="gram")

    is_gate = models.BooleanField(default=False)


    online_wallet_id = models.CharField(max_length=150,default="-")
    text = models.TextField(default="")


    need_pending = models.BooleanField(default=False)
    card_withdrawal_sell = models.IntegerField(default=0)
    payment_method_withdrawal = models.IntegerField(default=0)
  
    transaction_id = models.CharField(max_length=150,default="-")
    irt_amount = models.FloatField(default=0.0)

    total_price_difference = models.IntegerField(default=0)

    @property
    def ToshamsiDate(self):
        return jdatetime.datetime.fromtimestamp(int(self.datetime))

    @property
    def ProccessTimeToshamsi(self):
        return jdatetime.datetime.fromtimestamp(int(self.proccess_time))

    @property
    def ToTypeShow(self):

        if self.bill_type == 'buy' : return 'خرید'
        if self.bill_type == 'sell' : return 'فروش'


    @property
    def ToStatusShow(self):

        if self.status == 'Pendding' : return 'در انتظار'
        if self.status == 'Success' : return 'موفق'
        if self.status == 'Rejected' : return 'ناموفق'
        if self.status == 'Canceled' : return 'لغو شده'
        if self.status == 'Connection_getway' : return 'اتصال به درگاه'

    @property
    def ToshamsiDate_desired(self):
        if self.desired_time == '-' :
            return self.desired_time
        return jdatetime.datetime.fromtimestamp(int(self.desired_time))

     
    def __str__(self):
        return str(self.pk)

    def save(self,*args,**kwargs):
        if self.proccess_time is None:
            self.proccess_time = time.time()
        return super().save(*args,**kwargs)


    @property
    def process_based(self):

        if self.process_based_on == 'price' : return 'براساس قیمت'
        if self.process_based_on == 'datetime' : return 'براساس زمان'


    @property
    def json_bill_list(self):

        ToshamsiDate = jdatetime.datetime.fromtimestamp(int(self.datetime))

        if self.desired_time and self.desired_time != '-':
            formatted_date = jdatetime.datetime.fromtimestamp(int(self.desired_time))
            ToshamsiDate_desired = formatted_date.strftime('%Y-%m-%d %H:%M:%S')
        else:
            ToshamsiDate_desired = '-'

        site_setting = Site_Settings.objects.get(code=1001)

        if self.bill_type == 'buy':
            ToTypeShow = 'خرید'
            buyer = self.uname.FullName
            seller = site_setting.title
        elif self.bill_type == 'sell':
            ToTypeShow = 'فروش'
            buyer = site_setting.title
            seller = self.uname.FullName
        else:
            ToTypeShow = 'نامشخص'
            buyer = None
            seller = None

        ProccessTimeToshamsi = f'فاکتور شما در {self.ProccessTimeToshamsi}  توسط ربات مورد بررسی قرار خواهد گرفت' if self.need_pending else 'در انتظار'

        if self.amount_type == 'gram':
            amount = self.amount
        else :
            amount = self.irt_amount

        return {
            'pk': self.pk,
            'uname': str(self.uname),
            'status': self.status,
            'ToStatusShow': self.ToStatusShow,
            'ToTypeShow': ToTypeShow,
            'bill_type': self.bill_type,
            'ToshamsiDate': ToshamsiDate.strftime('%Y-%m-%d %H:%M:%S'),
            'datetime': ToshamsiDate_desired,
            'ProccessTimeToshamsi': ProccessTimeToshamsi,
            'fa_title':  self.currency.fa_title,
            'amount': amount,
            'fee_amount': ('{:.{dp}f}'.format(float(self.fee_amount), dp=4)).rstrip('0').rstrip('.') ,
            'unit_price': self.unit_price,
            'total_price': self.total_price,
            # 'text': "" if self.text == "-"  or  self.text == "" or self.text ==  None else self.text,
            'buyer': buyer,  
            'seller': seller,
            'fee_irt': f'{self.fee_price:,}',
            'ip': self.ip,
            'signature':'/static/master/theme-01/assets/media/image/emza.png',
            'transaction_id':self.transaction_id,
            'amount_type':self.amount_type,
            'error':self.error
            
        }



class Daily_Buysell(models.Model):
    BILL_TYPES = [
        ('buy', 'Buy'),
        ('sell', 'Sell'),
    ]
    UNIT_TYPES = [
        ('fixed_w', 'Fixed Weight'),
        ('fixed_p', 'Fixed Price'),
        ('wallet', 'Wallet Amount'),
    ]
    PAYMENT_METHOD_TYPES = [
        ('DirectWithdrawal', 'Direct Withdraw'),
        ('IrtWallet', 'IRT Wallet')
    ]

    uname = models.ForeignKey('customer.Customer', on_delete=models.CASCADE, related_name='daily_bs_requests')

    bill_type = models.CharField(max_length=4, choices=BILL_TYPES, default='buy')
    unit_type = models.CharField(max_length=7, choices=UNIT_TYPES, default='fixed_p')

    payment_method = models.CharField(max_length=16, default='-', choices=PAYMENT_METHOD_TYPES)

    withdraw_method_pk = models.IntegerField(default=0)
    withdraw_card_pk = models.IntegerField(default=0)

    amount = models.FloatField(default=0)
    hour = models.CharField(max_length=2, default='-')
    act = models.BooleanField(default=True)
    is_show = models.BooleanField(default=True)
    datetime = models.CharField(max_length=150,default="-")
    last_time_date = models.CharField(max_length=150,default="-")
    process_time = models.IntegerField(default=0)

    @property
    def ToshamsiDate(self):
        return jdatetime.datetime.fromtimestamp(int(self.datetime))
    
    @property
    def ProcessTimeToshamsiDate(self):
        return jdatetime.datetime.fromtimestamp(int(self.process_time))

    @property
    def time_of_day(self):
        if int(self.hour) < 10:
            return f'{str(self.hour)[1]}:00'
        else:
            return f'{self.hour}:00'
    
    @property
    def bill_to_farsi(self):
        if self.bill_type == 'buy':
            return 'خرید'
        else:
            return 'فروش'
    
    @property
    def currency_to_farsi(self):
        if self.unit_type == 'fixed_p':
            return 'قیمت ثابت'
        elif self.unit_type == 'wallet' and self.bill_type == 'buy':
            return 'موجودی کل کیف پول'
        elif self.unit_type == 'wallet' and self.bill_type == 'sell':
            return 'موجودی کل صندوق طلا'
        else:
            return 'وزن ثابت'
        
    @property
    def json_buysell(self):

        return json.dumps(
            {
            'pk': self.pk,
            'bill_type': self.bill_type,
            'unit_type': self.unit_type,
            'amount': self.amount,
            'hour': self.time_of_day,
            'act': self.act
        }
        )



class Daily_Shopping_hours(models.Model):
    hour = models.CharField(max_length=2, default='-')
    act = models.BooleanField(default=False)
    datetime = models.CharField(max_length=150,default="-")

    def __str__(self):
        return self.hour

    @property
    def ToshamsiDate(self):
        return jdatetime.datetime.fromtimestamp(int(self.datetime))
    
    @property
    def time_of_day(self):
        if int(self.hour) < 10:
            return f'{str(self.hour)[1]}:00'
        else:
            return f'{self.hour}:00'
        

class Robot_Log(models.Model):
    robot = models.CharField(max_length=150, default='-')
    uname = models.ForeignKey('customer.Customer', on_delete=models.CASCADE, blank=True, null=True)
    description = models.CharField(max_length=150, default='-')
    datetime = models.CharField(max_length=150, default='-')

    @property
    def ToshamsiDate(self):
        return jdatetime.datetime.fromtimestamp(int(self.datetime))
    