
from account.models import *
from currency.models import *
from exchange.models import *
import customer
from exchange.func.public import *
from customer.func.public import *
from wallet.models import *
import datetime
import requests
import re 
from django.db.models import Q
from django.db import transaction
import time as timee
from django.db.models import Count, F, ExpressionWrapper, fields, Value, Subquery, OuterRef
from django.db.models.functions import Coalesce, Now, Cast
import jdatetime


def handly_buy():

    setting = Site_Settings.objects.get(code=1001)


    for counter in Currency_BuySell_List.objects.filter(status='Pendding', bill_type='buy', acc='handly',is_checked=False, proccess_time__lte=get_date_time()['timestamp']).order_by('pk')[:15]:
        
        bill = Currency_BuySell_List.objects.get(status='Pendding', pk=counter.pk)
        customer = Customer.objects.get(req_user=bill.uname.req_user)

        if bill.is_timer_buysell == True :

            try:
                timed_request = Currency_BuySell_Custom_Price.objects.get(pk=bill.timer_buysell_id,status='Pendding')
            except :
                timed_request.status = 'Rejected'
                timed_request.error = "درخواست فاکتور موردنظر یافت نشد"
                timed_request.save()

                bill.is_checked = True
                bill.status = 'Rejected'
                bill.error = "Invoice request not found"
                bill.save()

                break


        if customer.status == 'Suspended' :

            bill.is_checked = True
            bill.status = 'Rejected'
            bill.error = "Account Suspended"
            bill.save()

            break

        if bill.is_checked == False and bill.bill_type == 'buy' and bill.status == 'Pendding' :

            totalPrice = round((bill.amount * bill.unit_price) + bill.fee_price + bill.maintenance_cost)
           

            if bill.is_gate == False:

                try : 
                    
                    W = Wallet.objects.get(pk=bill.wallet_id)
                    wallet_amount = int(abs(W.amount))

                    if Currency_BuySell_List.objects.filter(wallet_id=W.pk).count() != 1 :

                        bill.is_checked = True
                        bill.status = 'Rejected'
                        bill.error = "transAction Dublicated"
                        bill.save()

                        if bill.is_timer_buysell == True :
                            timed_request.status = 'Rejected'
                            timed_request.error = "تراکنش تکراری می باشد"
                            timed_request.save()

                        break
                    
                except : 

                    bill.is_checked = True
                    bill.status = 'Rejected'
                    bill.error = "transaction not found"
                    bill.save()

                    if bill.is_timer_buysell == True :
                        
                        timed_request.status = 'Rejected'
                        timed_request.error = "تراکنش یافت نشد"
                        timed_request.save()

                    break
            
            else : 
                
                try : 
                    
                    OW = Online_Wallet.objects.get(pk=bill.online_wallet_id, status=100)
                    wallet_amount = int(OW.transactionAmount) / 10

                    if Currency_BuySell_List.objects.filter(online_wallet_id=OW.pk).count() != 1 :

                        bill.is_checked = True
                        bill.status = 'Rejected'
                        bill.error = "transAction Dublicated"
                        bill.save()

                        if bill.is_timer_buysell == True :
                            timed_request.status = 'Rejected'
                            timed_request.error = "تراکنش تکراری می باشد"
                            timed_request.save()

                        break
                    
                except : 
                    
                    bill.is_checked = True
                    bill.status = 'Rejected'
                    bill.error = "transAction Not Match"
                    bill.save()

                    if bill.is_timer_buysell == True :
                        timed_request.status = 'Rejected'
                        timed_request.error = "تراکنش مطابقت ندارد"
                        timed_request.save()

                    break



            # if bill.is_daily_buysell            

            if int(get_customer_balance(bill.uname.req_user,'IRT', True)["balance"]) < 0 :

                bill.is_checked = True
                bill.status = 'Rejected'
                bill.error = "negetive balance"
                bill.save()

                if bill.is_timer_buysell == True :
                    timed_request.status = 'Rejected'
                    timed_request.error = "موجودی ناکافی است "
                    timed_request.save() 
                break

            
            bill_total_price = bill.total_price   
            if bill.amount_irt_difference  < 0 : bill_total_price = bill.total_price + abs(bill.amount_irt_difference) 

                  
            if (totalPrice != bill.total_price and bill.is_timer_buysell == False and bill.is_daily_buysell == False )  or  (bill.is_timer_buysell == True and (totalPrice != bill_total_price))    :
          
                bill.is_checked = True
                bill.status = 'Rejected'
                bill.error = "total price not match"
                bill.save()

                if bill.is_timer_buysell == True :
                    timed_request.status = 'Rejected'
                    timed_request.error = f"عدم تطابق قیمت"
                    timed_request.save()

                Wallet(
            
                    uname = Customer.objects.get(req_user=bill.uname.req_user), 
                    wallet = 'IRT', 
                    desc = f'بابت برگشت خرید ناموفق فاکتور : {bill.pk}',
                    amount = wallet_amount, 
                    datetime = get_date_time()['timestamp'] ,
                    confirmed_datetime = get_date_time()['timestamp'] ,
                    ip = '0.0.0.0', 
                    is_verify = False,
            
                ).save()


                if not customer.req_user.startswith('customer-') :
                    Send_Sms_Queue(phone=customer.mobile,name ='MelliGoldReturn2Wallet',text=f'{wallet_amount}',representation=True ).save()
                else : Send_Sms_Queue(phone=customer.mobile,name ='MelliGoldReturn2Wallet',text=f'{wallet_amount}' ).save()

                break

        


            
            bill_total_price = bill.total_price      
            if bill.amount_irt_difference > 0 and bill.process_based_on == "price" :
                bill_total_price = bill.total_price + bill.amount_irt_difference
        
            

            if (bill.total_price != wallet_amount and bill.is_timer_buysell == False and bill.is_daily_buysell == False )  or  (bill.is_timer_buysell == True and (wallet_amount != (bill_total_price))  )  :
                    
              
                # try:
                #     timed_request = Currency_BuySell_Custom_Price.objects.get(pk=bill.timer_buysell_id,status='Pendding')
                #     timed_request.status = 'Rejected'
                #     timed_request.error = f"مبلغ فاکتور {bill.pk} با مبلغ پرداخت شده مطابقت ندارد"
                #     timed_request.save()
                # except:
                #     pass

                if bill.is_timer_buysell == True :

                    timed_request.status = 'Rejected'
                    timed_request.error = f"مبلغ فاکتور {bill.pk} با مبلغ پرداخت شده مطابقت ندارد"
                    timed_request.save()


                bill.is_checked = True
                bill.status = 'Rejected'
                bill.error = f"bill and paid not match {totalPrice} {bill.total_price}"
                bill.save()

                Wallet(
            
                    uname = Customer.objects.get(req_user=bill.uname.req_user), 
                    wallet = 'IRT', 
                    desc = f'بابت برگشت خرید ناموفق فاکتور : {bill.pk}',
                    amount = wallet_amount, 
                    datetime = get_date_time()['timestamp'] ,
                    confirmed_datetime = get_date_time()['timestamp'] ,
                    ip = '0.0.0.0', 
                    is_verify = False,
            
                ).save()

                if not customer.req_user.startswith('customer-') :
                    Send_Sms_Queue(phone=customer.mobile,name ='MelliGoldReturn2Wallet',text=f'{wallet_amount}',representation=True ).save()
                else : Send_Sms_Queue(phone=customer.mobile,name ='MelliGoldReturn2Wallet',text=f'{wallet_amount}' ).save()

                break

               
            

            if not (bill.is_daily_buysell or bill.is_timer_buysell):
            
                if bill.unit_price < bill.currency.BuySellPrice['buy'] and abs(bill.currency.BuySellPrice['buy'] - bill.unit_price) > (bill.unit_price / 100) and bill.need_pending == False :

                    bill.is_checked = True
                    bill.status = 'Rejected'
                    bill.error = "bill and melligold amount not match"
                    bill.save()

       

                    Wallet(
                
                        uname = Customer.objects.get(req_user=bill.uname.req_user), 
                        wallet = 'IRT', 
                        desc = f'بابت برگشت خرید ناموفق فاکتور : {bill.pk}',
                        amount = wallet_amount, 
                        datetime = get_date_time()['timestamp'] ,
                        confirmed_datetime = get_date_time()['timestamp'] ,
                        ip = '0.0.0.0', 
                        is_verify = False,
                
                    ).save()

                    if not customer.req_user.startswith('customer-') :
                        Send_Sms_Queue(phone=customer.mobile,name ='MelliGoldReturn2Wallet',text=f'{wallet_amount}',representation=True ).save()
                    else : Send_Sms_Queue(phone=customer.mobile,name ='MelliGoldReturn2Wallet',text=f'{wallet_amount}' ).save()


                    break

            if int(get_customer_balance(bill.uname.req_user,'IRT', True)["balance"]) < 0 :

                bill.is_checked = True
                bill.status = 'Rejected'
                bill.error = "negetive balance"
                bill.save()

                if bill.is_timer_buysell == True :

                    timed_request.status = 'Rejected'
                    timed_request.error = "موجودی ناکافی است"
                    timed_request.save()

                Wallet(
            
                    uname = Customer.objects.get(req_user=bill.uname.req_user), 
                    wallet = 'IRT', 
                    desc = f'بابت برگشت خرید ناموفق فاکتور : {bill.pk}',
                    amount = wallet_amount, 
                    datetime = get_date_time()['timestamp'] ,
                    confirmed_datetime = get_date_time()['timestamp'] ,
                    ip = '0.0.0.0', 
                    is_verify = False,
            
                ).save()

                if not customer.req_user.startswith('customer-') :
                    Send_Sms_Queue(phone=customer.mobile,name ='MelliGoldReturn2Wallet',text=f'{wallet_amount}',representation=True ).save()
                else : Send_Sms_Queue(phone=customer.mobile,name ='MelliGoldReturn2Wallet',text=f'{wallet_amount}' ).save()

        

                break

            if bill.is_checked == False and bill.bill_type == 'buy' and bill.status == 'Pendding' :


                bill.is_checked = True
                bill.status = 'Success'
                bill.save()

                if bill.is_timer_buysell == True :


                    timed_request.status = 'Success'

                    if totalPrice != bill.total_price :
                        bill.total_price_difference = bill.total_price - totalPrice 
                        bill.save()


                    if timed_request.process_based_on == 'price' and bill.amount_irt_difference > 0 :

                        Wallet(
            
                            uname = Customer.objects.get(req_user=bill.uname.req_user), 
                            wallet = 'IRT', 
                            desc = f'بابت ما به تفاوت درخواست خرید با تعیین قیمت به شناسه : {bill.timer_buysell_id}',
                            amount = bill.amount_irt_difference, 
                            datetime = get_date_time()['timestamp'] ,
                            confirmed_datetime = get_date_time()['timestamp'] ,
                            ip = '0.0.0.0', 
                            is_verify = False,
                    
                        ).save()
                        

                    timed_request.save()

                customer = Customer.objects.get(req_user=bill.uname.req_user)

                if customer.hour_to_pending > 0 :
                    if Currency_BuySell_List.objects.filter(is_gate=True,total_price__gte=1000000,uname=customer,need_pending=True).count() > 0 :
                        
                        customer.hour_to_pending = 0
                        customer.save()

                
                Wallet(
            
                    uname = customer, 
                    wallet = bill.currency.symbol, 
                    desc = f'خرید {bill.currency.fa_title} به شماره فاکتور : {bill.pk}',
                    amount = bill.amount, 
                    datetime = get_date_time()['timestamp']   if bill.is_timer_buysell == False and bill.is_daily_buysell == False else bill.datetime,
                    confirmed_datetime = get_date_time()['timestamp'] ,
                    ip = '0.0.0.0', 
                    is_verify = True,
            
                ).save()
                # try :
                    
                #     Account_Balance_log(
                #         acc = bill.acc,
                #         symbol = bill.currency.symbol,
                #         date = get_date_time()['timestamp'],
                #         active_balance = round(float(bill.currency.Balance),2) - round(float(bill.amount),2),
                #         locked_balance = float(0)
                #     ).save() 
                
                # except : pass
                
                if Currency_BuySell_List.objects.filter(uname=customer, bill_type='buy').count() == 1:
                    if not customer.req_user.startswith('customer-') :
                        Send_Sms_Queue(phone=customer.mobile,name ='SpecialNum',text=setting.first_purchase_sms,representation=True).save()
                    else : 
                        Send_Sms_Queue(phone=customer.mobile,name ='SpecialNum',text=setting.first_purchase_sms).save()

                gift_user(customer.req_user)


                if customer.up_referral_link != "-" :

                    if customer.req_user.startswith("customer-"):
                        amount = round((bill.total_price * bill.currency.profit_percent) / 100, 0)
                    else :    
                        pass
                    
                    # ProfitAssigne(customer.up_referral_link, amount, bill.pk)


                    if  customer.reseller_upper_link != "-" : 

                        try :

                            pass
                        except : pass 




                elif customer.operator != None :  

                    # ProfitAssigneRepresentative(customer.pk,bill.total_price, bill.pk)
                    pass

                customer.buy_price += bill.total_price
                customer.last_buysell_time = get_date_time()['timestamp']
                customer.save()
                
                if bill.currency.symbol != "MGR" :
                    # customer_get_ruby(customer,bill.total_price,bill.currency.present_mcm_buy,bill.pk)
                    pass

                
                arz = Currency_List.objects.get(symbol=bill.currency.symbol)
                arz.buy += bill.total_price
                arz.save()

                # last = Account_Balance_log.objects.filter(acc='handly', symbol='ZAR').last().active_balance
                # Account_Balance_log(acc='handly', symbol=bill.currency.symbol, date=get_date_time()['timestamp'], active_balance=(last - bill.amount), locked_balance=0.0).save()



def handly_sell():



    for counter in Currency_BuySell_List.objects.filter(status='Pendding', bill_type='sell', acc='handly',is_checked=False).order_by('pk')[:15]:
        
        bill = Currency_BuySell_List.objects.get(status='Pendding', pk=counter.pk)

        if bill.is_timer_buysell == True :

            try:
                timed_request = Currency_BuySell_Custom_Price.objects.get(pk=bill.timer_buysell_id,status='Pendding')
            except :
                timed_request.status = 'Rejected'
                timed_request.error = "درخواستی فاکتور موردنظر یافت نشد"
                timed_request.save()

                bill.is_checked = True
                bill.status = 'Rejected'
                bill.error = "Invoice request not found"
                bill.save()

                break

        if bill.is_checked == False and bill.bill_type == 'sell' and bill.status == 'Pendding' :

            if float(bill.currency.sell_fee) != float(0) :

                f = ((bill.currency.sell_fee * bill.amount) / 100)
                if f < bill.currency.sell_fee_lower : fee = bill.currency.sell_fee_lower
                elif f > bill.currency.sell_fee_upper : fee = bill.currency.sell_fee_upper
                else : fee = f
                fee_price = round(fee * bill.unit_price , 0)

            else:

                fee = 0
                fee_price = 0


            if  bill.sell_payment_method == "DirectWithdrawal":   

                try:
                    withdraw_method = WithdrawPaymentMethodIRT.objects.get(pk=bill.payment_method_withdrawal)
                except: 

                    bill.is_checked = True
                    bill.status = 'Rejected'
                    bill.error = "transaction not found"
                    bill.save()

                    if bill.is_timer_buysell == True :
                        timed_request.status = 'Rejected'
                        timed_request.error = "تراکنش یافت نشد"
                        timed_request.save()

                    break

                totalPrice = round((bill.amount * bill.unit_price) -  bill.fee_price) - withdraw_method.wage

            else : 
                totalPrice = round((bill.amount * bill.unit_price) -  bill.fee_price)  


            try : wallet_amount = float(abs(Wallet.objects.get(pk=bill.wallet_id).amount))
            except : 

                bill.is_checked = True
                bill.status = 'Rejected'
                bill.error = "transaction not found"
                bill.save()

                if bill.is_timer_buysell == True :

                    timed_request.status = 'Rejected'
                    timed_request.error = "تراکنش یافت نشد"
                    timed_request.save()

                break
            

            if totalPrice != bill.total_price :
                    
                # if (bill.is_timer_buysell == False and bill.is_daily_buysell == False)  or  (bill.is_timer_buysell == True and abs(totalPrice - bill.total_price) > 100 ) or (bill.is_daily_buysell == True and abs(totalPrice - bill.total_price) > 100 ) :
            
                bill.is_checked = True
                bill.status = 'Rejected'
                bill.error = "price not match"
                bill.save()

                if bill.is_timer_buysell == True :

                    timed_request.status = 'Rejected'
                    timed_request.error = "عدم تطابق قیمت"
                    timed_request.save()

                Wallet(
            
                    uname = Customer.objects.get(req_user=bill.uname.req_user), 
                    wallet = bill.currency.symbol, 
                    desc = f'بابت برگشت فروش ناموفق فاکتور : {bill.pk}',
                    amount = wallet_amount, 
                    datetime = get_date_time()['timestamp'] ,
                    confirmed_datetime = get_date_time()['timestamp'] ,
                    ip = '0.0.0.0', 
                    is_verify = False,
            
                ).save()

                break

            bill_amount = bill.amount + bill.amount_gram_difference

            if (bill.amount != wallet_amount and  bill.is_timer_buysell == False and bill.is_daily_buysell == False) or (bill.is_timer_buysell == True  and  bill_amount != wallet_amount ) :

           

                if bill.is_timer_buysell == True :

                    timed_request.status = 'Rejected'
                    timed_request.error = "مبلغ فاکتور با مبلغ پرداخت شده مطابقت ندارد"
                    timed_request.save()
                
                bill.is_checked = True
                bill.status = 'Rejected'
                bill.error = "bill and paid not match"
                bill.save()

                Wallet(
            
                    uname = Customer.objects.get(req_user=bill.uname.req_user), 
                    wallet = bill.currency.symbol, 
                    desc = f'بابت برگشت فروش ناموفق فاکتور : {bill.pk}',
                    amount = wallet_amount, 
                    datetime = get_date_time()['timestamp'] ,
                    confirmed_datetime = get_date_time()['timestamp'] ,
                    ip = '0.0.0.0', 
                    is_verify = False,
            
                ).save()

                break
                  

            if not (bill.is_daily_buysell or bill.is_timer_buysell):

                if bill.unit_price > bill.currency.BuySellPrice['sell'] and abs(bill.currency.BuySellPrice['sell'] - bill.unit_price) > (bill.unit_price / 100) :

                    bill.is_checked = True
                    bill.status = 'Rejected'
                    bill.error = "bill and melligold amount not match"
                    bill.save()


                    Wallet(
                
                        uname = Customer.objects.get(req_user=bill.uname.req_user), 
                        wallet = bill.currency.symbol, 
                        desc = f'بابت برگشت فروش ناموفق فاکتور : {bill.pk}',
                        amount = wallet_amount, 
                        datetime = get_date_time()['timestamp'] ,
                        confirmed_datetime = get_date_time()['timestamp'] ,
                        ip = '0.0.0.0', 
                        is_verify = False,
                
                    ).save()

                    break

            if float(get_customer_balance(bill.uname.req_user,bill.currency.symbol, True)["balance"]) < 0.0 :

                bill.is_checked = True
                bill.status = 'Rejected'
                bill.error = "negetive balance"
                bill.save()

                if bill.is_timer_buysell == True :

                    timed_request.status = 'Rejected'
                    timed_request.error = "موجودی ناکافی است"
                    timed_request.save()

                Wallet(
            
                    uname = Customer.objects.get(req_user=bill.uname.req_user), 
                    wallet = bill.currency.symbol, 
                    desc = f'بابت برگشت فروش ناموفق فاکتور : {bill.pk}',
                    amount = wallet_amount, 
                    datetime = get_date_time()['timestamp'] ,
                    confirmed_datetime = get_date_time()['timestamp'] ,
                    ip = '0.0.0.0', 
                    is_verify = False,
            
                ).save()

                break

            if bill.is_checked == False and bill.bill_type == 'sell' and bill.status == 'Pendding' :

                bill.is_checked = True
                bill.status = 'Success'
                bill.save()
             
                    
            
                if bill.is_timer_buysell == True :

                    timed_request.status = 'Success'

                    if totalPrice != bill.total_price :
                        bill.total_price_difference = bill.total_price - totalPrice 
                        bill.save()

                    if timed_request.process_based_on == 'price' and bill.amount_gram_difference != 0 and abs(bill.amount_gram_difference) > 1e-4 :
                        Wallet(
            
                            uname = Customer.objects.get(req_user=bill.uname.req_user), 
                            wallet = timed_request.currency.symbol, 
                            desc = f'بابت ما به تفاوت درخواست فروش با تعیین قیمت به شناسه : {bill.timer_buysell_id}',
                            amount = none_round_custom_float_format(bill.amount_gram_difference, 4), 
                            datetime = get_date_time()['timestamp'] ,
                            confirmed_datetime = get_date_time()['timestamp'] ,
                            ip = '0.0.0.0', 
                            is_verify = False,
                    
                        ).save()
                        

                    timed_request.save()

                customer = Customer.objects.get(req_user=bill.uname.req_user)

                if customer.hour_to_pending > 0 :
                    
                    if Currency_BuySell_List.objects.filter(is_gate=True,total_price__gte=1000000,uname=customer,need_pending=True).count() > 0 :
                        
                        customer.hour_to_pending = 0
                        customer.save()

                if bill.sell_payment_method == "DirectWithdrawal":
                    
                    acc_settlement = Vandar_Automatic_Settlement.objects.get(code=1000)
                    now_timestamp = get_date_time()['timestamp']

                    if acc_settlement.divide_to == 0:

                        bill.is_checked = True
                        bill.status = 'Rejected'
                        bill.error = "vandar divide total price is equal to 0"
                        bill.save()

                        Wallet(
                    
                            uname = Customer.objects.get(req_user=bill.uname.req_user), 
                            wallet = bill.currency.symbol, 
                            desc = f'بابت برگشت خرید ناموفق فاکتور : {bill.pk}',
                            amount = wallet_amount , 
                            datetime = get_date_time()['timestamp'] ,
                            confirmed_datetime = get_date_time()['timestamp'] ,
                            ip = '0.0.0.0', 
                            is_verify = False,
                    
                        ).save()

                    if bill.total_price > acc_settlement.divide_to and acc_settlement.divide_to != 0:
                        
                        withdraw_list = divide_total_price_for_vandar(bill.total_price, customer, bill.pk, 'sell')
                        customer_card = Customer_card.objects.get(pk=bill.card_withdrawal_sell)
                        payment_method = WithdrawPaymentMethodIRT.objects.get(pk=bill.payment_method_withdrawal)

                        wallet_withdraws = []

                        for price in withdraw_list:

                            wallet_withdraws.append(
                                WalletWithdrawIRT(
                                    uname=customer,
                                    amount=price,
                                    datetime=now_timestamp,
                                    remain_wallet=get_customer_balance(customer.req_user, 'IRT')["balance"],
                                    card=customer_card,
                                    payment_method=payment_method,
                                    is_check=False
                                )
                            )

                        WalletWithdrawIRT.objects.bulk_create(wallet_withdraws)
                        
                    if bill.total_price < acc_settlement.divide_to and acc_settlement.divide_to != 0:

                        WalletWithdrawIRT(uname=customer,amount=bill.total_price,datetime= get_date_time()['timestamp'],remain_wallet=get_customer_balance(customer.req_user,'IRT')["balance"],card=Customer_card.objects.get(pk=bill.card_withdrawal_sell),payment_method =  WithdrawPaymentMethodIRT.objects.get(pk=bill.payment_method_withdrawal),is_check=False).save()
                else :

                    Wallet(
                
                        uname = customer, 
                        wallet = 'IRT', 
                        desc = f'فروش {bill.currency.fa_title} به شماره فاکتور : {bill.pk}',
                        amount = bill.total_price, 
                        datetime =  get_date_time()['timestamp']   if bill.is_timer_buysell == False and bill.is_daily_buysell == False else bill.datetime ,
                        confirmed_datetime = get_date_time()['timestamp'] ,
                        ip = '0.0.0.0', 
                        is_verify = True,
                
                    ).save()




                if customer.up_referral_link != "-" :

                    if customer.req_user.startswith("customer-"):
                        amount = round((bill.total_price * bill.currency.profit_percent_sell) / 100, 0)
                    else :    
                        pass

                    # ProfitAssigne(customer.up_referral_link, amount, bill.pk)

                    if  customer.reseller_upper_link != "-" : 

                        pass

 
                customer.sell_price += bill.total_price
                customer.last_buysell_time = get_date_time()['timestamp']
                customer.save()

                arz = Currency_List.objects.get(symbol=bill.currency.symbol)
                arz.sell += bill.total_price
                arz.save()     







def check_buy_price_requests():
    
    setting = Site_Settings.objects.get(code=1001)
    
    datetime = get_date_time()['timestamp']
    currency = Currency_List.objects.get(symbol='XAU18')
    last_gold_price = currency.BuySellPrice['buy']


    if setting.is_timer_buysell_robot and setting.is_getprice_buy and currency.is_sell :
        
        pending_requests = Currency_BuySell_Custom_Price.objects.filter(status="Pendding",process_based_on="price",desired_price__gte=last_gold_price,is_checked=False,bill_type='buy', proccess_time__lte=datetime).order_by('pk')[:5]
        
        for timed_request in pending_requests:

            if timed_request.is_gate == False:

                try : 
                    
                    W = Wallet.objects.get(pk=timed_request.wallet_id)
                    wallet_amount = int(abs(W.amount))

                    if Currency_BuySell_Custom_Price.objects.filter(wallet_id=W.pk).count() != 1 :

                        timed_request.is_checked = True
                        timed_request.status = 'Rejected'
                        timed_request.error = "تراکنش تکراری می باشد"
                        timed_request.save()

                        break
                    
                except : 

                    timed_request.is_checked = True
                    timed_request.status = 'Rejected'
                    timed_request.error = "تراکنش یافت نشد"
                    timed_request.save()

                    break
            
            else : 
                
                try : 
                    
                    OW = Online_Wallet.objects.get(pk=timed_request.online_wallet_id, status=100)
                    wallet_amount = int(OW.transactionAmount) / 10

                    if Currency_BuySell_Custom_Price.objects.filter(online_wallet_id=OW.pk).count() != 1 :

                        timed_request.is_checked = True
                        timed_request.status = 'Rejected'
                        timed_request.error = "تراکنش تکراری می باشد"
                        timed_request.save()

                        break
                    
                except : 
                    
                    timed_request.is_checked = True
                    timed_request.status = 'Rejected'
                    timed_request.error = "تراکنش مطابقت ندارد"
                    timed_request.save()

                    break




            try : currency = Currency_List.objects.get(symbol=timed_request.currency.symbol)
            except : 
                timed_request.is_checked = True
                timed_request.status = 'Rejected'
                timed_request.error = 'در خرید طلا خطایی رخ داده است'
                timed_request.save()

                Robot_Log(robot='درخواست خرید با تعیین قیمت', datetime=datetime, uname=timed_request.uname, description=f' طلا یافت نشد | کد درخواست: {timed_request.pk}').save()
                
                break

            if timed_request.uname.status == 'Suspended' :

                timed_request.is_checked = True
                timed_request.status = 'Rejected'
                timed_request.error = 'وضعیت حساب کاربری موردنظر مسدود است'
                timed_request.save()
                
                Robot_Log(robot='درخواست خرید با تعیین قیمت', datetime=datetime, uname=timed_request.uname, description=f' وضعیت حساب کاربری موردنظر مسدود است | کد درخواست: {timed_request.pk}').save()
                
                break

            Unitprice = float(currency.BuySellPrice['buy'])

            amount_irt_difference = 0

            if timed_request.amount_type == 'gram' : 

                gram_amount = timed_request.amount

                if float(currency.buy_fee) != float(0) :

                    f = ((currency.buy_fee * gram_amount) / 100)
                    if f < currency.buy_fee_lower : fee = currency.buy_fee_lower
                    elif f > currency.buy_fee_upper : fee = currency.buy_fee_upper
                    else : fee = f
                    fee_price = round(fee * Unitprice , 0)

                else:

                    fee = 0
                    fee_price = 0


                maintenance_cost = int(gram_amount * currency.maintenance_cost)
                        
                totalPrice = round((gram_amount * Unitprice) + fee_price + maintenance_cost)     
                
                if timed_request.total_price > totalPrice :
                    amount_irt_difference = timed_request.total_price - totalPrice  


            else : 

                get_pure_gram = convert_irt_xau18(timed_request.irt_amount,'XAU18',Unitprice)
                fee = get_pure_gram['fee']
                fee_price = get_pure_gram['fee_price']
                gram_amount = get_pure_gram['pure_amount']
                maintenance_cost = get_pure_gram['maintenance_cost']

                

                totalPrice = round((gram_amount * Unitprice) + fee_price + maintenance_cost)

                total_price_percent = (wallet_amount * 0.01) / 100
                
                amount_irt_difference = (wallet_amount - totalPrice)

                if abs(amount_irt_difference) > total_price_percent:

                    if amount_irt_difference < 0 :
                    
                        timed_request.is_checked = True
                        timed_request.status = 'Rejected'
                        timed_request.error = "خطایی رخ داده است"
                        timed_request.save()

                        Wallet.objects.create(
                    
                            uname = timed_request.uname, 
                            wallet = 'IRT', 
                            desc = f'بابت برگشت درخواست خرید ناموفق به شناسه : {timed_request.pk}',
                            amount = wallet_amount, 
                            datetime = datetime ,
                            confirmed_datetime = datetime ,
                            ip = '0.0.0.0', 
                            is_verify = False,
                        )

                    
                        Robot_Log(robot='درخواست خرید با تعیین قیمت', datetime=datetime, uname=timed_request.uname, description=f' عدم تطابق میزان قیمت درخواست با میزان محاسبه شده | کد درخواست: {timed_request.pk}').save()

                        break

                if amount_irt_difference < 0 : 
                    totalPrice = wallet_amount
                

            celling_buy = get_customer_CeilingRemain(timed_request.uname.req_user)["buy"]

            if float(celling_buy) < float(totalPrice):
                timed_request.is_checked = True
                timed_request.status = 'Rejected'
                timed_request.error = f'مانده سقف مجاز خرید روزانه شما {celling_buy:,} تومان است'
                timed_request.save()

                break


            if gram_amount < timed_request.currency.lower_amount :

                timed_request.is_checked = True
                timed_request.status = 'Rejected'
                timed_request.error = f'حداقل میزان خرید {timed_request.currency.lower_amount} است'
                timed_request.save()

                Wallet.objects.create(
                
                    uname = timed_request.uname, 
                    wallet = 'IRT', 
                    desc = f'بابت برگشت درخواست خرید ناموفق به شناسه : {timed_request.pk}',
                    amount = wallet_amount, 
                    datetime = datetime ,
                    confirmed_datetime = datetime ,
                    ip = '0.0.0.0', 
                    is_verify = False,
            
                )

                Robot_Log(robot='درخواست خرید با تعیین قیمت', datetime=datetime, uname=timed_request.uname, description=f'مقدار گرم محاسبه شده کمتر از حد مجاز ({timed_request.currency.lower_amount}) است | کد درخواست: {timed_request.pk}').save()

                break


            balance =  timed_request.currency.Balance - (((timed_request.currency.Balance * timed_request.currency.acc_fee) / 100) + (round(get_asset_wallet_reserved(timed_request.currency.symbol)['reserved'], 6))  +  (round(get_asset_bill_reserved(timed_request.currency.symbol)['pendding'], 6)))
            if gram_amount + ((gram_amount * timed_request.currency.acc_fee) / 100) > (balance):
                timed_request.proccess_time = datetime + 3600
                timed_request.save()
                
                break
                

            with transaction.atomic():


                new_transaction = Currency_BuySell_List(

                    uname = timed_request.uname,
                    acc = timed_request.acc,
                    currency = timed_request.currency,
                    wallet_id = timed_request.wallet_id,
                    amount = gram_amount,

                    fee_amount = fee,
                    fee_price = fee_price,
                    unit_price = Unitprice,
                    total_price = totalPrice,
                    maintenance_cost = maintenance_cost,
                    amount_irt_difference = amount_irt_difference,

                    deposite_on_wallet = False,
                    datetime = datetime,
                    ip = timed_request.ip,
                    is_timer_buysell = True,
                    timer_buysell_id = timed_request.pk,
                    amount_type = timed_request.amount_type,
                    process_based_on = timed_request.process_based_on,
                    is_gate = timed_request.is_gate,
                    online_wallet_id = timed_request.online_wallet_id
                )
                
                new_transaction.save()

                timed_request.is_checked = True
                timed_request.transaction_id = new_transaction.pk
                timed_request.save()
                



def check_sell_price_requests():

    
    setting = Site_Settings.objects.get(code=1001)
    datetime = get_date_time()['timestamp']
    currency = Currency_List.objects.get(symbol='XAU18')
    last_gold_price = currency.BuySellPrice['sell']


    if setting.is_timer_buysell_robot and setting.is_getprice_sell and setting.is_sale and currency.is_buy :

        pending_requests = Currency_BuySell_Custom_Price.objects.filter(status="Pendding",process_based_on="price",desired_price__lte=last_gold_price,is_checked=False,bill_type='sell').order_by('pk')[:5]
        
        with transaction.atomic():

            for timed_request in pending_requests:

                try : wallet_amount = float(abs(Wallet.objects.get(pk=timed_request.wallet_id).amount))
                except : 

                    timed_request.is_checked = True
                    timed_request.status = 'Rejected'
                    timed_request.error = "تراکنش یافت نشد"
                    timed_request.save()

                try : currency = Currency_List.objects.get(symbol=timed_request.currency.symbol)
                except : 
                    timed_request.is_checked = True
                    timed_request.status = 'Rejected'
                    timed_request.error = 'در فروش طلا خطایی رخ داده است'
                    timed_request.save()

                    Robot_Log(robot='درخواست فروش با تعیین قیمت', datetime=datetime, uname=timed_request.uname, description=f' طلا یافت نشد | کد درخواست: {timed_request.pk}').save()

                    break

                if timed_request.uname.status == 'Suspended' :

                    timed_request.is_checked = True
                    timed_request.status = 'Rejected'
                    timed_request.error = 'وضعیت حساب کاربری موردنظر مسدود میباشد'
                    timed_request.save()

                    Robot_Log(robot='درخواست فروش با تعیین قیمت', datetime=datetime, uname=timed_request.uname, description=f' وضعیت حساب کاربری موردنظر مسدود است | کد درخواست: {timed_request.pk}').save()

                    break

                Unitprice = float(last_gold_price)
                

                withdraw_method = 0
                if timed_request.sell_payment_method == "DirectWithdrawal" :

                    try:
                        withdraw_method = WithdrawPaymentMethodIRT.objects.get(pk=timed_request.payment_method_withdrawal,is_active=True).wage
                    except:   
                        timed_request.is_checked = True
                        timed_request.status = 'Rejected'
                        timed_request.error = 'روش برداشت نامعتبر است'
                        timed_request.save()

                        Robot_Log(robot='درخواست فروش با تعیین قیمت', datetime=datetime, uname=timed_request.uname, description=f' روش برداشت نامعتبر است | کد درخواست: {timed_request.pk}').save()

                        break

                    try :
                        Customer_card.objects.get(is_verify=True,uname=timed_request.uname,is_show=True,pk=timed_request.card_withdrawal_sell)
                    except : 
                        timed_request.is_checked = True
                        timed_request.status = 'Rejected'
                        timed_request.error = 'کارت نامعتبر است'
                        timed_request.save()

                        Robot_Log(robot='درخواست فروش با تعیین قیمت', datetime=datetime, uname=timed_request.uname, description=f' کارت نامعتبر است | کد درخواست: {timed_request.pk}').save()

                        break

                amount_gram_difference = 0

                if timed_request.amount_type == 'gram' : 

                    if float(currency.sell_fee) != float(0) :

                        f = ((currency.sell_fee * timed_request.amount) / 100)
                        if f < currency.sell_fee_lower : fee = currency.sell_fee_lower
                        elif f > currency.sell_fee_upper : fee = currency.sell_fee_upper
                        else : fee = f
                        fee_price = round(fee * Unitprice , 0)

                    else:

                        fee = 0
                        fee_price = 0

                    gram_amount = timed_request.amount
                    totalPrice = round((timed_request.amount * Unitprice) -  fee_price) - withdraw_method

                else : 

                    get_pure_gram = convert_sell_irt_xau18(timed_request.irt_amount,'XAU18',Unitprice)
                    fee = get_pure_gram['fee']
                    fee_price = get_pure_gram['fee_price']
                    gram_amount = get_pure_gram['pure_amount']
                    totalPriceCalculated = ((get_pure_gram['pure_amount'] * Unitprice) -  get_pure_gram['fee_price']) - withdraw_method
                    totalPrice = timed_request.irt_amount

                    # if abs(totalPriceCalculated - timed_request.irt_amount) > 100 :
                    #     timed_request.is_checked = True
                    #     timed_request.status = 'Rejected'
                    #     timed_request.error = f"عدم تطابق قیمت"
                    #     timed_request.save()

                    #     Wallet(
                
                    #         uname = timed_request.uname, 
                    #         wallet = timed_request.currency.symbol, 
                    #         desc = f'بابت برگشت درخواست فروش ناموفق : {timed_request.currency.fa_title}',
                    #         amount = wallet_amount, 
                    #         datetime = get_date_time()['timestamp'] ,
                    #         confirmed_datetime = get_date_time()['timestamp'] ,
                    #         ip = '0.0.0.0', 
                    #         is_verify = False,
                    
                    #     ).save()
                        
                    #     Robot_Log(robot='درخواست فروش با تعیین قیمت', datetime=datetime, uname=timed_request.uname, description=f' عدم تطابق میزان قیمت درخواست با میزان محاسبه شده | کد درخواست: {timed_request.pk}').save()

                    #     break
                
                    celling_sell = get_customer_CeilingRemain(timed_request.uname.req_user)["sell"]

                    if float(celling_sell) < float(totalPrice):

                        timed_request.is_checked = True
                        timed_request.status = 'Rejected'
                        timed_request.error = f'مانده سقف مجاز فروش روزانه شما {celling_sell:,} تومان است'
                        timed_request.save()
                        break
                    

                    if timed_request.amount != gram_amount :

                        if timed_request.amount > gram_amount :

                            amount_gram_difference = timed_request.amount - gram_amount

                        else:
                            timed_request.is_checked = True
                            timed_request.status = 'Rejected'
                            timed_request.error = 'در فروش طلا خطایی رخ داده است'
                            timed_request.save()

                            Wallet(
                    
                                uname = timed_request.uname, 
                                wallet = timed_request.currency.symbol, 
                                desc = f'بابت برگشت درخواست فروش ناموفق به شناسه : {timed_request.pk}',
                                amount = wallet_amount, 
                                datetime = get_date_time()['timestamp'] ,
                                confirmed_datetime = get_date_time()['timestamp'] ,
                                ip = '0.0.0.0', 
                                is_verify = False,
                        
                            ).save()

                            Robot_Log(robot='درخواست فروش با تعیین قیمت', datetime=datetime, uname=timed_request.uname, description=f' گرم محاسبه شده کم تر از میزان ثبت شده است | کد درخواست: {timed_request.pk}').save()

                            break

                if totalPrice - fee_price <= 0 :
                    timed_request.is_checked = True
                    timed_request.status = 'Rejected'
                    timed_request.error = 'میزان فروش وارد شده نامعتبر است'
                    timed_request.save()

                    Wallet(
                
                        uname = timed_request.uname, 
                        wallet = timed_request.currency.symbol, 
                        desc = f'بابت برگشت درخواست فروش ناموفق به شناسه : {timed_request.pk}',
                        amount = wallet_amount, 
                        datetime = get_date_time()['timestamp'] ,
                        confirmed_datetime = get_date_time()['timestamp'] ,
                        ip = '0.0.0.0', 
                        is_verify = False,
                
                    ).save()

                    Robot_Log(robot='درخواست فروش با تعیین قیمت', datetime=datetime, uname=timed_request.uname, description=f' میزان فروش وارد شده نامعتبر است | کد درخواست: {timed_request.pk}').save()

                    break

                if gram_amount < currency.lower_amount :
                    timed_request.is_checked = True
                    timed_request.status = 'Rejected'
                    timed_request.error = f'حداقل میزان فروش {currency.lower_amount} است'
                    timed_request.save()

                    Wallet(
                
                        uname = timed_request.uname, 
                        wallet = timed_request.currency.symbol, 
                        desc = f'بابت برگشت درخواست فروش ناموفق به شناسه : {timed_request.pk}',
                        amount = wallet_amount, 
                        datetime = get_date_time()['timestamp'] ,
                        confirmed_datetime = get_date_time()['timestamp'] ,
                        ip = '0.0.0.0', 
                        is_verify = False,
                
                    ).save()

                    Robot_Log(robot='درخواست فروش با تعیین قیمت', datetime=datetime, uname=timed_request.uname, description=f'مقدار گرم محاسبه شده کمتر از حد مجاز ({timed_request.currency.lower_amount}) است | کد درخواست: {timed_request.pk}').save()

                    break

            

                with transaction.atomic():

                    new_transaction = Currency_BuySell_List(

                        uname = timed_request.uname,
                        acc = timed_request.acc,
                        currency = timed_request.currency,
                        wallet_id = timed_request.wallet_id,
                        amount = gram_amount,

                        fee_amount = fee,
                        fee_price = fee_price,
                        unit_price = Unitprice,
                        total_price = totalPrice,
                        amount_gram_difference = amount_gram_difference,

                        deposite_on_wallet = False,
                        datetime = get_date_time()['timestamp'],
                        ip = timed_request.ip,
                        bill_type = timed_request.bill_type,
                        is_timer_buysell = True,
                        timer_buysell_id = timed_request.pk,
                        sell_payment_method = timed_request.sell_payment_method,
                        card_withdrawal_sell = timed_request.card_withdrawal_sell,
                        payment_method_withdrawal = timed_request.payment_method_withdrawal,
                        amount_type = timed_request.amount_type

                    )
                    new_transaction.save()

                    timed_request.is_checked = True
                    timed_request.transaction_id = new_transaction.pk
                    timed_request.save()

                

def check_buy_time_requests():

    setting = Site_Settings.objects.get(code=1001)
    datetime_timestamp = get_date_time()['timestamp']
    currency = Currency_List.objects.get(symbol='XAU18')


    if setting.is_timer_buysell_robot and setting.is_timer_sell and setting.is_buy_wallet and currency.is_sell:

        pending_requests = Currency_BuySell_Custom_Price.objects.filter(status="Pendding",process_based_on="datetime",desired_time__lte=datetime_timestamp,is_checked=False,bill_type='buy', proccess_time__lte=datetime_timestamp).order_by('pk')[:5]

        for timed_request in pending_requests :    

            try : 

                created_at_datetime = datetime.fromtimestamp(int(timed_request.desired_time))
                desired_time_plus_one_hour = created_at_datetime.replace(minute=59, second=59, microsecond=0)
                desired_time_plus_one_hour = desired_time_plus_one_hour.timestamp()

                price_log = Account_Price_log.objects.filter(date__gte=timed_request.desired_time,date__lte=desired_time_plus_one_hour).order_by('pk').first()
                Unitprice = price_log.buy

            except :

                if (timed_request.proccess_time < desired_time_plus_one_hour) and (desired_time_plus_one_hour > datetime_timestamp) : 

                    timed_request.proccess_time = datetime_timestamp + 300
                    timed_request.save()

                    continue


                else :    

                    timed_request.is_checked = True
                    timed_request.status = 'Rejected'
                    timed_request.error = 'در خرید طلا خطایی رخ داده است'
                    timed_request.save()

                    Robot_Log(robot='درخواست خرید با تعیین زمان', datetime=datetime_timestamp, uname=timed_request.uname, description=f'قیمت لحظه ای در ساعت موردنظر کاربر یافت نشد | کد درخواست: {timed_request.pk}').save()

                    continue

            if timed_request.uname.status == 'Suspended' :
                timed_request.is_checked = True
                timed_request.status = 'Rejected'
                timed_request.error = 'وضعیت حساب کاربری موردنظر مسدود میباشد'
                timed_request.save()

                Robot_Log(robot='درخواست خرید با تعیین زمان', datetime=datetime_timestamp, uname=timed_request.uname, description=f' وضعیت حساب کاربری موردنظر مسدود است | کد درخواست: {timed_request.pk}').save()

                continue

            amount_irt_difference = 0

            if timed_request.amount_type == 'gram' :

                gram_amount = float(timed_request.amount)

                if float(timed_request.currency.buy_fee) != float(0) :

                    f = ((timed_request.currency.buy_fee * gram_amount) / 100)
                    if f < timed_request.currency.buy_fee_lower : fee = timed_request.currency.buy_fee_lower
                    elif f > timed_request.currency.buy_fee_upper : fee = timed_request.currency.buy_fee_upper
                    else : fee = f
                    fee_price = round(fee * Unitprice , 0)

                else:

                    fee = 0
                    fee_price = 0

                maintenance_cost = int(gram_amount * timed_request.currency.maintenance_cost)
                totalPrice = round((gram_amount * Unitprice) + fee_price + maintenance_cost)


            celling_buy = get_customer_CeilingRemain(timed_request.uname.req_user)["buy"]

            if float(celling_buy) < float(totalPrice):

                timed_request.is_checked = True
                timed_request.status = 'Rejected'
                timed_request.error = f'مانده سقف مجاز خرید روزانه شما {celling_buy:,} تومان است'
                timed_request.save()

                continue


            if totalPrice > float(get_customer_balance(timed_request.uname.req_user,'IRT')["balance"]) :


                timed_request.is_checked = True
                timed_request.status = 'Rejected'
                timed_request.error = 'مبلغ فاکتور شما بیشتر از موجودی کیف پول است'
                timed_request.save()

                Robot_Log(robot='درخواست خرید با تعیین زمان', datetime=datetime_timestamp, uname=timed_request.uname, description=f' مبلغ فاکتور کاربر بیشتر از موجودی کیف پول است | کد درخواست: {timed_request.pk}').save()

                continue





            balance = timed_request.currency.Balance - (((timed_request.currency.Balance * timed_request.currency.acc_fee) / 100) + (round(get_asset_wallet_reserved(timed_request.currency.symbol)['reserved'], 6))  +  (round(get_asset_bill_reserved(timed_request.currency.symbol)['pendding'], 6)))

            if gram_amount + ((gram_amount * timed_request.currency.acc_fee) / 100) > (balance):

                timed_request.proccess_time = datetime_timestamp + 3600
                timed_request.save()

                continue

            if gram_amount < timed_request.currency.lower_amount :
                timed_request.is_checked = True
                timed_request.status = 'Rejected'
                timed_request.error = f'حداقل میزان خرید {timed_request.currency.lower_amount} است'
                timed_request.save()

                Robot_Log(robot='درخواست خرید با تعیین زمان', datetime=datetime_timestamp, uname=timed_request.uname, description=f'مقدار گرم محاسبه شده کمتر از حد مجاز ({timed_request.currency.lower_amount}) است | کد درخواست: {timed_request.pk}').save()

                continue
    
            if totalPrice > float(get_customer_balance(timed_request.uname.req_user,'IRT')["balance"]) :
                
                timed_request.is_checked = True
                timed_request.status = 'Rejected'
                timed_request.error = 'مبلغ فاکتور شما بیشتر از موجودی کیف پول است'
                timed_request.save()

                Robot_Log(robot='درخواست خرید با تعیین زمان', datetime=datetime_timestamp, uname=timed_request.uname, description=f' مبلغ فاکتور کاربر بیشتر از موجودی کیف پول است | کد درخواست: {timed_request.pk}').save()

                continue

            with transaction.atomic():

                w = Wallet(

                    uname = timed_request.uname,
                    wallet = 'IRT',
                    desc = f'بابت درخواست خرید با تعیین زمان به شناسه : {timed_request.pk}',
                    amount = totalPrice * (-1),
                    datetime = timed_request.desired_time,
                    confirmed_datetime = datetime_timestamp,
                    ip = timed_request.ip,
                    is_verify = True,

                )
                w.save()


                new_transaction = Currency_BuySell_List(

                    uname = timed_request.uname,
                    acc = timed_request.currency.acc,
                    currency = timed_request.currency,

                    wallet_id = w.pk,

                    amount = gram_amount,
                    fee_amount = fee,

                    fee_price = fee_price,
                    unit_price = Unitprice,
                    total_price = totalPrice,

                    deposite_on_wallet = False,

                    datetime = timed_request.desired_time,
                    ip = timed_request.ip,
                    maintenance_cost = maintenance_cost,
                    is_timer_buysell = True,
                    timer_buysell_id = timed_request.pk,
                    amount_type = timed_request.amount_type,
                    amount_irt_difference = amount_irt_difference,
                    process_based_on = timed_request.process_based_on


                )
                
                new_transaction.save()

                w.desc=f'بابت درخواست خرید با تعیین زمان به شناسه : {new_transaction.pk}'
                w.save()

                timed_request.fee_amount = new_transaction.fee_amount
                timed_request.fee_price = new_transaction.fee_price
                timed_request.unit_price = new_transaction.unit_price
                timed_request.total_price = new_transaction.total_price
                timed_request.maintenance_cost = new_transaction.maintenance_cost
                timed_request.amount = new_transaction.amount
                timed_request.is_checked = True
                timed_request.transaction_id = new_transaction.pk
                timed_request.save()
                



def check_sell_time_requests():


    setting = Site_Settings.objects.get(code=1001)
    datetime_timestamp = get_date_time()['timestamp']
    currency = Currency_List.objects.get(symbol='XAU18')

    if setting.is_timer_buysell_robot and setting.is_timer_sell and setting.is_sale and currency.is_buy :

        pending_requests = Currency_BuySell_Custom_Price.objects.filter(status="Pendding",process_based_on="datetime",desired_time__lte=datetime_timestamp,is_checked=False,bill_type='sell').order_by('pk')[:5]
        
        # with transaction.atomic():

        for timed_request in pending_requests :    

            try :

                created_at_datetime = datetime.fromtimestamp(int(timed_request.desired_time))
                desired_time_plus_one_hour = created_at_datetime.replace(minute=59, second=59, microsecond=0)
                desired_time_plus_one_hour = desired_time_plus_one_hour.timestamp()

                price_log = Account_Price_log.objects.filter(date__gte=timed_request.desired_time,date__lt=desired_time_plus_one_hour).order_by('pk').first()
                Unitprice = price_log.sell


            except:

                if (timed_request.proccess_time < desired_time_plus_one_hour) and (desired_time_plus_one_hour > datetime_timestamp) : 

                    timed_request.proccess_time = datetime_timestamp + 300
                    timed_request.save()

                    continue

                else :    

                    timed_request.is_checked = True
                    timed_request.status = 'Rejected'
                    timed_request.error = 'در فروش طلا خطایی رخ داده است'
                    timed_request.save()

                    Robot_Log(robot='درخواست فروش با تعیین زمان', datetime=datetime_timestamp, uname=timed_request.uname, description=f'قیمت لحظه ای در ساعت موردنظر کاربر یافت نشد | کد درخواست: {timed_request.pk}').save()

                    continue

            if timed_request.uname.status == 'Suspended' :

                timed_request.is_checked = True
                timed_request.status = 'Rejected'
                timed_request.error = 'وضعیت حساب کاربری موردنظر مسدود میباشد'
                timed_request.save()

                Robot_Log(robot='درخواست فروش با تعیین زمان', datetime=datetime_timestamp, uname=timed_request.uname, description=f' وضعیت حساب کاربری موردنظر مسدود است | کد درخواست: {timed_request.pk}').save()

                continue

            try : currency = Currency_List.objects.get(symbol=timed_request.currency.symbol)
            except : 
                timed_request.is_checked = True
                timed_request.status = 'Rejected'
                timed_request.error = 'در فروش طلا خطایی رخ داده است'
                timed_request.save()

                Robot_Log(robot='درخواست فروش با تعیین زمان', datetime=datetime_timestamp, uname=timed_request.uname, description=f' طلا یافت نشد | کد درخواست: {timed_request.pk}').save()

                continue

            #new
            # if timed_request.sell_payment_method != "DirectWithdrawal" and  timed_request.sell_payment_method != "IrtWallet" :
            #     timed_request.is_checked = True
            #     timed_request.status = 'Rejected'
            #     timed_request.error = 'روش فروش انتخاب شده نامعتبر است'
            #     timed_request.save()
            #     break

            withdraw_method = 0
            if timed_request.sell_payment_method == "DirectWithdrawal" :

                try:
                    withdraw_method = WithdrawPaymentMethodIRT.objects.get(pk=timed_request.payment_method_withdrawal,is_active=True).wage

                except:   
                    timed_request.is_checked = True
                    timed_request.status = 'Rejected'
                    timed_request.error = 'روش برداشت نامعتبر است'
                    timed_request.save()

                    Robot_Log(robot='درخواست فروش با تعیین زمان', datetime=datetime_timestamp, uname=timed_request.uname, description=f' روش برداشت نامعتبر است | کد درخواست: {timed_request.pk}').save()

                    continue

                try :
                    Customer_card.objects.get(is_verify=True,uname=timed_request.uname,is_show=True,pk=timed_request.card_withdrawal_sell)
                except : 
                    timed_request.is_checked = True
                    timed_request.status = 'Rejected'
                    timed_request.error = 'کارت نامعتبر است'
                    timed_request.save()

                    Robot_Log(robot='درخواست فروش با تعیین زمان', datetime=datetime_timestamp, uname=timed_request.uname, description=f' کارت نامعتبر است | کد درخواست: {timed_request.pk}').save()

                    continue

            if timed_request.amount_type == 'gram' : 
                if float(currency.sell_fee) != float(0) :

                    f = ((currency.sell_fee * timed_request.amount) / 100)
                    if f < currency.sell_fee_lower : fee = currency.sell_fee_lower
                    elif f > currency.sell_fee_upper : fee = currency.sell_fee_upper
                    else : fee = f
                    fee_price = round(fee * Unitprice , 0)

                else:

                    fee = 0
                    fee_price = 0
                
                totalPrice = round((timed_request.amount * Unitprice) -  fee_price) - withdraw_method
                gram_amount = timed_request.amount

            else : 

                get_pure_gram = convert_sell_irt_xau18(timed_request.irt_amount,'XAU18',Unitprice)
                fee = get_pure_gram['fee']
                fee_price = get_pure_gram['fee_price']
                gram_amount = get_pure_gram['pure_amount']
                totalPrice = timed_request.irt_amount

            if totalPrice - fee_price <= 0 :
                timed_request.is_checked = True
                timed_request.status = 'Rejected'
                timed_request.error = 'میزان فروش وارد شده نامعتبر است'
                timed_request.save()

                Robot_Log(robot='درخواست فروش با تعیین زمان', datetime=datetime_timestamp, uname=timed_request.uname, description=f' میزان فروش وارد شده نامعتبر است | کد درخواست: {timed_request.pk}').save()

                continue

            if gram_amount < currency.lower_amount :
                timed_request.is_checked = True
                timed_request.status = 'Rejected'
                timed_request.error = f'حداقل میزان فروش {currency.lower_amount} است'
                timed_request.save()

                Robot_Log(robot='درخواست فروش با تعیین زمان', datetime=datetime_timestamp, uname=timed_request.uname, description=f'مقدار گرم محاسبه شده کمتر از حد مجاز ({timed_request.currency.lower_amount}) است | کد درخواست: {timed_request.pk}').save()

                continue


            if float(get_customer_balance(timed_request.uname.req_user, currency.symbol)["balance"]) < gram_amount :

                timed_request.is_checked = True
                timed_request.status = 'Rejected'
                timed_request.error = 'موجودی کیف پول شما کمتر از میزان فروش است'
                timed_request.save()

                Robot_Log(robot='درخواست فروش با تعیین زمان', datetime=datetime_timestamp, uname=timed_request.uname, description=f' موجودی کیف پول کاربر کمتر از میزان فروش است | کد درخواست: {timed_request.pk}').save()

                continue

            celling_sell = get_customer_CeilingRemain(timed_request.uname.req_user)["sell"]

            if float(celling_sell) < float(totalPrice):

                timed_request.is_checked = True
                timed_request.status = 'Rejected'
                timed_request.error = f'مانده سقف مجاز فروش روزانه شما {celling_sell:,} تومان است'
                timed_request.save()

                continue

            with transaction.atomic():

                w = Wallet(

                    uname = timed_request.uname,
                    wallet = currency.symbol,
                    desc = f'بابت درخواست فروش با تعیین زمان به شناسه : {timed_request.pk}',
                    amount = gram_amount * (-1),
                    datetime = timed_request.desired_time,
                    confirmed_datetime = datetime_timestamp,
                    ip = timed_request.ip,
                    is_verify = True,

                )
                w.save()

                new_transaction = Currency_BuySell_List(

                    uname = timed_request.uname,
                    acc = currency.acc,
                    currency = currency,

                    wallet_id = w.pk,
                    amount = gram_amount,

                    fee_amount = fee,
                    fee_price = fee_price,

                    bill_type='sell',

                    unit_price = Unitprice,
                    total_price = (totalPrice),

                    datetime = timed_request.desired_time,
                    ip = timed_request.ip,
                    sell_payment_method = timed_request.sell_payment_method,
                    card_withdrawal_sell = timed_request.card_withdrawal_sell,
                    payment_method_withdrawal = timed_request.payment_method_withdrawal,
                    is_timer_buysell = True,
                    timer_buysell_id = timed_request.pk,
                    amount_type = timed_request.amount_type

                )
                new_transaction.save()

                w.desc=f'بابت درخواست فروش با تعیین زمان به شناسه : {new_transaction.pk}'
                w.save()

                timed_request.fee_amount = new_transaction.fee_amount
                timed_request.fee_price = new_transaction.fee_price
                timed_request.unit_price = new_transaction.unit_price
                timed_request.total_price = new_transaction.total_price
                timed_request.is_checked = True
                timed_request.transaction_id = new_transaction.pk
                timed_request.amount = new_transaction.amount
                timed_request.save()




def check_buysell_cancel_requests():
    
    datetime = get_date_time()['timestamp']

    if Site_Settings.objects.get(code=1001).is_timer_buysell_robot:
        
        for i in Currency_BuySell_Custom_Price.objects.filter(status='Canceled', acc='handly',process_based_on='price',is_checked=False,transaction_id="-").order_by('-pk')[:5]:
            
            timed_request = i
            
            with transaction.atomic():

                if Wallet.objects.filter(refund_buysell_request_pk=timed_request.pk).count() == 0 :

                    timed_request.is_checked = True
                    timed_request.save()

                    if timed_request.bill_type == 'buy' : description = f'لغو درخواست خرید'
                    elif timed_request.bill_type == 'sell' : description = f'لغو درخواست فروش'


                    if timed_request.is_gate == False:

                        try : 
                            
                            trans = Wallet.objects.get(pk=timed_request.wallet_id)
                            wallet_amount = trans.amount

                            if Currency_BuySell_Custom_Price.objects.filter(wallet_id=trans.pk).count() != 1 :

                                timed_request.status = 'Rejected'
                                timed_request.error = "تراکنش یافت نشد"
                                timed_request.save()

                                Robot_Log(robot='لغو درخواست با تعیین قیمت', datetime=datetime, uname=timed_request.uname, description=f' تراکنش کاربر یافت نشد | کد درخواست: {timed_request.pk}').save()

                                continue
                                
                        except : 

                            timed_request.status = 'Rejected'
                            timed_request.error = "تراکنش یافت نشد"
                            timed_request.save()

                            Robot_Log(robot='لغو درخواست با تعیین قیمت', datetime=datetime, uname=timed_request.uname, description=f' تراکنش کاربر یافت نشد | کد درخواست: {timed_request.pk}').save()

                            continue
                        
                    else : 
                        
                        try : 
                            
                            trans = Online_Wallet.objects.get(pk=timed_request.online_wallet_id, status=100)
                            wallet_amount = int(trans.transactionAmount) / 10

                            if Currency_BuySell_Custom_Price.objects.filter(online_wallet_id=trans.pk).count() != 1 :

                                timed_request.status = 'Rejected'
                                timed_request.error = "تراکنش یافت نشد"
                                timed_request.save()

                                Robot_Log(robot='لغو درخواست با تعیین قیمت', datetime=datetime, uname=timed_request.uname, description=f' تراکنش کاربر یافت نشد | کد درخواست: {timed_request.pk}').save()

                                continue
                            
                        except : 
                            
                            timed_request.status = 'Rejected'
                            timed_request.error = "تراکنش یافت نشد"
                            timed_request.save()

                            Robot_Log(robot='لغو درخواست با تعیین قیمت', datetime=datetime, uname=timed_request.uname, description=f' تراکنش کاربر یافت نشد | کد درخواست: {timed_request.pk}').save()

                            continue

    

                    cancel_transaction = Wallet(

                        uname = timed_request.uname,
                        wallet = 'IRT' if timed_request.bill_type == 'buy' else 'XAU18' ,
                        desc = f'بابت {description} با تعیین قیمت به شناسه : {timed_request.pk}',
                        amount = abs(wallet_amount) ,
                        datetime = datetime,
                        confirmed_datetime = datetime,
                        ip = timed_request.ip,
                        is_verify = False,
                        refund_buysell_request_pk = timed_request.pk,

                    )
                    cancel_transaction.save()
                    
                else :
                    timed_request.status = 'Rejected'
                    timed_request.is_checked = True
                    timed_request.error = "تراکنش یافت نشد"
                    timed_request.save()

                    Robot_Log(robot='لغو درخواست با تعیین قیمت', datetime=datetime, uname=timed_request.uname, description=f' تراکنش کاربر یافت نشد | کد درخواست: {timed_request.pk}').save()

