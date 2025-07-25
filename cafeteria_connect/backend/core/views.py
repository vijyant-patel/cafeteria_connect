from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .forms import CustomUserCreationForm, CustomAuthenticationForm, AddressForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Address

def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('shop-list')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')




@login_required
def profile_view(request):
    addresses = Address.objects.filter(user=request.user).order_by('-is_default')
    return render(request, 'profile.html', {'addresses': addresses})


@login_required
def add_address(request):
    if request.method == "POST":
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            if address.is_default:
                Address.objects.filter(user=request.user).update(is_default=False)
            address.save()
            return redirect('profile')
    else:
        form = AddressForm()
    return render(request, 'address_form.html', {'form': form, 'action': 'Add'})


@login_required
def edit_address(request, pk):
    address = get_object_or_404(Address, id=pk, user=request.user)
    if request.method == "POST":
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            address = form.save(commit=False)
            if address.is_default:
                Address.objects.filter(user=request.user).update(is_default=False)
            address.save()
            return redirect('profile')
    else:
        form = AddressForm(instance=address)
    return render(request, 'address_form.html', {'form': form, 'action': 'Edit', 'address': address})


@login_required
def delete_address(request, pk):
    address = get_object_or_404(Address, id=pk, user=request.user)
    address.delete()
    return redirect('profile')
