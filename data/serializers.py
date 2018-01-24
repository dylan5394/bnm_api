from rest_framework import serializers

from data.models import Item, Store, BrickAndMortrUser, Designer, SubCategory


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = BrickAndMortrUser
        fields = ('id', 'username', 'is_staff', 'favorites_json', 'bag_json')


class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = ('id', 'display_name', 'parent_category')


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        depth = 1
        fields = ('id', 'name', 'sku', 'upc', 'price', 'images', 'store', 'category', 'subcategory', 'designer',
                  'thumbnail', 'sizes', 'sale', 'old_price', 'added_on')


class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ('id', 'lat', 'lon', 'name', 'address', 'contact_email', 'contact_phone', 'thumbnail', 'hours')


class DesignerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Designer
        fields = ('id', 'name', 'category', 'image')
