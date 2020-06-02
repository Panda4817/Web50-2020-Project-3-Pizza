from django.contrib import admin
from django.contrib.auth.models import User
from .models import *
from django.contrib import messages
from django.utils.translation import ngettext

# Register your models here. Also classes to customise admin view.


class FoodAdmin(admin.ModelAdmin):
    model = Food
    list_display = ['pk', 'food_type', 'name', 'size', 'price', 'extraOTC']
    actions = ['make_extraOTCtrue']

    # Custom action to change extraOTC to true for foods
    def make_extraOTCtrue(self, request, queryset):
        updated = queryset.update(extraOTC=True)
        self.message_user(request, ngettext(
            '%d food now accepts extras otherthan cheese',
            '%d foods now accepts extras otherthan cheese',
            updated,
        ) % updated, messages.SUCCESS)
    make_extraOTCtrue.short_description = "Change to true to indicate extras allowed"


class OrderToFoodAdmin(admin.ModelAdmin):
    model = OrderToFood
    list_display = ['pk', 'order', 'food_item',
                    'get_toppings', 'get_extra', 'quantity']


class ToppingAdmin(admin.ModelAdmin):
    model = Topping
    list_display = ['pk', 'name']


class SizeAdmin(admin.ModelAdmin):
    model = Size
    list_display = ['pk', 'name']


class FoodTypeAdmin(admin.ModelAdmin):
    model = FoodType
    list_display = ['pk', 'name']


class ExtraForSubAdmin(admin.ModelAdmin):
    model = ExtraForSub
    list_display = ['pk', 'name', 'price']


class OrderAdmin(admin.ModelAdmin):
    model = Order
    list_display = ['pk', 'user', 'total', 'status',
                    'delivery_type', 'delivery_intructions', 'payment']


class AddressAdmin(admin.ModelAdmin):
    model = Address
    list_display = ['pk', 'user', 'street_address_1',
                    'street_address_2', 'city', 'post_code', 'email_confirmed', 'tel']


admin.site.register(Food, FoodAdmin)
admin.site.register(OrderToFood, OrderToFoodAdmin)
admin.site.register(Size, SizeAdmin)
admin.site.register(FoodType, FoodTypeAdmin)
admin.site.register(Topping, ToppingAdmin)
admin.site.register(ExtraForSub, ExtraForSubAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Address, AddressAdmin)
