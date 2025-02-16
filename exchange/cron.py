
from account.func.price_check import *
from account.func.currency_buySell import *
from currency.func.gold_price_log import gold_price_log_check
from exchange.func.goldPrice import *
import time


def currency_buySell_check():

    handly_sell()
    handly_buy()
    

def currency_swap_check():

    Swap_check()

def currency_transfer_check():

    Transfer_check()


def dollar_price_check():

    dollar_price_update()


def handly_price_check():
    
    handly_price_update()
    time.sleep(50)
    handly_price_update()



def system_close_ticket():

    close_ticket_Func()




def send_sms_birthday() :   
    customer_sms_birthday()



def check_card():
    
    check_ownership_card()


def check_withdraw_irt():
    

    withdraw_check()     
  
    increase_irt()  
    
    time.sleep(30)
    increase_irt() 

      


    gold_price_log_check()

def gold_price_check():

    gold_price_update()
    time.sleep(45)
    gold_price_update()
   


def customer_mobile_ownership_confirmation_check():
    customer_mobile_ownership_check()



def currency_buySell_price_requests_check():

    check_buy_price_requests()
    check_sell_price_requests()


def currency_buySell_time_requests_check():

    check_buy_time_requests()
    check_sell_time_requests()


def currency_buySell_cancel_requests_check():

    check_buysell_cancel_requests()

