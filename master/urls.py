from django.urls import path, include
from . import views

urlpatterns = [

    path('master/login/', views.master_login, name='master_login'),
    path('master/login/submit/', views.master_login_submit, name='master_login_submit'),
    path('master/code/verify/', views.master_code_verify, name='master_code_verify'),
    path('master/code/verify/request/', views.master_code_verify_request, name='master_code_verify_request'),
    path('master/code/verify/submit/', views.master_code_verify_submit, name='master_code_verify_submit'),
    path('master/panel/', views.master_panel, name='master_panel'),

    path('master/site/settings/', views.master_site_settings, name='master_site_settings'),
    path('master/site/settings/submit/', views.master_site_settings_submit, name='master_site_settings_submit'),
    path('master/site/logo/', views.master_site_logo, name='master_site_logo'),
    path('master/site/logo/submit/', views.master_site_logo_submit, name='master_site_logo_submit'),
    path('master/site/icon/', views.master_site_icon, name='master_site_icon'),
    path('master/site/favicon/', views.master_site_favicon, name='master_site_favicon'),
   
   
    path('', views.master_app_logo, name='master_app_logo'),
    path('', views.master_app_logo_submit, name='master_app_logo_submit'),
    path('', views.master_site_icon_submit, name='master_site_icon_submit'),
    path('', views.master_site_favicon_submit, name='master_site_favicon_submit'),
    path('', views.master_site_seo, name='master_site_seo'),
    path('', views.master_site_seo_submit, name='master_site_seo_submit'),
    
    path('', views.master_site_bank, name='master_site_bank'),
    path('', views.master_site_bank_submit, name='master_site_bank_submit'),
    path('', views.master_site_bank_status_change, name='master_site_bank_status_change'),
    path('', views.master_site_bank_delete_submit, name='master_site_bank_delete_submit'),
    path('', views.master_site_bank_edit_submit, name='master_site_bank_edit_submit'),
    path('', views.master_site_bank_search, name='master_site_bank_search'),

    path('', views.master_customer_cards_all, name='master_customer_cards_all'),
    path('', views.master_customer_cards_waiting, name='master_customer_cards_waiting'),
    path('', views.master_reject_card, name='master_reject_card'),
    path('', views.master_confirm_card, name='master_confirm_card'),
    path('', views.master_edit_card, name='master_edit_card'),

    path('', views.master_settings, name='master_settings'),
    path('', views.master_site_change_password_submit, name='master_site_change_password_submit'),

    path('', views.master_customer_modify, name='master_customer_modify'),
    path('', views.master_customer_code_send_submit, name='master_customer_code_send_submit'),
    path('', views.master_customer_create_submit, name='master_customer_create_submit'),
    path('', views.master_customer_list, name='master_customer_list'),
    path('master/customer/search/', views.master_customer_search, name='master_customer_search'),
    path('master/customer/<pk>/detail/', views.master_customer_detail, name='master_customer_detail'),
    path('master/customer/<pk>/detail/reports/search/', views.master_customer_detail_reports_search, name='master_customer_detail_reports_search'),
    path('', views.master_customer_edit_detail, name='master_customer_edit_detail'),
    
    path('', views.master_customer_suspicious_submit, name='master_customer_suspicious_submit'),
    path('', views.master_customers_suspicious, name='master_customers_suspicious'),
    path('', views.master_customer_suspicious_search, name='master_customer_suspicious_search'),

    
    path('', views.master_customer_auth_submit, name='master_customer_auth_submit'),
    path('', views.master_customer_identity_inquiry_list, name='master_customer_identity_inquiry_list'),
    path('', views.master_customer_identity_inquiry_search, name = 'master_customer_identity_inquiry_search'),

    path('', views.master_customer_change_pass, name='master_customer_change_pass'),


    path('master/customer/<pk>/note/submit/', views.master_customer_note_submit, name='master_customer_note_submit'),


    path('master/about/', views.master_about, name='master_about'),
    path('master/about/submit/', views.master_about_submit, name='master_about_submit'),

    # path('', views.master_app_config, name='master_app_config'),
    # path('', views.master_app_config_submit, name='master_app_config_submit'),

    # path('', views.master_contact, name='master_contact'),
    # path('', views.master_contact_submit, name='master_contact_submit'),

    # path('', views.master_customer_ceiling, name='master_customer_ceiling'),

    # path('', views.master_customer_gift, name='master_customer_gift'),

    # path('', views.master_representatives_gift, name='master_representatives_gift'),
    # path('', views.master_customer_gift_submit, name='master_customer_gift_submit'),
    # path('', views.master_representatives_gift_submit, name='master_representatives_gift_submit'),

    # path('', views.master_rules_register, name='master_rules_register'),
    # path('', views.master_rules_representation, name='master_rules_representation'),
    # path('', views.master_rules_representation_submit, name='master_rules_representation_submit'),
    # path('', views.master_rules_card, name='master_rules_card'),
    # path('', views.master_rules_card_submit, name='master_rules_card_submit'),

    # path('', views.master_rules_phonenumber, name='master_rules_phonenumber'),
    # path('', views.master_rules_phonenumber_submit, name='master_rules_phonenumber_submit'),

    # path('', views.master_rules_profile, name='master_rules_profile'),
    # path('', views.master_rules_profile_submit, name='master_rules_profile_submit'),
    
    # path('', views.master_rules_authenticated, name='master_rules_authenticated'),
    # path('', views.master_rules_authenticated_submit, name='master_rules_authenticated_submit'),
    # path('', views.master_rules_ceiling, name='master_rules_ceiling'),
    # path('', views.master_rules_ceiling_submit, name='master_rules_ceiling_submit'),
    # path('', views.master_rules_error_report, name='master_rules_error_report'),
    # path('', views.master_rules_error_report_submit, name='master_rules_error_report_submit'),
    # path('', views.master_rules_deposit, name='master_rules_deposit'),
    # path('', views.master_rules_deposit_submit, name='master_rules_deposit_submit'),
    # path('', views.master_rules_harvest, name='master_rules_harvest'),
    # path('', views.master_rules_harvest_submit, name='master_rules_harvest_submit'),

    # path('', views.master_search_resault, name='master_search_resault'),

    # path('', views.master_representation, name='master_representation'),
    # path('', views.master_representation_create_submit, name='master_representation_create_submit'),
    # path('', views.master_representation_list, name='master_representation_list'),
    # path('', views.master_representation_detail, name='master_representation_detail'),
    # path('', views.master_representation_detail_submit, name='master_representation_detail_submit'),
    # path('', views.master_representation_change_password_submit, name='master_representation_change_password_submit'),
    # path('', views.master_representation_ip_submit, name='master_representation_ip_submit'),
    # path('', views.master_representation_ip_delete_submit, name='master_representation_ip_delete_submit'),
    # path('', views.master_representation_situations_submit, name='master_representation_situations_submit'),
    # path('', views.master_representation_situations_delete_submit, name='master_representation_situations_delete_submit'),


    # path('', views.master_representation_office_detail, name='master_representation_office_detail'),
    # path('', views.master_representation_office_detail_submit, name='master_representation_office_detail_submit'),
    # path('', views.master_representation_office_change_password_submit, name='master_representation_office_change_password_submit'),
    # path('', views.master_representation_office_ip_submit, name='master_representation_office_ip_submit'),
    # path('', views.master_representation_office_ip_delete_submit, name='master_representation_office_ip_delete_submit'),


    # path('', views.master_representation_office_operator_detail, name='master_representation_office_operator_detail'),
    # path('', views.master_representation_office_operator_detail_submit, name='master_representation_office_operator_detail_submit'),
    # path('', views.master_representation_office_operator_change_password_submit, name='master_representation_office_operator_change_password_submit'),
    # path('', views.master_representation_office_operator_ip_submit, name='master_representation_office_operator_ip_submit'),
    # path('', views.master_representation_office_operator_ip_delete_submit, name='master_representation_office_operator_ip_delete_submit'),

    # delete url
    # delete url
    # delete url
    # delete url
    # delete url
    # delete url
    # .
    # .
    # .

    path('master/site/cities/with/represent/', views.master_site_cities_with_represent, name='master_site_cities_with_represent'),
    path('master/site/cities/with/represent/submit/', views.master_site_cities_with_represent_submit, name='master_site_cities_with_represent_submit'),
    path('master/site/cities/with/represent/status/change/<pk>/', views.master_site_cities_with_represent_status_change, name='master_site_cities_with_represent_status_change'),
    path('master/site/cities/with/represent/delete/submit/<pk>/', views.master_site_cities_with_represent_delete_submit, name='master_site_cities_with_represent_delete_submit'),
    path('master/site/cities/with/represent/edit/submit/<pk>/', views.master_site_cities_with_represent_edit_submit, name='master_site_cities_with_represent_edit_submit'),

    path('master/site/branches/each/representative/<pk>/', views.master_site_branches_each_representative, name='master_site_branches_each_representative'),
    path('master/site/branches/each/representative/submit/<pk>/', views.master_site_branches_each_representative_submit, name='master_site_branches_each_representative_submit'),
    path('master/site/branches/each/representative/status/change/<pk>/', views.master_site_branches_each_representative_status_change, name='master_site_branches_each_representative_status_change'),
    path('master/site/branches/each/representative/delete/submit/<pk>/', views.master_site_branches_each_representative_delete_submit, name='master_site_branches_each_representative_delete_submit'),
    path('master/site/branches/each/representative/edit/<pk>/', views.master_site_branches_each_representative_edit, name='master_site_branches_each_representative_edit'),
    path('master/site/branches/each/representative/edit/submit/<pk>/', views.master_site_branches_each_representative_edit_submit, name='master_site_branches_each_representative_edit_submit'),

    path('master/site/branch/working/days/<pk>/', views.master_site_branch_working_days, name='master_site_branch_working_days'),
    path('master/site/branch/working/days/submit/<pk>/', views.master_site_branch_working_days_submit, name='master_site_branch_working_days_submit'),
    path('master/site/branch/working/days/edit/submit/<pk>/', views.master_site_branch_working_days_edit_submit, name='master_site_branch_working_days_edit_submit'),
    path('master/site/branch/working/days/delete/submit/<pk>/', views.master_site_branch_working_days_delete_submit, name='master_site_branch_working_days_delete_submit'),
    path('master/site/branch/working/days/status/change/<pk>/', views.master_site_branch_working_days_status_change, name='master_site_branch_working_days_status_change'),

    path('master/site/product/list/', views.master_site_product_list, name='master_site_product_list'),
    path('master/site/product/melted/search/', views.master_site_product_melted_search, name='master_site_product_melted_search'),
    path('master/site/product/bullion_coin/search/', views.master_site_product_bullion_coin_search, name='master_site_product_bullion_coin_search'),
    path('master/site/product/add/submit/', views.master_site_product_add_submit, name='master_site_product_add_submit'),
    path('master/site/product/status/change/<pk>/', views.master_site_product_status_change, name='master_site_product_status_change'),
    path('master/site/product/edit/submit/<pk>/', views.master_site_product_edit_submit, name='master_site_product_edit_submit'),
    path('master/site/product/delete/submit/<pk>/', views.master_site_product_delete_submit, name='master_site_product_delete_submit'),
    path('master/site/product/inventory/<pk>/', views.master_site_product_inventory, name='master_site_product_inventory'),
    path('master/site/product/inventory/submit/<pk>/', views.master_site_product_inventory_submit, name='master_site_product_inventory_submit'),

    path('master/site/information/product/submit/', views.master_site_information_product_submit, name='master_site_information_product_submit'),

    path('master/rules/physical/delivery/', views.master_rules_physical_delivery, name='master_rules_physical_delivery'),
    path('master/rules/physical/delivery/submit/', views.master_rules_physical_delivery_submit, name='master_rules_physical_delivery_submit'),

    path('master/site/physical/delivery/information/', views.master_site_physical_delivery_information, name='master_site_physical_delivery_information'),
    path('master/site/physical/delivery/information/submit/', views.master_site_physical_delivery_information_submit, name='master_site_physical_delivery_information_submit'),
    path('master/site/product/list/information/submit/', views.master_site_product_list_information_submit, name='master_site_product_list_information_submit'),
    path('master/site/physical/gold/invoice/information/submit/', views.master_site_physical_gold_invoice_information_submit, name='master_site_physical_gold_invoice_information_submit'),
    path('master/site/edit/invoice/statuses/submit/', views.master_site_edit_invoice_statuses_submit, name='master_site_edit_invoice_statuses_submit'),

    path('master/site/customer/order/list/<type>/', views.master_site_customer_order_list, name='master_site_customer_order_list'),
    path('master/site/customer/order/status/change/<pk>/', views.master_site_customer_order_status_change, name='master_site_customer_order_status_change'),
    path('master/site/customer/order/detail/<pk>/', views.master_site_customer_order_detail, name='master_site_customer_order_detail'),

    path('master/physical/delivery/settings/', views.master_physical_delivery_settings, name='master_physical_delivery_settings'),

    path('master/physical/delivery/submit/', views.master_physical_delivery_submit, name='master_physical_delivery_submit'),
    path('master/physical/delivery/counter/submit/', views.master_physical_delivery_counter_submit, name='master_physical_delivery_counter_submit'),

    # delete url
    # delete url
    # delete url
    # delete url
    # delete url
    # delete url
    # .
    # .
    # .
    

    path('master/withdrawal/cancel/<pk>/', views.master_cancle_deposite_withdrawal, name='master_cancle_deposite_withdrawal'),
    # status

    # branch deliverer
    path('master/physical/delivery/deiverer/list/', views.master_physical_delivery_deliverers_list, name='master_physical_delivery_deliverers_list'),
    path('master/physical/delivery/deiverer/add/', views.master_physical_delivery_deliverers_add_submit, name='master_physical_delivery_deliverers_add_submit'),
    path('master/physical/delivery/deiverer/delete/submit/<pk>/', views.master_physical_delivery_deliverers_delete_submit, name='master_physical_delivery_deliverers_delete_submit'),
    path('master/physical/delivery/deiverer/edit/<pk>/', views.master_physical_delivery_deliverers_edit, name='master_physical_delivery_deliverers_edit'),
    path('master/physical/delivery/deiverer/edit/submit/<pk>/', views.master_physical_delivery_deliverers_edit_submit, name='master_physical_delivery_deliverers_edit_submit'),
    path('master/physical/delivery/deiverer/change/status/<pk>/', views.master_physical_delivery_deliverers_change_status, name='master_physical_delivery_deliverers_change_status'),
    # branch deliverer
    
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


