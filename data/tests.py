# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
import json

from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_api_key.models import APIKey

from data.models import BrickAndMortrUser, Item, Store, Designer, SubCategory


class UserTests(APITestCase):
    def setUp(self):
        self.user = BrickAndMortrUser.objects.create_user(username="test_saving@test.com", password="test")
        self.key = APIKey.objects.create(name="test_key", key="testing")

    def test_create_account(self):
        user_dict_location = {
            'name': 'Location User',
            'username': 'location_user@test.com',
            'password': 'test_password',
            'lat': '30.11',
            'lon': '90.11'
        }
        user_dict = {
            'name': 'Test User',
            'username': 'test_user@test.com',
            'password': 'test_password'
        }

        headers = {
            "HTTP_API_KEY": "testing"
        }

        response = self.client.post('/data/create_user', user_dict, format='json', **headers)
        location_response = self.client.post('/data/create_user', user_dict_location, format='json', **headers)

        # Accounts should be created
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(location_response.status_code, status.HTTP_201_CREATED)

        # Accounts should have the correct names
        self.assertEqual(BrickAndMortrUser.objects.get(username="location_user@test.com").name, "Location User")
        self.assertEqual(BrickAndMortrUser.objects.get(username="test_user@test.com").name, "Test User")

        # Accounts should have the correct lat and lon values
        self.assertEqual(BrickAndMortrUser.objects.get(username="location_user@test.com").lat, 30.11)
        self.assertEqual(BrickAndMortrUser.objects.get(username="location_user@test.com").lon, 90.11)
        self.assertEqual(BrickAndMortrUser.objects.get(username="test_user@test.com").lat, 32.7767)
        self.assertEqual(BrickAndMortrUser.objects.get(username="test_user@test.com").lon, -96.7970)

        duplicate_reponse = self.client.post('/data/create_user', user_dict_location, format='json', **headers)

        # Account creation attempts with usernames that already exist in our DB should fail
        self.assertEqual(duplicate_reponse.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(duplicate_reponse.data, {"message": "Username already in use."})

        no_api_key_response = self.client.post('/data/create_user', user_dict, format='json')

        # Requests without an API key should fail

        self.assertEqual(no_api_key_response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_favorites(self):
        self.client.force_authenticate(user=self.user)
        favorites = [
            'item 1'
        ]

        # Favorites should update and be retrieved
        response = self.client.post('/data/users/favorites', favorites, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get('/data/users/favorites')
        self.assertEqual(response.content, '["item 1"]')

    def test_bag(self):
        self.client.force_authenticate(user=self.user)
        bag = [
            'item 1'
        ]

        # Bag should update and be retrieved
        response = self.client.post('/data/users/bag', bag, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get('/data/users/bag')
        self.assertEqual(response.content, '["item 1"]')

    def test_preferences(self):
        self.client.force_authenticate(user=self.user)
        favorites = [
            'item 1'
        ]

        # Favorites should update and be retrieved
        response = self.client.post('/data/users/favorites', favorites, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get('/data/users/favorites', {}, format='json')
        self.assertEqual(response.content, '["item 1"]')


class ItemTests(APITestCase):
    def setUp(self):
        self.key = APIKey.objects.create(name="test_key", key="testing")

    def test_list(self):
        store = Store.objects.create(lat=30.00, lon=90.00, name="test store", address="123 test st",
                                     contact_email="contact@test.com", contact_phone="1111111", thumbnail="url.com",
                                     hours=[[8, 16], [8, 16], [8, 16], [8, 16], [8, 16], [8, 16], [8, 16]])
        designer = Designer.objects.create(name="test designer", image="url.com")
        designer2 = Designer.objects.create(name="test designer2", image="url2.com")

        now = datetime.datetime.now()
        ten_min = now - datetime.timedelta(minutes=10)
        twenty_min = now - datetime.timedelta(minutes=20)

        subcategory = SubCategory.objects.create(display_name="Denim Jackets")

        Item.objects.create(name="Clothing Item", sku="123", upc="234", price="12.29",
                            images=["url.com"], store=store, designer=designer, category="c", subcategory=subcategory,
                            designer_name=designer.name, thumbnail="thumbnail_url.com",
                            sizes=["small", "medium", "large", "x-large"], added_on=ten_min)

        Item.objects.create(name="Bag Item", sku="222", upc="333", price="22.29",
                            images=["url.com"], store=store, designer=designer, category="b",
                            designer_name=designer.name, thumbnail="thumbnail_url.com",
                            sizes=["small", "medium", "large", "x-large"], sale=True, added_on=twenty_min)

        Item.objects.create(name="Accessories Item", sku="444", upc="555", price="33.29",
                            images=["url.com"], store=store, designer=designer, category="a",
                            designer_name=designer.name, thumbnail="thumbnail_url.com",
                            sizes=["small", "medium", "large", "x-large"], added_on=twenty_min)

        Item.objects.create(name="Shoes Item", sku="666", upc="777", price="44.29",
                            images=["url.com"], store=store, designer=designer2, category="s",
                            designer_name=designer2.name, thumbnail="shoes_thumb_url.com",
                            sizes=["small", "medium", "large", "x-large"], added_on=twenty_min)

        Item.objects.create(name="testing", sku="666", upc="777", price="30.00",
                            images=["url.com"], store=store, designer=designer2, category="s",
                            designer_name=designer2.name, thumbnail="shoes_thumb_url.com",
                            sizes=["small", "medium", "large", "x-large"], added_on=twenty_min)
        headers = {
            "HTTP_API_KEY": "testing"
        }

        # Items should return all items
        response = self.client.get('/data/items/', **headers)
        self.assertEqual(response.data["count"], 5)
        self.assertEqual(response.data["results"][0]["name"], "Accessories Item")

        # Categories argument should filter results by categories supplied
        p1 = {
            "categories": ["c", "b"]
        }
        p2 = {
            "categories": ["s", "a"]
        }
        response = self.client.get('/data/items/?query_params=' + json.dumps(p1), **headers)
        self.assertEqual(response.data["count"], 2)
        self.assertEqual(response.data["results"][0]["name"], "Bag Item")
        response = self.client.get('/data/items/?query_params=' + json.dumps(p2), **headers)
        self.assertEqual(response.data["count"], 3)
        self.assertEqual(response.data["results"][0]["name"], "Accessories Item")

        # Designers argument should filter results by designers supplied
        p1 = {
            "designers": [designer.id]
        }
        p2 = {
            "designers": [designer2.id]
        }
        response = self.client.get('/data/items/?query_params=' + json.dumps(p1), **headers)
        self.assertEqual(response.data["count"], 3)
        self.assertEqual(response.data["results"][0]["name"], "Accessories Item")
        response = self.client.get('/data/items/?query_params=' + json.dumps(p2), **headers)
        self.assertEqual(response.data["count"], 2)
        self.assertEqual(response.data["results"][0]["name"], "Shoes Item")

        # Sort by parameters should return appropriate sorted results
        p1 = {
            "sort": "price_low"
        }
        p2 = {
            "sort": "price_high"
        }
        p3 = {
            "sort": "new_items"
        }
        p4 = {
            "sort": "sale"
        }
        response = self.client.get('/data/items/?query_params=' + json.dumps(p1), **headers)
        self.assertEqual(response.data["results"][0]["name"], "Clothing Item")
        response = self.client.get('/data/items/?query_params=' + json.dumps(p2), **headers)
        self.assertEqual(response.data["results"][0]["name"], "Shoes Item")
        response = self.client.get('/data/items/?query_params=' + json.dumps(p3), **headers)
        self.assertEqual(response.data["results"][0]["name"], "Clothing Item")
        response = self.client.get('/data/items/?query_params=' + json.dumps(p4), **headers)
        self.assertEqual(response.data["results"][0]["name"], "Bag Item")

        # Search argument should filter by fuzzy matching item names
        p1 = {
            "search": "test"
        }
        response = self.client.get('/data/items/?query_params=' + json.dumps(p1), **headers)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["name"], "testing")

        # Min and max price arguments should filter items appropriately
        p1 = {
            "price": {
                "min": "20.00"
            }
        }
        p2 = {
            "price": {
                "max": "30.00"
            }
        }
        p3 = {
            "price": {
                "max": "40.00",
                "min": "30.00"
            }
        }
        response = self.client.get('/data/items/?query_params=' + json.dumps(p1), **headers)
        self.assertEqual(response.data["count"], 4)
        response = self.client.get('/data/items/?query_params=' + json.dumps(p2), **headers)
        self.assertEqual(response.data["count"], 3)
        response = self.client.get('/data/items/?query_params=' + json.dumps(p3), **headers)
        self.assertEqual(response.data["count"], 2)

        # Subcategories data should filter items appropriately
        p1 = {
            "subcategories": [
                {
                    "id": subcategory.id,
                    "sizes": ["large"]
                }
            ]
        }
        p2 = {
            "subcategories": [
                {
                    "id": subcategory.id,
                    "sizes": ["nonexistent-size"]
                }
            ]
        }
        response = self.client.get('/data/items/?query_params=' + json.dumps(p1), **headers)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["name"], "Clothing Item")
        response = self.client.get('/data/items/?query_params=' + json.dumps(p2), **headers)
        self.assertEqual(response.data["count"], 0)

    def test_detail(self):
        store = Store.objects.create(lat=30.00, lon=90.00, name="test store", address="123 test st",
                                     contact_email="contact@test.com", contact_phone="1111111", thumbnail="url.com",
                                     hours=[[8, 16], [8, 16], [8, 16], [8, 16], [8, 16], [8, 16], [8, 16]])
        designer2 = Designer.objects.create(name="test designer2", image="url2.com")
        test_item = Item.objects.create(name="testing", sku="666", upc="777", price="30.00",
                                        images=["url.com"], store=store, designer=designer2, category="s",
                                        designer_name=designer2.name, thumbnail="shoes_thumb_url.com",
                                        sizes=["small", "medium", "large", "x-large"])

        headers = {
            "HTTP_API_KEY": "testing"
        }

        response = self.client.get('/data/items/' + unicode(test_item.id) + '/', **headers)
        self.assertEqual(response.data["id"], test_item.id)
        self.assertEqual(response.data["name"], test_item.name)

    def test_featured(self):
        headers = {
            "HTTP_API_KEY": "testing"
        }
        store = Store.objects.create(lat=30.00, lon=90.00, name="test store", address="123 test st",
                                     contact_email="contact@test.com", contact_phone="1111111", thumbnail="url.com",
                                     hours=[[8, 16], [8, 16], [8, 16], [8, 16], [8, 16], [8, 16], [8, 16]])
        designer2 = Designer.objects.create(name="test designer2", image="url2.com")
        Item.objects.create(name="testing", sku="666", upc="777", price="30.00",
                                        images=["url.com"], store=store, designer=designer2, category="s",
                                        designer_name=designer2.name, thumbnail="shoes_thumb_url.com",
                                        sizes=["small", "medium", "large", "x-large"])
        response = self.client.get('/data/items/featured', **headers)
        self.assertEqual(response.data["count"], 1)
        response = self.client.get('/data/items/featured')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class StoreTests(APITestCase):
    def setUp(self):
        self.store = Store.objects.create(lat=30.00, lon=90.00, name="test store", address="123 test st",
                                          contact_email="contact@test.com", contact_phone="1111111",
                                          thumbnail="url.com",
                                          hours=[[8, 16], [8, 16], [8, 16], [8, 16], [8, 16], [8, 16], [8, 16]])
        self.key = APIKey.objects.create(name="test_key", key="testing")
        self.headers = {
            "HTTP_API_KEY": "testing"
        }

    def test_list(self):
        response = self.client.get('/data/stores/', **self.headers)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["id"], self.store.id)
        self.assertEqual(response.data["results"][0]["name"], self.store.name)

    def test_detail(self):
        response = self.client.get('/data/stores/' + unicode(self.store.id) + '/', **self.headers)
        self.assertEqual(response.data["id"], self.store.id)

    def test_store_items(self):
        designer = Designer.objects.create(name="test designer2", image="url")
        item = Item.objects.create(name="testing", sku="666", upc="777", price="30.00",
                                   images=["url.com"], store=self.store, designer=designer, category="s",
                                   designer_name=designer.name, thumbnail="shoes_thumb_url.com",
                                   sizes=["small", "medium", "large", "x-large"])
        response = self.client.get('/data/stores/' + unicode(self.store.id) + '/items/', **self.headers)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["id"], item.id)


class DesignerTests(APITestCase):
    def setUp(self):
        self.designer = Designer.objects.create(name="test designer2", image="url")
        self.key = APIKey.objects.create(name="test_key", key="testing")
        self.headers = {
            "HTTP_API_KEY": "testing"
        }

    def test_list(self):
        response = self.client.get('/data/designers/', **self.headers)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["id"], self.designer.id)

    def test_detail(self):
        response = self.client.get('/data/designers/' + unicode(self.designer.id) + '/', **self.headers)
        self.assertEqual(response.data["id"], self.designer.id)

    def test_designer_items(self):
        store = Store.objects.create(lat=30.00, lon=90.00, name="test store", address="123 test st",
                                     contact_email="contact@test.com", contact_phone="1111111",
                                     thumbnail="url.com",
                                     hours=[[8, 16], [8, 16], [8, 16], [8, 16], [8, 16], [8, 16], [8, 16]])
        item = Item.objects.create(name="testing", sku="666", upc="777", price="30.00",
                                   images=["url.com"], store=store, designer=self.designer, category="s",
                                   designer_name=self.designer.name, thumbnail="shoes_thumb_url.com",
                                   sizes=["small", "medium", "large", "x-large"])
        response = self.client.get('/data/designers/' + unicode(self.designer.id) + '/items/', **self.headers)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["id"], item.id)


class CategoryTests(APITestCase):
    def setUp(self):
        self.key = APIKey.objects.create(name="test_key", key="testing")
        self.headers = {
            "HTTP_API_KEY": "testing"
        }

    def test_subcategories(self):
        subcategory = SubCategory.objects.create(display_name="Denim Jackets")
        store = Store.objects.create(lat=30.00, lon=90.00, name="test store", address="123 test st",
                                     contact_email="contact@test.com", contact_phone="1111111", thumbnail="url.com",
                                     hours=[[8, 16], [8, 16], [8, 16], [8, 16], [8, 16], [8, 16], [8, 16]])
        designer2 = Designer.objects.create(name="test designer2", image="url2.com")
        item = Item.objects.create(name="testing", sku="666", upc="777", price="30.00",
                                        images=["url.com"], store=store, designer=designer2, category="s",
                                        subcategory=subcategory,
                                        designer_name=designer2.name, thumbnail="shoes_thumb_url.com",
                                        sizes=["small", "medium", "large", "x-large"])
        # Subcategories endpoint should return all currently related subcategories and sizes of related items
        response = self.client.get('/data/subcategories/', **self.headers)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["id"], subcategory.id)
        self.assertEqual(response.data["results"][0]["display_name"], subcategory.display_name)
        self.assertEqual(response.data["results"][0]["parent_category"], subcategory.parent_category)
        self.assertEqual(len(response.data["results"][0]["sizes"] & set(item.sizes)), len(item.sizes))
        response = self.client.get('/data/subcategories/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
