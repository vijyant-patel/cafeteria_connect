from django.urls import path
from . import views


urlpatterns = [
    path('', views.shop_list, name='shop-list'),
    path('create/', views.create_shop, name='create-shop'),
    path('edit/<int:shop_id>/', views.edit_shop, name='edit-shop'),
    path('<int:shop_id>/products/', views.shop_products, name='product-list'),
    path('<int:shop_id>/products/add/', views.add_product, name='add-product'),
    path('products/<int:product_id>/edit/', views.edit_product, name='edit-product'),

]
