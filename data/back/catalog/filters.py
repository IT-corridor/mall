from __future__ import unicode_literals

import django_filters as filters
from . import models


class CommodityFilter(filters.FilterSet):

    category = filters.NumberFilter(name='kind__category')

    class Meta:
        model = models.Commodity
        fields = ('title', 'year', 'season', 'kind', 'category', 'brand',
                  'store')
