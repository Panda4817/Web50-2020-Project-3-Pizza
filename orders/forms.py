from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import *


# Registration form, based on User model and addrress model
class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=64, help_text='Required')
    last_name = forms.CharField(max_length=64, help_text='Required')
    email = forms.EmailField(max_length=254, help_text='Required')
    street_address_1 = forms.CharField(max_length=64, help_text='Required')
    street_address_2 = forms.CharField(
        max_length=64, help_text='Optional', required=False)
    city = forms.CharField(
        max_length=64, help_text='Required', label="Town/City")
    post_code = forms.CharField(
        max_length=64, help_text='Required', label="Postal Code/Zip Code")

    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'email',
            'username',
            'password1',
            'password2',
            'street_address_1',
            'street_address_2',
            'city',
            'post_code',
        )


# Checkout details form based on User model
class CheckoutDetailsForm(forms.ModelForm):
    first_name = forms.CharField(max_length=64, help_text='Required', widget=forms.TextInput(
        attrs={'class': "form-control"}))
    last_name = forms.CharField(max_length=64, help_text='Required', widget=forms.TextInput(
        attrs={'class': "form-control"}))
    email = forms.EmailField(max_length=254, help_text='Required',
                             widget=forms.EmailInput(attrs={'class': "form-control"}))
    street_address_1 = forms.CharField(
        max_length=64, help_text='Required', widget=forms.TextInput(attrs={'class': "form-control"}))
    street_address_2 = forms.CharField(max_length=64, help_text='Optional',
                                       required=False, widget=forms.TextInput(attrs={'class': "form-control"}))
    city = forms.CharField(max_length=64, help_text='Required', label="Town/City",
                           widget=forms.TextInput(attrs={'class': "form-control"}))
    post_code = forms.CharField(max_length=64, help_text='Required', label="Postal Code/Zip Code",
                                widget=forms.TextInput(attrs={'class': "form-control"}))
    tel = forms.CharField(max_length=64, help_text='Optional', required=False,
                          widget=forms.TextInput(attrs={'class': "form-control"}))

    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'email',
            'street_address_1',
            'street_address_2',
            'city',
            'post_code',
            'tel'
        )


# Checkout delivery type form based on Order model
class CheckoutDeliveryForm(forms.ModelForm):
    delivery_type = forms.ChoiceField(widget=forms.Select(
        attrs={
            'id': "deliveryType",
            'onchange': "showPdiv(this)",
            'style': "diplay: block;",
            'class': 'form-control'
        }), choices=Order.DELIVERY_CHOICES, label='Delivery or Collection?', required=True)
    delivery_intructions = forms.CharField(widget=forms.Textarea(
        attrs={
            'placeholder': "Any delivery instructions...",
            'class': 'form-control',
            'row': '3'
        }), required=False)

    class Meta:
        model = Order
        fields = (
            'delivery_type',
            'delivery_intructions'
        )


# Checkout payment choice form based on Order model
class CheckoutPaymentForm(forms.ModelForm):
    payment = forms.ChoiceField(choices=Order.PAYMENT_CHOICES, widget=forms.RadioSelect(attrs={
        'class': 'form-check-input',
        'onload': 'checkSelectedPay(this)',
        'onchange': 'checkSelectedPay(this)'
    }), required=True,
        help_text="Card payments will be processed after confirming order. Cash payments are collected by delivery driver or restaurent staff. We will endevour to provide correct change but exact payment is most appreciated.")

    class Meta:
        model = Order
        fields = (
            'payment',
        )


# Staff page change status form based on Order Model
class ChangeStatusForm(forms.ModelForm):
    status = forms.ChoiceField(choices=Order.STATUS_CHOICES, widget=forms.Select(attrs={
        'class': 'form-control',
        'name': 'status'
    }), required=True, label="Update Status")

    class Meta:
        model = Order
        fields = (
            'status',
        )


# Contact form from page footer
class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Name'
    }))
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Email'
    }))
    cc_myself = forms.BooleanField(required=False)
    subject = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Subject'
    }))
    message = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'form-control',
        'placeholder': 'Message'
    }))
