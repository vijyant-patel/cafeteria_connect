from django.urls import path
from . import api_views

urlpatterns = [
    path('', api_views.shop_list, name='api-shop-list'),
    path('create/', api_views.create_shop, name='api-create-shop'),
    path('<int:shop_id>/edit/', api_views.edit_shop, name='api-edit-shop'),
    path('<int:shop_id>/products/', api_views.shop_products, name='api-shop-products'),
    path('<int:shop_id>/products/add/', api_views.add_product, name='api-add-product'),
    path('products/<int:product_id>/edit/', api_views.edit_product, name='api-edit-product'),
]
