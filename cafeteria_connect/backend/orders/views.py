from .tasks import generate_invoice
from core.kafka.producer import publish_order_placed
from django.shortcuts import render, get_object_or_404, redirect
from shops.models import Shop, Product
from cart.models import Cart
from .models import Order, OrderItem
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@login_required
def my_orders(request):
    user = request.user
    is_shopkeeper = user.role == 'shopkeeper' or False
    if is_shopkeeper:
        # Get orders for shops owned by this shopkeeper
        shops = Shop.objects.filter(owner=user)
        orders = Order.objects.filter(shop__in=shops).order_by('-created_at') \
                    .prefetch_related('items', 'items__product', 'shop', 'customer')
    else:
        # Regular customer orders
        orders = Order.objects.filter(customer=user).order_by('-created_at') \
                    .prefetch_related('items', 'items__product', 'shop')

    return render(request, 'orders/my_orders.html', {'orders': orders, 'is_shopkeeper': is_shopkeeper})

@csrf_exempt
@login_required
def place_order(request, cart_id):
    cart = get_object_or_404(Cart, id=cart_id, user=request.user, is_ordered=False)
    products = cart.items.all()

    if request.method == 'POST':
        is_json = request.headers.get('Content-Type') == 'application/json'
        if is_json:
            try:
                data = json.loads(request.body)
                selected_ids = data.get('product_ids', [])
                quantities = data.get('quantities', {})
            except Exception:
                return JsonResponse({'status': 'error', 'message': 'Invalid JSON data'}, status=400)
        else:
            selected_ids = request.POST.getlist('product_ids')
            quantities = {pid: request.POST.get(f'quantity_{pid}', 1) for pid in selected_ids}

        if not selected_ids:
            return JsonResponse({'status': 'error', 'message': 'No products selected'}, status=400)

        total = 0
        shop = products[0].product.shop if products else None  # Get shop from first product
        order = Order.objects.create(customer=request.user, shop=shop, status='pending')

        for item in products:
            pid = str(item.product.id)
            if pid in selected_ids:
                quantity = int(quantities.get(pid, item.quantity))  # fallback to cart quantity
                subtotal = item.product.price * quantity
                total += subtotal
                OrderItem.objects.create(order=order, product=item.product, quantity=quantity)

        order.total_price = total
        order.save()

        order_data = {
            'order_id': order.id,
            'customer_id': request.user.id,
            'shop_id': shop.id if shop else None,
            'total_price': float(order.total_price),
            'status': order.status,
            'items': [
                {
                    'product_id': item.product.id,
                    'product_name': item.product.name,
                    'quantity': item.quantity,
                    'price': float(item.product.price),
                }
                for item in order.items.all()
            ]
        }

        # ✅ Mark cart as ordered & delete it
        cart.items.all().delete()
        cart.delete()

        publish_order_placed(order_data)
        generate_invoice.delay(order.id)

        if is_json:
            return JsonResponse({'status': 'success', 'message': 'Order placed!', 'order_id': order.id})
        else:
            return redirect('order_success', order_id=order.id)

    return render(request, 'orders/shop_products.html', {'cart': cart, 'products': [item.product for item in products]})

@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    return render(request, 'orders/order_success.html', {'order': order})




@login_required
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS_CHOICES).keys():
            order.status = new_status
            order.save()
            # 🔁 (Optional) trigger Kafka/Celery event here
        return HttpResponseRedirect(reverse('my_orders'))  # or redirect to admin/order list

    return render(request, 'orders/update_status.html', {'order': order, 'status_choices': Order.STATUS_CHOICES})