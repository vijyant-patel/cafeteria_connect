# cart/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.cart_list_view, name='cart_list'),
    path('<int:cart_id>/', views.view_cart, name='view_cart'),
    path('add/', views.add_to_cart, name='add_to_cart'),
    path('clear/', views.clear_cart, name='clear_cart'),
    path('place-order/', views.place_order_from_cart, name='place_order_from_cart'),
    path('count/', views.cart_count, name='cart_count'),
]
