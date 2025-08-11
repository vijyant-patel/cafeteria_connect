# orders/tasks.py

from celery import shared_task
from .models import Order

@shared_task
def start_preparing(order_id):
    try:
        order = Order.objects.get(id=order_id)
        if order.status == 'confirmed':
            order.status = 'preparing'
            order.save()
            print(f"👨‍🍳 Order #{order.id} is now PREPARING")
            return f"Order #{order.id} marked as PREPARING"
        else:
            print(f"⏭ Order #{order.id} not in confirmed state, skipping...")
            return f"Order #{order.id} is not confirmed, no update"
    except Order.DoesNotExist:
        return f"❌ Order ID {order_id} not found"

@shared_task
def generate_invoice(order_id):
    try:
        order = Order.objects.get(id=order_id)

        # 🧾 Fake invoice generation logic for now
        print(f"📄 Generating invoice for Order #{order.id} (Customer: {order.user.username})")

        # Future: generate PDF, save to media/invoices/, etc.
        return f"✅ Invoice generated for Order #{order.id}"

    except Order.DoesNotExist:
        return f"❌ Order ID {order_id} not found"
