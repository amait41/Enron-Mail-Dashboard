#!/usr/bin/env python3
import pickle

def load_data(pickle_fp):
    print('Load data: ...', end='\r')
    with open(pickle_fp, "rb") as data:
        emails = pickle.load(data)
    print(f'Load data: succeeds. {len(emails)} emails have been loaded.')
    return emails

fp = '/home/amait/Documents/Employees-mails/emd-project/headers.pkl'

emails = load_data(fp)

print(len(set(list(emails.keys()))))