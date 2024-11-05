#

import datetime

from django.db import models


class Appp(models.Model):

    app_status = models.IntegerField(default=0)
    type_proc = models.IntegerField(default=0)

    dogovor = models.CharField(max_length=10, blank=True)
    n_order = models.CharField(max_length=12, blank=True)

    street = models.CharField(max_length=30)
    build = models.CharField(max_length=10)
    kv = models.CharField(max_length=6, blank=True)
    fio = models.CharField(max_length=320, blank=True)
    prim = models.CharField(max_length=180, blank=True)
    comment = models.CharField(max_length=360, blank=True)
    resource = models.CharField(max_length=2048, blank=True)
    pause_type = models.CharField(max_length=40, blank=True)
    box_port = models.IntegerField(default=0)

    man_oper = models.CharField(max_length=30, blank=True)
    man_install = models.CharField(max_length=30, blank=True)

    date_1 = models.DateTimeField(default=datetime.datetime.now)    #принято
    date_2 = models.DateTimeField(default=datetime.datetime.now)    #обработано
    date_3 = models.DateTimeField(default=datetime.datetime.now)    #выполнено

    def __str__(self):
        return f"{self.id} | {self.dogovor} | {self.street} {self.build} kv:{self.kv}"
