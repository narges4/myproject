from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from customer.models import *
import jdatetime
from master.models import *
from khayyam import *

TICKETDEPARTMENT = [
    ('dep1','پشتیبانی مشتریان'),
    ('dep2','امور مالی'),
    ('dep3','آموزش و مشاوره تخصصی'),
    ('dep4','انتقادات و پیشنهادات'),
    ('dep5','ارسال شکایات به واحد نظارت'),
    ('dep6','دفتر مدیرعامل'),

    ('dep7','پشتیبانی مشتریان'),
    ('dep8','مشارکت'),
    ('dep9','شکایت ,انتقادات و پیشنهادات'),
    ('dep10','دفتر مدیرعامل'),
]


TICKETSTATUS = [
    ('Closed','Closed'),
    ('Ckecking','Ckecking'),
    ('Answered','Answered'),
    ('Waitting','Waitting'),
    ('FromMaster','FromMaster'),
] 


TICKETRATE = [
    ('Excellent','Excellent'),
    ('Good','Good'),
    ('Average','Average'),
    ('Bad','Bad'),
    ('VeryBad','VeryBad'),
]


class Ticket(models.Model):
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)
    master = models.ForeignKey(Master, on_delete=models.CASCADE, null=True, blank=True, related_name='ticket')
    crm = models.ForeignKey(Master, on_delete=models.CASCADE, null=True, blank=True, related_name='ticket_crm')
    title = models.CharField(max_length=250,default="-")
    date = models.CharField(max_length=150, default='-')
    last_update = models.CharField(max_length=50,default="-")
    department = models.CharField(max_length=50,choices=TICKETDEPARTMENT, default="Support")
    status = models.CharField(max_length=50,choices=TICKETSTATUS, default="Waitting")
    rate = models.CharField(max_length=50,choices=TICKETRATE, null=True, blank=True)
    count = models.IntegerField(default=0)
    from_master = models.BooleanField(default=False)
    is_show = models.BooleanField(default=True)
    descriptipn = models.TextField(default="-")
    
    @property
    def ToshamsiDate(self):
        date = jdatetime.datetime.fromtimestamp(int(self.date))
        lastdate = jdatetime.datetime.fromtimestamp(int(self.last_update))
        dateinnum = str(date).split()[0].split('-')
        lastdateinnum = str(lastdate).split()[0].split('-')
        time = str(date).split()[1]
        lasttime = str(lastdate).split()[1]
        dateinletter = JalaliDate(dateinnum[0], dateinnum[1], dateinnum[2]).strftime('%A %D %B %N')
        lastdateinletter = JalaliDate(lastdateinnum[0], lastdateinnum[1], lastdateinnum[2]).strftime('%A %D %B %N')
        return {'dateinnum':dateinnum,'dateinletter':dateinletter, 'time':time, 'toshamsidate':date, 'lastdateinletter':lastdateinletter}
    

    @property
    def TickateStatus(self):

        if self.status == 'Answered' : return {'status':'پاسخ داده شده','color':'green'}
        if self.status == 'FromMaster' : return {'status':'ارسال شده','color':'orange'}
        if self.status == 'Waitting' : return {'status':'در انتظار بررسی','color':'orange'}
        if self.status == 'Ckecking' : return {'status':'در حال پیگیری','color':'orange'}
        if self.status == 'Closed' : return {'status':'بسته شده','color':'red'}

        return {'status':'نامشخص','color':'primary'} 

    @property
    def TickateDepartment(self):

        if self.department == 'dep1' : return {'department':'پشتیبانی مشتریان' }
        if self.department == 'dep2' : return {'department':'امور مالی' }
        if self.department == 'dep3' : return {'department':'آموزش و مشاوره تخصصی' }
        if self.department == 'dep4' : return {'department':'انتقادات و پیشنهادات' }
        if self.department == 'dep5' : return {'department':'ارسال شکایات به واحد نظارت' }
        if self.department == 'dep6' : return {'department':'دفتر مدیرعامل' }


        if self.department == 'dep7' : return {'department':'پشتیبانی مشتریان' }
        if self.department == 'dep8' : return {'department':'مشارکت'}
        if self.department == 'dep9' : return {'department':'شکایت ,انتقادات و پیشنهادات' }
        if self.department == 'dep10' : return {'department':'دفتر مدیرعامل' }

        return {'department':'نامشخص','color':'primary'} 

    @property
    def TickateType(self):
        if self.customer != None and self.master == None : return {'type':'user'}
        if self.master != None and self.customer != None : return {'type':'admin'}

        return {'status':'نامشخص','color':'primary'} 

    def __str__(self):
        return self.title 


class Sticker(models.Model):
    
    file_name = models.CharField(max_length=350,default="-")
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.file_name


class Ticket_answer(models.Model):
    
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)
    master = models.ForeignKey(Master, on_delete=models.CASCADE, null=True, blank=True)
    desc = models.TextField(default="-")
    sticker = models.ForeignKey(Sticker, on_delete=models.CASCADE, null=True, blank=True)
    date = models.CharField(max_length=150, default='-')
    file_name = models.CharField(max_length=350,default="-")
    file_url = models.CharField(max_length=350,default="-")

    @property
    def ToshamsiDate(self):
        date = jdatetime.datetime.fromtimestamp(int(self.date))
        dateinnum = str(date).split()[0].split('-')
        time = str(date).split()[1]
        dateinletter = JalaliDate(dateinnum[0], dateinnum[1], dateinnum[2]).strftime('%A %D %B %N')
        return {'dateinnum':dateinnum,'dateinletter':dateinletter, 'time':time, 'toshamsidate':date}
    
        
    @property
    def TickateAnswerType(self):
        if self.customer != None and self.master == None : return {'type':'user'}
        if self.master != None and self.customer == None : return {'type':'admin'}
        if self.master != None and self.customer != None : return {'type':'admin'}

        return {'status':'نامشخص','color':'primary'} 

    def __str__(self):
        return self.ticket.title 

