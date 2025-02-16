from django.contrib.sitemaps import Sitemap
from django.shortcuts import reverse
import urllib
from currency.models import *
from datetime import datetime, timedelta
import pytz
from exchange.func.public import get_date_time

class ExchangeSiteMap(Sitemap):

    priority = 0.5

    def items(self):
        return ['', '/account/', '/application/', '/about-us/', '/contact-us/', '/academy/', '/faq/']
    
    def lastmod(self, obj):
        return datetime.now()
    
    def location(self, item):
        return item


