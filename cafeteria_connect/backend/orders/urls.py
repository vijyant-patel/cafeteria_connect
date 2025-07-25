from django.urls import path
from . import views

urlpatterns = [
    path('my/', views.my_orders, name='my_orders'),
    path('place/<int:cart_id>/', views.place_order, name='place_order'),
    path('success/<int:order_id>/', views.order_success, name='order_success'),
    path('<int:order_id>/update/', views.update_order_status, name='update_order_status'),
    
]
