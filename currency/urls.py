from django.urls import path, include
from . import views

urlpatterns = [
    
    path('master/BuySell/<type>/', views.master_buySell_list, name='master_buySell_list'),
    path('master/BuySell/search/<type>/', views.master_buySell_search, name='master_buySell_search'),
    # path('master/Swap/<type>/', views.master_swap_list, name='master_swap_list'),
    path('master/Swap/search/<type>/', views.master_swap_search, name='master_swap_search'),
    path('master/Transfer/<type>/', views.master_transfer_list, name='master_transfer_list'),
    path('master/Transfer/search/<type>/', views.master_transfer_search, name='master_transfer_search'),
    # path('master/currency/withdrawal/<type>/', views.master_currency_withdrawal_handly, name='master_currency_withdrawal_handly'),
    path('master/currency/withdrawal/edit/handly/<pk>/', views.master_currency_withdrawal_handly_edit, name='master_currency_withdrawal_handly_edit'),
    # path('master/currency/deposit/<type>/', views.master_currency_deposit_handly, name='master_currency_deposit_handly'),
    path('master/currency/deposit/edit/handly/<pk>/', views.master_currency_deposit_handly_edit, name='master_currency_deposit_handly_edit'),
    path('master/rial/deposit/<type>/', views.master_rial_deposit_handly, name='master_rial_deposit_handly'),
    path('master/rial/deposit/search/<type>/', views.master_rial_deposit_handly_search, name='master_rial_deposit_handly_search'),
    path('master/currency/withdrawal/search/<type>/', views.master_currency_withdrawal_handly_search, name='master_currency_withdrawal_handly_search'),

    path('master/all/currency/balance/', views.master_all_currency_balance, name='master_all_currency_balance'),
    path('master/all/currency/price/', views.master_all_currency_price, name='master_all_currency_price'),
    path('master/all/currency/price/search/', views.master_all_currency_price_search, name='master_all_currency_price_search'),
    path('master/all/currency/balance/search/', views.master_all_currency_balance_search, name='master_all_currency_balance_search'),
    path('master/currency/deposite/search/', views.master_currency_deposite_search, name='master_currency_deposite_search'),
    # path('master/currency/deposit/gateway/<type>/', views.master_currency_deposit_gateway, name='master_currency_deposit_gateway'),
    path('master/currency/direct/wallet/<wid>/<pk>/', views.master_currency_direct_wallet, name='master_currency_direct_wallet'),

    path('master/BuySell/custom/price/<type>/', views.master_buySell_custom_price_list, name='master_buySell_custom_price_list'),
    path('master/BuySell/custom/price/search/<type>/', views.master_buySell_custom_price_search, name='master_buySell_custom_price_search'),

    path('master/BuySell/custom/datetime/<type>/', views.master_buySell_custom_datetime_list, name='master_buySell_custom_datetime_list'),
    path('master/BuySell/custom/datetime/search/<type>/', views.master_buySell_custom_datetime_search, name='master_buySell_custom_datetime_search'),

    path('master/daily_buysell/list/<bills_type>/', views.master_daily_buysell_list, name='master_daily_buysell_list'),
    path('master/daily_buysell/search/<bills_type>/', views.master_daily_buysell_search, name='master_daily_buysell_search'),



]

