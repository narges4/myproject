from django.urls import path, include
from . import views

urlpatterns = [

    path('customer/ticket/', views.customer_ticket, name='customer_ticket'),
    path('customer/ticket/modify/submit/', views.customer_ticket_modify_submit, name='customer_ticket_modify_submit'),
    path('customer/ticket/detail/<pk>/', views.customer_ticket_detail, name='customer_ticket_detail'),
    path('customer/ticket/answer/<pk>/submit/', views.customer_ticket_answer_submit, name='customer_ticket_answer_submit'),
    path('customer/ticket/rate/<pk>/submit/', views.customer_ticket_rate_submit, name='customer_ticket_rate_submit'),

    path('master/ticket/', views.master_ticket, name='master_ticket'),
    path('master/ticket/archive/', views.master_ticket_archive, name='master_ticket_archive'),
    path('master/ticket/modify/submit/', views.master_ticket_modify_submit, name='master_ticket_modify_submit'),
    path('master/ticket/detail/<pk>/', views.master_ticket_detail, name='master_ticket_detail'),
    path('master/ticket/answer/<pk>/submit/', views.master_ticket_answer_submit, name='master_ticket_answer_submit'),
    path('master/ticket/ckecking/<pk>/submit/', views.master_ticket_ckecking_submit, name='master_ticket_ckecking_submit'),
    path('master/ticket/ckecking/<pk>/<crm>/submit/', views.master_ticket_ckecking_submit, name='master_ticket_ckecking_submit'),
    path('master/ticket/closed/<pk>/submit/', views.master_ticket_closed_submit, name='master_ticket_closed_submit'),
    path('master/ticket/serach/', views.master_ticket_search, name='master_ticket_search'),
    path('master/ticket/answer/<pk>/edit/submit/', views.master_ticket_answer_edit_submit, name='master_ticket_answer_edit_submit'),


    path('master/sticker/', views.master_sticker, name='master_sticker'),
    path('master/sticker/modify/submit/', views.master_sticker_modify_submit, name='master_sticker_modify_submit'),
    path('master/sticker/active/<pk>/submit/', views.master_sticker_active_submit, name='master_sticker_active_submit'),
    path('master/sticker/delete/<pk>/submit/', views.master_sticker_delete_submit, name='master_sticker_delete_submit'),

    path('pwa/ticket/', views.customer_ticket, name='pwa_customer_ticket'),
    path('pwa/ticket/modify/submit/', views.customer_ticket_modify_submit, name='pwa_customer_ticket_modify_submit'),
    path('pwa/ticket/detail/<pk>/', views.customer_ticket_detail, name='pwa_customer_ticket_detail'),
    path('pwa/ticket/answer/<pk>/submit/', views.customer_ticket_answer_submit, name='pwa_customer_ticket_answer_submit'),
    path('pwa/ticket/rate/<pk>/submit/', views.customer_ticket_rate_submit, name='pwa_customer_ticket_rate_submit'),
   
]

