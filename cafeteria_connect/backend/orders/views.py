from .tasks import generate_invoice
from core.kafka.producer import publish_order_placed
from django.shortcuts import render, get_object_or_404, redirect
from shops.models import Shop, Product
from cart.models import Cart
from core.models import Address
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
                address_id = data.get('address_id')
            except Exception:
                return JsonResponse({'status': 'error', 'message': 'Invalid JSON data'}, status=400)
        else:
            selected_ids = request.POST.getlist('product_ids')
            quantities = {pid: request.POST.get(f'quantity_{pid}', 1) for pid in selected_ids}
            address_id = request.POST.get('address_id')

        if not selected_ids or not address_id:
            return JsonResponse({'status': 'error', 'message': 'Missing product(s) or address'}, status=400)

        selected_address = get_object_or_404(Address, id=address_id, user=request.user)

        total = 0
        shop = products[0].product.shop if products else None
        order = Order.objects.create(
            customer=request.user,
            shop=shop,
            status='pending',
            address=selected_address  # 👈 attach the address
        )

        for item in products:
            pid = str(item.product.id)
            if pid in selected_ids:
                quantity = int(quantities.get(pid, item.quantity))
                subtotal = item.product.price * quantity
                total += subtotal
                OrderItem.objects.create(order=order, product=item.product, quantity=quantity)

        order.total_price = total
        order.save()

        cart.items.all().delete()
        cart.delete()

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

        publish_order_placed(order_data)
        generate_invoice.delay(order.id)

        return JsonResponse({'status': 'success', 'message': 'Order placed!', 'order_id': order.id})

    return render(request, 'orders/shop_products.html', {
        'cart': cart,
        'products': [item.product for item in products]
    })
@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    return render(request, 'orders/order_success.html', {'order': order, 'address': order.address})




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