#!/usr/bin/env python3
import os
import sys
import pickle
import re
import email
from time import time
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()
import django.db.utils
from django.utils.timezone import datetime, timezone, timedelta
from app.models import mailAddress, Mail, User
import xml.etree.ElementTree as ET
from collections import defaultdict
from multiprocessing import Pool
from tqdm import tqdm


## Preprocessing employes_enron.xml ##########################################

def preprocessXMLFile():
    path = os.getcwd()
    tree = ET.parse(path + '/employees_enron.xml')
    root = tree.getroot()

    for child in root:
        current_user = User(in_enron = True)
        current_user.save()
        
        last_name = ''
        first_name = ''

        try:
            current_user.category = child.attrib['category']
        except KeyError:
            current_user.category = 'Employee'

        for subchild in child:
            if subchild.tag == 'lastname':
                last_name = subchild.text

            elif subchild.tag == 'firstname':
                first_name = subchild.text

            elif subchild.tag == 'email':
                new_mail = mailAddress(address = subchild.attrib['address'], user = current_user)
                try:
                    new_mail.save()
                except django.db.utils.IntegrityError as e:
                    print(e)
        
        current_user.name = f"{first_name} {last_name}"
        current_user.save()
    # 149 users
    # 297 mailAddress


## Usefull function ##########################################################

def convert(date):
    #converts a naive datetime into an aware django datetime in UTC timezone
    #e.g. 4 Dec 2000 02:09:00 -0800 (PST) into 2000-12-04 10:09:00+00:00
    if date[1] == ' ':            #ie if the day has only one digit
        date = '0' + date             #for string length consistency
    try:
        converted_date = datetime.strptime(date, '%d %b %Y %H:%M:%S %z')
    except ValueError:
        return '2001-03-09 11:15:36:00+00:00'
    #converting the date in UTC format
    UTC = timezone(timedelta(hours = 0))
    converted_date = converted_date.astimezone(UTC)
    return converted_date

def get_name(mail_address):
    
    mail_address = re.sub(r'[\'\"]', "", mail_address)

    if len(mail_address) > 100:
        regex0 = re.compile(r'_([0-9a-zA-Z]*)@newman.oscar.aol.com$')
        found = regex0.search(mail_address)
        if found:
            return found.group(1).strip()

    regex1 = re.compile(r'^([a-zA-Z]*[\._-][a-zA-Z]*)@.*\..{,3}')
    found = regex1.search(mail_address)
    if found:
        return str.title(re.sub(r'[\._-]', ' ',found.group(1))).strip()

    regex4 = re.compile(r'^([a-zA-Z]\.\.[a-zA-Z]*)@.*\..{,3}')
    found = regex4.search(mail_address)
    if found:
        return str.title(re.sub(r'\.\.', ' ',found.group(1))).strip()

    regex2 = re.compile(r'^<?(.*)@.*>$')
    found = regex2.search(mail_address)
    if found:
        return str.title(found.group(1)).strip()
    
    regex3 = re.compile(r'^([A-Za-z]*)@')
    found = regex3.search(mail_address)
    if found:
        return re.sub(r"([A-Z])", r" \1", found.group(1)).strip()

    return mail_address

def inEnron(mail_address):
    regex = re.compile(r'.*@enron\..*', re.IGNORECASE)
    found = regex.search(mail_address)
    return False if found==None else True

def isReply(mail_subject):
    regex = re.compile(r'^[Rr][Ee]:')
    found = regex.search(mail_subject)
    return False if found==None else True

def isIntern(sender, recipients):
    if not inEnron(sender):
        return False
    for recipient in recipients:
        if not inEnron(recipient):
            return False
    return True

def progress_info(n, prefix="Computing:", size=40, file=sys.stdout):
    if n%10 == 0:
        print("{} {} / {:2.1%}".format(prefix, n, n/517401), end="\r")
    return n + 1

##############################################################################

## Create pickle #############################################################

def create_pickle(data_fp, name):
    n = 0
    emails = {}
    t0 = time()
    for root, dirs, files in os.walk(data_fp, topdown=False):
        for file in files:
            fp = os.path.join(root, file)
            n  = progress_info(n, prefix="Analyzing data:")
            with open(fp, 'r', encoding='utf-8') as f:
                try:
                    e = email.message_from_file(f)
                except UnicodeDecodeError as error:
                    with open(fp, 'r', encoding='iso-8859-1') as f:
                        try:
                            e = email.message_from_file(f)
                        except UnicodeDecodeError as error:
                            print('UnicodeDecodeError:', fp)

            mail_id = e.get('Message-ID')
            emails[mail_id] = {key:value for key, value in e.items()}
            emails[mail_id]['fp'] = fp

    print(f'Completed: {n} files have been read in {round(time()-t0,2)}s.')

    print('Create pickle: ...', end="\r")
    with open(os.path.join(name), "wb") as data:
        pickle.dump(emails, data)
    print(f'Create pickle: succeeds. {len(emails)} emails have been save.')

    return os.path.join(name)


def load_data(pickle_fp):
    print('Load data: ...', end='\r')
    with open(pickle_fp, "rb") as data:
        emails = pickle.load(data)
    print(f'Load data: succeeds. {len(emails)} emails have been loaded.')
    return emails


def catch_infos(email):

    # mail_id
    regex = re.compile(r'^<([0-9]*\.[0-9]*)\.JavaMail\.evans@thyme>$')
    email_id = regex.search(email['Message-ID']).group(1)
    
    # mail_date
    try:
        email_date = convert(email['Date'][5:-6])
    except KeyError:
        # there is only one email that throws an exception.
        # --> /home/amait/Downloads/maildir/lokey-t/calendar/33.
        email_date = None

    # subject
    email_subject = email['Subject']
    if len(email_subject) > 200:
        email_subject = email_subject[:200]

    # is_reply
    is_reply = isReply(email['Subject'])
    
    # mail_sender
    email_sender = email['From']

    # mail_recipients
    email_recipients = []
    recipient_fields = ['To', 'Cc', 'Bcc']
    for field in recipient_fields:
        try:
            email_recipients += re.split(',', re.sub(r"\s+", "", email[field])) #flags=re.UNICODE))
        except KeyError:
            pass

    if len(email_recipients) == 0:
        recipient_fields = ['X-To', 'X-cc', 'X-bcc']
        for field in recipient_fields:
            try:
                email_recipients += re.split(',', re.sub(r"\s+", "", email[field])) #flags=re.UNICODE))
            except KeyError:
                pass

    # remove recipients without '@'
    regex = re.compile(r'.*@.*')
    email_recipients = [elm for elm in email_recipients if regex.match(elm)]
    # remove duplicate recipients
    email_recipients = list(set(email_recipients))

    #is_intern
    is_intern = isIntern(email_sender, email_recipients)

    infos = [email_id, email_date, email_subject, is_reply, is_intern, email_sender, email_recipients]
    
    return infos


def update_db(infos):
    
    mail_id, mail_date, mail_subject, is_reply, is_intern, sender_address, recipients_address = infos

    try:
        sender_address_ = mailAddress.objects.get(address=sender_address)
    except django.core.exceptions.ObjectDoesNotExist:
        name = get_name(sender_address)
        try:
            sender_ = User.objects.get(name=name)
        except:
            sender_ = User(name=name,
                          in_enron=inEnron(sender_address),
                          category='Unknown')
            sender_.save()
            '''try:
                sender_.save()
            except Exception as e:
                print(mail_id)
                print(e, '----->', sender_)
                return False'''
        sender_address_ = mailAddress(address=sender_address, user=sender_)
        sender_address_.save()
        '''
        try:
            sender_address_.save()
        except Exception as e:
            print(mail_id)
            print(e, ':', sender_address_)
            return False'''

    for recipient_address in recipients_address:
        try:
            recipient_address_ = mailAddress.objects.get(address=recipient_address)
        except django.core.exceptions.ObjectDoesNotExist:
            name = get_name(recipient_address)
            try:
                recipient_ = User.objects.get(name=name)
            except:
                recipient_ = User(name=name,
                              in_enron=inEnron(recipient_address),
                              category='Unknown')
                recipient_.save()
                '''
                try:
                    recipient_.save()
                except Exception as e:
                    print(mail_id)
                    print(e, '----->', recipient_)
                    return False
                '''
            recipient_address_ = mailAddress(address=recipient_address, user=recipient_)
            recipient_address_.save()
            '''
            try:
                recipient_address_.save()
            except Exception as e:
                print(mail_id)
                print(e, ':', recipient_address_)
                return False
            '''
        mail_ = Mail(enron_id=mail_id,
                    date=mail_date,
                    subject=mail_subject,
                    sender=sender_address_,
                    recipient=recipient_address_,
                    is_intern = is_intern,
                    is_reply=is_reply)
        mail_.save()
        '''
        try:
            mail_.save()
        except Exception as e:
            print(mail_id)
            print(e, '----->', mail_)
            return False
        return True
        '''

if __name__=="__main__":

    data_fp = '/users/2021ds/192009056/Téléchargements/maildir'
    #data_fp = '/home/amait/Downloads/maildir'
    pkl_file_name = 'headers.pkl'
    
    x = input('Preprocess XML file (0/1)? ')
    if x == '1':
        preprocessXMLFile()
    
    x = input('Create pickle file (0/1)? ')
    if x == '1':
        pkl_fp = create_pickle(data_fp, name=pkl_file_name)
    else:
        pkl_fp = os.path.join(pkl_file_name)

    x = input('Update database (0/1)? ')
    if x == '1':
        error = []
        emails = load_data(pickle_fp=pkl_fp)
        n = 1
        errors = 0
        regex = re.compile(r'^<([0-9]*\.[0-9]*)\.JavaMail\.evans@thyme>$')
        for email in emails.values():
            try:
                email_id = regex.search(email['Message-ID']).group(1)
                mail = Mail.objects.get(enron_id=email_id)    
            except ValueError as ve:
                print(ve, ':', email_id)
            except django.core.exceptions.ObjectDoesNotExist:
                infos = catch_infos(email)
                try:
                    update_db(infos)
                except Exception as e:
                    print(e)
                    errors += 1
                    print(f"# errors: {errors}", end='\r')
                    with open("update_errors.txt", "a") as filout:
                        filout.write(f'{email_id}\n')
            
            n = progress_info(n, prefix='Updating database:')
        
        print('Update database: succeeds.')
