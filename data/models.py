# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField
from django.db import models

CLOTHING_CATEGORIES = (
    ('c', 'clothing'),
    ('s', 'shoes'),
    ('b', 'bags'),
    ('a', 'accessories')
)

DESIGNER_CATEGORIES = (
    ('m', 'men'),
    ('w', 'women')
)


class Store(models.Model):
    lat = models.FloatField()
    lon = models.FloatField()
    name = models.CharField(max_length=100)
    address = models.TextField()
    contact_email = models.CharField(max_length=20)
    contact_phone = models.CharField(max_length=12)
    thumbnail = models.TextField()
    hours = ArrayField(ArrayField(models.IntegerField()))

    def __str__(self):
        return self.name


class Designer(models.Model):
    category = models.CharField(max_length=1, choices=DESIGNER_CATEGORIES, default='m')
    name = models.CharField(max_length=100)
    image = models.TextField()

    def __str__(self):
        return self.name


class SubCategory(models.Model):
    display_name = models.TextField()
    parent_category = models.CharField(max_length=1, choices=CLOTHING_CATEGORIES, default="c")

    class Meta:
        verbose_name = "Subcategories"

    def __str__(self):
        return self.display_name


class Item(models.Model):
    name = models.CharField(max_length=100)
    sku = models.TextField()
    upc = models.TextField()
    price = models.CharField(max_length=100)
    images = ArrayField(models.TextField())
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    designer = models.ForeignKey(Designer, on_delete=models.CASCADE)
    category = models.CharField(max_length=1, choices=CLOTHING_CATEGORIES, default='c')
    subcategory = models.ForeignKey(SubCategory, on_delete=models.SET_NULL, null=True, blank=True)
    designer_name = models.CharField(max_length=100)
    thumbnail = models.TextField()
    sizes = ArrayField(models.CharField(max_length=20))
    sale = models.BooleanField(default=False)
    old_price = models.CharField(max_length=100, default="", null=True, blank=True)
    added_on = models.DateTimeField(default=datetime.datetime.now())
    featured = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class BrickAndMortrUser(AbstractUser):
    name = models.CharField(max_length=100)
    lat = models.FloatField(default=32.7767)
    lon = models.FloatField(default=-96.7970)
    bag_json = models.TextField(default="[]")
    favorites_json = models.TextField(default="[]")
    preferences_json = models.TextField(default="{}")
    password_reset_code = models.TextField(null=True, blank=True)
    password_reset_code_expires = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.username
