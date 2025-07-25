# cart/views.py
import json
from orders.models import Order, OrderItem
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from shops.models import Product
from .models import CartItem
from django.shortcuts import render
from cart.context_processors import cart_item_count


def view_cart(request):
    cart_items = CartItem.objects.filter(user=request.user)
    return render(request, 'cart/cart.html', {"cart_items": cart_items})


def add_to_cart(request):
    user = request.user

    try:
        data = json.loads(request.body)
        product_id = data.get("product_id")
        quantity = int(data.get("quantity", 1))
    except Exception as e:
        return JsonResponse({"status": "error", "message": "Invalid data format."})

    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Product not found."})

    product_shop = product.shop
    existing_items = CartItem.objects.filter(user=user)

    if existing_items.exists():
        existing_shop = existing_items.first().product.shop
        if existing_shop != product_shop:
            return JsonResponse({
                "status": "error",
                "message": f"Your cart contains products from '{existing_shop.name}'. Clear cart to add from '{product_shop.name}'."
            })

    cart_item, created = CartItem.objects.get_or_create(
        user=user, product=product,
        defaults={"quantity": quantity}
    )
    if not created:
        cart_item.quantity += quantity
        cart_item.save()
    return JsonResponse({"status": "success", "message": "Added to cart!", 'cart_count': cart_item_count(request)['cart_item_count']})

@csrf_exempt
def clear_cart(request):
    CartItem.objects.filter(user=request.user).delete()
    return JsonResponse({"status": "success", "message": "Cart cleared.", "cart_count": cart_item_count(request)['cart_item_count']})



def place_order_from_cart(request):
    user = request.user
    cart_items = CartItem.objects.filter(user=user)
    if not cart_items.exists():
        return JsonResponse({"status": "error", "message": "Cart is empty."})

    shop = cart_items.first().product.shop
    total = sum(item.product.price * item.quantity for item in cart_items)

    order = Order.objects.create(user=user, shop=shop, total_price=total)

    for item in cart_items:
        OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity)

    # Clear cart
    cart_items.delete()

    return JsonResponse({"status": "success", "message": "Order placed!"})


def cart_count(request):
    if request.user.is_authenticated:
        count = CartItem.objects.filter(user=request.user).count()
    else:
        count = 0
    return JsonResponse({"count": count})