from .models import *
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

def validate_food_choices(food_id, toppings, extras):
    food = Food.objects.get(pk=food_id)
    if toppings == None:
        toppings_len = 0
    else:
        toppings_len = len(toppings)
    if extras == None:
        extras_len = 0
    else:
        extras_len = len(extras)
    
    if 'pizza' in food.food_type.name:
        if '1' in food.name and toppings_len == 1:
            return
        elif '2' in food.name and toppings_len == 2:
            return
        elif '3' in food.name and toppings_len == 3:
            return
        elif food.name == 'cheese' or food.name == 'special':
            if toppings_len == 0:
                return
        else:
            raise ValidationError(_('Only certain pizzas are allowed custon toppings'))
    elif 'pizza' not in food.food_type.name and toppings_len > 0:
        raise ValidationError(_('Only certain pizzas are allowed custon toppings'))
    elif 'sub' not in food.food_type.name and extras_len > 0:
        raise ValidationError(_('Only subs are allowed extras'))
    else:
        return

        
def calc_total(user_id, quantity, food_id, extras):
    order = Order.objects.filter(user=user_id).filter(status='checkout')
    food = Food.objects.get(pk=food_id)
    food_total = food.price
    
    if extras is not None:
        extra_prices = []
        for extra in extras:
            e = ExtraForSub.objects.get(name=extra)
            extra_prices.append(e.price)
        for p in extra_prices:
            food_total += p
    
    food_total *= quantity
    
    if order.count() == 0:  
        total = food_total
    else:
        total = order[0].total + food_total
    return total

def add_order(user_id, total_price):
    user = User.objects.get(pk=user_id)
    order = Order.objects.filter(user=user).filter(status='checkout')
    
    if order.count() == 0:
        new_order = Order(user=user, total=total_price)
        new_order.save()
        order_id = new_order.id
    else:
        order = Order.objects.get(pk=order[0].id)
        order.total = total_price
        order.save()
        order_id = order.id
    
    return order_id

def updateOrderItem(id, quantity):
    orderToUpdate = OrderToFood.objects.get(pk=id)
    new_qty = orderToUpdate.quantity + quantity
    orderToUpdate.quantity = new_qty
    orderToUpdate.save()
    return

def add_order_items(order_id, food_id, toppings, extras, quantity):
    order = Order.objects.get(pk=order_id)
    food = Food.objects.get(pk=food_id)
    order_items = list(OrderToFood.objects.filter(order=order))
    order_updated = False
    OrderToFood_id = ''
    for x in order_items:
        if x.food_item == food:
            if 'pizza' in x.food_item.food_type.name:
                if 'topping' in x.food_item.name:
                    xt = list(x.topping.all().values_list('name', flat=True))
                    xt.sort() 
                    toppings.sort()
                    if toppings == xt:
                        updateOrderItem(x.id, quantity)
                        OrderToFood_id = x.id
                        order_updated = True
                else:
                    updateOrderItem(x.id, quantity)
                    OrderToFood_id = x.id
                    order_updated = True
            elif 'sub' in x.food_item.food_type.name:
                xe =list(x.extra.all().values_list('name', flat=True))
                xe.sort()
                extras.sort()
                if extras == xe:
                    updateOrderItem(x.id, quantity)
                    OrderToFood_id = x.id
                    order_updated = True
            else:
                updateOrderItem(x.id, quantity)
                OrderToFood_id = x.id
                order_updated = True
    
    if order_updated == False:
        new_item = OrderToFood(order=order, food_item=food, quantity=quantity)
        new_item.save()
        OrderToFood_id = new_item.id

        if toppings is not None:
            for topping in toppings:
                t = Topping.objects.get(name=topping)
                new_item.topping.add(t)
                new_item.save()
        
        if extras is not None:
            for extra in extras:
                e = ExtraForSub.objects.get(name=extra)
                new_item.extra.add(e)
                new_item.save()
    return OrderToFood_id

def check_cart(user_id):
    order = Order.objects.filter(user=user_id).filter(status='checkout')
    if order.count() == 0:
        return None
    else:
       order = Order.objects.get(pk=order[0].id)
       order_items = OrderToFood.objects.filter(order=order) 
       return list(order_items)

def get_order(user_id):
    order = Order.objects.filter(user=user_id).filter(status='checkout')
    order = Order.objects.get(pk=order[0].id)
    return order

def get_total_qty(cart_items):
    total_qty = 0
    for item in cart_items:
        total_qty += item.quantity
    return total_qty

def check_order(user_id):
    order = Order.objects.filter(user=user_id).exclude(status='checkout').exclude(status='completed')
    if order.count() == 0:
        return None
    else:
        order = Order.objects.get(pk=order[0].id)
    return order

def get_order_food(order):
    order_items = OrderToFood.objects.filter(order=order)
    return list(order_items)

def update_total(user_id, OrderToFood_id, extras, quantity):
    order_list = Order.objects.filter(user=user_id).filter(status='checkout')
    order = Order.objects.get(pk=order_list[0].id)
    item = OrderToFood.objects.get(pk=OrderToFood_id)
    
    old_price = item.get_overall_price()
    old_total = order.total
    food_price = item.food_item.price

    if extras is not None:
        extra_prices = []
        for extra in extras:
            e = ExtraForSub.objects.get(name=extra)
            extra_prices.append(e.price)
        for p in extra_prices:
            food_price += p
    
    new_price = food_price * quantity

    new_total = (old_total - old_price) + new_price

    order.total = new_total
    order.save()
    return new_total

def update_item(OrderToFood_id, extras, toppings, quantity):
    item = OrderToFood.objects.get(pk=OrderToFood_id)

    item.quantity = quantity
    item.save()
    item.topping.clear()
    item.extra.clear()

    if toppings is not None:
        for topping in toppings:
            t = Topping.objects.get(name=topping)
            item.topping.add(t)
            item.save()
        
    if extras is not None:
        for extra in extras:
            e = ExtraForSub.objects.get(name=extra)
            item.extra.add(e)
            item.save()
    
    return item
    
