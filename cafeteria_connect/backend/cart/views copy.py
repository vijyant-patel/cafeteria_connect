# cart/views.py
import json
from orders.models import Order, OrderItem
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from shops.models import Product
from .models import CartItem, Cart
from django.shortcuts import render, get_object_or_404
from cart.context_processors import cart_item_count


def view_cart(request):
    cart_items = CartItem.objects.filter(cart__user=request.user)
    return render(request, 'cart/cart.html', {"cart_items": cart_items})


def add_to_cart(request):
    user = request.user

    try:
        data = json.loads(request.body)
        product_id = data.get("product_id")
        quantity = int(data.get("quantity", 1))
    except Exception:
        return JsonResponse({"status": "error", "message": "Invalid data format."})

    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Product not found."})

    # Find or create cart for this user and shop
    cart, _ = Cart.objects.get_or_create(user=user, shop=product.shop, is_ordered=False)

    # Add or update cart item
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart, product=product,
        defaults={"quantity": quantity}
    )
    if not created:
        cart_item.quantity += quantity
        cart_item.save()

    return JsonResponse({
        "status": "success",
        "message": "Added to cart!",
        "cart_count": cart_item_count(request)['cart_item_count']
    })

@csrf_exempt
def clear_cart(request):
    Cart.objects.filter(user=request.user, is_ordered=False).delete()
    return JsonResponse({"status": "success", "message": "Cart cleared.", "cart_count": cart_item_count(request)['cart_item_count']})



def place_order_from_cart(request):
    user = request.user
    cart = get_object_or_404(Cart, id=cart_id, user=user, is_ordered=False)
    cart_items = cart.items.all()

    if not cart_items.exists():
        return JsonResponse({"status": "error", "message": "Cart is empty."})

    shop = cart_items.first().product.shop
    total = sum(item.product.price * item.quantity for item in cart_items)

    order = Order.objects.create(user=user, shop=shop, total_price=total)

    for item in cart_items:
        OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity)
    

    cart.is_ordered = True
    cart.save()
    # Clear cart
    cart_items.delete()

    return JsonResponse({"status": "success", "message": "Order placed!"})


def cart_count(request):
    if request.user.is_authenticated:
        count = CartItem.objects.filter(user=request.user).count()
    else:
        count = 0
    return JsonResponse({"count": count})


def cart_list_view(request):
    user_carts = Cart.objects.filter(user=request.user, is_ordered=False).prefetch_related('items', 'shop')
    return render(request, "cart/cart_list.html", {"carts": carts})

def view_cart(request, cart_id):
    cart = get_object_or_404(Cart, id=cart_id, user=request.user)
    cart_items = cart.items.all()
    return render(request, 'cart/cart.html', {
        "cart_items": cart_items,
        "cart": cart,
    })
