# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from models import Item, Store, BrickAndMortrUser, Designer, SubCategory

admin.site.register(Item)
admin.site.register(Store)
admin.site.register(BrickAndMortrUser)
admin.site.register(Designer)
admin.site.register(SubCategory)