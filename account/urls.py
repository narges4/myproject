from django.urls import path, include
from . import views

urlpatterns = [

    path('master/currency/list/', views.master_currency_list, name='master_currency_list'),
    path('master/currency/search/', views.master_currency_search, name='master_currency_search'),
    path('master/currency/pricing/<pk>/', views.master_currency_pricing, name='master_currency_pricing'),
    path('master/currency/access/<pk>/', views.master_currency_access, name='master_currency_access'),
    path('master/currency/about/<pk>/', views.master_currency_about, name='master_currency_about'),
    path('master/currency/guide/<pk>/', views.master_currency_guide, name='master_currency_guide'),

    path('master/account/handly/', views.master_account_handly, name='master_account_handly'),
    path('master/account/handly/price/submit/', views.master_account_handly_price_submit, name='master_account_handly_price_submit'),
    path('master/account/handly/balance/submit/', views.master_account_handly_balance_submit, name='master_account_handly_balance_submit'),


    path('master/setting/direct/wallet/submit/', views.master_direct_wallet_submit, name='master_direct_wallet_submit'),


]  



