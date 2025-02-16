from __future__ import unicode_literals
from django.db import models
from exchange.models import *
import jdatetime
from django.contrib.auth.models import User


class Master(models.Model):
    
    first_name = models.CharField(max_length=350,default="-")
    last_name = models.CharField(max_length=350,default="-")
    nick_name = models.CharField(max_length=350,default="-")
    position = models.CharField(max_length=350,default="-")
    national_id = models.CharField(max_length=15,default="-")
    mobile = models.CharField(max_length=15,default="-")
    req_user = models.CharField(max_length=350,default="-")
    last_modify = models.CharField(max_length=150,default="-")
    last_ip = models.CharField(max_length=100,default="-")
    last_code = models.CharField(max_length=50,default="-")
    last_code_datetime = models.CharField(max_length=150,default="-")
    is_force_code_verify = models.BooleanField(default=False)
    profile_pic_name = models.CharField(max_length=250,default="-")
    about = models.TextField(default="-")
    is_master = models.BooleanField(default=False)
    master_agent = models.TextField(default="-")
    internal_number = models.IntegerField(default=0)
    customer_communication_goals = models.ManyToManyField('customer.Customer_Relationship_Goal', blank=True, related_name='related_customer_goals')
    department = models.ForeignKey('master.support_Category', on_delete=models.CASCADE,null=True, blank=True)
    is_toverification = models.BooleanField(default=False)
    is_toverification_requird = models.BooleanField(default=False)
    crm_expert = models.BooleanField(default=False)
    pyotp_hash = models.CharField(max_length=350,default="-")
    master_ip = models.ManyToManyField('exchange.Site_ip', blank=True)

    @property
    def ToshamsiDate(self):
        try : return jdatetime.datetime.fromtimestamp(int(self.last_modify))
        except : return "نامشخص"

    def __str__(self):
        return f'{self.first_name} {self.last_name}'
   
