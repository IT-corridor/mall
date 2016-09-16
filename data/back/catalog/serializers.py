from __future__ import unicode_literals

from rest_framework import serializers
from . import models


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Category


class KindSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Kind


class KindVerboseSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)

    class Meta:
        model = models.Kind


class BrandSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Brand


class PromotionSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Promotion


class ColorSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Color


class SizeSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Size


class GallerySerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Gallery


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Tag


class StockSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Stock
        extra_kwargs = {'commodity': {'allow_null': True, 'required': False}}


# COMMODITY Serializers

class CommodityListSerializer(serializers.ModelSerializer):

    # TODO: set parent serializers read-only and add its ids,
    # because of issues with creating/updating)
    # TODO: add store serializer (avatar of the store needed)
    tags = TagSerializer(source='tag_set', many=True, read_only=True)
    name = serializers.CharField(source='__unicode__', read_only=True)
    season_text = serializers.CharField(source='get_season_display',
                                        read_only=True)

    cover = serializers.SerializerMethodField(read_only=True)
    category = serializers.PrimaryKeyRelatedField(source='kind.category',
                                                  read_only=True)
    stock_set = StockSerializer(read_only=True, many=True)

    def get_cover(self, obj):
        gallery = obj.gallery_set.first()
        if gallery and gallery.thumb.name:
            request = self.context.get('request', None)
            url = gallery.thumb.url
            if request is not None:
                return request.build_absolute_uri(url)
            return url
        return

    class Meta:
        model = models.Commodity


class CommodityListVerboseSerializer(CommodityListSerializer):
    kind = KindVerboseSerializer(read_only=True)
    brand = BrandSerializer(read_only=True)
    colors = ColorSerializer(read_only=True, many=True)
    sizes = SizeSerializer(read_only=True, many=True)


class CommodityDetailSerializer(CommodityListSerializer):
    gallery_set = GallerySerializer(many=True, read_only=True)


class CommodityVerboseSerializer(CommodityListVerboseSerializer):
    gallery_set = GallerySerializer(many=True, read_only=True)


class CommodityLinkSerializer(serializers.ModelSerializer):
    """ This serializer is used to present nested data in the
    :model:`snapshot.Link` serializer """
    kind = KindSerializer(read_only=True)
    colors = ColorSerializer(read_only=True, many=True)
    crop = serializers.SerializerMethodField(read_only=True)

    def get_crop(self, obj):
        gallery = obj.gallery_set.first()
        if gallery and gallery.crop.name:
            request = self.context.get('request', None)
            url = gallery.crop.url
            if request is not None:
                return request.build_absolute_uri(url)
            return url
        return

    class Meta:
        model = models.Commodity
        fields = ('pk', 'colors', 'crop', 'kind', 'title')


class EventSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Event
