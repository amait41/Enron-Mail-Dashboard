# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

#from django.contrib.auth.models import User
from django.db import models


class User(models.Model):
  
    name = models.CharField(max_length=100,unique=True,null=False)
    in_enron = models.BooleanField(null=False)
    category = models.CharField(max_length=40,null=False)

    def __str__(self):
        return f"{self.id}, {self.name}, {self.in_enron}, {self.category}"


class mailAddress(models.Model):
    
    address = models.EmailField(max_length=200, unique=True,null=False)
    user = models.ForeignKey(User,on_delete=models.CASCADE,null=False)

    def __str__(self):
        return f"{self.id}, {self.address}, {self.user.name}"


class Mail(models.Model):
    enron_id = models.CharField(max_length=30,primary_key=True)
    date = models.DateTimeField(null=False)
    sender = models.ForeignKey(mailAddress,on_delete=models.CASCADE,related_name='sender',null=False)
    recipient = models.ForeignKey(mailAddress,on_delete=models.CASCADE,related_name='recipient',null=False)
    is_reply = models.BooleanField(null=False)
    is_intern = models.BooleanField(null=False)
    subject = models.CharField(max_length=200, null=True)

    def __str__(self):
        return f"{self.enron_id}, {self.date}, {self.sender.address}, {self.recipient.address}, {self.is_reply}, {self.is_intern}"