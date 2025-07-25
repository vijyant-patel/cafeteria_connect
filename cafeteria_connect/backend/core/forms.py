# core/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
# from core.forms import CustomUserCreationForm, CustomAuthenticationForm
from django.contrib.auth import get_user_model
from .models import Address

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-md text-gray-900 focus:outline-none focus:ring-2 focus:ring-indigo-500'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-md text-gray-900 focus:outline-none focus:ring-2 focus:ring-indigo-500'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-md text-gray-900 focus:outline-none focus:ring-2 focus:ring-indigo-500'
        })
        self.fields['role'].widget.attrs.update({
            'class': 'w-full px-4 py-2 border border-gray-300 bg-white rounded-md text-gray-900 focus:outline-none focus:ring-2 focus:ring-indigo-500'
        })
    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'is_shopkeeper', 'role')


class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(CustomAuthenticationForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-md text-gray-900 focus:outline-none focus:ring-2 focus:ring-indigo-500'
        })
        self.fields['password'].widget.attrs.update({
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-md text-gray-900 focus:outline-none focus:ring-2 focus:ring-indigo-500'
        })
    class Meta:
        model = User




class AddressForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(AddressForm, self).__init__(*args, **kwargs)
        common_class = 'w-full px-4 py-2 border border-gray-300 rounded-md text-gray-900 focus:outline-none focus:ring-2 focus:ring-indigo-500'

        self.fields['name'].widget.attrs.update({'class': common_class})
        self.fields['line1'].widget.attrs.update({'class': common_class})
        self.fields['line2'].widget.attrs.update({'class': common_class})
        self.fields['city'].widget.attrs.update({'class': common_class})
        self.fields['state'].widget.attrs.update({'class': common_class})
        self.fields['pincode'].widget.attrs.update({'class': common_class})
        self.fields['phone'].widget.attrs.update({'class': common_class})
        self.fields['is_default'].widget.attrs.update({'class': 'h-4 w-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500'})
    class Meta:
        model = Address
        fields = ['name', 'line1', 'line2', 'city', 'state', 'pincode', 'phone', 'is_default']