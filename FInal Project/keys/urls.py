# -*- coding: utf-8 -*-
# from __future__ import unicode_literals

from django.urls import re_path

from django.urls import path

from . import views

urlpatterns = [
    re_path(r'^listen', views.listen, name='listen'),
    re_path(r'^temp_keys_listen', views.temp_keys_listen, name='temp_keys_listen'),
    re_path(r'^dropdwnln', views.dropdwnln, name='dropdwnln'),
    re_path(r'^dropdwnlisten2', views.dropdwnlisten2, name='dropdwnlisten2'),
    re_path(r'^listn2', views.listn2, name='listn2'),
    re_path(r'^mousee', views.mousee, name='mousee'),
    re_path(r'^mousee2', views.mousee2, name='mousee2'),
    re_path(r'^signup1', views.say_hello, name='say_hello'),
    re_path(r'^signup1', views.signup1, name='signup1'),    
    re_path(r'^signup2', views.signup2, name='signup2'),
    re_path(r'^forgotpwd1', views.forgotpwd1, name='forgotpwd1'),
    re_path(r'^forgotpwd2', views.forgotpwd2, name='forgotpwd2'),
    re_path(r'^forgotpwd3', views.forgotpwd3, name='forgotpwd3'),
    re_path(r'^forgotpwd4', views.forgotpwd4, name='forgotpwd4'),
    re_path(r'^resendEmail', views.resendEmail, name='resendEmail'),
    re_path(r'^email_resend', views.email_resend, name='email_resend'),
    re_path(r'^email_verification', views.email_verification, name='email_verification'),
    re_path(r'^success2', views.success2, name='success2'),
    re_path(r'^participant_list', views.participant_list, name='participant_list'),
    re_path(r'^attack_list', views.attack_list, name='attack_list'),
    re_path(r'^sendUserReminder', views.sendUserReminder, name='sendUserReminder'),
    re_path(r'^sendAttackReminder', views.sendAttackReminder, name='sendAttackReminder'),
    re_path(r'^landingpage', views.landingpage, name='landingpage'),
    re_path(r'^update_session', views.update_session, name='update_session'),
    
]
