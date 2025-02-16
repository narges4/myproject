from django.urls import path, include
from . import views

urlpatterns = [

    path('under/update/', views.under_update, name='under_update'),
    path('', views.home, name='home'),
    path('account/', views.account, name='account'),
    path('about-us/', views.about_us, name='about_us'),
    path('contact-us/', views.contact_us, name='contact_us'),
    path('contact-us/form/', views.contact_us_form, name='contact_us_form'),
    path('faq/', views.faq, name='faq'),
    path('academy/<title>/', views.academy, name='academy'),
    path('academy/category/<title>/<category>/', views.academy_category, name='academy_category'),
    path('account/ref/<code>/', views.account_ref_code, name='account_ref_code'),
    path('academy/search/submit/', views.academy_search_submit, name='academy_search_submit'),
    path('melligold/path/', views.melligold_path, name='melligold_path'),
    path('application/', views.application, name='application'),
    path('user/question/', views.user_question, name='user_question'),
    path('contact/user/registered/', views.contact_user_registered, name='contact_user_registered'),
    path('currency/detail/<symbol>/', views.currency_detail, name='currency_detail'),     
    path('site/awards/', views.site_awards, name='site_awards'),

    path('academy/', views.academies, name='academies'),

    path('melligold/media/', views.melligold_media, name='melligold_media'),
    path('category/media/<title>/', views.category_media, name='category_media'),
    path('episode/category/<title>/', views.episode_category, name='episode_category'),
    path('melligold/podcast/', views.melligold_podcast, name='melligold_podcast'),
    path('melligold/newspaper/', views.melligold_newspaper, name='melligold_newspaper'),

    path('physical/delivery/', views.physical_delivery, name='physical_delivery'),

    path('register/', views.register_theme02, name='register_theme02'),
    path('register/ref/<code>/', views.register_theme02_ref_code, name='register_theme02_ref_code'),

    path('forget/password/', views.forget_password_theme02, name='forget_password_theme02'),

    # path('piggy/bank/', views.piggy_bank, name='piggy_bank'),
    
    path('get/detail/episode/<pk>/', views.get_detail_episode, name='get_detail_episode'),
    path('licenses/', views.licenses, name='licenses'),

    path('gold/transfer/', views.transmission, name='transmission'),
    path('generate/price/chart/<asset>/<range_type>/', views.generate_price_chart, name='generate_price_chart'),


    path('report/discrepancy/physical/delivery/<pk>/', views.report_discrepancy_physical_delivery, name='report_discrepancy_physical_delivery'),

    path('bank/gold/resources/', views.bank_resources, name='bank_resources'),
    

]