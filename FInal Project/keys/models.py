# -*- coding: utf-8 -*-
from django.db import models


class Keys(models.Model):
    user = models.CharField(max_length=20)
    key_name = models.CharField(max_length=20)
    release = models.IntegerField(default=0)
    timestamp = models.BigIntegerField(default=0)
    widgetName = models.CharField(max_length=20)
    iteration = models.CharField(max_length=30, null=True)
    genuine = models.IntegerField(default=1)
    decision = models.CharField(max_length=50, default='')


class Impostors_Keys(models.Model):
    ip = models.CharField(max_length=20)
    claimed_id = models.CharField(max_length=20)
    key_name = models.CharField(max_length=20)
    release = models.IntegerField(default=0)
    timestamp = models.BigIntegerField(default=0)
    widgetName = models.CharField(max_length=20)
    intention = models.CharField(max_length=30)


class Temp_Keys(models.Model):
    user = models.CharField(max_length=20)
    key_name = models.CharField(max_length=20)
    release = models.IntegerField(default=0)
    timestamp = models.BigIntegerField(default=0)
    widgetName = models.CharField(max_length=20)
    iteration = models.CharField(max_length=3, null=True)


class Data(models.Model):
    ip = models.CharField(max_length=20)
    key_name = models.CharField(max_length=20)
    release = models.IntegerField(default=0)
    timestamp = models.BigIntegerField(default=0)
    widgetName = models.CharField(max_length=20)
    iteration = models.CharField(max_length=3, null=True)


class LoginAttempt(models.Model):
    ip = models.CharField(max_length=20)
    claimed_id = models.CharField(max_length=20)
    timestamp = models.BigIntegerField(default=0)
    score = models.FloatField(default=0)
    threshold = models.FloatField()
    status = models.CharField(max_length=50)


class RecoveryAttempt(models.Model):
    ip = models.CharField(max_length=20)
    claimed_id = models.CharField(max_length=20)
    timestamp = models.BigIntegerField(default=0)
    score = models.FloatField(default=0)
    threshold = models.FloatField()
    status = models.CharField(max_length=50)


class Input(models.Model):
    memberID = models.CharField(max_length=30)
    fname = models.CharField(max_length=30)
    lname = models.CharField(max_length=30)
    dob = models.DateField(null=True)
    address = models.CharField(max_length=60)
    city = models.CharField(max_length=30)
    state = models.CharField(max_length=2)
    zipcode = models.IntegerField(default=0)
    country = models.CharField(max_length=3, null=True)
    mail = models.CharField(max_length=50)
    phone = models.CharField(max_length=13)


class Temp_Input(models.Model):
    memberID = models.CharField(max_length=30)
    fname = models.CharField(max_length=30)
    lname = models.CharField(max_length=30)
    dob = models.DateField(null=True)
    address = models.CharField(max_length=60)
    city = models.CharField(max_length=30)
    state = models.CharField(max_length=2)
    zipcode = models.IntegerField(default=0)
    country = models.CharField(max_length=3, null=True)
    mail = models.CharField(max_length=50)
    phone = models.CharField(max_length=13)


class Users(models.Model):
    memberID = models.CharField(max_length=30)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    dob = models.DateField(null=True)
    address = models.CharField(max_length=60)
    city = models.CharField(max_length=30)
    state = models.CharField(max_length=2)
    zipcode = models.IntegerField(default=0)
    country = models.CharField(max_length=3, null=True)
    mail = models.CharField(max_length=50)
    phone = models.CharField(max_length=13)
    username = models.CharField(max_length=50)
    pwd_status = models.IntegerField(default=0)
    password = models.CharField(max_length=1000)
    login_template = models.IntegerField(default=0)
    AR_template = models.IntegerField(default=0)
    otp = models.IntegerField(default=0)
    expire_at = models.BigIntegerField(default=0)
    login_attempt = models.IntegerField(default=0)
    login_weekly_task_left = models.IntegerField(default=20)
    login_attacked = models.IntegerField(default=0)
    AR_attempt = models.IntegerField(default=0)
    AR_weekly_task_left = models.IntegerField(default=5)
    AR_attacked = models.IntegerField(default=0)
    last_visited = models.CharField(max_length=30, default="02/17/2021")


class Temp_User(models.Model):
    memberID = models.CharField(max_length=30)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    dob = models.DateField(null=True)
    address = models.CharField(max_length=60)
    city = models.CharField(max_length=30)
    state = models.CharField(max_length=2)
    zipcode = models.IntegerField(default=0)
    country = models.CharField(max_length=3, null=True)
    mail = models.CharField(max_length=50)
    phone = models.CharField(max_length=13)
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=1000)
    activation = models.IntegerField(default=0)


class Mouse(models.Model):
    user = models.CharField(max_length=30)
    event = models.CharField(max_length=30, null=True)  # Mount enter, mouse leave
    x_pos = models.IntegerField(default=None, null=True)  # x position of the mouse
    y_pos = models.IntegerField(default=None, null=True)  # y position of the mouse
    widgetType = models.CharField(max_length=30, default=None, null=True)  # E.g.Text box, Image etc
    widgetName = models.CharField(max_length=30, default=None, null=True)  # E.g. Tasks, Prompts, keyboards
    page = models.CharField(max_length=30, default='')  # home, registration, keyboards, tasks, prompts
    resolution = models.CharField(default=None, max_length=20, null=True)
    timestamp = models.BigIntegerField(default=0)
    genuine = models.IntegerField(default=1)
    decision = models.CharField(max_length=50, default='')
    iteration = models.CharField(max_length=30, default='')


class Temp_Mouse(models.Model):
    user = models.CharField(max_length=30)
    event = models.CharField(max_length=30, null=True)  # Mount enter, mouse leave
    x_pos = models.IntegerField(default=None, null=True)  # x position of the mouse
    y_pos = models.IntegerField(default=None, null=True)  # y position of the mouse
    widgetType = models.CharField(max_length=30, default=None, null=True)  # E.g.Text box, Image etc
    widgetName = models.CharField(max_length=30, default=None, null=True)  # E.g. Tasks, Prompts, keyboards
    page = models.CharField(max_length=30, default='')  # home, registration, keyboards, tasks, prompts
    resolution = models.CharField(default=None, max_length=20, null=True)
    timestamp = models.BigIntegerField(default=0)
    # genuine = models.IntegerField(default=0)
    iteration = models.CharField(max_length=50, default='')


class Dropdown(models.Model):
    user = models.CharField(max_length=30)
    widgetName = models.CharField(max_length=32)
    action = models.CharField(max_length=32)
    widgetStatus = models.CharField(max_length=16)
    timestamp = models.BigIntegerField(default=0)
    genuine = models.IntegerField(default=0)
    decision = models.CharField(max_length=50, default='')
    iteration = models.CharField(max_length=50, default='')


class Temp_Dropdown(models.Model):
    user = models.CharField(max_length=30)
    widgetName = models.CharField(max_length=32)
    action = models.CharField(max_length=32)
    widgetStatus = models.CharField(max_length=16)
    timestamp = models.BigIntegerField(default=0)
    iteration = models.CharField(max_length=32, default='')


class Attacks(models.Model):
    attacker = models.CharField(max_length=16)
    attacks = models.CharField(max_length=16)
    login_attempts = models.IntegerField(default=0)
    AR_attempts = models.IntegerField(default=0)
