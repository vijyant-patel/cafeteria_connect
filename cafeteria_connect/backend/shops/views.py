from django.shortcuts import render, redirect
from .models import Shop, Product
from django.contrib.auth.decorators import login_required
from .forms import ShopForm, ProductForm
from django.shortcuts import get_object_or_404

@login_required
def shop_list(request):
    user = request.user
    is_shopkeeper = user.role == 'shopkeeper' or False
    if is_shopkeeper:
        shops = Shop.objects.filter(owner=user)
    else:
        shops = Shop.objects.all()
    return render(request, 'shop_list.html', {'shops': shops, 'is_shopkeeper': is_shopkeeper})


@login_required
def create_shop(request):
    if request.method == 'POST':
        form = ShopForm(request.POST)
        if form.is_valid():
            shop = form.save(commit=False)
            shop.owner = request.user
            shop.save()
            return redirect('shop-list')
    else:
        form = ShopForm()
    return render(request, 'create_shop.html', {'form': form})

@login_required
def edit_shop(request, shop_id):
    shop = get_object_or_404(Shop, id=shop_id, owner=request.user)
    if request.method == 'POST':
        form = ShopForm(request.POST, instance=shop)
        if form.is_valid():
            form.save()
            return redirect('shop-list')
    else:
        form = ShopForm(instance=shop)
        return render(request, 'edit_shop.html', {'form': form, 'edit': True, 'shop': shop})

@login_required
def shop_products(request, shop_id):
    shop = get_object_or_404(Shop, id=shop_id)
    products = shop.products.all()
    is_owner = request.user == shop.owner
    if is_owner:
        return render(request, 'product_list.html', {
            'shop': shop,
            'products': products,
            'is_owner': is_owner
        })
    else:
        # return redirect('place_order', shop_id=shop.id)
        return render(request, 'orders/shop_products.html', {'products': products})

@login_required
def add_product(request, shop_id):
    shop = get_object_or_404(Shop, id=shop_id)
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.shop = shop
            product.save()
            return redirect('product-list', shop_id=shop.id)
    else:
        form = ProductForm()
    return render(request, 'add_product.html', {'form': form, 'shop': shop})

@login_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':  # ✅ Make sure it's method
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            product = form.save(commit=False)
            product.shop = product.shop  # manually reassign same value
            product.save()
            return redirect('product-list', shop_id=product.shop.id)  # Or use product.id
    else:
        form = ProductForm(instance=product)

    return render(request, 'edit_product.html', {
        'form': form,
        'edit': True,
        'product': product
    })