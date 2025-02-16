from exchange.models import *


def get_front_theme():

    return "front/fa/theme-01/"


def get_customer_theme(customer=None):

    if customer and customer.is_from_pwa == True :
        return get_pwa_theme()

    return "customer/fa/theme-02/"


def get_master_theme():

    return "master/fa/theme-01/"


def get_representation_theme():

    return "representation/fa/theme-01/"


def get_office_theme():

    return "office/fa/theme-01/"


def get_operator_theme():

    return "operator/fa/theme-01/"



def get_pwa_theme():
    return "pwa/fa/theme-01/"
