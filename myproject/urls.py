"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf.urls.static import static
from django.conf import settings
from django.views.static import serve
from customer.models import *
# from django_otp.admin import OTPAdminSite
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import  Permission
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied
from ticket.models import *
from django.contrib.sitemaps.views import sitemap
from django.contrib.sitemaps import views
from exchange.sitemaps import *
from django.views.generic.base import TemplateView

def protected_file(request, path, document_root=None, show_indexes=False):

    userPermCodes = [x.codename for x in Permission.objects.filter(user=request.user)]
    if "master_exchange_access" in userPermCodes : return serve(request, path, document_root, show_indexes)
    raise PermissionDenied()  

sitemaps = {

    'exchange': ExchangeSiteMap,

}

urlpatterns = [

    path('superadminPanel/', admin.site.urls),

    path('', include('exchange.urls')),
    path('', include('master.urls')),
    path('', include('currency.urls')),
    path('', include('customer.urls')),
    path('', include('wallet.urls')),
    path('', include('ticket.urls')),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    re_path(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}),
    re_path(r'^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}),
    re_path(r'^icon/(?P<path>.*)$', serve,{'document_root': settings.ICON_ROOT}),
    re_path(r'^usermedia/(?P<path>.*)$', protected_serve,{'document_root': settings.USERMEDIA_ROOT}),
    re_path (r'^%s(?P<path>.*)$' % settings.FILEMEDIA_URL[1:], protected_file, {'document_root': settings.FILEMEDIA_ROOT}),

    re_path(r'^podcast/(?P<path>.*)$', serve,{'document_root': settings.PODCAST_ROOT}),

    path(
        "sitemap.xml",
        views.sitemap,
        {"sitemaps": sitemaps, "template_name": "custom_sitemap.html"},
        name="django.contrib.sitemaps.views.sitemap",
    ),

    path("robots.txt",TemplateView.as_view(template_name="robots.txt",content_type="text/plain"),),
# ]
]


if settings.DEBUG:

    urlpatterns += static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.USERMEDIA_URL,document_root=settings.USERMEDIA_ROOT)
    urlpatterns += static(settings.FILEMEDIA_URL,document_root=settings.FILEMEDIA_ROOT)
    urlpatterns += static(settings.PODCAST_URL,document_root=settings.PODCAST_ROOT)

