from customer.models import *
from wallet.models import *
from django.db.models import Avg, Count, Min, Sum
from currency.models import *
from exchange.func.public import *
from django.contrib.auth.models import User , Group , Permission
from decimal import Decimal
from authentication.models import *

def get_customer_balance(Id,wId, check=False):

    customer = Customer.objects.get(req_user=Id)
    count = Wallet.objects.filter(uname=customer, wallet=wId).count()

    pendding = Wallet.objects.filter(uname=customer, wallet=wId, is_verify=False, is_rejected=False, is_locked=False).aggregate(Sum('amount'))['amount__sum']
    if str(pendding) == 'None' : pendding = 0  
    if str(pendding).endswith('.0'): pendding = int(pendding)
    

    loucked = Wallet.objects.filter(uname=customer, wallet=wId, is_verify=False, is_rejected=False, is_locked=True).aggregate(Sum('amount'))['amount__sum']
    if str(loucked) == 'None' : loucked = 0  
    if str(loucked).endswith('.0'): loucked = int(loucked)
    

    availible = Wallet.objects.filter(uname=customer, wallet=wId, is_verify=True, is_rejected=False, is_locked=False).aggregate(Sum('amount'))['amount__sum']
    if str(availible) == 'None' : availible = 0  
    if str(availible).endswith('.0'): availible = int(availible)

    balance = availible - abs(loucked)

    if balance < 0 and check == False : balance = 0

    deposit = Wallet.objects.filter(uname=customer, wallet=wId, is_verify=True, is_rejected=False, is_locked=False, amount__gt=0.0).aggregate(Sum('amount'))['amount__sum']
    if str(deposit) == 'None' : deposit = 0  
    if str(deposit).endswith('.0'): deposit = int(deposit)

    withdraw = Wallet.objects.filter(uname=customer, wallet=wId, is_verify=True, is_rejected=False, is_locked=False, amount__lt=0.0).aggregate(Sum('amount'))['amount__sum']
    if str(withdraw) == 'None' : withdraw = 0  
    if str(withdraw).endswith('.0'): withdraw = abs(int(withdraw))

    return {'trans_count': count, 'deposit':deposit, 'withdraw':withdraw, 'availible':availible, 'pendding':pendding, 'louck':loucked, 'balance':round(balance,6), 'deposit':deposit, 'withdraw':withdraw}



def get_customer_CeilingRemain(Id):

    today = datetime.now()
    y = str(today.date()).split('-')
    daily = y[0] + '-' + y[1] + '-' + y[2] + ' 00:00:00'
    daily = int(datetime.strptime(daily,"%Y-%m-%d %H:%M:%S").timestamp())

    customer = Customer.objects.get(req_user=Id)
    ceiling = Customer_Ceiling.objects.get(code=1001)

    current_time = today.time()
    # بررسی بازه‌های زمانی
    last_ceiling_buy = Time_Based_Ceiling.objects.filter(type_ceiling='buy',start_time__lte=current_time, end_time__gte=current_time,act=True).last()
    last_ceiling_sell = Time_Based_Ceiling.objects.filter(type_ceiling='sell',start_time__lte=current_time, end_time__gte=current_time,act=True).last()
    last_ceiling_increas = Time_Based_Ceiling.objects.filter(type_ceiling='increas',start_time__lte=current_time, end_time__gte=current_time,act=True).last()


    today_buy_currency = Currency_BuySell_List.objects.filter(uname=customer,datetime__gte=str(daily), bill_type='buy').exclude(status="Rejected").aggregate(Sum('total_price'))
    today_buy_currency =  0 if not today_buy_currency["total_price__sum"] else today_buy_currency["total_price__sum"]

    if last_ceiling_buy : buy =  (last_ceiling_buy.amount + customer.buy) - today_buy_currency
    else : buy =  (ceiling.purchase_ceiling + customer.buy) - today_buy_currency


    today_sell_currency = Currency_BuySell_List.objects.filter(uname=customer,datetime__gte=str(daily), bill_type='sell').exclude(status="Rejected").aggregate(Sum('total_price'))
    today_sell_currency =  0 if not today_sell_currency["total_price__sum"] else today_sell_currency["total_price__sum"]

    if last_ceiling_sell : sell =  (last_ceiling_sell.amount + customer.sell) - today_sell_currency
    else : sell =  (ceiling.sales_ceiling + customer.sell) - today_sell_currency


    today_trade_currency = Currency_Swap_List.objects.filter(uname=customer,datetime__gte=str(daily),bill_type="swap").exclude(status="Rejected").aggregate(Sum('irt_price'))
    today_trade_currency =  0 if not today_trade_currency["irt_price__sum"] else today_trade_currency["irt_price__sum"]

    trade = (ceiling.conversion_ceiling + customer.trade) - today_trade_currency


    today_transfer_currency = Currency_Transfer_List.objects.filter(uname=customer,datetime__gte=str(daily),bill_type="transfer").exclude(status="Rejected").aggregate(Sum('amount'))
    today_transfer_currency =  0 if not today_transfer_currency["amount__sum"] else today_transfer_currency["amount__sum"]


    transfer = (ceiling.transmission_ceiling + customer.transfer)  - today_transfer_currency


    today_req_pay_online = Online_Wallet.objects.filter(owner=customer,datetime__gte=str(daily),is_completed=True,getway_buy=False).aggregate(Sum('amount'))
    today_req_pay_online =  0 if not today_req_pay_online["amount__sum"] else today_req_pay_online["amount__sum"]

    if last_ceiling_increas : increase  =  (last_ceiling_increas.amount)  - today_req_pay_online
    else : increase  =  (ceiling.increase_ceiling)  - today_req_pay_online


    if int(increase) < 0 :  increase = 0 
    if int(buy) < 0 :  buy = 0 
    if int(sell) < 0 :  sell = 0 
    if int(trade) < 0 :  trade = 0 
    if float(transfer) < 0 :  transfer = 0 

    return {"buy":buy,"sell":sell,"trade":trade,"transfer":transfer,"increase":increase}



def customer_sms_birthday():

    sett = Site_Settings.objects.get(pk=1)

    if sett.sms == True   and  sett.birthday_sms == True  :

        today = get_date_time()
        year = today["shamsi_date"][0:4]

        for i in Customer.objects.filter(brith_month=today["shamsi_date"][5:7],birth_day=today["shamsi_date"][8:10],req_user__startswith="customer-").exclude(send_birth_sms=year)[:25]:

            if  today["time"][:2] > "09" and today["time"][:2] < "17" :

                name = i.first_name.replace(' ','_')
                Send_Sms_Queue(phone=i.mobile,name ='MelligoldBrirthday',text=name).save()  

                i.send_birth_sms = year
                i.save()
 



        
def customer_mobile_ownership_check():

    # if Site_Settings.objects.get(code=1001).is_nationalid_mobile_check == True:

    date_time = get_date_time()['timestamp'] 
    customers = Customer.objects.filter(is_mobile_ownership=False, mobile_ownership_description_reject='', mobile_ownership_counter__lt=3, mobile_ownership_time__lte=date_time)
    if customers.exists():
        for i in customers.order_by('?')[:10]:

            customer = i
            response_data = Shahkar_APi().check_shahkar(customer.national_id, customer.mobile)

            if (response_data['is_success'] == True) and (response_data['data']['meta']['isSuccess'] == True) and (response_data['data']['data']['isMatch'] == True):

                customer.is_mobile_ownership = True
                customer.save() 

            elif (response_data['is_success'] == True) and (response_data['data']['meta']['isSuccess'] == True) and (response_data['data']['data']['isMatch'] == False):
                customer.is_mobile_ownership = False
                customer.mobile_ownership_description_reject = "مالکیت تلفن همراه با کد ملی مطابقت ندارد"
                customer.save()

            else: 
                customer.mobile_ownership_counter += 1
                customer.mobile_ownership_time = date_time + 900
                customer.save()

            time.sleep(1)








def calculate_price_or_grams(current_gold_price, wages, fee, grams):
    try:
        
        fee = Decimal(fee if fee is not None else 0)
        grams = Decimal(grams if grams is not None else 0)
        current_gold_price = Decimal(current_gold_price)
        wages = Decimal(wages)

       
        a = (current_gold_price * grams)
        final_toman = a + ((wages / Decimal(100)) * a) + ((fee / Decimal(100)) * a)
        
        final_gram = grams + ((wages / Decimal(100)) * grams) + ((fee / Decimal(100)) * grams)


        return {'final_toman': round(final_toman,2), 'final_gram': round(final_gram, 4)}
    

    except Exception as e:
        return {'final_toman': 0, 'final_gram': 0}

def calculate_product_inventory(pk):

    try:
        product_inventory = 0

        product_inventory = Site_Product_Inventory.objects.filter(product=Site_Products.objects.get(pk=pk)).aggregate(Sum('quantity'))['quantity__sum']
        if str(product_inventory) == 'None' : product_inventory = 0

        reserved_quantity = Customer_Cart_Products.objects.filter(order__status__in=['Connection_getway','Pending'], product__pk=pk).aggregate(Sum('quantity'))['quantity__sum'] or 0  # در صورت نبود داده، مقدار 0 برمی‌گردد
        available_quantity = product_inventory - reserved_quantity

        return {'product_inventory': available_quantity}
    
    except Exception as e:
        return {'product_inventory': 0}









def error_logs_access_check(customer_pk, identify, error_count, error_time, block_time, log_type=None, user_agent=None):

    def convert_time_to_timedelta(time_data): 
        time_type = time_data.get('type')
        time_value = time_data.get('value') 
        if time_type == 'hours': return timedelta(hours=time_value), f"{time_value} ساعت"
        if time_type == 'minutes': return timedelta(minutes=time_value), f"{time_value} دقیقه"
        if time_type == 'seconds': return timedelta(seconds=time_value), f"{time_value} ثانیه"
        return timedelta(0), "0"
    
    ddd1, text_error_time = convert_time_to_timedelta(error_time)
    ddd2, text_block_time = convert_time_to_timedelta(block_time)
    datetime_now = datetime.now()
    datetime_ago = datetime_now - ddd1 

    if log_type == 'ip':  
        error_logs = Customer_Requests_Logs.objects.filter(identify=identify, ip=customer_pk, user_agent=user_agent,).order_by('-pk') 
        if error_logs.exists():   
            customer_block_query = Customer_Requests_Block.objects.get_or_create(identify=identify, ip=customer_pk, user_agent=user_agent,) 
        else: return {'type': 'success', 'msg': f""}
    else:
        customer = Customer.objects.get(pk=customer_pk) 
        error_logs = Customer_Requests_Logs.objects.filter(uname=customer, identify=identify).order_by('-pk') 
        if error_logs.exists():   
            customer_block_query = Customer_Requests_Block.objects.get_or_create(identify=identify, uname=customer) 
        else: return {'type': 'success', 'msg': f""}

    last_req_datetime = datetime.fromtimestamp(float(error_logs.first().datetime))
    block_datetime = last_req_datetime + ddd2 
    
    customer_block_query = customer_block_query[0]
    customer_block = customer_block_query.status
    
    if (customer_block and block_datetime > datetime_now): 
        return {'type': 'danger', 'msg': f"به دلیل تلاش‌های ناموفق، درخواست شما به مدت {text_block_time} مسدود شد. بعداً دوباره تلاش کنید."}
    
    elif (customer_block and block_datetime < datetime_now):
        Customer_Requests_Block.objects.filter(pk=customer_block_query.pk).update(status=False) 
    
    else:  
        last_req_logs_check = error_logs.filter(datetime__gte=str(datetime_ago.timestamp()), datetime__lte=str(get_date_time()['timestamp'])) 
        if last_req_logs_check.exists() and last_req_logs_check.count() >= error_count:
            last_req_log_datetime = datetime.fromtimestamp(float(last_req_logs_check.last().datetime)) 

            if last_req_log_datetime + ddd2 > datetime_now: 
                Customer_Requests_Block.objects.filter(pk=customer_block_query.pk).update(status = True) 
                return {'type': 'danger', 'msg': f"به دلیل تلاش‌های ناموفق، درخواست شما به مدت {text_block_time} مسدود شد. بعداً دوباره تلاش کنید."}
        # else: 
        #     Customer_Requests_Block.objects.filter(pk=customer_block_query.pk).update(status=False)
    return {'type': 'success', 'msg': f""}

