# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
import django
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.template import loader
from django.http import HttpResponse
from django import template
from app.models import User, mailAddress, Mail
from django.db.models import Count, Avg, Q, Case, When
from django.db.models.functions import TruncDate
from django.utils.timezone import datetime


@login_required(login_url="/login/")
def index(request):

    template = 'index.html'

    email_exchanges = Mail.objects.count()
    num_collaborators = User.objects.filter(in_enron=True).count()
    extern_contact = User.objects.filter(in_enron=False).count()
    intern_exchange = Mail.objects.filter(is_intern=True).count() / Mail.objects.filter(is_intern=False).count()

    context = {'email_exchanges':email_exchanges,
               'num_collaborators':num_collaborators,
               'extern_contact':extern_contact,
               'intern_exchange':round(intern_exchange,1),}

    return render(request, template, context)


@login_required(login_url="/login/")
def employees(request):

    template = 'employees.html'

    start_date = request.GET.get('start_date')
    if not start_date:
        start_date = datetime(1900,1,1)

    end_date = request.GET.get('end_date')
    if not end_date:
        end_date=datetime(2100,1,1)

    lines = request.GET.get('lines')
    if not lines:
        lines = 5
    
    low_thr = request.GET.get('low_thr')
    if not low_thr:
        low_thr = 0
    else:
        try:
            low_thr = int(low_thr)
        except ValueError:
            low_thr = 0

    high_thr = request.GET.get('high_thr')
    if not high_thr:
        high_thr = 10**6
    else:
        try:
            high_thr = int(high_thr)
        except ValueError:
            high_thr = 10**6

    mci = User.objects.raw(f"""SELECT cnt.id, cnt.name, cnt.category, cnt.c
                                FROM(
                                    SELECT u.name AS name, u.category AS category, u.id, count(u.id) AS c
                                    FROM app_user as u, app_mailaddress as ma, app_mail as m
                                    WHERE u.id=ma.user_id AND ma.id=m.sender_id
                                                         AND m.is_intern=True
                                                         AND date(m.date) > '{start_date}'
                                                         AND date(m.date) < '{end_date}'

                                    GROUP BY u.id
                                ) AS cnt
                                WHERE cnt.c > {low_thr} AND cnt.c < {high_thr}
                                ORDER BY cnt.c DESC
                                LIMIT {lines};""")

    tqr = User.objects.raw(f""" SELECT u.id, u.name, u.category, s.c AS sent_reply_cnt, r.c AS received_cnt, s.c*100/r.c AS ratio
                                FROM app_user AS u,
                                (SELECT u.id, count(u.id) AS c
                                   FROM app_user as u, app_mailaddress as ma, app_mail as m
                                   WHERE u.id=ma.user_id AND ma.id=m.recipient_id
                                                         AND date(m.date) > '{start_date}'
                                                         AND date(m.date) < '{end_date}'        
                                   GROUP BY u.id
                                ) AS r,
                                (SELECT u.id, count(u.id) AS c
                                   FROM app_user as u, app_mailaddress as ma, app_mail as m
                                   WHERE u.id=ma.user_id AND ma.id=m.sender_id
                                                         AND m.is_reply=True
                                                         AND date(m.date) > '{start_date}'
                                                         AND date(m.date) < '{end_date}'    
                                   GROUP BY u.id
                                ) AS s
                                WHERE u.id=r.id AND u.id=s.id
                                                AND s.c*100/r.c < 100
                                                AND s.c*100/r.c > {low_thr}
                                                AND s.c*100/r.c < {high_thr}
                                ORDER BY ratio DESC
                                LIMIT {lines};
                                """)
    
    gib = User.objects.raw(f""" SELECT u.id, u.name, u.category, s.c AS sent_cnt, r.c AS received_cnt, s.c - r.c AS diff
                                FROM app_user AS u,
                                (SELECT u.name, u.category, u.id, count(u.id) AS c
                                   FROM app_user as u, app_mailaddress as ma, app_mail as m
                                   WHERE u.id=ma.user_id AND ma.id=m.recipient_id
                                                         AND m.is_reply = True
                                                         AND date(m.date) > '{start_date}'
                                                         AND date(m.date) < '{end_date}'        
                                   GROUP BY u.id
                                ) AS r,
                                (SELECT u.id, count(u.id) AS c
                                   FROM app_user as u, app_mailaddress as ma, app_mail as m
                                   WHERE u.id=ma.user_id AND ma.id=m.sender_id
                                                         AND m.is_reply=False
                                                         AND date(m.date) > '{start_date}'
                                                         AND date(m.date) < '{end_date}'    
                                   GROUP BY u.id
                                ) AS s
                                WHERE u.id=r.id AND u.id=s.id
                                                AND s.c - r.c > {low_thr}
                                                AND s.c - r.c < {high_thr}
                                ORDER BY diff DESC
                                LIMIT {lines};
                                """)

    context = {
        'mci':mci,
        'tqr':tqr,
        'gib':gib,
        'start_date':start_date,
        'end_date':end_date,
        'low_thr':low_thr if low_thr != 0 else '',
        'high_thr':high_thr if high_thr != 10**6 else ''
        }

    return render(request, template, context)


@login_required(login_url="/login/")
def couples(request):
    
    template = 'couples.html'

    start_date = request.GET.get('start_date')
    if not start_date:
        start_date = datetime(1900,1,1)

    end_date = request.GET.get('end_date')
    if not end_date:
        end_date = datetime(2100,1,1)

    lines = request.GET.get('lines')
    if not lines:
        lines = 5
    else:
        try:
            lines = int(lines)
        except ValueError:
            lines = 5
    
    low_thr = request.GET.get('low_thr')
    if not low_thr:
        low_thr = 0
    else:
        try:
            low_thr = int(low_thr)
        except ValueError:
            low_thr = 0

    high_thr = request.GET.get('high_thr')
    if not high_thr:
        high_thr = 10**6
    else:
        try:
            high_thr = int(high_thr)
        except ValueError:
            high_thr = 10**6

    couples = Mail.objects.filter(date__gte=start_date,date__lte=end_date,is_intern=1)\
                            .values('sender_id__user_id__name','sender_id__user_id__category','recipient_id__user_id__name','recipient_id__user_id__category')\
                            .annotate(dcount=Count('enron_id')).order_by('-dcount').filter(dcount__gte=low_thr,dcount__lte=high_thr)[:lines]
    context = {
        'couples':couples,
        'start_date':start_date,
        'end_date':end_date,
        'low_thr':low_thr if low_thr != 0 else '',
        'high_thr':high_thr if high_thr != 10**6 else ''
        }

    return render(request, template, context)


@login_required(login_url="/login/")
def days(request):

    template = 'days.html'

    start_date = request.GET.get('start_date')
    if not start_date:
        start_date = datetime(1900,1,1)

    end_date = request.GET.get('end_date')
    if not end_date:
        end_date = datetime(2100,1,1)
    
    threshold = request.GET.get('threshold')
    if not threshold:
        threshold = 0
    else:
        try:
            threshold = int(threshold)
        except ValueError:
            threshold = 0

    mails_per_day = Mail.objects.annotate(time=TruncDate('date')).values('time')\
                    .filter(date__gte=start_date,date__lte=end_date).annotate(dcount=Count('enron_id'))\
                    .order_by('-dcount').filter(dcount__gte=threshold)

    lines = request.GET.get('lines')
    if not lines:
        paginator = Paginator(mails_per_day, 10)
    else:
        try:
            paginator = Paginator(mails_per_day, int(lines))
        except ValueError:
            paginator = Paginator(mails_per_day, 10)

    page = request.GET.get('page')
    try:
        mails_per_day = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        mails_per_day = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        mails_per_day = paginator.page(paginator.num_pages)

    context = {
        "days":mails_per_day,
        'start_date':start_date,
        'end_date':end_date,
        'threshold':threshold if threshold != 0 else ''
        }

    return render(request, template, context)


@login_required(login_url="/login/")
def profile(request):

    template = 'profile.html'

    name = request.GET.get('name')
    if not name:
        context = {'code':0}
        return render(request, template, context)
    
    try:
        user = User.objects.get(name=name)
    except:
        context = {'code':-1,
                    'name':name
                    }
        return render(request, template, context)

    if user.in_enron == False:
        context = {'code':-2,
                    'name':name
                    }
        return render(request, template, context)
    
    response_time = request.GET.get('response_time')
    if not response_time:
        response_time = 0
    else:
        try:
            response_time = int(response_time)
        except ValueError:
            response_time = 0
    
    
    #mails sent / received per day
    user_mails = mailAddress.objects.filter(user_id=user.id)
    mails = Mail.objects.filter(Q(sender_id__in=user_mails)|Q(recipient_id__in=user_mails))

    sent_per_day = mails.filter(sender_id__in=user_mails).annotate(time=TruncDate('date'))\
                .values('time').annotate(dcount=Count('enron_id')).aggregate(Avg('dcount'))['dcount__avg']
    
    received_per_day = mails.filter(recipient_id__in=user_mails).annotate(time=TruncDate('date'))\
                .values('time').annotate(dcount=Count('subject')).aggregate(Avg('dcount'))['dcount__avg']

    if sent_per_day is None:
        sent_per_day = 0
    if received_per_day is None:
        received_per_day = 0
    
    
    #average response time
    average_response_time = 0
    if response_time==1:
        replies = mails.filter(sender_id__in=user_mails,is_reply=1)
        number_of_responses = 0
        for mail in replies:
            previous_mail = mails.filter(sender_id=mail.recipient_id, recipient_id=mail.sender_id,
                                date__lt=mail.date, subject__contains=mail.subject[4:]).order_by('-date')[:1]

            previous_mail = list(previous_mail)

            if previous_mail != []:
                previous_mail = previous_mail[0]
                number_of_responses += 1
                average_response_time += (mail.date - previous_mail.date).total_seconds()

        if number_of_responses!=0:
            average_response_time /= number_of_responses

    #I/E Ratio
    number_of_internal_mails = mails.filter(is_intern=1).annotate(count=Count('is_intern'))
    number_of_external_mails = mails.filter(is_intern=0).annotate(count=Count('is_intern'))

    
    #Internal contacts
    contacts = User.objects.raw(f"""SELECT u.id, u.name, u.category, u.in_enron, contact.id
                                            FROM app_user AS u,
                                                (SELECT m.recipient_id AS id FROM app_user AS u, app_mailaddress AS ma, app_mail AS m
                                                 WHERE m.sender_id=ma.id AND ma.user_id={user.id}
                                                 GROUP BY m.recipient_id
                                                 ) AS contact
                                            WHERE u.id=contact.id AND u.in_enron=True;""")

    context = {'code':1,
               'name':name,
               'category':user.category,
               'average_sent':round(sent_per_day,2),
               'average_received':round(received_per_day,2),
               'average_response_time':f'{round(average_response_time/3600,2)}h',
               'number_of_internal_mails':number_of_internal_mails,
               'number_of_external_mails':number_of_external_mails,
               'contacts':contacts,
               }

    return render(request, template, context)