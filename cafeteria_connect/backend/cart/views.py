# cart/views.py
import json
from orders.models import Order, OrderItem
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from shops.models import Product
from .models import CartItem, Cart
from core.models import Address
from django.shortcuts import render, get_object_or_404
from cart.context_processors import cart_item_count
from django.contrib.auth.decorators import login_required

@login_required
def view_cart(request, cart_id):
    cart = get_object_or_404(Cart, id=cart_id, user=request.user, is_ordered=False)
    cart_items = cart.items.all()
    addresses = Address.objects.filter(user=request.user)

    return render(request, 'cart/cart.html', {"cart_items": cart_items, "cart": cart, 'addresses': addresses})


@login_required
def add_to_cart(request):
    user = request.user

    try:
        data = json.loads(request.body)
        product_id = data.get("product_id")
        quantity = int(data.get("quantity", 1))
    except Exception:
        return JsonResponse({"status": "error", "message": "Invalid data format."})

    try:
        product = Product.objects.select_related('shop').get(id=product_id)
    except Product.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Product not found."})

    # 🟢 Get or create a cart for this user and this product's shop
    cart, _ = Cart.objects.get_or_create(user=user, shop=product.shop, is_ordered=False)

    # ✅ Add or update cart item
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={"quantity": quantity}
    )
    if not created:
        cart_item.quantity += quantity
        cart_item.save()

    return JsonResponse({
        "status": "success",
        "message": f"Added to cart for {product.shop.name}!",
        "cart_count": cart.items.count()  # Total items in that shop's cart
    })


@csrf_exempt
@login_required
def clear_cart(request):
    cart = Cart.objects.filter(user=request.user, is_ordered=False).first()
    if cart:
        cart.items.all().delete()
        cart.delete()  # ✅ delete the empty cart too

    return JsonResponse({
        "status": "success",
        "message": "Cart cleared.",
        "cart_count": cart_item_count(request)['cart_item_count']
    })


@login_required
def place_order_from_cart(request):
    user = request.user
    cart = Cart.objects.filter(user=user, is_ordered=False).first()
    if not cart or not cart.items.exists():
        return JsonResponse({"status": "error", "message": "Cart is empty."})

    shop = cart.items.first().product.shop
    total = sum(item.product.price * item.quantity for item in cart.items.all())

    order = Order.objects.create(user=user, shop=shop, total_price=total)

    for item in cart.items.all():
        OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity)

    cart.is_ordered = True
    cart.save()

    return JsonResponse({"status": "success", "message": "Order placed!"})


@login_required
def cart_count(request):
    count = CartItem.objects.filter(cart__user=request.user, cart__is_ordered=False).count()
    return JsonResponse({"count": count})


@login_required
def cart_list_view(request):
    user_carts = Cart.objects.filter(user=request.user, is_ordered=False).prefetch_related('items', 'shop')
    return render(request, "cart/cart_list.html", {"carts": user_carts})


@login_required
def view_cart_by_id(request, cart_id):
    cart = get_object_or_404(Cart, id=cart_id, user=request.user)
    cart_items = cart.items.all()
    return render(request, 'cart/cart.html', {
        "cart_items": cart_items,
        "cart": cart,
    })
