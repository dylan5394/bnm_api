# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
import hashlib
import logging
import smtplib

from django.contrib import messages
from django.core.mail import EmailMessage
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render
from django.utils import timezone
from django.utils.crypto import random

from brickandmortr_server import settings
from models import Contact
from data.models import BrickAndMortrUser

logger = logging.getLogger(__name__)


def index(request):
    return render(request, 'splash_page/index.html', None)


def submit_email(request):
    if request.method == "POST":
        email = request.POST["email"]
        Contact.objects.create(email=email)
    return HttpResponseRedirect("/")


def generate_code(email):
    salt = hashlib.sha1(str(random.random())).hexdigest()[:5]
    if isinstance(email, unicode):
        email = email.encode('utf8')
    return hashlib.sha1(salt + email).hexdigest()


def forgot_password(request):
    if request.method == "POST":
        try:
            to_email = request.POST["email"]
            code = generate_code(to_email)
            user = BrickAndMortrUser.objects.get(username=to_email)
            user.password_reset_code = code
            user.password_reset_code_expires = timezone.now() + datetime.timedelta(minutes=20)
            user.is_active = False
            link = "https://brickandmortr.com/reset-password?code=" + code
            subject = "brick&mortr password reset request"
            body = "Click the following link to finish resetting your brick&mortr password: %s\n\n" \
                   "If you did not make a request to reset your password, please contact support@brickandmortr.com" \
                   "" % link
            from_email = settings.EMAIL_HOST_USER
            email = EmailMessage(subject, body, from_email, [to_email])
            try:
                email.send(fail_silently=False)
                user.save()
                messages.success(request, "Password reset link was sent to the specified email address.")
            except smtplib.SMTPException:
                logger.exception(datetime.datetime.now())
                messages.error(request, "Failed to send password reset email.")
        except BrickAndMortrUser.DoesNotExist, BrickAndMortrUser.MultipleObjectsReturned:
            messages.error(request, "No user found for specified email.")
    return render(request, 'auth/forgot_password.html', None)


def reset_password(request):
    context = dict()
    if request.method == "GET":
        try:
            code = request.GET["code"]
            context["code"] = code
            user = BrickAndMortrUser.objects.get(password_reset_code=code)
            code_expires = user.password_reset_code_expires
            if code_expires and timezone.now() > code_expires:
                messages.error(request, "Password reset request expired.")
        except (KeyError, BrickAndMortrUser.DoesNotExist):
            raise Http404
    elif request.method == "POST":
        code = request.POST["code"]
        password = request.POST["new_password"]
        user = BrickAndMortrUser.objects.get(password_reset_code=code)
        user.set_password(password)
        user.password_reset_code = ""
        user.is_active = True
        user.save()
        messages.info(request, "Password successfully reset.")
    return render(request, 'auth/reset_password.html', context)


def page_not_found(request):
    return render(request, '404.html', None)