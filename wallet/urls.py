from django.urls import path, include
from . import views

urlpatterns = [

    path('master/customer/<pk>/wallet/<wallet>/', views.master_wallet_dpwt, name='master_wallet_dpwt'),
    path('master/customer/wallet/submit/', views.master_wallet_dpwt_submit, name='master_wallet_dpwt_submit'),

    # delete url
    # delete url
    # delete url
    # delete url
    # delete url
    # delete url
    # .
    # .
    # .
    

    path('master/wallet/transaction/all/', views.master_transaction_all, name='master_transaction_all'),
    path('master/wallet/transaction/all/search/', views.master_transaction_all_search, name='master_transaction_all_search'),
    path('master/wallet/transaction/waiting/', views.master_transaction_waiting, name='master_transaction_waiting'),
    path('master/wallet/transaction/waiting/search/', views.master_transaction_waiting_search, name='master_transaction_waiting_search'),
    path('master/confirm/transaction/<pk>/', views.master_confirm_transaction, name='master_confirm_transaction'),
    path('master/reject/transaction/<pk>/', views.master_reject_transaction, name='master_reject_transaction'),
    path('customer/withdraw/', views.customer_harvest, name='customer_harvest'),

    # delete url
    # delete url
    # delete url
    # delete url
    # delete url
    # delete url
    # .
    # .
    # .
    
    
    path('master/wallet/withdraw/irt/all/', views.master_all_WalletWithdrawIRT, name='master_all_WalletWithdrawIRT'),
    path('master/wallet/withdraw/irt/all/search/', views.master_all_WalletWithdrawIRT_search, name='master_all_WalletWithdrawIRT_search'),
    path('master/wallet/withdraw/irt/accept/', views.master_accept_WalletWithdrawIRT, name='master_accept_WalletWithdrawIRT'),
    path('master/wallet/withdraw/irt/accept/search/', views.master_accept_WalletWithdrawIRT_search, name='master_accept_WalletWithdrawIRT_search'),
    path('master/wallet/withdraw/irt/reject/', views.master_reject_WalletWithdrawIRT, name='master_reject_WalletWithdrawIRT'),
    path('master/wallet/withdraw/irt/reject/search/', views.master_reject_WalletWithdrawIRT_search, name='master_reject_WalletWithdrawIRT_search'),
    path('master/wallet/withdraw/irt/waiting/', views.master_waiting_WalletWithdrawIRT, name='master_waiting_WalletWithdrawIRT'),
    path('master/wallet/withdraw/irt/waiting/search/', views.master_waiting_WalletWithdrawIRT_search, name='master_waiting_WalletWithdrawIRT_search'),



    path('pwa/withdraw/', views.customer_harvest, name='pwa_customer_harvest'),

    # delete url
    # delete url
    # delete url
    # delete url
    # delete url
    # delete url
    # .
    # .
    # .
    

]

