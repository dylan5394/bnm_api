# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import logging
import random

from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from oauth2_provider.ext.rest_framework import OAuth2Authentication
from rest_framework import status
from rest_framework.decorators import authentication_classes, api_view, permission_classes

from rest_framework.generics import RetrieveAPIView, ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from data.util import haversine, fuzzy_match
from models import Item, Store, BrickAndMortrUser, Designer, SubCategory
from serializers import ItemSerializer, StoreSerializer, DesignerSerializer, SubCategorySerializer

logger = logging.getLogger(__name__)


class DesignersResultsSetPagination(PageNumberPagination):
    page_size = 20


@csrf_exempt
@api_view(["POST"])
def create_user(request):
    params = request.data
    name = params["name"]
    username = params["username"]
    password = params["password"]
    lat = params.get("lat", "")
    lon = params.get("lon", "")
    user, created = BrickAndMortrUser.objects.get_or_create(username=username)
    if created:
        if lat and lon:
            user.lat = float(lat)
            user.lon = float(lon)
        user.name = name
        user.set_password(password)
        user.save()
        return Response({"message": "Created user."}, status=status.HTTP_201_CREATED)
    return Response({"message": "Username already in use."}, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes((OAuth2Authentication,))
@permission_classes((IsAuthenticated,))
def update_favorites(request):
    if request.method == "GET":
        return Response(json.loads(request.user.favorites_json), status=status.HTTP_200_OK)
    else:
        request.user.favorites_json = json.dumps(request.data)
        request.user.save()
        return Response({"message": "Updated user favorites."}, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes((OAuth2Authentication,))
@permission_classes((IsAuthenticated,))
def update_bag(request):
    if request.method == "GET":
        return Response(json.loads(request.user.bag_json), status=status.HTTP_200_OK)
    else:
        request.user.bag_json = json.dumps(request.data)
        request.user.save()
        return Response({"message": "Updated user bag."}, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes((OAuth2Authentication,))
@permission_classes((IsAuthenticated,))
def update_preferences(request):
    if request.method == "GET":
        return Response(json.loads(request.user.preferences_json), status=status.HTTP_200_OK)
    else:
        request.user.preferences_json = json.dumps(request.data)
        request.user.save()
        return Response({"message": "Updated user preferences."}, status=status.HTTP_200_OK)


@api_view(['GET'])
def subcategory_list(request):
    if request.method == "GET":
        subcategory_ids = [item.subcategory_id for item in Item.objects.all()]
        subcategories = SubCategorySerializer(list(SubCategory.objects.filter(id__in=subcategory_ids)), many=True)
        for subcategory in subcategories.data:
            sizes = set()
            for item in Item.objects.all():
                if item.subcategory_id == subcategory["id"]:
                    sizes.update(set(item.sizes))
            subcategory["sizes"] = sizes
        return Response({"results": subcategories.data}, status=status.HTTP_200_OK)


class FeaturedItems(ListAPIView):
    serializer_class = ItemSerializer

    def get_queryset(self):
        featured_items = Item.objects.filter(featured=True)
        e = Item.objects.extra(select={'price_float': 'CAST(price AS FLOAT)'}, order_by=['-price_float', 'name'])[:10]
        return featured_items if featured_items.count() > 0 else e


class ItemList(ListAPIView):
    serializer_class = ItemSerializer

    def get_queryset(self):
        items = Item.objects.order_by('name').all()
        param_string = self.request.GET.get("query_params", "")
        if param_string:
            params = json.loads(param_string)
            categories = params.get("categories", [])
            designers = params.get("designers", [])
            stores = params.get("stores", [])
            subcategories = params.get("subcategories", [])
            search_term = params.get("search", "")
            price_info = params.get("price", {})
            sort = params.get("sort", "")

            if sort == "new_items":
                items = Item.objects.order_by('-added_on', 'name').all()
            elif sort == "sale":
                items = Item.objects.order_by('-sale', 'name').all()
            elif sort == "price_low":
                items = Item.objects.extra(select={'price_float': 'CAST(price AS FLOAT)'},
                                           order_by=['price_float', 'name'])
            elif sort == "price_high":
                items = Item.objects.extra(select={'price_float': 'CAST(price AS FLOAT)'},
                                           order_by=['-price_float', 'name'])

            if search_term:
                item_ids = [item.id for item in items if fuzzy_match(item.name, search_term)]
                items = items.filter(id__in=item_ids)
            if categories:
                items = items.filter(category__in=categories)
            if designers:
                items = items.filter(designer__in=designers)
            if stores:
                items = items.filter(store__in=stores)
            if subcategories:
                item_ids = list()
                for item in items:
                    for subcategory in subcategories:
                        sizes = subcategory.get("sizes", item.sizes)
                        intersection = set(item.sizes).intersection(sizes)
                        if item.subcategory and item.subcategory_id == subcategory["id"] and intersection:
                            item_ids.append(item.id)
                items = items.filter(id__in=item_ids)
            if "max" in price_info:
                prices = [item.price for item in items if float(item.price) <= float(price_info["max"])]
                items = items.filter(price__in=prices)
            if "min" in price_info:
                prices = [item.price for item in items if float(item.price) >= float(price_info["min"])]
                items = items.filter(price__in=prices)
        return items


class ItemDetail(RetrieveAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer


class StoreList(ListAPIView):
    serializer_class = StoreSerializer

    def get_queryset(self):
        lat = self.request.GET.get("lat", "")
        lon = self.request.GET.get("lon", "")
        radius = self.request.GET.get("radius", "")

        stores = Store.objects.order_by('name').all()
        if lat and lon and radius:
            store_ids = [store.id for store in Store.objects.all() if haversine(lon, lat, store.lon, store.lat, radius)]
            stores = stores.filter(id__in=store_ids)
        return stores


class StoreDetail(RetrieveAPIView):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer


class StoreItems(ListAPIView):
    serializer_class = ItemSerializer

    def get_queryset(self):
        store_id = self.kwargs['store_id']
        return Store.objects.get(id=store_id).item_set.order_by('name').all()


class DesignerList(ListAPIView):
    serializer_class = DesignerSerializer
    pagination_class = DesignersResultsSetPagination

    def get_queryset(self):
        name = self.request.GET.get("name", "")
        lat = self.request.GET.get("lat", "")
        lon = self.request.GET.get("lon", "")
        radius = self.request.GET.get("radius", "")
        category = self.request.GET.get("category", "")
        designers = Designer.objects.order_by('name').all()
        if lat and lon and radius:
            store_ids = [store.id for store in Store.objects.all() if haversine(lon, lat, store.lon, store.lat, radius)]
            designer_ids = list()
            for store in Store.objects.filter(id__in=store_ids):
                designer_ids.extend([item.designer.id for item in store.item_set.all()])
            designers = designers.filter(id__in=designer_ids)
        if name:
            fuzzy_match_ids = [designer.id for designer in designers if fuzzy_match(name, designer.name)]
            designers = designers.filter(id__in=fuzzy_match_ids)
        if category:
            designers = designers.filter(category=category)
        return designers


class DesignerDetail(RetrieveAPIView):
    queryset = Designer.objects.all()
    serializer_class = DesignerSerializer


class DesignerItems(ListAPIView):
    serializer_class = ItemSerializer

    def get_queryset(self):
        designer_id = self.kwargs['designer_id']
        return Designer.objects.get(id=designer_id).item_set.order_by('name').all()


def generate_clothing_subcategories():
    names = ["Denim Jackets", "Jeans", "Chinos", "T-Shirts", "Hoodies"]
    for name in names:
        SubCategory.objects.create(display_name=name, parent_category="c")


def generate_bags_subcategories():
    names = ["Totes", "Clutches", "Wallets"]
    for name in names:
        SubCategory.objects.create(display_name=name, parent_category="b")


def generate_shoes_subcategories():
    names = ["Sneakers", "Boots", "Loafers"]
    for name in names:
        SubCategory.objects.create(display_name=name, parent_category="s")


def generate_accessories_subcategories():
    names = ["Bracelets", "Necklaces", "Watches"]
    for name in names:
        SubCategory.objects.create(display_name=name, parent_category="a")


def generate_items(request):
    if SubCategory.objects.filter(parent_category="c").count() == 0:
        generate_clothing_subcategories()
    if SubCategory.objects.filter(parent_category="s").count() == 0:
        generate_shoes_subcategories()
    if SubCategory.objects.filter(parent_category="b").count() == 0:
        generate_bags_subcategories()
    if SubCategory.objects.filter(parent_category="a").count() == 0:
        generate_accessories_subcategories()
    subcategory_dictionary = {
        "c": list(SubCategory.objects.filter(parent_category="c")),
        "b": list(SubCategory.objects.filter(parent_category="b")),
        "a": list(SubCategory.objects.filter(parent_category="a")),
        "s": list(SubCategory.objects.filter(parent_category="s"))
    }

    category = request.GET.get("category", "c")
    subcategories = subcategory_dictionary[category]

    if category == "c":
        images = [
            'https://cdn.zeplin.io/5969021e44c5978909d5278b/assets/1CE5FF07-E70F-4413-85BF-49C08AA559DE.png?1=1',
            'https://cdn.zeplin.io/5969021e44c5978909d5278b/assets/1CE5FF07-E70F-4413-85BF-49C08AA559DE.png'
        ]
        thumbnail = 'https://cdn.zeplin.io/5969021e44c5978909d5278b/assets/1CE5FF07-E70F-4413-85BF-49C08AA559DE.png'
    elif category == "s":
        images = [
            'https://cdn.zeplin.io/5969021e44c5978909d5278b/assets/70D7F146-B088-4EE7-9A3F-9EF0AB3C852B.png?1=1',
            'https://cdn.zeplin.io/5969021e44c5978909d5278b/assets/70D7F146-B088-4EE7-9A3F-9EF0AB3C852B.png'
        ]
        thumbnail = 'https://cdn.zeplin.io/5969021e44c5978909d5278b/assets/70D7F146-B088-4EE7-9A3F-9EF0AB3C852B.png'
    elif category == "b":
        images = [
            'https://cdn.zeplin.io/5969021e44c5978909d5278b/assets/A6002DA0-2769-4768-92EA-F9CBC3218188.png?1=1',
            'https://cdn.zeplin.io/5969021e44c5978909d5278b/assets/A6002DA0-2769-4768-92EA-F9CBC3218188.png'
        ]
        thumbnail = 'https://cdn.zeplin.io/5969021e44c5978909d5278b/assets/A6002DA0-2769-4768-92EA-F9CBC3218188.png'
    else:
        images = [
            'https://cdn.zeplin.io/5969021e44c5978909d5278b/assets/2744EF67-0E2F-4E98-BDF0-5623507CE75F.png?1=1',
            'https://cdn.zeplin.io/5969021e44c5978909d5278b/assets/2744EF67-0E2F-4E98-BDF0-5623507CE75F.png'
        ]
        thumbnail = 'https://cdn.zeplin.io/5969021e44c5978909d5278b/assets/2744EF67-0E2F-4E98-BDF0-5623507CE75F.png'

    sizes = ["small", "medium", "large", "x-large"]
    for i in range(Item.objects.all().count(), Item.objects.all().count() + 100):
        random_store_name = "Store " + unicode(random.randint(0, Store.objects.all().count() - 1))
        store = Store.objects.get(name=random_store_name)
        random_designer_name = "Designer " + unicode(random.randint(0, Designer.objects.all().count() - 1))
        designer = Designer.objects.get(name=random_designer_name)
        Item.objects.create(name="Item " + unicode(i),
                            sku=unicode(i),
                            upc=unicode(i) + unicode(i),
                            price=unicode("{0:.2f}".format(random.uniform(10.00, 1000.00))),
                            images=images,
                            store=store,
                            designer=designer,
                            category=category,
                            subcategory=subcategories[random.randint(0, len(subcategories) - 1)],
                            designer_name=random_designer_name,
                            thumbnail=thumbnail,
                            sizes=sizes)
    return HttpResponse(json.dumps({"message": "Added items to db!"}))


def generate_stores(request):
    hours = [[8, 16], [8, 16], [8, 16], [8, 16], [8, 16], [8, 16], [8, 16]]
    thumbnail = "https://cdn.zeplin.io/5969021e44c5978909d5278b/assets/198CD09C-1814-4FD9-84E1-CC0156C6C742.png"
    for i in range(Store.objects.all().count(), Store.objects.all().count() + 100):
        lat = round(random.uniform(30.20, 30.29), 2)
        lon = round(random.uniform(-97.70, -97.79), 2)
        Store.objects.create(lat=lat,
                             lon=lon,
                             name="Store " + unicode(i),
                             address="Address " + unicode(i),
                             contact_email="email" + unicode(i) + "@test.com",
                             contact_phone=unicode(i) + "-111-1111",
                             thumbnail=thumbnail,
                             hours=hours)
    return HttpResponse(json.dumps({"message": "Added stores to db!"}))


def generate_designers(request):
    image = "https://cdn.zeplin.io/5969021e44c5978909d5278b/assets/3DD29AFB-028A-483D-8FE1-5678407C4189.png"
    for i in range(Designer.objects.all().count(), Designer.objects.all().count() + 20):
        if i % 2 == 0:
            category = "m"
        else:
            category = "w"
        Designer.objects.create(name="Designer " + unicode(i),
                                category=category,
                                image=image)
    return HttpResponse(json.dumps({"message": "Added designers to db!"}))


def page_not_found(request):
    return render(request, '404.html', None)
