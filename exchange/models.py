from __future__ import unicode_literals
from statistics import mode
from exchange.func.hash import *
from django.db import models
import jdatetime
from khayyam import *
from master.models import *

NOTIFICATIONSTYPE = [
    ("Public", "Public"),
    ("Private", "Private"),
]

PART = [
    ("dep1", "مشاوره فاندامنتال بازار"),
    ("dep2", "مشاوره تکنیکال بازار"),
    ("dep3", "بررسی پروژه های کریپتوکارنسی"),
    ("dep4", "مدیریت سرمایه"),
    ("dep5", "سنتیمنت بازار"),
]

GOLDS = [
    ("gold1", "آبشده"),
    ("gold2", "سکه"),
    ("gold3", "شمش"),
]


DEPARTMENT = [
    ("-", "-"),
    ("Ticket", "Ticket"),
]

GATEWAYS = [
    ("mellipay", "mellipay"),
    ("idpay", "idpay"),
    ("paystar", "paystar"),
]

RUBYSETTING = [
    ("buy", "خرید"),
    ("sell", "فروش"),
    ("transfer", "انتقال"),
    ("exchange", "تبدیل"),
    ("gateway", "درگاه ارزی"),
]


TYPECONSULTING = [
    ("ticket", "مکالمه صوتی"),
    ("whatsapp", "مکالمه تصویری"),
]

IMPORTANCE = [
    ("Necessary", "ضروری"),
    ("Important", "مهم"),
    ("Normal", "معمولی"),
]


class Site_Front_Template(models.Model):

    theme_name = models.CharField(max_length=300, default="-")
    theme_desc = models.CharField(max_length=350, default="-")
    theme_date = models.CharField(max_length=15, default="-")
    theme_designer = models.CharField(max_length=150, default="-")
    theme_lan = models.CharField(max_length=15, default="-")
    theme_url = models.CharField(max_length=300, default="-")
    theme_activation = models.BooleanField(default=False)
    is_default_theme = models.BooleanField(default=False)


class Site_Customer_Template(models.Model):

    theme_name = models.CharField(max_length=300, default="-")
    theme_desc = models.CharField(max_length=350, default="-")
    theme_date = models.CharField(max_length=15, default="-")
    theme_designer = models.CharField(max_length=150, default="-")
    theme_lan = models.CharField(max_length=15, default="-")
    theme_url = models.CharField(max_length=300, default="-")
    theme_activation = models.BooleanField(default=False)
    is_default_theme = models.BooleanField(default=False)


class Site_Master_Template(models.Model):

    theme_name = models.CharField(max_length=300, default="-")
    theme_desc = models.CharField(max_length=350, default="-")
    theme_date = models.CharField(max_length=15, default="-")
    theme_designer = models.CharField(max_length=150, default="-")
    theme_lan = models.CharField(max_length=15, default="-")
    theme_url = models.CharField(max_length=300, default="-")
    theme_activation = models.BooleanField(default=False)
    is_default_theme = models.BooleanField(default=False)


class Site_Representation_Template(models.Model):

    theme_name = models.CharField(max_length=300, default="-")
    theme_desc = models.CharField(max_length=350, default="-")
    theme_date = models.CharField(max_length=15, default="-")
    theme_designer = models.CharField(max_length=150, default="-")
    theme_lan = models.CharField(max_length=15, default="-")
    theme_url = models.CharField(max_length=300, default="-")
    theme_activation = models.BooleanField(default=False)
    is_default_theme = models.BooleanField(default=False)


class Site_Office_Template(models.Model):

    theme_name = models.CharField(max_length=300, default="-")
    theme_desc = models.CharField(max_length=350, default="-")
    theme_date = models.CharField(max_length=15, default="-")
    theme_designer = models.CharField(max_length=150, default="-")
    theme_lan = models.CharField(max_length=15, default="-")
    theme_url = models.CharField(max_length=300, default="-")
    theme_activation = models.BooleanField(default=False)
    is_default_theme = models.BooleanField(default=False)


class Site_Operator_Template(models.Model):

    theme_name = models.CharField(max_length=300, default="-")
    theme_desc = models.CharField(max_length=350, default="-")
    theme_date = models.CharField(max_length=15, default="-")
    theme_designer = models.CharField(max_length=150, default="-")
    theme_lan = models.CharField(max_length=15, default="-")
    theme_url = models.CharField(max_length=300, default="-")
    theme_activation = models.BooleanField(default=False)
    is_default_theme = models.BooleanField(default=False)


class Site_Settings(models.Model):

    title = models.CharField(max_length=350, default="-")
    title_en = models.CharField(max_length=350, default="-")
    desc = models.CharField(max_length=350, default="-")
    url = models.CharField(max_length=350, default="-")
    help_txt = models.TextField(default="-")
    front_help_txt = models.TextField(default="-")
    show_address = models.TextField(default="-")

    logo_name = models.TextField(default="-")
    icon_name = models.TextField(default="-")
    favicon_name = models.TextField(default="-")
    app_logo_name = models.TextField(default="-")

    seo_google = models.TextField(default="-")
    seo_keywords = models.TextField(default="-")

    is_customer_login = models.BooleanField(default=True)
    is_customer_register = models.BooleanField(default=True)
    is_app_login = models.BooleanField(default=True)
    is_app_register = models.BooleanField(default=True)
    is_representation_login = models.BooleanField(default=True)
    is_office_login = models.BooleanField(default=True)
    is_operator_login = models.BooleanField(default=True)

    is_nationalid_mobile_check = models.BooleanField(default=False)

    is_buy_wallet = models.BooleanField(default=True)
    is_buy_port = models.BooleanField(default=True)
    is_sale = models.BooleanField(default=True)
    is_trade = models.BooleanField(default=True)
    is_transfer = models.BooleanField(default=True)
    is_increase_credit = models.BooleanField(default=True)
    is_deposite = models.BooleanField(default=True)
    is_withdraw = models.BooleanField(default=True)
    is_withdraw_request = models.BooleanField(default=True)

    is_under_update = models.BooleanField(default=False)

    rules_register = models.TextField(default="-")
    rules_representation = models.TextField(default="-")
    rules_card = models.TextField(default="-")
    rules_phone = models.TextField(default="-")
    rules_profile = models.TextField(default="-")
    rules_authenticated = models.TextField(default="-")
    rules_ceiling = models.TextField(default="-")
    rules_error = models.TextField(default="-")
    rules_deposit = models.TextField(default="-")
    rules_harvest = models.TextField(default="-")
    rules_game_question = models.TextField(default="-")
    rules_survey = models.TextField(default="-")
    rules_market = models.TextField(default="-")
    rules_physical_delivery = models.TextField(default="-")
    title_rules_physical_delivery = models.TextField(default="-")
    rules_getprice_buy = models.TextField(default="-")
    rules_getprice_sell = models.TextField(default="-")
    rules_timer_buy = models.TextField(default="-")
    rules_timer_sell = models.TextField(default="-")
    rules_daily_buy = models.TextField(default="-")
    rules_daily_sell = models.TextField(default="-")
    rules_instant_buy = models.TextField(default="-")
    rules_instant_sell = models.TextField(default="-")
    

    rules_register_reps = models.TextField(default="-")
    rules_representation_reps = models.TextField(default="-")
    rules_card_reps = models.TextField(default="-")
    rules_phone_reps = models.TextField(default="-")
    rules_profile_reps = models.TextField(default="-")
    rules_authenticated_reps = models.TextField(default="-")
    rules_ceiling_reps = models.TextField(default="-")
    rules_error_reps = models.TextField(default="-")
    rules_deposit_reps = models.TextField(default="-")
    rules_harvest_reps = models.TextField(default="-")
    rules_game_question_reps = models.TextField(default="-")
    rules_survey_reps = models.TextField(default="-")
    rules_market_reps = models.TextField(default="-")
    rules_physical_delivery_reps = models.TextField(default="-")

    dollar_auto_update = models.BooleanField(default=True)
    dollar_min_price = models.IntegerField(default=0)

    chat_code = models.TextField(default="-")
    is_chat = models.BooleanField(default=True)
    chat_app_code = models.TextField(default="-")
    is_app_chat = models.BooleanField(default=True)
    
    game_wheels = models.BooleanField(default=True)
    title_game_wheels = models.CharField(max_length=350, default="-")
    pic_game_wheels = models.TextField(default="-")
    desc_game_wheels = models.TextField(default="-")
    game_question = models.BooleanField(default=True)
    title_game_question = models.CharField(max_length=350, default="-")
    pic_game_question = models.TextField(default="-")
    desc_game_question = models.TextField(default="-")
    time_game_question = models.IntegerField(default=0)

    game_guess_picture = models.BooleanField(default=True)
    title_game_guess_picture = models.CharField(max_length=350, default="-")
    pic_game_guess_picture = models.TextField(default="-")
    desc_game_guess_picture = models.TextField(default="-")

    code = models.IntegerField(default=1000)
    sms = models.BooleanField(default=True)

    time_counseling = models.CharField(max_length=350, default="-")
    phone_counseling = models.CharField(max_length=350, default="-")
    phone_number_counseling = models.CharField(max_length=350, default="-")
    email_counseling = models.CharField(max_length=350, default="-")
    text_counseling = models.TextField(default="-")

    text_airdrop_token = models.TextField(default="-")
    text_exchange = models.TextField(default="-")

    app_text = models.TextField(default="-")

    emergency_text_show = models.BooleanField(default=False)
    emergency_text = models.TextField(default="-")

    birthday_sms = models.BooleanField(default=False)

    getway_personal = models.BooleanField(default=False)
    download_brochure = models.BooleanField(default=False)
    download_brochure_file = models.TextField(default="-")

    transaction_tracking = models.BooleanField(default=False)

    vector_login_name = models.TextField(default="-")
    vector_swap_name = models.TextField(default="-")
    vector_currency_deposite_name = models.TextField(default="-")
    vector_currency_withdraw_name = models.TextField(default="-")
    vector_irt_deposite_name = models.TextField(default="-")
    vector_irt_withdraw_name = models.TextField(default="-")
    vector_transfer_name = models.TextField(default="-")
    vector_inquiry_name = models.TextField(default="-")
    vector_password_name = models.TextField(default="-")
    vector_twostep_name = models.TextField(default="-")
    vector_error_name = models.TextField(default="-")
    vector_app_name = models.TextField(default="-")
    vector_awards_name = models.TextField(default="-")

    vector_search_uv_name = models.TextField(default="-")

    melliPay = models.TextField(default="-")
    melliTech = models.TextField(default="-")
    melliLand = models.TextField(default="-")

    representation_panel_login = models.BooleanField(default=False)
    representation_panel_register = models.BooleanField(default=False)

    meta_description = models.TextField(default="-")

    rules_create_wallet_direct = models.TextField(default="-")
    rules_transfer_wallet_direct = models.TextField(default="-")
    rules_import_wallet_direct = models.TextField(default="-")
    rules_delete_wallet_direct = models.TextField(default="-")

    max_wallet_create_allow_trc20 = models.IntegerField(default=3)
    time_token = models.CharField(max_length=150, default="0")

    max_wallet_create_allow_erc20 = models.IntegerField(default=3)
    max_wallet_create_allow_polygon = models.IntegerField(default=3)
    max_wallet_create_allow_bsc = models.IntegerField(default=3)

    Header_title = models.TextField(default="-")
    Header_pic = models.TextField(default="-")
    Header_desc = models.TextField(default="-")
    Header_text1 = models.TextField(default="-")
    Header_text2 = models.TextField(default="-")
    Header_text3 = models.TextField(default="-")
    Header_text4 = models.TextField(default="-")
    Header_text5 = models.TextField(default="-")
    Header_text6 = models.TextField(default="-")
    Header_text7 = models.TextField(default="-")
    Header_text8 = models.TextField(default="-")
    Header_pic1 = models.TextField(default="-")
    Header_pic2 = models.TextField(default="-")
    Header_pic3 = models.TextField(default="-")
    Header_pic4 = models.TextField(default="-")

    evidence_title = models.TextField(default="-")
    evidence_desc = models.TextField(default="-")
    evidence_pic_name = models.TextField(default="-")

    faq_title = models.TextField(default="-")
    faq_desc = models.TextField(default="-")
    faq_pic_name = models.TextField(default="-")

    deposit_title = models.TextField(default="-")
    deposit_pic = models.TextField(default="-")
    deposit_desc = models.TextField(default="-")
    deposit_show = models.BooleanField(default=False)

    path_title = models.TextField(default="-")
    path_desc = models.TextField(default="-")
    path_caption1 = models.TextField(default="-")
    path_caption2 = models.TextField(default="-")
    path_caption3 = models.TextField(default="-")
    path_caption4 = models.TextField(default="-")
    path_caption5 = models.TextField(default="-")
    path_caption6 = models.TextField(default="-")
    path_desc1 = models.TextField(default="-")
    path_desc2 = models.TextField(default="-")
    path_desc3 = models.TextField(default="-")
    path_desc4 = models.TextField(default="-")
    path_desc5 = models.TextField(default="-")
    path_desc6 = models.TextField(default="-")
    path_pic1 = models.TextField(default="-")
    path_pic2 = models.TextField(default="-")
    path_pic3 = models.TextField(default="-")
    path_pic4 = models.TextField(default="-")
    path_pic5 = models.TextField(default="-")
    path_pic6 = models.TextField(default="-")
    path_show = models.BooleanField(default=False)

    service_caption1 = models.TextField(default="-")
    service_caption2 = models.TextField(default="-")
    service_caption3 = models.TextField(default="-")
    service_caption4 = models.TextField(default="-")
    service_desc1 = models.TextField(default="-")
    service_desc2 = models.TextField(default="-")
    service_desc3 = models.TextField(default="-")
    service_desc4 = models.TextField(default="-")

    box_title1 = models.TextField(default="-")
    box_title2 = models.TextField(default="-")
    box_title3 = models.TextField(default="-")
    box_desc1 = models.TextField(default="-")
    box_desc2 = models.TextField(default="-")
    box_desc3 = models.TextField(default="-")
    box_pic3 = models.TextField(default="-")

    pic1 = models.TextField(default="-")
    pic2 = models.TextField(default="-")
    pic3 = models.TextField(default="-")
    pic4 = models.TextField(default="-")
    pic5 = models.TextField(default="-")

    title_feature = models.TextField(default="-")
    desc_feature = models.TextField(default="-")

    text_footer = models.TextField(default="-")

    qrcodeAndroid = models.TextField(default="-")
    qrcodeIOS = models.TextField(default="-")
    linkAndroid = models.TextField(default="-")
    linkBazar = models.TextField(default="-")
    linkMyket = models.TextField(default="-")
    linkSibapp = models.TextField(default="-")

    guide_deposit_calculatore = models.TextField(default="-")
    guide_buysell_calculatore = models.TextField(default="-")

    academy_title = models.CharField(max_length=350, default="-")
    academy_short_title = models.TextField(default="-")
    academy_text = models.TextField(default="-")

    academy_title1 = models.CharField(max_length=350, default="-")
    academy_short_title1 = models.TextField(default="-")
    academy_text1 = models.TextField(default="-")
    academy_pic1 = models.TextField(default="-")
    academy_pic2 = models.TextField(default="-")

    meligold_media_title = models.CharField(max_length=350, default="-")
    meligold_media_text = models.TextField(default="-")
    melligold_media_pic1 = models.TextField(default="-")
    melligold_media_pic2 = models.TextField(default="-")
    melligold_newspaper_banner = models.CharField(max_length=350, default="-")
    melligold_media_banner = models.CharField(max_length=350, default="-")
    melligold_podcast_banner = models.CharField(max_length=350, default="-")

    investment_title = models.TextField(default="-")
    investment_pic = models.TextField(default="-")
    investment_desc = models.TextField(default="-")
    investment_text1 = models.TextField(default="-")
    investment_text2 = models.TextField(default="-")
    investment_text3 = models.TextField(default="-")
    investment_title_list = models.TextField(default="-")
    investment_text_list = models.TextField(default="-")
    investment_pic1 = models.TextField(default="-")
    investment_pic2 = models.TextField(default="-")
    investment_pic3 = models.TextField(default="-")

    investment_registration_title1 = models.TextField(default="-")
    investment_registration_desc1 = models.TextField(default="-")
    investment_registration_title2 = models.TextField(default="-")
    investment_registration_desc2 = models.TextField(default="-")

    investment_rules_pic = models.TextField(default="-")
    investment_rules_desc = models.TextField(default="-")

    investment_status_pic = models.TextField(default="-")
    investment_status_desc = models.TextField(default="-")
    investment_status_desc1 = models.TextField(default="-")
    investment_status_icon = models.TextField(default="-")

    wallet_feature_title = models.TextField(default="-")
    wallet_feature_text1 = models.TextField(default="-")
    wallet_feature_text2 = models.TextField(default="-")
    wallet_feature_text3 = models.TextField(default="-")
    wallet_feature_text4 = models.TextField(default="-")
    wallet_feature_picture = models.TextField(default="-")
    wallet_feature_link1 = models.TextField(default="-")
    wallet_feature_link2 = models.TextField(default="-")

    wallet_gold_feature_title = models.TextField(default="-")
    wallet_gold_feature_text1 = models.TextField(default="-")
    wallet_gold_feature_text2 = models.TextField(default="-")
    wallet_gold_feature_text3 = models.TextField(default="-")
    wallet_gold_feature_text4 = models.TextField(default="-")
    wallet_gold_feature_picture = models.TextField(default="-")
    wallet_gold_feature_link1 = models.TextField(default="-")
    wallet_gold_feature_link2 = models.TextField(default="-")

    enamad = models.TextField(default="-")

    cal_info_title = models.TextField(default="-")
    cal_info_desc = models.TextField(default="-")
    cal_deposit_show = models.BooleanField(default=False)
    cal_buysell_show = models.BooleanField(default=False)

    title_deposit_chart = models.CharField(max_length=350, default="-")
    title_price_chart = models.CharField(max_length=350, default="-")
    title_deposit_chart1 = models.CharField(max_length=350, default="-")
    title_price_chart1 = models.CharField(max_length=350, default="-")
    title_deposit_chart2 = models.CharField(max_length=350, default="-")
    title_price_chart2 = models.CharField(max_length=350, default="-")
    desc_deposit_chart = models.TextField(default="-")
    desc_price_chart = models.TextField(default="-")
    title_button_deposit_chart = models.CharField(max_length=350, default="-")
    title_button_price_chart = models.CharField(max_length=350, default="-")
    deposit_chart_show = models.BooleanField(default=False)

    site_deposit_show = models.BooleanField(default=False)
    reseller_deposit_show = models.BooleanField(default=False)

    tag_landing = models.TextField(default="-")
    tag_about_us = models.TextField(default="-")
    tag_contact_us = models.TextField(default="-")
    tag_faq = models.TextField(default="-")
    tag_academy = models.TextField(default="-")

    title_product = models.TextField(default="-")
    desc_product = models.TextField(default="-")

    physical_delivery_title = models.TextField(default="-")
    physical_delivery_desc = models.TextField(default="-")
    physical_delivery_text = models.TextField(default="-")
    physical_delivery_pic1 = models.TextField(default="-")

    delivery_basket_icon = models.TextField(default="-")
    product_desc = models.TextField(default="-")

    title_delivery_basket_box = models.TextField(default="-")
    title_delivery_basket_invoice = models.TextField(default="-")
    delivery_cart_payment_description = models.TextField(default="-")

    text_rejected = models.TextField(default="-")
    picture_rejected = models.TextField(default="-")
    text_not_received = models.TextField(default="-")
    picture_not_received = models.TextField(default="-")
    text_canceled = models.TextField(default="-")
    picture_canceled = models.TextField(default="-")
    text_pending_delivery = models.TextField(default="-")
    picture_pending_delivery = models.TextField(default="-")
    text_received = models.TextField(default="-")
    picture_received = models.TextField(default="-")
    desc_received = models.TextField(default="-")
    delivery_conditions = models.TextField(default="-")
    delivery_documents = models.TextField(default="-")

    physical_delivery_show = models.BooleanField(default=False)

    physical_delivery_page_title = models.TextField(default="-")
    physical_delivery_page_desc = models.TextField(default="-")
    physical_delivery_page_pic = models.TextField(default="-")

    physical_delivery_counter_title1 = models.TextField(default="-")
    physical_delivery_counter_picture1 = models.TextField(default="-")
    physical_delivery_counter1 = models.CharField(max_length=350, default="-")
    physical_delivery_counter_title2 = models.TextField(default="-")
    physical_delivery_counter_picture2 = models.TextField(default="-")
    physical_delivery_counter2 = models.CharField(max_length=350, default="-")
    physical_delivery_counter_title3 = models.TextField(default="-")
    physical_delivery_counter_picture3 = models.TextField(default="-")
    physical_delivery_counter3 = models.CharField(max_length=350, default="-")
    physical_delivery_counter_title4 = models.TextField(default="-")
    physical_delivery_counter_picture4 = models.TextField(default="-")
    physical_delivery_counter4 = models.CharField(max_length=350, default="-")
    physical_delivery_video = models.TextField(default="-")

    dashboard_box1_title = models.TextField(default="-")
    dashboard_box1_text = models.TextField(default="-")

    dashboard_box2_title1 = models.TextField(default="-")
    dashboard_box2_title2 = models.TextField(default="-")
    dashboard_box2_text1 = models.TextField(default="-")
    dashboard_box2_text2 = models.TextField(default="-")
    dashboard_box2_text3 = models.TextField(default="-")
    dashboard_box2_text4 = models.TextField(default="-")
    dashboard_box2_text5 = models.TextField(default="-")
    dashboard_box2_text6 = models.TextField(default="-")
    dashboard_box2_pic = models.TextField(default="-")
    dashboard_box2_show = models.BooleanField(default=True)

    dashboard_box3_text1 = models.TextField(default="-")
    dashboard_box3_text2 = models.TextField(default="-")
    dashboard_box3_text3 = models.TextField(default="-")
    dashboard_box3_show = models.BooleanField(default=True)

    dashboard_box4_title = models.TextField(max_length=50, default="-")
    dashboard_box4_text = models.TextField(max_length=100, default="-")

    referral_title = models.TextField(default="-")
    referral_desc = models.TextField(default="-")
    referral_pic = models.TextField(default="-")
    card_shakar_check = models.BooleanField(default=False)
    identity_check = models.BooleanField(default=False)

    license_title = models.CharField(max_length=350, default="-")
    license_text = models.TextField(default="-")
    license_pic = models.TextField(default="-")

    transmission_title1 = models.CharField(max_length=350, default="-")
    transmission_text1 = models.TextField(default="-")
    transmission_pic1 = models.TextField(default="-")

    transmission_title2 = models.CharField(max_length=350, default="-")
    transmission_text2 = models.TextField(default="-")

    new_investment_show = models.BooleanField(default=False)
    automatic_deposit = models.BooleanField(default=False)

    getprice_buysell_title = models.CharField(max_length=350, default="-")
    getprice_buysell_text = models.TextField(default="-")
    instant_buysell_title = models.CharField(max_length=350, default="-")
    instant_buysell_text = models.TextField(default="-")
    timer_buysell_title = models.CharField(max_length=350, default="-")
    timer_buysell_text = models.TextField(default="-")
    daily_buysell_title = models.CharField(max_length=350, default="-")
    daily_buysell_text = models.TextField(default="-")

    is_getprice_buy = models.BooleanField(default=True)
    is_getprice_sell = models.BooleanField(default=True)

    is_instant_buysell = models.BooleanField(default=True)

    is_daily_buy = models.BooleanField(default=True)
    is_daily_sell = models.BooleanField(default=True)

    is_timer_buy = models.BooleanField(default=True)
    is_timer_sell = models.BooleanField(default=True)
    
    is_timer_buysell = models.BooleanField(default=True)

    is_timer_buysell_robot = models.BooleanField(default=True)

    deposit_with_id_rules_title = models.CharField(max_length=350, default="-")
    deposit_with_id_rules_content = models.TextField(default="-")

    heir_title = models.CharField(max_length=350, default="-")
    heir_rules = models.TextField(default="-")

    first_purchase_sms = models.TextField(default="-")

    get_text_gift = models.TextField(default="-")


    title_quick_buy_packages = models.CharField(max_length=350, default="-")
    rules_quick_buy_packages = models.TextField(default="-")

    bank_resources_title = models.TextField(default="-")
    bank_resources_desc = models.TextField(default="-")
    bank_resources_pic_name = models.TextField(default="-")

    is_draw = models.BooleanField(default=False)


class Site_Dollar_log(models.Model):

    dollar_price_new = models.IntegerField(default=0)
    dollar_price_old = models.IntegerField(default=0)
    datetime = models.CharField(max_length=150, default="-")
    dollar_auto_update = models.BooleanField(default=True)
    modify = models.CharField(max_length=50, default="robat")
    symbol = models.CharField(max_length=50, default="-")

    @property
    def ToshamsiDate(self):
        date = jdatetime.datetime.fromtimestamp(int(self.datetime))
        dateinnum = str(date).split()[0].split("-")
        time = str(date).split()[1]
        return {"dateinnum": dateinnum, "time": time, "toshamsidate": date}


class Site_Banks(models.Model):

    title = models.CharField(max_length=350, default="-")
    code = models.CharField(max_length=350, default="-")
    datetime = models.DateTimeField()
    logo_name = models.TextField(default="-")
    act = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class Site_Country(models.Model):

    title = models.CharField(max_length=350, default="-")

    def __str__(self):
        return self.title


class Site_State(models.Model):

    title = models.CharField(max_length=350, default="-")
    country_id = models.CharField(max_length=350, default="-")
    sort = models.IntegerField(default=0)

    @property
    def CountryName(self):
        try:
            return Site_Country.objects.get(pk=self.country_id).title
        except:
            return "-"

    def __str__(self):
        return self.title


class Site_City(models.Model):

    title = models.CharField(max_length=350, default="-")
    country_id = models.CharField(max_length=350, default="-")
    state_id = models.CharField(max_length=350, default="-")

    @property
    def CountryName(self):
        try:
            return Site_Country.objects.get(pk=self.country_id).title
        except:
            return "-"

    @property
    def StateName(self):
        try:
            return Site_State.objects.get(pk=self.state_id).title
        except:
            return "-"

    def __str__(self):
        return self.title


class Site_Static_log(models.Model):

    uname = models.ForeignKey("customer.Customer", on_delete=models.CASCADE, null=True)
    master = models.ForeignKey("master.Master", on_delete=models.CASCADE, null=True)
    desc = models.TextField(default="-")
    date = models.CharField(max_length=150, default="-")
    ip = models.CharField(max_length=100, default="-")
    status = models.CharField(max_length=50, default="primary")
    is_app = models.BooleanField(default=False)
    is_reseller = models.BooleanField(default=False)

    @property
    def ToshamsiDate(self):
        return jdatetime.datetime.fromtimestamp(int(self.date))


class Site_Static_Representation_log(models.Model):

    representation = models.ForeignKey(
        "representation.Representation", on_delete=models.CASCADE, null=True
    )
    office = models.ForeignKey("office.Office", on_delete=models.CASCADE, null=True)
    operator = models.ForeignKey(
        "operators.Operators", on_delete=models.CASCADE, null=True
    )
    desc = models.TextField(default="-")
    date = models.CharField(max_length=150, default="-")
    ip = models.CharField(max_length=100, default="-")
    status = models.CharField(max_length=50, default="primary")
    is_app = models.BooleanField(default=False)

    @property
    def ToshamsiDate(self):
        return jdatetime.datetime.fromtimestamp(int(self.date))


class AboutUs(models.Model):

    txt = models.TextField(default="-")
    desc = models.TextField(default="-")
    pic_name = models.TextField(default="-")
    code = models.IntegerField(default=1000)


class ContactUs(models.Model):

    address = models.CharField(max_length=250, default="-")
    phone = models.CharField(max_length=250, default="-")
    email = models.CharField(max_length=500, default="-")
    location = models.TextField(default="-")
    whatapp = models.TextField(default="-")
    instagram = models.TextField(default="-")
    telegram = models.TextField(default="-")
    code = models.IntegerField(default=1000)

    eta = models.TextField(default="-")
    aparat = models.TextField(default="-")
    youtub = models.TextField(default="-")

    linkdin = models.TextField(default="-")
    twitter = models.TextField(default="-")
    hours_work = models.TextField(default="-")

    text = models.TextField(default="-")


class Customer_Ceiling(models.Model):

    purchase_ceiling = models.IntegerField(default=0)
    sales_ceiling = models.IntegerField(default=0)
    transmission_ceiling = models.FloatField(default=0.0)
    conversion_ceiling = models.IntegerField(default=0)
    increase_ceiling = models.IntegerField(default=0)
    code = models.IntegerField(default=1000)
    calassic_market_ceiling_buy = models.IntegerField(default=0)
    calassic_market_ceiling_sell = models.IntegerField(default=0)


class Site_Gift(models.Model):

    registration_gift = models.CharField(max_length=350, default="-")
    registration_gift_amount = models.FloatField(default=0.0)
    intro_gift = models.CharField(max_length=350, default="-")
    introduced_gift_amount = models.FloatField(default=0.0)
    register_buy = models.IntegerField(default=0)
    introduced_transaction = models.IntegerField(default=0)
    people = models.CharField(max_length=20, choices=[("all", "همه کاربران"), ("up_referral_link", "کاربران معرفی شده")], null=True, blank=True)

    customer_gift = models.CharField(max_length=350, default="-")
    customer_gift_amount = models.FloatField(default=0.0)
    representative_gift = models.CharField(max_length=350, default="-")
    representative_gift_amount = models.FloatField(default=0.0)

    code = models.IntegerField(default=1000)

    app_first_login_amount = models.FloatField(default=0.0)
    app_first_login_wallet = models.CharField(max_length=350, default="-")


class Site_Sms_setting(models.Model):

    kavenegar_apikey = models.TextField(default="-")
    last_modify = models.CharField(max_length=150, default="-")
    code = models.IntegerField(default=1000)
    line_number = models.CharField(max_length=50, default="-")

    @property
    def ToshamsiDate(self):
        return jdatetime.datetime.fromtimestamp(int(self.last_modify))

    @property
    def DecryptText(self):
        return {
            "apikey": decrypt_message(
                bytes(self.kavenegar_apikey[2:].replace("'", ""), "utf-8")
            ),
        }


class Site_Sms_log(models.Model):

    acc = models.CharField(max_length=30, default="-")
    datetime = models.CharField(max_length=150, default="-")
    reciver = models.CharField(max_length=30, default="-")
    pattern = models.CharField(max_length=30, default="-")
    res = models.TextField(default="-")
    success = models.BooleanField(default=False)

    @property
    def ToshamsiDate(self):
        return jdatetime.datetime.fromtimestamp(int(self.datetime))


class Site_Department(models.Model):

    fa_name = models.CharField(max_length=350, default="-")
    na_name = models.CharField(max_length=350, default="-")

    def __str__(self):
        return self.fa_name


class ContactForm(models.Model):

    name = models.CharField(max_length=200, default="-")
    number = models.CharField(max_length=50, default="-")
    department = models.ForeignKey("Site_Department", on_delete=models.CASCADE, null=True)
    txt = models.TextField(default="-")
    ip = models.CharField(max_length=150, null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    datetime = models.CharField(max_length=150, default="-")
    act = models.BooleanField(default=False)

    @property
    def ToshamsiDate(self):
        return jdatetime.datetime.fromtimestamp(int(self.datetime))



class Site_notifications(models.Model):

    title = models.CharField(max_length=350, default="-")
    desc = models.TextField(default="-")
    link = models.TextField(default="-")
    icon_name = models.TextField(default="-")
    master = models.ForeignKey("master.Master", on_delete=models.CASCADE, null=True)
    customer = models.ForeignKey(
        "customer.Customer", on_delete=models.CASCADE, null=True, blank=True
    )
    type = models.CharField(max_length=150, choices=NOTIFICATIONSTYPE, default="Public")
    department = models.CharField(max_length=150, choices=DEPARTMENT, default="-")
    date = models.CharField(max_length=150, default="-")
    code = models.IntegerField(default=1000)
    active = models.BooleanField(default=True)
    is_seen = models.BooleanField(default=False)

    @property
    def ToshamsiDate(self):
        date = jdatetime.datetime.fromtimestamp(int(self.date))
        dateinnum = str(date).split()[0].split("-")
        time = str(date).split()[1]
        dateinletter = JalaliDate(dateinnum[0], dateinnum[1], dateinnum[2]).strftime(
            "%A %D %B %N"
        )
        return {
            "dateinnum": dateinnum,
            "dateinletter": dateinletter,
            "time": time,
            "toshamsidate": date,
        }


class Site_ip(models.Model):

    ip = models.CharField(max_length=100, default="-")
    date = models.CharField(max_length=150, default="-")
    manager = models.CharField(max_length=150, default="-")

    @property
    def ToshamsiDate(self):
        return jdatetime.datetime.fromtimestamp(int(self.date))

    def __str__(self):
        return str(self.ip) + "  |  " + str(self.manager)


class Time_Consulting(models.Model):
    time = models.CharField(max_length=100)

    def __str__(self):
        return self.time




class Ruby_Setting(models.Model):

    ruby = models.CharField(max_length=150, choices=RUBYSETTING, default="Public")
    count_ruby = models.FloatField(default=0.0)
    ruby_txt = models.TextField(default="-")

    @property
    def RubyType(self):

        if self.ruby == "buy":
            return "خرید"
        if self.ruby == "sell":
            return "فروش"
        if self.ruby == "transfer":
            return "انتقال"
        if self.ruby == "exchange":
            return "تبدیل"

        return "نامشخص"


class Exchange_Request(models.Model):

    uname = models.ForeignKey("customer.Customer", on_delete=models.CASCADE, null=True)
    txt = models.TextField(default="-")
    datetime = models.CharField(max_length=150, default="-")
    date = models.CharField(max_length=30, default="-")
    time = models.IntegerField(default=0)
    title = models.CharField(max_length=150, default="-")
    act = models.BooleanField(default=False)

    @property
    def ToshamsiDate(self):
        return jdatetime.datetime.fromtimestamp(int(self.datetime))



class Site_Missions(models.Model):

    title = models.CharField(max_length=200, default="-")
    desc = models.TextField(default="-")
    picture = models.TextField(default="-")
    datetime = models.CharField(max_length=150, default="-")
    status = models.BooleanField(
        default=None, null=True
    )  # None : Not answered / True : accept / False : Reject
    is_done = models.BooleanField(
        default=None, null=True
    )  # True : answered / False : all answered
    for_all = models.BooleanField(default=None)
    master = models.ForeignKey("master.Master", on_delete=models.CASCADE, null=True)
    uname = models.ForeignKey("customer.Customer", on_delete=models.CASCADE, null=True)
    bonus = models.FloatField(default=0.0)
    end_time = models.IntegerField(default=0)
    importance = models.CharField(max_length=150, choices=IMPORTANCE, default="-")
    hour = models.IntegerField(default=0)

    @property
    def ToshamsiDate(self):
        start_date = jdatetime.datetime.fromtimestamp(int(self.datetime))
        end_time = jdatetime.datetime.fromtimestamp(int(self.end_time))
        return {"start_date": start_date, "end_time": end_time}

    @property
    def importanceType(self):

        if self.importance == "Necessary":
            return "ضروری"
        if self.importance == "Important":
            return "مهم"
        if self.importance == "Normal":
            return "معمولی"

        return "نامشخص"

    def __str__(self):
        return self.title


class Site_Path(models.Model):

    title = models.CharField(max_length=200, default="-")
    desc = models.TextField(default="-")
    year = models.IntegerField(default=0)
    datetime = models.CharField(max_length=150, default="-")
    master = models.ForeignKey("master.Master", on_delete=models.CASCADE, null=True)
    act = models.BooleanField(default=False)
    month = models.CharField(max_length=50, default="-")

    @property
    def ToshamsiDate(self):
        return jdatetime.datetime.fromtimestamp(int(self.datetime))


class SitePicture(models.Model):

    picture = models.TextField(default="-")


class Customer_Question(models.Model):

    number = models.CharField(max_length=50, default="-")
    txt = models.TextField(default="-")
    datetime = models.CharField(max_length=150, default="-")
    act = models.BooleanField(default=False)

    @property
    def ToshamsiDate(self):
        return jdatetime.datetime.fromtimestamp(int(self.datetime))



class Ruby_Setting_Fee(models.Model):
    fee_counseling = models.FloatField(default=0)
    code = models.IntegerField(default=0)


class Contact_Users(models.Model):
    name = models.CharField(max_length=150, default="-")
    mobile = models.CharField(max_length=50, default="-")
    act = models.BooleanField(default=False)
    datetime = models.CharField(max_length=150, default="-")

    @property
    def ToshamsiDate(self):
        return jdatetime.datetime.fromtimestamp(int(self.datetime))


class Site_Ruby_Award(models.Model):

    text_award = models.TextField(default="-")
    min_ruby = models.FloatField(default=0.0)
    max_ruby = models.FloatField(default=0.0)
    score = models.FloatField(default=0.0)
    title_gift_mcr_first = models.CharField(max_length=50, default="-")
    title_gift_mcr_second = models.CharField(max_length=50, default="-")
    title_gift_mcr_third = models.CharField(max_length=50, default="-")
    title_gift_mcr_fourth = models.CharField(max_length=50, default="-")

    text_gift_mcr_first = models.CharField(max_length=50, default="-")
    text_gift_mcr_second = models.CharField(max_length=50, default="-")
    text_gift_mcr_third = models.CharField(max_length=50, default="-")
    text_gift_mcr_fourth = models.CharField(max_length=50, default="-")
    text_awards = models.TextField(default="-")

    code = models.IntegerField(default=0)


class InviteUserWithSms(models.Model):

    uname = models.ForeignKey("customer.Customer", on_delete=models.CASCADE, null=True)
    mobile = models.CharField(max_length=50, default="-")
    datetime = models.CharField(max_length=150, default="-")

    @property
    def ToshamsiDate(self):
        try:
            return jdatetime.datetime.fromtimestamp(int(self.datetime))
        except:
            return "-"


class SiteBanner(models.Model):
    banner = models.TextField(default="-")
    url = models.CharField(max_length=350, default="-")


class Daily_Activity_log(models.Model):

    currency = models.ForeignKey("currency.Currency_List", on_delete=models.CASCADE)
    sell_amount = models.FloatField(default=0.0)
    buy_amount = models.FloatField(default=0.0)
    total_price_sell = models.IntegerField(default=0)
    total_price_buy = models.IntegerField(default=0)
    start_datetime = models.CharField(max_length=150, default="-")
    total_price_gateway = models.IntegerField(default=0)
    end_datetime = models.CharField(max_length=150, default="-")

    @property
    def ToshamsiDate(self):

        return {
            "start_time": jdatetime.datetime.fromtimestamp(int(self.start_datetime)),
            "end_time": jdatetime.datetime.fromtimestamp(int(self.end_datetime)),
        }

    def __str__(self):

        toshamsi_date_info = self.ToshamsiDate
        return f"Start Time: {str(toshamsi_date_info['start_time'])}, End Time: {str(toshamsi_date_info['end_time'])}"


class SiteFeatures(models.Model):

    title = models.TextField(default="-")
    desc = models.TextField(default="-")
    datetime = models.CharField(max_length=150, default="-")
    picname = models.CharField(max_length=350, default="-")

    @property
    def ToshamsiDate(self):
        try:
            return jdatetime.datetime.fromtimestamp(int(self.datetime))
        except:
            return self.datetime


class SiteEvidence(models.Model):

    title = models.CharField(max_length=350, default="-")
    desc = models.TextField(default="-")
    picname = models.CharField(max_length=350, default="-")
    date_time = models.CharField(max_length=150, default="-")
    manager = models.CharField(max_length=350, default="-")
    act = models.BooleanField(default=True)
    url = models.CharField(max_length=350, default="-")

    @property
    def ToshamsiDate(self):
        return jdatetime.datetime.fromtimestamp(int(self.date_time))


class UserOpinion(models.Model):

    title = models.CharField(max_length=350, default="-")
    desc = models.TextField(default="-")
    picname = models.CharField(max_length=350, default="-")
    date_time = models.CharField(max_length=150, default="-")
    manager = models.CharField(max_length=350, default="-")
    side = models.CharField(max_length=350, default="-")
    act = models.BooleanField(default=True)

    @property
    def ToshamsiDate(self):
        return jdatetime.datetime.fromtimestamp(int(self.date_time))


class SitePartner(models.Model):

    title = models.CharField(max_length=350, default="-")
    desc = models.TextField(default="-")
    picname = models.CharField(max_length=350, default="-")
    date_time = models.CharField(max_length=150, default="-")
    manager = models.CharField(max_length=350, default="-")
    act = models.BooleanField(default=True)

    @property
    def ToshamsiDate(self):
        return jdatetime.datetime.fromtimestamp(int(self.date_time))


class Site_Photo_Gallery(models.Model):

    picture = models.TextField(default="-")


class Method_Introduction(models.Model):

    title = models.CharField(default="-", max_length=100)
    act = models.BooleanField(default=True)


class Members_Categories(models.Model):

    title = models.CharField(max_length=350, default="-")
    picture = models.CharField(max_length=350, default="-")
    act = models.BooleanField(default=True)
    sort = models.IntegerField(default=0)

    def __str__(self):
        return self.title


class Site_Board_Of_Directors(models.Model):

    name = models.CharField(max_length=400, default="-")
    logo_name = models.TextField(default="-")
    side = models.CharField(max_length=350, default="-")
    datetime = models.DateTimeField()
    category = models.ForeignKey(
        "Members_Categories", on_delete=models.CASCADE, null=True, blank=True
    )
    sort = models.IntegerField(default=0)
    is_ceo = models.BooleanField(default=False)
    act = models.BooleanField(default=True)
    desc = models.TextField(default="-")


class Site_Managers(models.Model):

    name = models.CharField(max_length=400, default="-")
    logo_name = models.TextField(default="-")
    side = models.CharField(max_length=350, default="-")
    datetime = models.DateTimeField()
    category = models.ForeignKey("Members_Categories", on_delete=models.CASCADE)
    sort = models.IntegerField(default=0)
    act = models.BooleanField(default=True)
    desc = models.TextField(default="-")


class Members_Subcategories(models.Model):

    title = models.CharField(max_length=400, default="-")
    datetime = models.DateTimeField()
    category = models.ForeignKey("Members_Categories", on_delete=models.CASCADE)
    sort = models.IntegerField(default=0)
    act = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class Site_Managers_Subset(models.Model):

    name = models.CharField(max_length=400, default="-")
    logo_name = models.TextField(default="-")
    side = models.CharField(max_length=350, default="-")
    datetime = models.DateTimeField()
    category = models.ForeignKey(
        "Members_Categories", on_delete=models.CASCADE, null=True
    )
    subcategory = models.ForeignKey(
        "Members_Subcategories", on_delete=models.CASCADE, null=True
    )
    sort = models.IntegerField(default=0)
    act = models.BooleanField(default=True)
    desc = models.TextField(default="-")


class Site_Cities_With_Represent(models.Model):

    name = models.CharField(max_length=350, default="-")
    logo_name = models.TextField(default="-")
    act = models.BooleanField(default=True)
    established = models.BooleanField(default=True)
    sort = models.IntegerField(default=0)

    def __str__(self):
        return self.name
    

class Site_Branches_Deliverer(models.Model):
    
    first_name = models.CharField(max_length=350, default="-")
    last_name =  models.CharField(max_length=350, default="-")
    personal_code =  models.CharField(max_length=50, default="-")
    organizational_position = models.CharField(max_length=350, default="-")
    act = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Site_Branches_Each_Representative(models.Model):

    name = models.CharField(max_length=350, default="-")
    address = models.TextField(default="-")
    city = models.ForeignKey("Site_Cities_With_Represent", on_delete=models.CASCADE)
    act = models.BooleanField(default=True)
    datetime = models.CharField(max_length=150, default="-")
    working_time = models.TextField(default="-")
    phone_numbers = models.CharField(max_length=500, default="-")
    manager = models.ManyToManyField(Master, blank=True)
    deliverer = models.ForeignKey(Site_Branches_Deliverer, on_delete=models.CASCADE, null=True)
    picture = models.TextField(default="-")
    location = models.TextField(default="-")


    def __str__(self):
        return f'{self.name}'
    
class BranchImage(models.Model):

    picture = models.TextField(default="-")
    branch = models.ForeignKey("Site_Branches_Each_Representative", on_delete=models.CASCADE)


class BranchPersonel(models.Model):

    first_name = models.CharField(max_length=350, default="-")
    last_name =  models.CharField(max_length=350, default="-")    
    organizational_position = models.CharField(max_length=350, default="-")
    branch = models.ForeignKey("Site_Branches_Each_Representative", on_delete=models.CASCADE)
    datetime = models.CharField(max_length=150, default="-")
    picname = models.CharField(max_length=350, default="-")

    @property
    def ToshamsiDate(self):
        try:
            return jdatetime.datetime.fromtimestamp(int(self.datetime))
        except:
            return self.datetime


class Site_Branch_Working_Days(models.Model):

    capacity = models.IntegerField(default=0)
    branch = models.ForeignKey("Site_Branches_Each_Representative", on_delete=models.CASCADE)
    act = models.BooleanField(default=True)
    working_date = models.CharField(max_length=150, default="-")

    jalali_date = models.CharField(max_length=20, null=True, blank=True)  # تاریخ شمسی
    weekday = models.CharField(max_length=10, null=True, blank=True)  # روز هفته

    @property
    def week_day(self):

        if self.weekday == 'Monday':
            return 'دوشنبه'
        if self.weekday == 'Tuesday':
            return 'سه‌شنبه'
        if self.weekday == 'Wednesday':
            return 'چهارشنبه'
        if self.weekday == 'Thursday':
            return 'پنج‌شنبه'
        if self.weekday == 'Friday':
            return 'جمعه'
        if self.weekday == 'Saturday':
            return 'شنبه'
        if self.weekday == 'Sunday':
            return 'یکشنبه'

     

    @property
    def ToshamsiDate(self):
        return jdatetime.datetime.fromtimestamp(int(self.working_date))

    def __str__(self):
        return str(self.ToshamsiDate)


class Site_Products(models.Model):

    title = models.CharField(max_length=400, default="-")
    logo_name = models.TextField(default="-")
    act = models.BooleanField(default=False)
    city = models.ForeignKey(
        Site_Cities_With_Represent, on_delete=models.CASCADE, null=True
    )
    cutie = models.IntegerField(default=0)  # عیار
    grams = models.FloatField(default=0.0)  # گرم
    fee = models.FloatField(default=0.0)
    type_gold = models.CharField(max_length=50, choices=GOLDS, default="-")

    wages = models.FloatField(
        default=0.0, null=True, blank=True
    )  # برای شمش و سکه، اجرت

    tracking_code = models.TextField(null=True, blank=True)  # برای آبشده
    desc = models.TextField(null=True, blank=True)  # برای آبشده

    branch = models.ForeignKey(
        Site_Branches_Each_Representative, on_delete=models.SET_NULL, null=True
    )

    pure_grams = models.FloatField(default=0.0, blank=True)
    lab = models.CharField(max_length=350, default="-")

    @property
    def TypeOfGold(self):

        if self.type_gold == "gold1":
            return "آبشده"
        if self.type_gold == "gold2":
            return "سکه"
        if self.type_gold == "gold3":
            return "شمش"

        return "نامشخص"

    def __str__(self):
        return self.title


class Site_Product_Inventory(models.Model):

    product = models.ForeignKey(Site_Products, on_delete=models.CASCADE, null=True)
    quantity = models.IntegerField(default=0)
    datetime = models.CharField(max_length=150, default="-")

    @property
    def ToshamsiDate(self):
        return jdatetime.datetime.fromtimestamp(int(self.datetime))


class PriceMonitoring(models.Model):
    manager = models.ForeignKey(Master, on_delete=models.CASCADE)
    current_price = models.IntegerField(default=0)
    controlled_price = models.IntegerField(default=0)
    desc = models.TextField(default="-")
    datetime = models.CharField(max_length=150, default="-")

    @property
    def ToshamsiDate(self):
        return jdatetime.datetime.fromtimestamp(int(self.datetime))

    def __str__(self):
        return f"{self.manager}"


class Slider(models.Model):
    title = models.CharField(max_length=255, default="-")
    url = models.CharField(max_length=350, default="-")
    picname = models.CharField(max_length=350, default="-")
    act = models.BooleanField(default=False)
    sort = models.IntegerField(default=0)

    def __str__(self):
        return self.title


REPORT_DISCREPANCY_STATUS = [
    ('0', "در انتظار"),
    ('1', "تایید شده"),
    ('2', "رد شده"),
]

class ReportDiscrepancy(models.Model):
    
    order = models.ForeignKey('customer.Customer_Gold_Order', on_delete=models.CASCADE, related_name="report_discrepancy", null=True, blank=True)
    full_name = models.CharField(max_length=250, default="-")
    mobile = models.CharField(max_length=150, default="-") 
    desc = models.TextField(default="-") 
    status = models.CharField(max_length=150, choices=REPORT_DISCREPANCY_STATUS, default=0)
    
    created_at = models.CharField(max_length=150, default="-")
    updated_at = models.CharField(max_length=150, default="-")

    @property
    def ToshamsiDate(self):
        try:
            create_at = jdatetime.datetime.fromtimestamp(int(self.created_at)) if self.created_at != '-' else '-'
            update_at = jdatetime.datetime.fromtimestamp(int(self.updated_at)) if self.updated_at != '-' else '-'
            return {'create_at': create_at, 'update_at': update_at}
        except: return {'create_at': '-', 'update_at': '-'}

    def __str__(self):
        return self.full_name



class Motivational_Quotes(models.Model):
    text = models.TextField(default="-")
    act = models.BooleanField(default=True)

    def __str__(self):
        return self.text


class Time_Based_Ceiling(models.Model):


    type_ceiling = models.CharField(max_length=150, default="-")
    amount = models.IntegerField(default=0)
    master = models.ForeignKey(Master, on_delete=models.CASCADE,null=True,blank=True)
    start_time = models.TimeField(null=False, blank=False)
    end_time = models.TimeField(null=False, blank=False)
    act = models.BooleanField(default=True)

    @property
    def ToTypeShow(self):

        if self.type_ceiling == 'buy' : return 'خرید'
        if self.type_ceiling == 'sell' : return 'فروش'
        if self.type_ceiling == 'increas' : return 'افزایش اعتبار'


class Direct_Transfer_Card(models.Model):
    master = models.ForeignKey(Master, on_delete=models.CASCADE)
    card_name = models.CharField(max_length=150, default="-")
    iban_number = models.CharField(max_length=150, default="-")
    desc = models.CharField(max_length=300, default="-")
    act = models.BooleanField(default=False)
    datetime = models.CharField(max_length=150, default="-")

    @property
    def ToshamsiDate(self):
        return jdatetime.datetime.fromtimestamp(int(self.datetime))
    


class RewardCode(models.Model):

    uname = models.ForeignKey("customer.Customer", on_delete=models.CASCADE, null=True)
    code = models.CharField(max_length=12, unique=True) 
    used = models.BooleanField(default=False)
    datetime = models.CharField(max_length=150, default="-")
    used_datetime = models.CharField(max_length=150, default="-")
    wallet = models.CharField(max_length=50,default="-")
    amount = models.FloatField(default=0.0)

    @property
    def ToshamsiDate(self):
        try:
            create_at = jdatetime.datetime.fromtimestamp(int(self.datetime)) if self.datetime  != '-' else '-'
            used_datetime = jdatetime.datetime.fromtimestamp(int(self.used_datetime)) if self.used_datetime != '-' else '-'
            return {'create_at': create_at, 'used': used_datetime}
        except: return {'create_at': '-', 'used': '-'}

class Bank_Resources_Receipt(models.Model):

    gram_amount = models.FloatField(default=0.0)
    equivalent_gram_amount = models.FloatField(default=0.0)
    picname = models.CharField(max_length=350,default="-")
    date = models.CharField(max_length=150,default="1719741445")


    def __str__(self):
        return f"وزن خالص: {self.gram_amount}"

    @property
    def ToshamsiDate(self):
        date = jdatetime.datetime.fromtimestamp(int(self.date))
        dateinnum = str(date).split()[0]
        time = str(date).split()[1]
        return {'dateinnum':dateinnum, 'time':time, 'toshamsidate':date}  
    