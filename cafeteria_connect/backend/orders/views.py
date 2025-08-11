from .tasks import generate_invoice, start_preparing
from core.kafka.producer import publish_order_placed, publish_order_status_update
from django.shortcuts import render, get_object_or_404, redirect
from shops.models import Shop, Product
from cart.models import Cart
from core.models import Address
from .models import Order, OrderItem
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.http import Http404, HttpResponse, HttpResponseRedirect
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
                    .prefetch_related('items', 'items__product', 'shop', 'user')
    else:
        # Regular user orders
        orders = Order.objects.filter(user=user).order_by('-created_at') \
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
            user=request.user,
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
            'user_id': request.user.id,
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
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_success.html', {'order': order, 'address': order.address})


from django.http import JsonResponse

@login_required
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.method == 'POST':
        data = json.loads(request.body)
        new_status = data.get('status')
        if new_status in dict(Order.STATUS_CHOICES).keys():
            allowed_transitions = Order.VALID_STATUS_TRANSITIONS.get(order.status, [])
            if new_status in allowed_transitions or True:
                # order.status = new_status
                # order.save()
                order_data = {
                    'order_id': order.id,
                    'new_status': new_status,
                    'timestamp': str(order.updated_at)  # Or use datetime.now()
                }
                publish_order_status_update(order_data)

                # Example async task
                if new_status == 'preparing':
                    start_preparing.delay(order.id)

                return JsonResponse({
                    "success": True,
                    "new_status": order.status,
                    "message": "Status updated successfully"
                })

            return JsonResponse({"success": False, "message": "Invalid status transition"}, status=400)

        return JsonResponse({"success": False, "message": "Invalid status"}, status=400)

    return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)


# @login_required
# def update_order_status(request, order_id):
#     order = get_object_or_404(Order, id=order_id)

#     if request.method == 'POST':
#         new_status = request.POST.get('status')

#         # ✅ Valid status choice check
#         if new_status in dict(Order.STATUS_CHOICES).keys():
#             # ✅ Transition allowed check
#             allowed_transitions = Order.VALID_STATUS_TRANSITIONS.get(order.status, [])
#             if new_status in allowed_transitions:
#                 order.status = new_status
#                 order.save()

#                 # 📦 Example: Preparing case me async task
#                 if new_status == 'preparing':
#                     if "requires_manual_preparation" == "requires_manual_preparation":
#                         start_preparing.delay(order.id)
#                     else:
#                         start_preparing.delay(order.id)

#                 # 🔁 Kafka / Redis / WebSocket trigger yaha laga sakte ho

#                 return HttpResponseRedirect(reverse('my_orders'))
#             else:
#                 return HttpResponse("Invalid status transition", status=400)

#     return render(request, 'orders/update_status.html', {
#         'order': order,
#         'status_choices': Order.STATUS_CHOICES
#     })


# @login_required
# def update_order_status(request, order_id):
#     order = get_object_or_404(Order, id=order_id)

#     if request.method == 'POST':
#         new_status = request.POST.get('status')
#         if new_status in dict(Order.STATUS_CHOICES).keys():
#             order.status = new_status
#             order.save()
#             if new_status == 'preparing':
#                 if "requires_manual_preparation" == "requires_manual_preparation":
#                     start_preparing.delay(order.id)
#                 else:
#                     start_preparing.delay(order.id)
#             # 🔁 (Optional) trigger Kafka/Celery event here
#         return HttpResponseRedirect(reverse('my_orders'))  # or redirect to admin/order list

#     return render(request, 'orders/update_status.html', {'order': order, 'status_choices': Order.STATUS_CHOICES})

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    status_list = [choice[0] for choice in order.STATUS_CHOICES]
    current_index = status_list.index(order.status)

    return render(request, "orders/order_detail.html", {
        "order": order,
        "current_index": current_index,
        "status_choices": order.STATUS_CHOICES if request.user.is_shopkeeper else None,
        "is_shopkeeper": request.user.is_shopkeeper
    })

