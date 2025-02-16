from django.urls import path


from . import views
from . import pwa_urls

urlpatterns = [

    ################################################################################
    #                  ***** Register And Authentication *****                     #
    ################################################################################


    # Register
    path('customer/register/submit/', views.customer_register_submit, name='customer_register_submit'),
    path('customer/register/ref/submit/<code>/', views.customer_register_ref_submit, name='customer_register_ref_submit'),

    # Login
    path('customer/login/check/', views.customer_login_nationalId_check, name='customer_login_nationalId_check'),
    path('customer/login/pass/', views.customer_login_pass, name='customer_login_pass'),

    # 2FA
    path('customer/two/step/', views.customer_two_step, name='customer_two_step'),
    path('customer/two/step/verify/', views.customer_two_step_check, name='customer_two_step_check'),

    # OTP
    path('customer/verify/code/<uname>/', views.customer_code_verify_request, name='customer_code_verify_request'),
    path('customer/check/code/submit/<pk>/', views.customer_code_verify_submit, name='customer_code_verify_submit'),

    # Forget Password
    path('customer/forget/password/', views.customer_forget_password, name='customer_forget_password'),
    path('customer/forget/password/check/<pk>/', views.customer_forget_password_check, name='customer_forget_password_check'),

    # Check National Code
    path('customer/national/code/verify/request/', views.customer_national_code_verify_request, name='customer_national_code_verify_request'),

    # Check Mobile Ownership
    path('customer/mobile/ownership/check/', views.customer_mobile_ownership_check, name='customer_mobile_ownership_check'),
    path('customer/mobile/verify/code/request/', views.customer_register_code_verify_request, name='customer_register_code_verify_request'),
    path('customer/mobile/verify/code/request/submit/', views.customer_register_code_verify_request_submit, name='customer_register_code_verify_request_submit'),

    # Rulles
    path('customer/rulls/accept/', views.customer_rulls_accept, name='customer_rulls_accept'),

    # Finish Registeration
    path('customer/profile/complate/', views.customer_profile_complate, name='customer_profile_complate'),
    path('customer/profile/complate/submit/', views.customer_profile_complate_submit, name='customer_profile_complate_submit'),


    ################################################################################
    #                        ***** Customer Panel *****                            #
    ################################################################################
    

    # Panel Main
    path('customer/panel/', views.customer_panel, name='customer_panel'),

    # Profile Edit
    path('customer/profile/edit/', views.customer_profile_edit, name='customer_profile_edit'),
    path('customer/profile/edit/submit/', views.customer_profile_edit_submit, name='customer_profile_edit_submit'),

    # Security
    path('customer/toverification/authenticated/submit/', views.customer_toverification_authenticated_submit, name='customer_toverification_authenticated_submit'),

    # Password Change
    path('customer/change_password/', views.customer_change_password, name='customer_change_password'),
    path('customer/change_password/verify/request/', views.customer_change_password_verify_request, name='customer_change_password_verify_request'),

    # Wallets
    path('customer/wallet/irt/', views.customer_toman_wallet, name='customer_irt_wallet'),
    path('customer/wallet/gold/', views.customer_gold_wallet, name='customer_gold_wallet'),

    # Bank Cards
    path('customer/cards/', views.customer_cards, name='customer_cards'),
    path('customer/card/add/submit/', views.customer_card_add_submit, name='customer_card_add_submit'),

    # Earn Income

    # Cellings
    path('customer/request/ceiling/increase/', views.customer_request_ceiling_increase, name='customer_request_ceiling_increase'),
    path('customer/request/ceiling/increase/submit/', views.customer_request_ceiling_increase_submit, name='customer_request_ceiling_increase_submit'),

    # Error Reports

    # Credit increase
    path('customer/wallet/online/increase/inventory/', views.customer_wallet_online_increase_inventory, name='customer_wallet_online_increase_inventory'),
    path('customer/wallet/confirm/online/increase/<pk>/<pid>/', views.customer_wallet_online_increase_confirm, name='customer_wallet_online_increase_confirm'),

    # Financial 
    path('customer/buy/sell/currency/<symbol>/', views.customer_currency_buysell_2, name='customer_currency_buysell_2'),
    path('customer/<symbol>/buy/submit/', views.customer_currency_buy_submit, name='customer_currency_buy_submit'),
    path('customer/<symbol>/sell/submit/', views.customer_currency_sell_submit, name='customer_currency_sell_submit'),

    # Receipts
    path('customer/BuySell/list/', views.customer_buysell_list, name='customer_buysell_list'),
    path('customer/withdrawal/list/', views.customer_harvest_list, name='customer_harvest_list'),
    path('customer/wallet/irt/search/', views.customer_wallet_irt_search, name='customer_wallet_irt_search'),
    path('customer/wallet/gold/search/', views.customer_wallet_gold_search, name='customer_wallet_gold_search'),
    path('customer/BuySell/list/search/', views.customer_buysell_list_search, name='customer_buysell_list_search'),

    # Receipts Excell

    # Notifications

    # Live Price API

    # Physical Delivery
    path('customer/inperson/delivery/list/', views.inperson_delivery_list, name='inperson_delivery_list'),
    path('customer/inperson/delivery/', views.inperson_delivery, name='inperson_delivery'),
    path('customer/select/city/<pk>/', views.customer_select_city, name='customer_select_city'),
    path('customer/select/products/<pk>/', views.customer_select_products, name='customer_select_products'),
    path('customer/select/products/search/<int:pk>/', views.customer_search_products, name='customer_search_products'),
    path('customer/add/to/order/<pk>/', views.customer_add_to_order, name='customer_add_to_order'),
    path('customer/remove/from/order/<pk>/', views.customer_remove_from_order, name='customer_remove_from_order'),
    path('customer/select/branch/<pk>/', views.customer_select_branch, name='customer_select_branch'),
    path('customer/cart/payment/wallet/<pk>/', views.customer_cart_payment_wallet, name='customer_cart_payment_wallet'),
    path('customer/cart/payment/port/<pk>/<id>/', views.customer_cart_payment_port, name='customer_cart_payment_port'),
    path('customer/cancellation/physical/delivery/<pk>/', views.customer_cancellation_physical_delivery, name='customer_cancellation_physical_delivery'),
    
    # Internal Transfer

    # Quick Purchase Packages

    # Automatic Buysell

    # Instant Exchange

    # Timer Buy sell
    path('customer/gold/buy/request/<symbol>/', views.customer_gold_buy_request, name='customer_gold_buy_request'),
    path('customer/gold/sell/request/<symbol>/', views.customer_gold_sell_request, name='customer_gold_sell_request'),
    path('customer/gold/buysell/request/cancel/<pk>/', views.customer_gold_buysell_request_cancel, name='customer_gold_buysell_request_cancel'),


] 
