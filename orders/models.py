from datetime import datetime
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# food types model
class FoodType(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name

# size model
class Size(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name


# Food model
class Food(models.Model):
    food_type = models.ForeignKey(FoodType, on_delete=models.CASCADE, related_name="types")
    name = models.CharField(max_length=64)
    size = models.ForeignKey(Size, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    extraOTC = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.food_type} - {self.name} - {self.size} for ${self.price}"

# Orders
class Order(models.Model):
    STATUS_CHOICES = [
        ('checkout', 'checkout'),
        ('confirmed', 'confirmed'),
        ('preparing', 'preparing'),
        ('ready to collect', 'ready to collect'),
        ('collected', 'collected'),
        ('out for delivery', 'out for delivery'),
        ('delivered', 'delivered'),
        ('completed', 'completed'),
    ]
    DELIVERY_CHOICES = [
        ('delivery', 'delivery'),
        ('collection', 'collection'),
    ]
    PAYMENT_CHOICES = [
        ('cash', 'cash'),
        ('card', 'card')
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total = models.DecimalField(max_digits=6, decimal_places=2)
    status = models.CharField(max_length=64, choices=STATUS_CHOICES, default='checkout')
    delivery_type = models.CharField(max_length=64, choices=DELIVERY_CHOICES, default='delivery')
    delivery_intructions = models.TextField(blank=True)
    payment = models.CharField(max_length=4, choices=PAYMENT_CHOICES, default="cash")
    timestamp = models.DateTimeField(default=datetime.utcnow)

    def __str__(self):
        return f"{self.id} - {self.user} - {self.total}  - {self.status} - {self.delivery_type}"


# topping
class Topping(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name

# extras for sub
class ExtraForSub(models.Model):
    name = models.CharField(max_length=64)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"{self.name} for ${self.price}"


# Shopping cart items
class OrderToFood(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    food_item = models.ForeignKey(Food, on_delete=models.CASCADE)
    topping = models.ManyToManyField(Topping, blank=True)
    extra = models.ManyToManyField(ExtraForSub, blank=True)
    quantity = models.PositiveIntegerField()

    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(quantity__gt=0), name='quantity_gt_0')
        ]
    
    def get_toppings(self):
        return ", ".join([str(t) for t in self.topping.all()])
    
    def get_extra(self):
        return ", ".join([str(e) for e in self.extra.values_list('name', flat=True)])
    
    def getfood_type(self):
        return self.food_item.food_type.name
    
    def get_overall_price(self):
        ex = list(self.extra.all().values_list('name', flat=True))
        if len(ex) == 0: 
            return self.food_item.price * self.quantity
        else:
            exp = list(self.extra.all().values_list('price', flat=True))
            extras_price = 0
            for p in exp:
                extras_price += p
            return (self.food_item.price + extras_price) * self.quantity

    
    def __str__(self):
        t = self.get_toppings()
        e = self.get_extra()
        return f"{self.food_item.size.name} {self.food_item.name } {self.food_item.food_type.name} - ${self.food_item.price}"
        
# User address - extending user model
class Address(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    street_address_1 = models.CharField(max_length=64)
    street_address_2 = models.CharField(max_length=64, blank=True)
    city = models.CharField(max_length=64)
    post_code = models.CharField(max_length=64)
    email_confirmed = models.BooleanField(default=False)
    tel = models.CharField(max_length=64, blank=True)

@receiver(post_save, sender=User)
def create_user_address(sender, instance, created, **kwargs):
    if created:
        Address.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_address(sender, instance, **kwargs):
    instance.address.save()       
            





