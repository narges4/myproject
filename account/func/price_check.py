
from account.models import *
from currency.models import *
from exchange.func.public import *
import datetime
import requests
import re 
import json


def handly_price_update():


    for asset in Currency_List.objects.filter(acc='handly') :

        if asset.symbol == 'XAU18' :
            
            if asset.is_price_update == True :
                
                try :
                    
                    dollar = Site_Dollar_log.objects.filter(symbol='XAU18').last().dollar_price_new

                    buy = int(dollar)
                    sell = int(dollar)

                    if int(buy) + asset.buy_extera_price > asset.buy_lower_price and int(sell) + asset.sell_extera_price < asset.sell_upper_price :
                        
                        Account_Price_log(acc='handly', symbol=asset.symbol, modify='robat', date=get_date_time()['timestamp'], buy=int(buy) + asset.buy_extera_price, sell=int(sell) + asset.sell_extera_price).save()
                
                except : pass

