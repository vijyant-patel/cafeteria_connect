# cart/views.py
import json
from orders.models import Order, OrderItem
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
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
        is_update = data.get("is_update", False)
        if quantity < 1:
            return JsonResponse({"status": "error", "message": "Invalid quantity. Must be at least 1."})
    except Exception:
        return JsonResponse({"status": "error", "message": "Invalid data format."})

    try:
        product = Product.objects.select_related('shop').get(id=product_id)
    except Product.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Product not found."})

    # 🟢 Get or create a cart for this user and this product's shop
    cart, _ = Cart.objects.get_or_create(user=user, shop=product.shop, is_ordered=False)

    # ✅ Check if item already exists
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={"quantity": quantity}
    )

    if not created:
        if is_update:
            if quantity > product.stock:
                return JsonResponse({
                    "status": "error",
                    "message": f"Only {product.stock} in stock.",
                })
            cart_item.quantity = quantity  # ✅ direct update
        else:
            total_quantity = cart_item.quantity + quantity
            if total_quantity > product.stock:
                return JsonResponse({
                    "status": "error",
                    "message": f"Only {product.stock - cart_item.quantity} more available in stock.",
                })
            cart_item.quantity = total_quantity
        cart_item.save()
    else:
        if quantity > product.stock:
            cart_item.delete()  # remove the just-created item if it exceeds stock
            return JsonResponse({
                "status": "error",
                "message": f"Only {product.stock} available in stock.",
            })

    return JsonResponse({
        "status": "success",
        "message": f"Added to cart for {product.shop.name}!",
        "cart_count": cart.items.count()  # Total unique items in cart
    })



@csrf_exempt
@login_required
def clear_cart(request, cart_id):
    try:
        cart = Cart.objects.get(id=cart_id, user=request.user, is_ordered=False)
    except Cart.DoesNotExist:
        return JsonResponse({
            "status": "error",
            "message": "Cart not found."
        })

    cart.items.all().delete()
    cart.delete()

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



@require_POST
@login_required
def remove_from_cart(request, product_id):
    cart = Cart.objects.filter(user=request.user, is_ordered=False).first()
    if not cart:
        return JsonResponse({'status': 'error', 'message': 'Cart not found'}, status=404)

    item = CartItem.objects.filter(cart=cart, product_id=product_id).first()
    if item:
        item.delete()
        return JsonResponse({'status': 'success', 'message': 'Item removed from cart'})
    return JsonResponse({'status': 'error', 'message': 'Item not found in cart'}, status=404)
