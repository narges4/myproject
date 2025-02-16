import datetime
from account.models import Account_Price_log
from exchange.models import Site_Settings 

def gold_price_log_check():

    last_log = Account_Price_log.objects.order_by('-pk').first()

    if last_log: 
        now_naive = datetime.datetime.now().replace(tzinfo=None) 
        timestamp_value_naive = datetime.datetime.fromtimestamp(int(last_log.date)).replace(tzinfo=None) 
        if now_naive - timestamp_value_naive >= datetime.timedelta(minutes=3):

            fields = [
                "is_buy_wallet", "is_buy_port", "is_sale",
                "is_getprice_buy", "is_getprice_sell", 
                "is_instant_buysell",
                "is_daily_buy", "is_daily_sell", 
                "is_timer_buy", "is_timer_sell", "is_timer_buysell", "is_timer_buysell_robot"
            ]
            
            update_data = {
                field: False for field in fields
            }
         
            Site_Settings.objects.filter(code=1001).update(**update_data)