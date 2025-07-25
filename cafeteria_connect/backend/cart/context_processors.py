from .models import Cart

def cart_item_count(request):
    count = 0
    current_cart = None

    if request.user.is_authenticated:
        current_cart = Cart.objects.filter(user=request.user).last()
        if current_cart:
            count = current_cart.items.count()

    return {
        "cart_item_count": count,
        "current_cart": current_cart,
    }
