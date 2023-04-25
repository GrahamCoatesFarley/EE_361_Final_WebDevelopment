# -*- coding: utf-8 -*-
# encoding = utf8
import datetime
import random
import re
import time
from datetime import date, datetime as dt
from math import floor

# from background_task import background
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db.models import F
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template import loader
from django.template.loader import get_template
from django.utils.datastructures import MultiValueDictKeyError
from django.views.decorators.csrf import csrf_exempt
from fuzzywuzzy import fuzz
from twilio.rest import Client
from keys.database_helper import *

from keys.manhattan import manhattan
from keys.models import Input
from keys.models import Keys, Users, Temp_User, Temp_Keys, Temp_Input, Temp_Mouse, Data, RecoveryAttempt, LoginAttempt, \
    Impostors_Keys, Dropdown, Temp_Dropdown, Attacks
from keys.models import Mouse

# Global parameters
REPEAT1 = 5
REPEAT2 = 5
REPEAT3 = 10
min_enrol = 5
recoveryThreshold = 1.2
loginThreshold = 0.6
weeklyLogin = 20
weeklyAR = 5
total = 10
INTERVAL = 30
testdetails = {}


# @background(schedule=0)
def SaveAsImpostorKeys(ip_address, claimed_id, iteration, intention):
    """ Save impostor keystrokes data """
    keys = Data.objects.filter(ip=ip_address, iteration=iteration)
    # Get last attempt number
    user = Users.objects.get(memberID=claimed_id)
    imp_attempts_no = user.imp_attempts_no + 1
    Users.objects.filter(memberID=claimed_id).update(imp_attempts_no=imp_attempts_no)
    if keys:
        for i in keys:
            imp_keys = Impostors_Keys(ip=ip_address, claimed_id=claimed_id, key_name=i.key_name, release=i.release,
                                      timestamp=i.timestamp, widgetName=i.widgetName,
                                      intention=iteration + str(imp_attempts_no))
            imp_keys.save()
        Data.objects.filter(ip=ip_address, iteration=iteration).delete()



    
def say_hello(request):
    states = get_all_states()
    state_s = {}
    names=[]
    for i in states:
        state_s[i['code']] = i['name']
        names.append(i['name'])
                
    return render(request, 'signup1.html' , {'data': state_s})


def clear(ip_address):
    Data.objects.filter(ip=ip_address).delete()


def getIP(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip_address = x_forwarded_for.split(',')[0]
    else:
        ip_address = request.META.get('REMOTE_ADDR')
    request.session['ip_address'] = ip_address
    return ip_address


def checkWeeklyTasks(request):
    context = ''
    loginWeeklyTaskLeft = -1
    all_users_list = Users.objects.all()
    for user in all_users_list:
        f_name = str(user.first_name.lower()) + ' ' + str(user.last_name.lower())
        if fuzz.ratio(f_name, request.session['sessionUserFullname'].lower()) > 80:
            """Found the user"""
            d1 = datetime.datetime.strptime(date.today().strftime("%m/%d/%Y"), "%m/%d/%Y")  # Current time
            d2 = datetime.datetime.strptime(user.last_visited, "%m/%d/%Y")  # Last visited
            if abs((d2 - d1).days) >= 1:
                # update last visited and reset weekly tasks
                Users.objects.filter(memberID=user.memberID).update(last_visited=date.today().strftime("%m/%d/%Y"))
                if user.login_attempt < 100:
                    if (100 - user.login_attempt) < weeklyLogin:
                        Users.objects.filter(memberID=user.memberID).update(
                            login_weekly_task_left=(100 - user.login_attempt))
                    else:
                        Users.objects.filter(memberID=user.memberID).update(login_weekly_task_left=weeklyLogin)
                if user.AR_attempt < 20:
                    if (20 - user.AR_attempt) < weeklyAR:
                        Users.objects.filter(memberID=user.memberID).update(AR_weekly_task_left=(20 - user.AR_attempt))
                    else:
                        Users.objects.filter(memberID=user.memberID).update(AR_weekly_task_left=weeklyAR)
                loginWeeklyTaskLeft = weeklyLogin
                recovWeeklyTaskLeft = weeklyAR
            else:
                loginWeeklyTaskLeft = user.login_weekly_task_left
            context = {'showWelcomeMessage': False, 'tasksleft': loginWeeklyTaskLeft}
            break
        else:
            context = {'showWelcomeMessage': False, 'tasksleft': loginWeeklyTaskLeft}  # Unregistered user
    return context


def useKeystrokesDynamics(request, ip_address, username, pwd, phone, email, isTrueUser, user):
    context = {}
    # Get profile keystrokes
    all_keys = Keys.objects.filter(user=attempt_user)
    p1 = sorted([(i.timestamp, i.key_name, i.release) for i in all_keys if i.release == 0 and
                 i.widgetName == 'userName' and i.genuine == 1 and i.decision == 'granted'])
    p2 = sorted([(i.timestamp, i.key_name, i.release) for i in all_keys if i.release == 0 and
                 (
                         i.widgetName == 'password' or i.widgetName == 'reTypePwd') and i.genuine == 1 and i.decision == 'granted'])

    # Get test samples
    samples = Data.objects.filter(ip=ip_address)
    s1 = sorted([(i.timestamp, i.key_name, i.release) for i in samples if
                 i.release == 0 and (i.widgetName == 'userName')])
    s2 = sorted([(i.timestamp, i.key_name, i.release) for i in samples if
                 i.release == 0 and (i.widgetName == 'password' or i.widgetName == 'reTypePwd')])
    # calculate distance score
    score1, sharedDigraph1 = manhattan(p1, s1)
    if score1 != -1:
        score2, sharedDigraph2 = manhattan(p2, s2)
        if score2 != -1:
            c = sharedDigraph1 + sharedDigraph2
            w1 = sharedDigraph1 / c
            w2 = sharedDigraph2 / c
            distance_score = (w1 * score1 + w2 * score2) * 0.5

            min_digraph = floor(0.8 * (len(username) + len(pwd)))  # 80% shared digraph
            if c >= min_digraph:
                # Get the last iteration in DB
                lastAttempt = (
                    Keys.objects.filter(user=attempt_user, iteration__startswith='UL').last()).iteration
                lastAttempt = int(lastAttempt.replace('UL', '')) + 1
                if distance_score <= loginThreshold:
                    request.session['is_loggedin'] = True
                    request.session['loggedin_user'] = fullname
                    request.session['loggedin_username'] = username

                    # Save data
                    if isTrueUser:
                        status = "Granted (TA)"
                        # Update weekly task left
                        if user.login_weekly_task_left > 0:
                            Users.objects.filter(memberID=attempt_user).update(
                                login_weekly_task_left=(user.login_weekly_task_left - 1))
                            # Update login attempt count
                            Users.objects.filter(memberID=attempt_user).update(
                                login_attempt=user.login_attempt + 1)
                        # Push keystrokes and mouse data to database
                        addKeystrokesToProfile('UL', ip_address, attempt_user, 1, 'granted',
                                               lastAttempt)
                        addMouseToProfile('UL', ip_address, attempt_user, 1, 'granted', lastAttempt)
                    else:
                        status = "Granted (FA)"
                        # Update user record with the attacked attempt
                        Users.objects.filter(memberID=attempt_user).update(
                            login_attacked=user.login_attacked + 1)
                        # Update Attacks table with impostor attempt
                        try:
                            print('Impostor ID:', impostorID)
                            if Attacks.objects.filter(attacker=impostorID, attacks=attempt_user).exists():
                                attack_count = Attacks.objects.get(attacker=impostorID, attacks=attempt_user)
                                if attack_count.login_attempts < 10:
                                    Attacks.objects.filter(attacker=impostorID, attacks=attempt_user).update(
                                        login_attempts=F("login_attempts") + 1)
                        except:
                            print('Could not find attacker or attacked user')
                        addKeystrokesToProfile('UL', ip_address, attempt_user, 0, 'granted',
                                               lastAttempt)
                        addMouseToProfile('UL', ip_address, attempt_user, 0, 'granted', lastAttempt)
                    # Save attempt
                    attempt = LoginAttempt(ip=ip_address, claimed_id=attempt_user,
                                           timestamp=int(time.time()),
                                           score='%.3f' % (distance_score),
                                           threshold=loginThreshold, status=status)
                    attempt.save()
                    response = redirect('/soteria/landingpage')
                    return response
                else:
                    # TODO: Enable OTP only as second factor if keystrokes fail
                    if isTrueUser:
                        status = "Denied (FR)"
                    else:
                        status = "Denied (TR)"
                        # Update Attacks table with impostor attempt
                        try:
                            print('Impostor ID:', impostorID)
                            if Attacks.objects.filter(attacker=impostorID, attacks=attempt_user).exists():
                                attack_count = Attacks.objects.get(attacker=impostorID, attacks=attempt_user)
                                if attack_count.login_attempts < 10:
                                    Attacks.objects.filter(attacker=impostorID, attacks=attempt_user).update(
                                        login_attempts=F("login_attempts") + 1)
                        except:
                            print('Could not find attacker or attacked user')

                        # Update attacked attempt count
                        Users.objects.filter(memberID=attempt_user).update(
                            login_attacked=user.login_attacked + 1)
                        # Push keystrokes and mouse data to database
                        addKeystrokesToProfile('UL', ip_address, attempt_user, 0, 'denied', lastAttempt)
                        addMouseToProfile('UL', ip_address, attempt_user, 0, 'denied', lastAttempt)
                    # Save attempt
                    attempt = LoginAttempt(ip=ip_address, claimed_id=attempt_user,
                                           timestamp=int(time.time()), score='%.3f' % (distance_score),
                                           threshold=loginThreshold, status=status)
                    attempt.save()

                    #  Escalate Login process by splitting OTP
                    otp1 = random.randint(000, 999)
                    otp2 = random.randint(000, 999)
                    otp = str(otp1) + str(otp2)
                    Users.objects.filter(memberID=attempt_user).update(otp=otp)
                    # Set expiration
                    Users.objects.filter(memberID=attempt_user).update(expire_at=int(time.time() + 600))
                    sendSMS("Your login verification code is : " + str(
                        otp) + ". It expires in 10 minutes. Please ignore if you did not request for this. SOTERIA",
                            phone)
                    # context_mail = {'fn': user.first_name, 'otp2': otp2, 'otp': True}
                    # SendCustomEmail([email], context_mail, "Verification Required")
                    context = {'enterOTP': True, 'split': True}
                    url = 'home.html'
                    return render(request, url, context)
            else:
                # Insufficient keystrokes
                if isTrueUser:
                    status = "Insufficient Keystrokes (FR)"
                else:
                    status = "Insufficient Keystrokes (TR)"
                    # Get the last iteration in DB
                    lastAttempt = (Keys.objects.filter(user=attempt_user,
                                                       iteration__startswith='UL').last()).iteration
                    lastAttempt = int(lastAttempt.replace('UL', '')) + 1
                    # Update Attacks table with impostor attempt
                    try:
                        if Attacks.objects.filter(attacker=impostorID, attacks=attempt_user).exists():
                            attack_count = Attacks.objects.get(attacker=impostorID, attacks=attempt_user)
                            if attack_count.login_attempts < 10:
                                Attacks.objects.filter(attacker=impostorID, attacks=attempt_user).update(
                                    login_attempts=F("login_attempts") + 1)
                    except:
                        print('Could not find attacker or attacked user')

                    # Update attacked attempt count
                    Users.objects.filter(memberID=attempt_user).update(
                        login_attacked=user.login_attacked + 1)
                    # Push keystrokes and mouse data to database
                    addKeystrokesToProfile('UL', ip_address, attempt_user, 0, 'denied', lastAttempt)
                    addMouseToProfile('UL', ip_address, attempt_user, 0, 'denied', lastAttempt)
                # Save attempt
                attempt = LoginAttempt(ip=ip_address, claimed_id=attempt_user,
                                       timestamp=int(time.time()), score='%.3f' % (distance_score),
                                       threshold=loginThreshold, status=status)
                attempt.save()
                #  Escalate Login process by splitting OTP
                otp1 = random.randint(000, 999)
                otp2 = random.randint(000, 999)
                otp = str(otp1) + str(otp2)
                Users.objects.filter(memberID=attempt_user).update(otp=otp)
                # Set expiration
                Users.objects.filter(memberID=attempt_user).update(expire_at=int(time.time() + 600))
                sendSMS("Your login verification code is : " + str(
                    otp) + ". It expires in 10 minutes. Please ignore if you did not request for this. SOTERIA",
                        phone)
                # context_mail = {'fn': user.first_name, 'otp2': otp2, 'otp': True}
                # SendCustomEmail([email], context_mail, "Verification Required")
                context = {'enterOTP': True, 'split': True}
                url = 'home.html'
                return render(request, url, context)
        else:
            context = {'error': 'ACCESS DENIED.',
                       'tasksleft': loginWeeklyTaskLeft}  # Invalid Data. Ensure content is typed
    else:
        context = {'error': 'ACCESS DENIED.',
                   'tasksleft': loginWeeklyTaskLeft}  # Invalid Data. Ensure content is typed

    return context


def home(request):
    global fullname, attempt_user, impostorPhone, loginWeeklyTaskLeft, impostorID
    ip_address = getIP(request)
    print(request.session['ip_address'])
    request.session['counter'] = 0
    request.session['phase'] = 0

    # Default
    loginWeeklyTaskLeft = -1
    context = {'showWelcomeMessage': False, 'tasksleft': loginWeeklyTaskLeft}

    # Check the session user or show welcome message
    if request.session.get('sessionUserFullname', '') == '':
        context = {'showWelcomeMessage': True, 'tasksleft': loginWeeklyTaskLeft}
    else:
        _return = checkWeeklyTasks(request)
        if isinstance(_return, dict):
            context = _return

    request.session['action'] = 'login'

    # Sign out all users when here
    request.session['is_loggedin'] = False
    request.session['loggedin_user'] = 'Unknown User'

    try:
        username = request.POST.get('userName')
        pwd = request.POST.get('password')
        if Users.objects.filter(username=request.POST['userName']).exists():
            print('User found')
            user = Users.objects.get(username=username)
            true_pwd, true_username, attempt_user = user.password, user.username, user.memberID
            fullname = user.first_name.lower() + ' ' + user.last_name.lower()
            phone, email, login_template = user.phone, user.mail, user.login_template

            # Only used by OTP page, clear elsewhere
            request.session['tempUser'] = attempt_user

            if request.session.get('sessionUserFullname', '') != '':
                if fuzz.ratio(fullname, request.session['sessionUserFullname'].lower()) > 80:
                    isTrueUser = True
                else:
                    isTrueUser = False
                    impostorPhone = ''
                    all_users_list = Users.objects.all()
                    for imp_user in all_users_list:
                        fulname = str(imp_user.first_name.lower()) + ' ' + str(imp_user.last_name.lower())
                        if fuzz.ratio(fulname, request.session['sessionUserFullname'].lower()) > 80:
                            # That's the impostor, get the phone and ID'
                            impostorPhone = imp_user.phone
                            impostorID = imp_user.memberID
                            print('Impostor phone is: ' + impostorPhone)
                            break
            else:
                context = {'error': 'Session Expired.', 'showWelcomeMessage': True}
                url = 'home.html'
                ip_address = getIP(request)
                clear(ip_address)
                clearMouseData(ip_address)
                return render(request, url, context)

            # auth = pbkdf2_sha256.verify(pwd, true_pwd)
            if true_username == username and pwd == true_pwd:  # credentials are correct, check keystrokes
                # check if user has at least 4 password enrollment sample
                if isTrueUser and login_template < 4:
                    #  Use single OTP
                    otp = random.randint(00000, 99999)
                    Users.objects.filter(memberID=attempt_user).update(otp=otp)
                    # Set expiration
                    Users.objects.filter(memberID=attempt_user).update(expire_at=int(time.time() + 600))
                    sendSMS("Your login verification code is : " + str(
                        otp) + ". It expires in 10 minutes. Please ignore if you did not request for this. SOTERIA",
                            phone)
                    context = {'enterOTP': True}
                    return render(request, 'home.html', context)
                else:
                    _return1 = useKeystrokesDynamics(request, ip_address, username, pwd, phone, email, isTrueUser, user)
                    if isinstance(_return1, dict):
                        context = _return1
                    else:
                        return _return1
                clear(ip_address)
                clearMouseData(ip_address)
                url = 'home.html'
                return render(request, url, context)

            else:
                context = {'error': 'ACCESS DENIED.', 'tasksleft': loginWeeklyTaskLeft}
                clear(ip_address)
                clearMouseData(ip_address)
                url = 'home.html'
                if isTrueUser:
                    status = "Wrong Credentials (FR)"
                else:
                    status = "Wrong Credentials (TR)"
                attempt = LoginAttempt(ip=ip_address, claimed_id=attempt_user, timestamp=int(time.time()), score=0,
                                       threshold=loginThreshold, status=status)
                attempt.save()
                return render(request, url, context)
        else:
            print('Wrong login credentials.')
            context = {'error': 'ACCESS DENIED.', 'tasksleft': loginWeeklyTaskLeft}
            url = 'home.html'
            clear(ip_address)
            clearMouseData(ip_address)
            return render(request, url, context)

    except MultiValueDictKeyError:
        try:  # Check OTP validation
            otp = request.POST.get('otp')
            attempt_user = request.session['tempUser']
            user = Users.objects.get(memberID=attempt_user)
            if str(otp) == str(user.otp):
                # Check if OTP has expired
                if int(user.expire_at) < int(time.time()):
                    clear(ip_address)
                    clearMouseData(ip_address)
                    context = {'error': 'OTP Expired.', 'tasksleft': loginWeeklyTaskLeft}
                    # Delete the tempUser
                    request.session.pop('tempUser', None)
                    return render(request, 'home.html', context)
                print('OTP is valid!')
                request.session['is_loggedin'] = True
                request.session['loggedin_user'] = user.first_name + ' ' + user.last_name
                request.session['loggedin_username'] = user.username
                print("Building Template")
                # Save attempt
                attempt = LoginAttempt(ip=ip_address, claimed_id=attempt_user, timestamp=int(time.time()),
                                       score='%.3f' % (0), threshold=loginThreshold, status='Building Template')
                attempt.save()
                # Get the last iteration in DB
                if Keys.objects.filter(user=attempt_user, iteration__startswith='UL').exists():
                    lastAttempt = (Keys.objects.filter(user=attempt_user, iteration__startswith='UL').last()).iteration
                    lastAttempt = int(lastAttempt.replace('UL', '')) + 1
                else:
                    lastAttempt = user.login_attempt + 1
                # Update login template count
                if fuzz.ratio(user.first_name.lower() + ' ' + user.last_name.lower(),
                              request.session['sessionUserFullname'].lower()) > 80:
                    # True user
                    Users.objects.filter(memberID=attempt_user).update(login_template=(user.login_template + 1))
                    if user.login_weekly_task_left > 0:
                        Users.objects.filter(memberID=attempt_user).update(
                            login_weekly_task_left=(user.login_weekly_task_left - 1))
                        # Update login attempt count
                        Users.objects.filter(memberID=attempt_user).update(login_attempt=user.login_attempt + 1)
                    # Save login keystrokes to profile
                    addKeystrokesToProfile('UL', ip_address, attempt_user, 1, 'granted', lastAttempt)
                    addMouseToProfile('UL', ip_address, attempt_user, 1, 'granted', lastAttempt)

                response = redirect('/soteria/landingpage')
                return response
            elif otp is None:
                clear(ip_address)
                clearMouseData(ip_address)
                request.session.pop('tempUser', None)
                return render(request, 'home.html', context)
            else:
                clear(ip_address)
                clearMouseData(ip_address)
                context = {'enterOTP': True, 'error': 'WRONG OTP, Please retry.'}
                return render(request, 'home.html', context)
        except (MultiValueDictKeyError, KeyError):
            print("Welcome")
            clear(ip_address)
            clearMouseData(ip_address)
            # Delete the tempUser
            request.session.pop('tempUser', None)
            return render(request, 'home.html', context)


# @background(schedule=0)
def addKeystrokesToProfile(iteration, ip_address, memberID, genuine, decision, login_attempt):
    # Save user keystrokes
    data = Data.objects.filter(ip=ip_address, iteration=iteration)
    if data:
        for i in data:
            keys = Keys(user=memberID, key_name=i.key_name, release=i.release, timestamp=i.timestamp,
                        widgetName=i.widgetName,
                        iteration=i.iteration + str(login_attempt), genuine=genuine, decision=decision)
            keys.save()
        Data.objects.filter(ip=ip_address, iteration=iteration).delete()


# @background(schedule=0)
def addMouseToProfile(iteration, ip_address, attempt_user, genuine, decision, login_attempt):
    # Save user Mouse
    user_mouse = Temp_Mouse.objects.filter(user=ip_address)
    if user_mouse:
        for i in user_mouse:
            mouse = Mouse(user=attempt_user, event=i.event, widgetType=i.widgetType, widgetName=i.widgetName,
                          page=i.page, timestamp=i.timestamp, genuine=genuine, decision=decision,
                          iteration=iteration + str(login_attempt), resolution=i.resolution, x_pos=i.x_pos,
                          y_pos=i.y_pos)
            mouse.save()
        Temp_Mouse.objects.filter(user=ip_address).delete()


def sendSMS(message, phone):
    if '+' not in str(phone):
        phone = '+1' + str(phone)
    account_sid = settings.TWILIO_ACCOUNT_SID
    auth_token = settings.TWILIO_AUTH_TOKEN
    client = Client(account_sid, auth_token)
    client.messages.create(to=phone, from_=settings.TWILIO_PHONE_NUMBER, body=message)


def index(request):
    latest_question_list = ''
    template = loader.get_template('index.html')
    context = {
        'latest_question_list': latest_question_list,
    }
    return HttpResponse(template.render(context, request))


# For Account Recovery
def listen(request):
    m = 'RFA'
    username = request.session.get('memberID', '')
    if username != '':
        iterat = m[request.session.get('phase', 0)] + str(request.session['counter'] + 1)
        e = eval(request.path.split('n/')[-1])
        saveKeys(username, e, iterat)
    return HttpResponse(request)


# comment - @background(schedule=0)
def saveKeys(username, e, iterat):
    b = Keys(user=username, key_name=e.get("k"), release=e.get("r"), timestamp=e.get("t"),
             widgetName=e.get("s"), iteration=iterat)
    b.save()


# For Enrollment
def temp_keys_listen(request):
    username = request.session.get('memberID', '')
    if username != '':
        iterat = 'R' + str(request.session['counter'] + 1)
        e = eval(request.path.split('n/')[-1])
        saveTempKeys(username, e, iterat)
    return HttpResponse(request)


# comment - @background(schedule=0)
def saveTempKeys(username, e, iterat):
    b = Temp_Keys(user=username, key_name=e.get("k"), release=e.get("r"), timestamp=e.get("t"),
                  widgetName=e.get("s"), iteration=iterat)
    b.save()


# For Account Recovery
def dropdwnln(request):
    ip_address = request.session.get('ip_address', '')
    if ip_address != '':
        e = eval(request.path.split('dropdwnln')[-1])
        saveDropdown(ip_address, e, '')
    return HttpResponse(request)


# For Enrollment
def dropdwnlisten2(request):
    ip_address = request.session.get('ip_address', '')
    if ip_address != '':
        e = eval(request.path.split('dropdwnlisten2')[-1])
        iterat = 'R' + str(request.session['counter'] + 1)
        saveDropdown(ip_address, e, iterat)
    return HttpResponse(request)


# comment - @background(schedule=0)
def saveDropdown(ip_address, e, iterat):
    b = Temp_Dropdown(user=ip_address, timestamp=e['t'], widgetName=e['w'], widgetStatus=e['s'], action=e['a'],
                      iteration=iterat)
    b.save()


# For Account Recovery
def mousee(request):
    data = eval(request.path.split('mousee')[-1])
    ip_address = request.session.get('ip_address', '')
    print(ip_address)
    if ip_address != '':
        saveMouse(ip_address, data, '')
    return HttpResponse(request)


# For Enrollment
def mousee2(request):
    data = eval(request.path.split('mousee2')[-1])
    ip_address = request.session.get('ip_address', '')
    if ip_address != '':
        iterat = 'R' + str(request.session['counter'] + 1)
        saveMouse(ip_address, data, iterat)
    return HttpResponse(request)


# comment - @background(schedule=0)
def saveMouse(ip_address, data, iterat):
    if data.get("e") != 'mouse_move':  # It is mouseovers, else mouse coordinates
        b = Temp_Mouse(user=ip_address, event=data.get("e"), widgetType=data.get("w"),
                       widgetName=data.get("c"), page=data.get("p"), timestamp=data.get("t"), iteration=iterat)
    else:
        b = Temp_Mouse(user=ip_address, event=data.get("e"), x_pos=data.get("x_po"), y_pos=data.get("y_po"),
                       page=data.get("p"), timestamp=data.get("t"), resolution=data.get("r"), iteration=iterat)
    b.save()


def listn2(request):
    ip_address = request.session.get('ip_address', '')
    if ip_address != '':
        if request.session['action'] == 'account_recovery':
            iterat = 'AR'  # AR stands for Account Recovery keystrokes
            e = eval(request.path.split('2/')[-1])
            saveTempData2(ip_address, e, iterat)  # Store Asynchronously
        else:
            iterat = 'UL'  # UL stands for User Login keystrokes
            e = eval(request.path.split('2/')[-1])
            print(e)
            saveTempData(ip_address, e, iterat)  # Store synchronously
    return HttpResponse(request)


# @background(schedule=0)
def saveTempData(ip_address, e, iterat):
    b = Data(ip=ip_address, key_name=e.get("k"), release=e.get("r"), timestamp=e.get("t"),
             widgetName=e.get("s"), iteration=iterat)
    b.save()


# @background(schedule=0)
def saveTempData2(ip_address, e, iterat):
    b = Data(ip=ip_address, key_name=e.get("k"), release=e.get("r"), timestamp=e.get("t"),
             widgetName=e.get("s"), iteration=iterat)
    b.save()


def forgotpwd1(request):
    recovWeeklyTaskLeft = -1  # Default
    request.session['action'] = 'account_recovery'
    if request.session.get('sessionUserFullname', '') == '':
        context = {'showWelcomeMessage': True, 'taskLeft': -1}
        ip_address = getIP(request)
        clear(ip_address)
        clearMouseData(ip_address)
        response = redirect('/')
        return response
    else:
        all_users_list = Users.objects.all()
        for user in all_users_list:
            fulname = str(user.first_name.lower()) + ' ' + str(user.last_name.lower())
            if fuzz.ratio(fulname, request.session['sessionUserFullname'].lower()) > 80:
                d1 = datetime.datetime.strptime(date.today().strftime("%m/%d/%Y"), "%m/%d/%Y")  # Current time
                d2 = datetime.datetime.strptime(user.last_visited, "%m/%d/%Y")  # Last visited
                if abs((d2 - d1).days) >= 1:
                    # update last visited
                    Users.objects.filter(memberID=user.memberID).update(last_visited=date.today().strftime("%m/%d/%Y"))
                    Users.objects.filter(memberID=user.memberID).update(login_weekly_task_left=weeklyLogin)
                    Users.objects.filter(memberID=user.memberID).update(AR_weekly_task_left=weeklyAR)
                    recovWeeklyTaskLeft = weeklyAR
                else:
                    recovWeeklyTaskLeft = user.AR_weekly_task_left
                break

    ip_address = request.session.get('ip_address', '')
    clear(ip_address)
    clearMouseData(ip_address)
    context = {'taskLeft': recovWeeklyTaskLeft}
    return render(request, 'forgotpwd1.html', context)


def forgotpwd2(request):
    request.session['action'] = 'account_recovery'
    testdetails.clear()
    request.session['memberID'] = request.POST.get('memberId')
    request.session['toEmail'] = request.POST.get('email')
    ip_address = request.session.get('ip_address', '')

    if request.session.get('sessionUserFullname', '') == '':
        ip_address = getIP(request)
        clear(ip_address)
        clearMouseData(ip_address)
        response = redirect('/')
        return response

    j = 0
    for i in request.POST:
        if i == 'csrfmiddlewaretoken' or i == 'day' or i == 'year' or i == 'reTypeEmail': continue
        if i == 'month':
            testdetails[request.session['memberID'] + '_' + str(j)] = dt(int(request.POST.get('year')),
                                                                         int(request.POST.get('month')),
                                                                         int(request.POST.get('day')))
        elif i == 'zipcode':
            testdetails[request.session['memberID'] + '_' + str(j)] = int(request.POST.get(i).strip())
        else:
            testdetails[request.session['memberID'] + '_' + str(j)] = request.POST.get(i).strip().lower()
        j += 1
    print(testdetails)
    context = {'user_name': {'fn': request.POST.get('fullFname'), 'ln': request.POST.get('fullLname')}, }
    return render(request, 'forgotpwd2.html', context)


def forgotpwd3(request):
    global impostorEmail, context, impostorID
    request.session['action'] = 'account_recovery'
    declaretext1 = request.POST.get('declaretext', '')
    attempt_user = request.session.get('memberID', '')

    ip_address = request.session.get('ip_address', '')
    if request.session.get('sessionUserFullname', '') == '':
        context = {'showWelcomeMessage': True}
        ip_address = getIP(request)
        clear(ip_address)
        clearMouseData(ip_address)
        response = redirect('/')
        return response

    try:
        # check if the declare text is at least 85% accurate
        declaretext2 = 'I declare that I am ' + testdetails[request.session['memberID'] + '_1'] + ' ' + \
                       testdetails[request.session['memberID'] + '_2'] + ' and everything I type here is true.'
        info = fuzz.ratio(declaretext1, declaretext2)

        # Get the user actual details
        if Users.objects.filter(memberID=attempt_user).exists():
            user_details = Users.objects.get(memberID=attempt_user)
            AR_template = user_details.AR_template
            phone = user_details.phone

            # Check who the current user is
            impostorID = ''
            fulname = str(user_details.first_name.lower()) + ' ' + str(user_details.last_name.lower())
            if fuzz.ratio(fulname, request.session['sessionUserFullname'].lower()) > 80:
                owner = True  # It's true owner
            else:
                owner = False  # Not true owner
                imp_users_list = Users.objects.all()
                for imp_user in imp_users_list:
                    fulname = str(imp_user.first_name.lower()) + ' ' + str(imp_user.last_name.lower())
                    if fuzz.ratio(fulname, request.session['sessionUserFullname'].lower()) > 80:
                        # That's the impostor, get the email address'
                        impostorEmail = imp_user.mail
                        impostorID = imp_user.memberID
                        break

            if info < 85:
                print("Incorrect declare statement")
                context = {'access_denied': True, 'message': 'ACCESS DENIED'}
                if owner:
                    status = "Wrong info (FR)"
                    clear(ip_address)
                    clearMouseData(ip_address)
                else:
                    status = "Wrong info (TR)"
                    clear(ip_address)
                    clearMouseData(ip_address)
                attempt = RecoveryAttempt(ip=ip_address, claimed_id=attempt_user, timestamp=int(time.time()), score=0,
                                          threshold=recoveryThreshold, status=status)
                attempt.save()
                # The declare texts were not entered correctly
                return render(request, 'forgotpwd3.html', context)

            details = [user_details.memberID, user_details.first_name.lower(), user_details.last_name.lower(),
                       user_details.dob, user_details.address.lower(), user_details.city.lower(),
                       user_details.state.lower(), user_details.zipcode, user_details.country.lower(),
                       user_details.phone,
                       user_details.mail.lower()]

            for eachdetail in testdetails:
                i = int(eachdetail[-1])

                # check if dob match
                if i == 3:
                    if str(details[i]) != str(testdetails[eachdetail])[:10]:
                        # Some information provided are not correct
                        print("DOB not correct")
                        context = {'access_denied': True, 'message': 'ACCESS DENIED'}
                        if owner:
                            status = "Wrong info (FR)"
                        else:
                            status = "Wrong info (TR)"
                        clear(ip_address)
                        clearMouseData(ip_address)
                        attempt = RecoveryAttempt(ip=ip_address, claimed_id=attempt_user, timestamp=int(time.time()),
                                                  score=0, threshold=recoveryThreshold, status=status)
                        attempt.save()
                        return render(request, 'forgotpwd3.html', context)

                # check if Fname, Lname and Email perfectly match
                elif i in [1, 2, 5, 6, 7, 8, 9]:  # The numbers are the position of items in "details" array
                    info = fuzz.ratio(testdetails[eachdetail], details[i])
                    if info < 100:
                        print(details[i], " not correct")
                        context = {'access_denied': True,
                                   'message': 'ACCESS DENIED'}  # Some information provided are not correct
                        if owner:
                            status = "Wrong info (FR)"
                        else:
                            status = "Wrong info (TR)"
                        clear(ip_address)
                        clearMouseData(ip_address)
                        attempt = RecoveryAttempt(ip=ip_address, claimed_id=attempt_user, timestamp=int(time.time()),
                                                  score=0, threshold=recoveryThreshold, status=status)
                        attempt.save()
                        return render(request, 'forgotpwd3.html', context)

                # check if other fields are at least 80% accurate
                else:
                    if eachdetail[-2:] == '10':
                        info = fuzz.ratio(testdetails[eachdetail], details[10])
                    else:
                        info = fuzz.ratio(testdetails[eachdetail], details[i])
                    if info < 80:
                        print('Failed here ', i)
                        context = {'access_denied': True,
                                   'message': 'ACCESS DENIED'}  # Some of the information provided are not correct
                        if owner:
                            status = "Wrong info (FR)"
                        else:
                            status = "Wrong info (TR)"
                        clear(ip_address)
                        clearMouseData(ip_address)
                        attempt = RecoveryAttempt(ip=ip_address, claimed_id=attempt_user, timestamp=int(time.time()),
                                                  score=0, threshold=recoveryThreshold, status=status)
                        attempt.save()
                        return render(request, 'forgotpwd3.html', context)

            # Check if account recovery samples is at least 4
            if AR_template < 4:
                otp = random.randint(00000, 99999)
                Users.objects.filter(memberID=attempt_user).update(otp=otp)
                # Set expiration
                Users.objects.filter(memberID=attempt_user).update(expire_at=int(time.time() + 600))
                sendSMS("Your account recovery verification code is : " + str(otp) +
                        ". It expires in 10 minutes. Please ignore if you did not request for this. SOTERIA", phone)
                context = {'enterOTP': True}
                return render(request, 'forgotpwd3.html', context)

            # Get profile
            all_keys = Keys.objects.filter(user=attempt_user)
            if not all_keys:
                context = {'access_denied': True,
                           'message': 'ACCESS DENIED'}  # The user does not exist. Ensure you type in a valid Member ID
                return render(request, 'forgotpwd3.html', context)

            # Use all keystroke (granted or denied) that belongs to the true user
            all_keys = Keys.objects.filter(user=attempt_user)
            p1 = sorted([(i.timestamp, i.key_name, i.release) for i in all_keys if i.release == 0 and
                         (
                                 i.widgetName == 'Fname' or i.widgetName == 'Lname') and i.genuine == 1 and i.decision == 'granted'])
            p2 = sorted([(i.timestamp, i.key_name, i.release) for i in all_keys if
                         i.release == 0 and (i.widgetName == 'declare') and i.genuine == 1 and i.decision == 'granted'])
            p3 = sorted([(i.timestamp, i.key_name, i.release) for i in all_keys if
                         i.release == 0 and (i.widgetName == 'address') and i.genuine == 1 and i.decision == 'granted'])
            p4 = sorted([(i.timestamp, i.key_name, i.release) for i in all_keys if
                         i.release == 0 and (i.widgetName == 'city') and i.genuine == 1 and i.decision == 'granted'])
            p5 = sorted([(i.timestamp, i.key_name, i.release) for i in all_keys if
                         i.release == 0 and (i.widgetName == 'zip') and i.genuine == 1 and i.decision == 'granted'])
            p6 = sorted([(i.timestamp, i.key_name, i.release) for i in all_keys if
                         i.release == 0 and (i.widgetName == 'phone') and i.genuine == 1 and i.decision == 'granted'])
            p7 = sorted([(i.timestamp, i.key_name, i.release) for i in all_keys if i.release == 0 and
                         (
                                 i.widgetName == 'email' or i.widgetName == 'reEmail') and i.genuine == 1 and i.decision == 'granted'])

            # Get test samples
            samples = Data.objects.filter(ip=ip_address)
            s1 = sorted([(i.timestamp, i.key_name, i.release) for i in samples if
                         i.release == 0 and (i.widgetName == 'Fname' or i.widgetName == 'Lname')])
            s2 = sorted([(i.timestamp, i.key_name, i.release) for i in samples if
                         i.release == 0 and (i.widgetName == 'declare')])
            s3 = sorted([(i.timestamp, i.key_name, i.release) for i in samples if
                         i.release == 0 and (i.widgetName == 'address')])
            s4 = sorted([(i.timestamp, i.key_name, i.release) for i in samples if
                         i.release == 0 and (i.widgetName == 'city')])
            s5 = sorted([(i.timestamp, i.key_name, i.release) for i in samples if
                         i.release == 0 and (i.widgetName == 'zip')])
            s6 = sorted([(i.timestamp, i.key_name, i.release) for i in samples if
                         i.release == 0 and (i.widgetName == 'phone')])
            s7 = sorted([(i.timestamp, i.key_name, i.release) for i in samples if
                         i.release == 0 and (i.widgetName == 'email' or i.widgetName == 'reEmail')])

            profile_lst = [p1, p2, p3, p4, p5, p6, p7]
            sample_lst = [s1, s2, s3, s4, s5, s6, s7]
            scores, sharedDigraphs = [], []
            for i in range(len(profile_lst)):
                score__, sharedDigraph__ = manhattan(profile_lst[i], sample_lst[i])
                if score__ == -1:
                    clear(ip_address)
                    clearMouseData(ip_address)
                    context = {'access_denied': True, 'message': 'ACCESS DENIED.'}
                    return render(request, 'forgotpwd3.html', context)

                scores.append(score__)
                sharedDigraphs.append(sharedDigraph__)

            distance_score = ((scores[0] * 0.15) + (scores[1] * 0.25) + (scores[2] * 0.05) + (
                    scores[3] * 0.1) + (scores[4] * 0.05) + (scores[5] * 0.05) + (scores[6] * 0.35))
            c = sum(sharedDigraphs)
            print('final score: ', distance_score)
            min_digraph = floor(0.8 * (len(testdetails[request.session['memberID'] + '_1']) + len(
                testdetails[request.session['memberID'] + '_2']) + len(
                testdetails[request.session['memberID'] + '_4']) + len(
                testdetails[request.session['memberID'] + '_5']) + len(
                str(testdetails[request.session['memberID'] + '_7'])) + len(
                str(testdetails[request.session['memberID'] + '_9'])) + 2 * (len(
                testdetails[request.session['memberID'] + '_10']))))  # 80% information shared digraph
            print('Min_Digraph: ', min_digraph)
            if c >= min_digraph:
                # Get the last iteration in DB
                lastAttempt = (Keys.objects.filter(user=attempt_user, iteration__startswith='AR').last()).iteration
                lastAttempt = int(lastAttempt.replace('AR', '')) + 1
                if distance_score <= recoveryThreshold:
                    # Check session user fullname
                    if owner:
                        status = "Granted (TA)"
                        # Update weekly task left
                        if user_details.AR_weekly_task_left > 0:
                            Users.objects.filter(memberID=attempt_user).update(
                                AR_weekly_task_left=(user_details.AR_weekly_task_left - 1))
                            # Update the recovery attempt
                            AR_attempt = user_details.AR_attempt + 1
                            Users.objects.filter(memberID=attempt_user).update(AR_attempt=AR_attempt)
                        # Save login keystrokes to profile
                        addKeystrokesToProfile('AR', ip_address, attempt_user, 1, 'granted', lastAttempt)
                        moveMouseData('AR', ip_address, attempt_user, 1, 'granted', lastAttempt)
                        context = {'message': 'Welcome back, ' + attempt_user + '. ' +
                                              'You have passed our credential checking.', 'owner': owner}
                    else:
                        status = "Granted (FA)"
                        # Update Attacks table with impostor attempt
                        try:
                            if Attacks.objects.filter(attacker=impostorID, attacks=attempt_user).exists():
                                attack_count = Attacks.objects.get(attacker=impostorID, attacks=attempt_user)
                                if attack_count.AR_attempts < 10:
                                    Attacks.objects.filter(attacker=impostorID, attacks=attempt_user).update(
                                        AR_attempts=F("AR_attempts") + 1)
                        except:
                            print('Attacker or Attacked user not found!')
                        # Update attacked attempt count
                        Users.objects.filter(memberID=attempt_user).update(
                            AR_attacked=user_details.AR_attacked + 1)
                        # Save login keystrokes to profile
                        addKeystrokesToProfile('AR', ip_address, attempt_user, 0, 'granted', lastAttempt)
                        moveMouseData('AR', ip_address, attempt_user, 0, 'granted', lastAttempt)
                        context = {'message': 'Welcome back, ' + attempt_user + '. ' +
                                              'You have passed our credential checking.', 'owner': owner}

                    # Save successful attempt
                    attempt = RecoveryAttempt(ip=ip_address, claimed_id=attempt_user, timestamp=int(time.time()),
                                              score='%.3f' % (distance_score), threshold=recoveryThreshold,
                                              status=status)
                    attempt.save()

                    # Clear Temp_Keys before storing new password keystokes
                    Temp_Keys.objects.filter(user=attempt_user).delete()

                    context = {'user_name': {'fn': user_details.first_name, 'ln': user_details.last_name}}
                    return render(request, 'forgotpwd4.html', context)
                else:
                    if owner:
                        status = "Denied (FR)"
                        # Save keystrokes only after OTP is verified

                    else:
                        status = "Denied (TR)"
                        # Update Attacks table with impostor attempt
                        try:
                            if Attacks.objects.filter(attacker=impostorID, attacks=attempt_user).exists():
                                attack_count = Attacks.objects.get(attacker=impostorID, attacks=attempt_user)
                                if attack_count.AR_attempts < 10:
                                    Attacks.objects.filter(attacker=impostorID, attacks=attempt_user).update(
                                        AR_attempts=F("AR_attempts") + 1)
                        except:
                            print('Attacker or Attacked user not found!')

                        # Update attacked attempt count
                        Users.objects.filter(memberID=attempt_user).update(AR_attacked=user_details.AR_attacked + 1)

                        # Save login keystrokes to profile
                        addKeystrokesToProfile('AR', ip_address, attempt_user, 0, 'denied', lastAttempt)
                        moveMouseData('AR', ip_address, attempt_user, 0, 'denied', lastAttempt)

                    # Save attempt
                    attempt = RecoveryAttempt(ip=ip_address, claimed_id=attempt_user, timestamp=int(time.time()),
                                              score='%.3f' % distance_score, threshold=recoveryThreshold, status=status)
                    attempt.save()

                    #  User OTP
                    print("Keystrokes failed.")
                    #  Escalate Login process by splitting OTP
                    otp1 = random.randint(000, 999)
                    otp2 = random.randint(000, 999)
                    otp = str(otp1) + str(otp2)
                    Users.objects.filter(memberID=attempt_user).update(otp=otp)
                    # Set expiration
                    Users.objects.filter(memberID=attempt_user).update(expire_at=int(time.time() + 600))
                    sendSMS(
                        "Your account recovery verification code is : " + str(otp) +
                        ". It expires in 10 minutes. Please ignore if you did not request for this. SOTERIA", phone)
                    # context_mail = {'fn': user_details.first_name, 'otp2': otp2, 'otp': True}
                    # SendCustomEmail([user_details.mail], context_mail, "Verification Required")
                    context = {'enterOTP': True, 'split': True}
                    return render(request, 'forgotpwd3.html', context)
            else:
                if owner:
                    status = "Insufficient Keystrokes (FR)"
                else:
                    status = "Denied (TR)"
                    # Get the last iteration in DB
                    lastAttempt = (Keys.objects.filter(user=attempt_user, iteration__startswith='AR').last()).iteration
                    lastAttempt = int(lastAttempt.replace('AR', '')) + 1
                    # Update Attacks table with impostor attempt
                    try:
                        if Attacks.objects.filter(attacker=impostorID, attacks=attempt_user).exists():
                            attack_count = Attacks.objects.get(attacker=impostorID, attacks=attempt_user)
                            if attack_count.AR_attempts < 10:
                                Attacks.objects.filter(attacker=impostorID, attacks=attempt_user).update(
                                    AR_attempts=F("AR_attempts") + 1)
                    except:
                        print('Attacker or Attacked user not found!')
                    # Update attacked attempt count
                    Users.objects.filter(memberID=attempt_user).update(AR_attacked=user_details.AR_attacked + 1)

                    # Save login keystrokes to profile
                    addKeystrokesToProfile('AR', ip_address, attempt_user, 0, 'denied', lastAttempt)
                    moveMouseData('AR', ip_address, attempt_user, 0, 'denied', lastAttempt)
                # Save attempt
                attempt = RecoveryAttempt(ip=ip_address, claimed_id=attempt_user, timestamp=int(time.time()),
                                          score='%.3f' % distance_score, threshold=recoveryThreshold, status=status)
                attempt.save()

                #  User OTP
                print("Keystrokes failed: Insufficient keystrokes")
                #  Escalate Login process by splitting OTP
                otp1 = random.randint(000, 999)
                otp2 = random.randint(000, 999)
                otp = str(otp1) + str(otp2)
                Users.objects.filter(memberID=attempt_user).update(otp=otp)
                # Set expiration
                Users.objects.filter(memberID=attempt_user).update(
                    expire_at=int(time.time() + 600))
                sendSMS("The first half of your account recovery verification code is : " + str(otp) +
                        ". It expires in 10 minutes. Please ignore if you did not request for this. SOTERIA", phone)
                # context_mail = {'fn': user_details.first_name, 'otp2': otp2, 'otp': True}
                # SendCustomEmail([user_details.mail], context_mail, "Verification Required")
                context = {'enterOTP': True, 'split': True}
                return render(request, 'forgotpwd3.html', context)

        else:
            ip_address = request.session.get('ip_address', '')
            clear(ip_address)
            clearMouseData(ip_address)
            context = {'access_denied': True,
                       'message': 'ACCESS DENIED'}  # The user does not exist. Ensure you type in a valid Member ID
            return render(request, 'forgotpwd3.html', context)

    except:
        print('Value Error: Something went wrong.')
        clear(ip_address)
        clearMouseData(ip_address)
        response = redirect('/soteria/forgotpwd1')
        return response


def forgotpwd4(request):
    global AR_attempt
    if request.session.get('sessionUserFullname', '') == '':
        ip_address = getIP(request)
        clear(ip_address)
        clearMouseData(ip_address)
        response = redirect('/')
        return response

    otp = request.POST.get('otp')
    attempt_user = request.session['memberID']
    user = Users.objects.get(memberID=attempt_user)
    ip_address = request.session.get('ip_address', '')
    if str(otp) == str(user.otp):
        # Check if OTP has expired
        if int(user.expire_at) < int(time.time()):
            clear(ip_address)
            clearMouseData(ip_address)
            context = {'access_denied': True, 'message': 'OTP Expired.'}
            return render(request, 'forgotpwd3.html', context)

        if user.AR_weekly_task_left > 0:
            Users.objects.filter(memberID=attempt_user).update(AR_weekly_task_left=(user.AR_weekly_task_left - 1))
            # Update the recovery attempt
            AR_attempt = user.AR_attempt + 1
            Users.objects.filter(memberID=attempt_user).update(AR_attempt=AR_attempt)
        if user.AR_attempt != 0:
            # Get the last iteration in DB and increment
            lastAttempt = (Keys.objects.filter(user=attempt_user, iteration__startswith='AR').last()).iteration
            lastAttempt = int(lastAttempt.replace('AR', '')) + 1
        else:
            lastAttempt = user.AR_attempt + 1
        # Update template
        Users.objects.filter(memberID=attempt_user).update(AR_template=user.AR_template + 1)
        addKeystrokesToProfile('AR', ip_address, attempt_user, 1, 'granted', lastAttempt)
        moveMouseData('AR', ip_address, attempt_user, 1, 'granted', lastAttempt)

        # Save attempt
        print("Building Template")
        attempt = RecoveryAttempt(ip=ip_address, claimed_id=attempt_user, timestamp=int(time.time()),
                                  score='%.3f' % 0, threshold=loginThreshold, status='Building Template')
        attempt.save()

        context = {'user_name': {'fn': user.first_name, 'ln': user.last_name}}
        return render(request, 'forgotpwd4.html', context)

    else:
        context = {'enterOTP': True, 'error': 'Wrong OTP, please try again.'}
        return render(request, 'forgotpwd3.html', context)


def resendEmail(request):
    attempt_user = request.session.get('memberID', '')

    if not Users.objects.filter(memberID=attempt_user).exists():
        return redirect('/')

    user_details = Users.objects.get(memberID=attempt_user)
    pwd = str(user_details.password)
    code = pwd[(len(pwd) // 2) - 7: (len(pwd) // 2) + 7]
    title = 'Password Reset Link'
    ip_address = request.session.get('ip_address', '')

    link = request.build_absolute_uri('/soteria/forgotpwd4?code=' + code + '&ip=' + ip_address + '&id=' + attempt_user + '&pwd_status=' + \
           request.session['pwd_status'])
    context_mail = {'fn': user_details.first_name, 'link': link, 'pwd_reset': True}

    SendCustomEmail([request.session['toEmail']], context_mail, title)

    context = {'email_resent': True, 'message': 'Link has been sent. Please check your email'}
    return render(request, 'resend_email.html', context)


def email_resend(request):
    mID = request.session.get('memberID', '')
    if not Temp_User.objects.filter(memberID=mID).exists():
        return redirect('/')
    newUser = Temp_User.objects.get(memberID=mID)
    pwd = newUser.password
    mail = newUser.mail
    fn, ln = newUser.first_name, newUser.last_name
    # Send verification email
    code = pwd[(len(pwd) // 2) - 7: (len(pwd) // 2) + 7]
    if '#' in code:
        code = code.split("#", 1)[0]
    title = 'Email Verification'
    link = request.build_absolute_uri('/soteria/email_verification?code=' + str(code) + '&id=' + mID)
    context = {'fn': fn, 'mID': mID, 'link': link, 'signup': True}
    SendCustomEmail([mail], context, title)

    context = {
        'user_name': {'fn': fn, 'ln': ln},
        'email': mail
    }
    return render(request, "signup_verification.html", context)


# This clears the select widget data also
def clearMouseData(ip_address):
    Temp_Mouse.objects.filter(user=ip_address).delete()
    Temp_Dropdown.objects.filter(user=ip_address).delete()


def cleanTempKeys(user):
    Temp_Keys.objects.filter(user=user, widgetName='password').delete()
    Temp_Keys.objects.filter(user=user, widgetName='reTypePwd').delete()


def success2(request):
    # Check if session has expired
    global lastAttempt
    if request.session.get('sessionUserFullname', '') == '':
        context = {'showWelcomeMessage': True}
        ip_address = getIP(request)
        clear(ip_address)
        clearMouseData(ip_address)
        response = redirect('/')
        return response
    attempt_user = request.session.get('memberID', '')
    user_details = Users.objects.get(memberID=attempt_user)
    NewP = request.POST.get('reTypePwd')
    # Ensure password requirements are met
    if NewP != user_details.username and len(NewP) >= 8 and bool(re.search(r'\d', NewP)) and NewP.lower().islower():
        if NewP != user_details.password:
            Users.objects.filter(memberID=attempt_user).update(login_template=0)
            # Save new password to users table
            pwd = request.POST.get('reTypePwd')
            Users.objects.filter(memberID=request.session['memberID']).update(password=pwd)
        # Get the last iteration in DB without increment
        lastAttempt = (Keys.objects.filter(user=attempt_user, iteration__startswith='AR').last()).iteration
        lastAttempt = int(lastAttempt.replace('AR', ''))

        if fuzz.ratio(user_details.first_name.lower() + ' ' + user_details.last_name.lower(),
                      request.session['sessionUserFullname'].lower()) > 80:
            # True User
            # Add new password keystrokes
            addKeystrokesToProfile('AR', request.session['ip_address'], attempt_user, 1, 'granted', lastAttempt)
            moveMouseData('AR', request.session['ip_address'], attempt_user, 1, 'granted', lastAttempt)
        else:
            # Add new password keystrokes
            addKeystrokesToProfile('AR', request.session['ip_address'], attempt_user, 0, 'granted', lastAttempt)
            moveMouseData('AR', request.session['ip_address'], attempt_user, 0, 'granted', lastAttempt)

        pwd_status = request.session.get('pwd_status', '0')
        Users.objects.filter(memberID=request.session['memberID']).update(pwd_status=pwd_status)

        if pwd_status == '2' or pwd_status == '1':
            homeLink = "/"
            context = {'status': homeLink, 'message': 'Your password has been updated.'}
        else:
            homeLink = "/"
            context = {'status': homeLink}

        return render(request, 'success.html', context)
    else:
        context = {'message': '* Ensure new password meets all requirements'}
        return render(request, 'forgotpwd4.html', context)


# comment - @background(schedule=3)
def moveNewPasswordData(user):
    # Create new user
    data1 = Temp_Keys.objects.filter(user=user, widgetName='password')
    data2 = Temp_Keys.objects.filter(user=user, widgetName='reTypePwd')
    if data1:
        for i in data1:
            keys = Keys(user=i.user, key_name=i.key_name, release=i.release, timestamp=i.timestamp,
                        widgetName=i.widgetName,
                        iteration=i.iteration)
            keys.save()
        Temp_Keys.objects.filter(user=user, widgetName='password').delete()
    if data2:
        for i in data2:
            keys = Keys(user=i.user, key_name=i.key_name, release=i.release, timestamp=i.timestamp,
                        widgetName=i.widgetName,
                        iteration=i.iteration)
            keys.save()
        Temp_Keys.objects.filter(user=user, widgetName='reTypePwd').delete()


# @background(schedule=0)
def moveMouseData(iteration, ip_address, attempt_user, genuine, decision, AR_attempt):
    user_Dropdwn = Temp_Dropdown.objects.filter(user=ip_address)
    if user_Dropdwn:
        for i in user_Dropdwn:
            dropdwn = Dropdown(user=attempt_user, timestamp=i.timestamp, widgetName=i.widgetName,
                               widgetStatus=i.widgetStatus, action=i.action, genuine=genuine, decision=decision,
                               iteration=iteration + str(AR_attempt))
            dropdwn.save()
        Temp_Dropdown.objects.filter(user=ip_address).delete()

    # Save user Mouse
    user_mouse = Temp_Mouse.objects.filter(user=ip_address)
    if user_mouse:
        for i in user_mouse:
            mouse = Mouse(user=attempt_user, event=i.event, widgetType=i.widgetType, widgetName=i.widgetName,
                          page=i.page, timestamp=i.timestamp, genuine=genuine, decision=decision,
                          iteration=iteration + str(AR_attempt), resolution=i.resolution, x_pos=i.x_pos, y_pos=i.y_pos)
            mouse.save()
        Temp_Mouse.objects.filter(user=ip_address).delete()


# comment - @background(schedule=0)
def movedata(userID, ip_address):
    # Create new user
    new_user = Temp_User.objects.filter(memberID=userID).first()
    if new_user:
        user = Users(memberID=new_user.memberID, first_name=new_user.first_name, dob=new_user.dob,
                     last_name=new_user.last_name, address=new_user.address, city=new_user.city, state=new_user.state,
                     zipcode=new_user.zipcode, country=new_user.country, mail=new_user.mail, phone=new_user.phone,
                     username=new_user.username, password=new_user.password)
        user.save()
        Temp_User.objects.filter(memberID=userID).delete()
    # Save user keystrokes
    user_keys = Temp_Keys.objects.filter(user=userID)
    if user_keys:
        for i in user_keys:
            keys = Keys(user=i.user, key_name=i.key_name, release=i.release, timestamp=i.timestamp,
                        widgetName=i.widgetName,
                        iteration=i.iteration)
            keys.save()
        Temp_Keys.objects.filter(user=userID).delete()
    # Save user input
    user_input = Temp_Input.objects.filter(memberID=userID)
    if user_input:
        for i in user_input:
            inputs = Input(memberID=i.memberID, fname=i.fname, dob=i.dob, lname=i.lname, address=i.address, city=i.city,
                           state=i.state, zipcode=i.zipcode, country=i.country, mail=i.mail, phone=i.phone)
            inputs.save()
        Temp_Input.objects.filter(memberID=userID).delete()
    # Save user mouse clicks
    user_mouse = Temp_Mouse.objects.filter(user=ip_address)
    if user_mouse:
        for i in user_mouse:
            mouse = Mouse(user=userID, event=i.event, widgetType=i.widgetType, widgetName=i.widgetName, page=i.page,
                          timestamp=i.timestamp, genuine=1, iteration=i.iteration)
            mouse.save()
        Temp_Mouse.objects.filter(user=ip_address).delete()
    # Save user dropdown
    user_dropdwn = Temp_Dropdown.objects.filter(user=ip_address)
    if user_dropdwn:
        for i in user_dropdwn:
            dropdwn = Dropdown(user=i.user, timestamp=i.timestamp, widgetName=i.widgetName, widgetStatus=i.widgetStatus,
                               action=i.action, genuine=1, iteration=i.iteration)
            dropdwn.save()
        Temp_Dropdown.objects.filter(user=ip_address).delete()


# @background(schedule=0)
def createNewUser(userID):
    # Create new user
    new_user = Temp_User.objects.filter(memberID=userID).first()
    if new_user:
        user = Users(memberID=new_user.memberID, first_name=new_user.first_name, dob=new_user.dob,
                     last_name=new_user.last_name, address=new_user.address, city=new_user.city, state=new_user.state,
                     zipcode=new_user.zipcode, country=new_user.country, mail=new_user.mail, phone=new_user.phone,
                     username=new_user.username, password=new_user.password)
        user.save()
        Temp_User.objects.filter(memberID=userID).delete()


def memberID(request):
    import os
    module_dir = os.path.dirname(__file__)  # get current directory
    file_path = os.path.join(module_dir, 'ids.txt')
    request.session['counter'] = 0
    ids = open(file_path).read().strip().split('\n')
    p = ids[Input.objects.values('memberID').distinct().count()]
    template = loader.get_template('memberID.html')
    return HttpResponse(template.render({}, request))


def signup1(request):
    request.session['action'] = 'account_recovery'
    return render(request, "signup1.html", {})


def signup2(request):
    ip_address = getIP(request)
    request.session['counter'] = 0
    username = request.POST.get('userName').strip()
    password = request.POST.get('password').strip()
    if password != username and len(password) >= 8 and bool(re.search(r'\d', password)) and password.lower().islower():
        fn = request.POST.get('fullFname').strip()
        ln = request.POST.get('fullLname').strip()
        mID = request.POST.get('memberId').strip()
        bd = request.POST.get('day')
        bm = request.POST.get('month')
        by = request.POST.get('year')
        daob = dt(int(by), int(bm), int(bd))
        add = request.POST.get('address').strip()
        cit = request.POST.get('city').strip()
        sta = request.POST.get('state')
        zipc = request.POST.get('zipcode').strip()
        phone = request.POST.get('phone').strip()
        count = request.POST.get('country')
        mail = request.POST.get('email').strip()
        pwd = request.POST.get('password').strip()
        # Clear old unused data
        Temp_Keys.objects.filter(user=mID).delete()
        Temp_Input.objects.filter(memberID=mID).delete()
        Temp_Mouse.objects.filter(user=mID).delete()
        Temp_Dropdown.objects.filter(user=mID).delete()
        # Check if username exist
        if Users.objects.filter(username=username).exists():
            context = {'message': 'Username has been used by another user'}
        # Check if memberID exist
        elif Users.objects.filter(memberID=mID).exists():
            context = {'message': 'MemberID has been used by another user'}
        elif (Users.objects.filter(first_name=fn).exists() and Users.objects.filter(
                last_name=request.POST['fullLname']).exists()):
            context = {'message': 'Name has been used by another user'}
        else:
            if Temp_User.objects.filter(memberID=mID).exists():
                print('Record found.')
                # Delete previous
                Temp_User.objects.get(memberID=mID).delete()

            # Save user input details
            temp = Temp_User(memberID=mID, first_name=fn, dob=daob, last_name=ln, address=add, city=cit, state=sta,
                             zipcode=zipc, country=count, mail=mail, phone=phone, username=username, password=pwd,
                             activation=0)
            temp.save()

            # Send verification email
            code = pwd[(len(pwd) // 2) - 7: (len(pwd) // 2) + 7]
            if '#' in code:
                code = code.split("#", 1)[0]
            title = 'Email Verification'
            link = request.build_absolute_uri('/soteria/email_verification?code=' + str(code) + '&id=' + mID + '&ip=' + ip_address)
            context = {'fn': fn, 'mID': mID, 'link': link, 'signup': True}
            SendCustomEmail([mail], context, title)

            request.session['memberID'] = mID
            for i in request.POST:
                request.session[i] = request.POST[i]

            context = {'user_name': {'fn': fn, 'ln': ln}, 'enrol_count': REPEAT1, 'email': mail}
        return render(request, "signup_verification.html", context)
    else:
        context = {'message': 'Ensure password requirements are met.'}
        return render(request, "signup_verification.html", context)


def email_verification(request):
    request.session['memberID'] = request.GET.get('id')
    ip_address = request.GET.get('ip')
    code = request.GET.get('code')
    if Temp_User.objects.filter(memberID=request.session['memberID']).exists():
        user_details = Temp_User.objects.get(memberID=request.session['memberID'])
        if code in str(user_details.password):
            # Link is genuine and has not been previously used
            print(request.session['memberID'])
            createNewUser(request.session['memberID'])
            addKeystrokesToProfile('AR', ip_address, request.session['memberID'], 1, 'granted',
                                   1)  # First keystrokes data in profile
            moveMouseData('AR', ip_address, request.session['memberID'], 1, 'granted', 1)  # First mouse data in profile
            context = {'user_name': {'fn': user_details.first_name, 'ln': user_details.last_name},
                       'enrol_count': REPEAT1}
        else:
            context = {'message': 'This link has either been used or does not exist.'}
    else:
        context = {'message': 'This link has either been used or does not exist.'}
    return render(request, 'signup2.html', context)


def landingpage(request):
    try:
        if not request.session['is_loggedin']:
            response = redirect('/')
        else:
            fullname = request.session['loggedin_user'].title()
            context = {'userName': fullname}
            url = 'landing_page.html'
            return render(request, url, context)
    except MultiValueDictKeyError:
        response = redirect('/')
    except KeyError:
        response = redirect('/')
    request.session['is_loggedin'] = False
    return response


def SendCustomEmail(toEmail, context, title):
    html_template = get_template('email_template.html')
    text_template = get_template('email_template.txt')
    html_alternative = html_template.render(context)
    text_alternative = text_template.render(context)
    msg = EmailMultiAlternatives(title, text_alternative, settings.DEFAULT_FROM_EMAIL, toEmail)
    msg.attach_alternative(html_alternative, "text/html")
    msg.send(fail_silently=False)
    print('Mail sent')


@csrf_exempt
def update_session(request):
    body = str(request.body)
    sessionUserFullname = body.split("b'", 1)[1].rsplit("'")[0]
    request.session['sessionUserFullname'] = sessionUserFullname.lower()
    print(sessionUserFullname)
    return HttpResponse(request)


def participant_list(request):
    ip = getIP(request)
    if str(ip) not in ['67.249.20.200']:  # The only IP that can access this page
        response = redirect('/')
        return response
    userlist = Users.objects.all()
    for eachUser in userlist:
        d1 = datetime.datetime.strptime(date.today().strftime("%m/%d/%Y"), "%m/%d/%Y")  # Current time
        d2 = datetime.datetime.strptime(eachUser.last_visited, "%m/%d/%Y")  # Last visited

        # update last visited and reset weekly tasks
        if eachUser.login_attempt < 100:
            if abs((d2 - d1).days) >= 1:
                if (
                        100 - eachUser.login_attempt) < weeklyLogin:  # Total Login task left is less than weekly tasks of 20
                    Users.objects.filter(memberID=eachUser.memberID).update(
                        login_weekly_task_left=(100 - eachUser.login_attempt))
                else:
                    Users.objects.filter(memberID=eachUser.memberID).update(login_weekly_task_left=weeklyLogin)
        else:
            if eachUser.login_weekly_task_left != 0:
                Users.objects.filter(memberID=eachUser.memberID).update(login_weekly_task_left=0)  # Force it to 0
        if eachUser.AR_attempt < 20:
            if abs((d2 - d1).days) >= 1:
                if (20 - eachUser.AR_attempt) < weeklyAR:  # Total AR task left is less than weekly tasks of 5
                    Users.objects.filter(memberID=eachUser.memberID).update(
                        AR_weekly_task_left=(20 - eachUser.AR_attempt))
                else:
                    Users.objects.filter(memberID=eachUser.memberID).update(AR_weekly_task_left=weeklyAR)
        else:
            if eachUser.AR_weekly_task_left != 0:
                Users.objects.filter(memberID=eachUser.memberID).update(AR_weekly_task_left=0)
    context = {'object_userlist': Users.objects.all()}
    return render(request, 'participant_list.html', context)


@csrf_exempt
def sendUserReminder(request):
    ip = getIP(request)
    if str(ip) not in ['67.249.20.200']:  # The only IP that can access this page
        response = redirect('/')
        return response
    global context_mail
    userlist = Users.objects.all()
    for eachUser in userlist:
        link = request.build_absolute_uri('/')
        d1 = datetime.datetime.strptime(date.today().strftime("%m/%d/%Y"), "%m/%d/%Y")  # Current time
        d2 = datetime.datetime.strptime(eachUser.last_visited, "%m/%d/%Y")  # Last visited
        if eachUser.login_attempt < 100 or eachUser.AR_attempt < 20:
            if str(eachUser.memberID) in ['6239364', '0812678']:  # User want to unsubscribe
                continue
            if eachUser.login_weekly_task_left > 0 or eachUser.AR_weekly_task_left > 0:
                context_mail = {'fn': eachUser.first_name, 'link': link, 'login_attempts': eachUser.login_attempt,
                                'AR_attempts': eachUser.AR_attempt, 'login_left': eachUser.login_weekly_task_left,
                                'AR_left': eachUser.AR_weekly_task_left, 'weekly_task': True}
            elif abs((d2 - d1).days) >= 1:
                context_mail = {'fn': eachUser.first_name, 'link': link, 'login_attempts': eachUser.login_attempt,
                                'AR_attempts': eachUser.AR_attempt, 'login_left': weeklyLogin,
                                'AR_left': weeklyAR, 'weekly_task': True}
            else:
                continue

            SendCustomEmail([eachUser.mail], context_mail, 'Your daily tasks reminder')

        elif eachUser.login_attempt >= 100 and eachUser.AR_attempt >= 20:
            # User have completed genuine login and recovery
            if eachUser.pwd_status == 0:
                # Send a completion email ONLY ONCE
                Users.objects.filter(memberID=eachUser.memberID).update(
                    pwd_status=2)  # NOTE: 2 means genuine tasks completion email has been sent
                context_mail = {'fn': eachUser.first_name, 'ln': eachUser.last_name, 'link': link,
                                'login_attempts': eachUser.login_attempt,
                                'AR_attempts': eachUser.AR_attempt, 'login_left': eachUser.login_weekly_task_left,
                                'AR_left': eachUser.AR_weekly_task_left, 'genuine_tasks_completed': True}

                SendCustomEmail([eachUser.mail], context_mail, 'Congratulations, Genuine Tasks Completed')
        else:
            continue
    return HttpResponse(request)


@csrf_exempt
def sendAttackReminder(request):
    ip = getIP(request)
    if str(ip) not in ['67.249.20.200']:  # The only IP that can access this page
        response = redirect('/')
        return response
    global title, message
    attackList = Attacks.objects.exclude(login_attempts=total,
                                         AR_attempts=total)  # Get currunt users connected to an impostor
    for impostor in attackList:
        # Look up impostor and user information
        impostorInfo = Users.objects.get(memberID=impostor.attacker)
        realInfo = Users.objects.get(memberID=impostor.attacks)
        if impostor.login_attempts < total and impostor.AR_attempts < total:
            message = 'Kindly complete ' + str(total - impostor.login_attempts) + ' IMPOSTOR LOGIN and ' + str(
                total - impostor.AR_attempts) + ' ACCOUNT RECOVERY attempts using the information provided below. Each impostor attempt is considered successful once you get to the OTP screen.'
            title = "Impostor tasks reminder for today"
        elif impostor.login_attempts < total:
            message = 'Kindly complete ' + str(
                total - impostor.login_attempts) + ' IMPOSTOR LOGIN attempts using the information provided below. Each impostor attempt is considered successful once you get to the OTP screen.'
            title = "Impostor Login tasks for today"
        elif impostor.AR_attempts < total:
            message = 'Kindly complete ' + str(
                total - impostor.AR_attempts) + ' IMPOSTOR ACCOUNT RECOVERY attempts using the information provided below. Each impostor attempt is considered successful once you get to the OTP screen.'
            title = "Impostor account recovery tasks for today"
        else:
            continue

        link = request.build_absolute_uri('/')
        context_mail = {'fn': impostorInfo.first_name, 'mID': realInfo.memberID, 'fn2': realInfo.first_name,
                        'ln2': realInfo.last_name, 'dob': realInfo.dob,
                        'address': realInfo.address, 'city': realInfo.city, 'state': realInfo.state,
                        'zip': realInfo.zipcode, 'country': realInfo.country,
                        'email': realInfo.mail, 'phone': realInfo.phone, 'username': realInfo.username,
                        'pwd': realInfo.password, 'link': link, 'message': message,
                        'title': title, 'impostor': True}

        SendCustomEmail([impostorInfo.mail], context_mail, "Impostor tasks for today")

    return HttpResponse(request)


def attack_list(request):
    ip = getIP(request)
    if str(ip) not in ['67.249.20.200']:  # The only IP that can access this page
        response = redirect('/')
        return response
    link = request.build_absolute_uri('/')
    userlist = Users.objects.all()  # Get all users
    for eachUser in userlist:  # Loop through users
        if eachUser.login_attempt >= 100 and eachUser.AR_attempt >= 20:  # User must have completed login and AR tasks
            if Attacks.objects.filter(
                    attacker=eachUser.memberID).exists():  # Check if user has ever been assigned an impostor
                if Attacks.objects.filter(
                        attacker=eachUser.memberID).count() < 5:  # Check is user has completed all impostor attacks on 5 other users
                    attackProfile = Attacks.objects.filter(attacker=eachUser.memberID).last()
                    if attackProfile.login_attempts >= total and attackProfile.AR_attempts >= total:  # Check if user has completed impostor attack on the current profile
                        # Ensure random user is not same as impostor or has not been previously attacked by same user
                        recursiveCount = 0
                        while recursiveCount < 20:  # Users must have sufficient profile
                            recursiveCount += 1
                            random_user = getRandomUser()
                            if random_user.memberID == eachUser.memberID or Attacks.objects.filter(
                                    attacker=eachUser.memberID,
                                    attacks=random_user.memberID).exists() or random_user.login_attempt < 100 or random_user.AR_attempt < 20 \
                                    or random_user.login_template < 4 or random_user.AR_template < 4:
                                continue
                            else:
                                newEntry = Attacks(attacker=eachUser.memberID, attacks=random_user.memberID)
                                newEntry.save()
                                break
                elif Attacks.objects.filter(attacker=eachUser.memberID).count() >= 5:
                    attackProfile = Attacks.objects.filter(attacker=eachUser.memberID).last()
                    if attackProfile.login_attempts >= total and attackProfile.AR_attempts >= total:
                        # Send a completion email ONLY ONCE
                        particular_user = Users.objects.get(memberID=eachUser.memberID)
                        if particular_user.pwd_status == 2:
                            Users.objects.filter(memberID=eachUser.memberID).update(
                                pwd_status=3)  # NOTE: 3 means impostor tasks completion email has been sent
                            link = request.build_absolute_uri('/')
                            context_mail = {'fn': eachUser.first_name, 'ln': eachUser.last_name, 'link': link,
                                            'impostor_tasks_completed': True}

                            SendCustomEmail([eachUser.mail], context_mail, 'Congratulations, Impostor Tasks Completed')

            else:
                # Ensure random user is not same as impostor
                recursiveCount = 0
                while recursiveCount < 20:  # Users must have sufficient profile
                    random_user = getRandomUser()
                    recursiveCount += 1
                    if random_user.memberID == eachUser.memberID or random_user.login_attempt < 100 or random_user.AR_attempt < 20 \
                            or random_user.login_template < 4 or random_user.AR_template < 4:
                        continue
                    else:
                        newEntry = Attacks(attacker=eachUser.memberID, attacks=random_user.memberID)
                        newEntry.save()
                        break
    context = {'object_attacklist': Attacks.objects.all().order_by('attacker')}
    return render(request, 'attack_list.html', context)


def getRandomUser():
    random_user = Users.objects.all()[random.randint(0, Users.objects.count() - 1)]
    return random_user
