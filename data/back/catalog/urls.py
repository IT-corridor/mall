from __future__ import unicode_literals

from . import views
from rest_framework.routers import DefaultRouter

catalog_router = DefaultRouter()
catalog_router.register(r'categories', views.CategoryViewSet, 'category')
catalog_router.register(r'kinds', views.KindViewSet, 'kind')
catalog_router.register(r'brands', views.BrandViewSet, 'brand')
catalog_router.register(r'promotions', views.PromotionViewSet, 'promotion')
catalog_router.register(r'colors', views.ColorViewSet, 'color')
catalog_router.register(r'sizes', views.SizeViewSet, 'size')
catalog_router.register(r'commodities', views.CommodityViewSet, 'commodity')
catalog_router.register(r'galleries', views.GalleryViewSet, 'gallery')
catalog_router.register(r'tags', views.TagViewSet, 'tag')
catalog_router.register(r'stocks', views.StockViewSet, 'stock')


urlpatterns = catalog_router.urls

