from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render, redirect, resolve_url
from django.urls import reverse_lazy
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode, url_has_allowed_host_and_scheme
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.template.loader import render_to_string
from django.views.generic.edit import FormView
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS
from django.contrib.auth import login, authenticate, update_session_auth_hash, REDIRECT_FIELD_NAME
from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import PasswordContextMixin
from django.contrib.auth.signals import user_logged_out, user_logged_in
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.db import transaction
from django.conf import settings
import stripe
from django.core.mail import send_mail

from .forms import SignUpForm, CheckoutDeliveryForm, CheckoutDetailsForm, CheckoutPaymentForm, ChangeStatusForm, ContactForm
from .tokens import account_activation_token
from .signals import show_login_message, show_logout_message
from .models import *
from .utils import *

stripe.api_key = settings.STRIPE_SECRET_KEY

# Create your views here.
def index(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            email = form.cleaned_data['email']
            cc_myself = form.cleaned_data['cc_myself']

            message_to_send = message + ' from ' + name
            recipients = ['webmaster@localhost']
            if cc_myself:
                recipients.append(email)

            send_mail(subject, message_to_send, email, recipients)
            messages.info(request, "Thank you for the message. We will get back to you as soon as possible.")
        return redirect('index')

    user_logged_in.connect(show_login_message)
    user_logged_out.connect(show_logout_message)
    form = ContactForm()
    if request.user.is_authenticated:
        user_id = request.user.id
        current_cart = check_cart(user_id)
        if current_cart != None:
            order = get_order(user_id)
            qty = get_total_qty(current_cart)
            context = {
                'cart': current_cart,
                'total': order.total,
                'no_items': qty,
                'cform': form,
            }
            return render(request, 'orders/index.html', context)
    
    return render(request, 'orders/index.html', {'cform': form})

def menu(request):
    if request.method == 'POST':
        user_id = request.user.id
        food_id = request.POST['food_id']
        extras = request.POST.getlist("extras[]")
        toppings = request.POST.getlist("toppings[]")
        quantity = int(request.POST['quantity'])
        
        try:
            validate_food_choices(food_id, toppings, extras)
        except ValidationError as e:
            non_field_errors = e.message_dict[NON_FIELD_ERRORS]
            messages.error(request, non_field_errors)
            return redirect('menu')
        
        total_price = calc_total(user_id, quantity, food_id, extras)
        order_id = add_order(user_id, total_price)
        ordertofood_id = add_order_items(order_id, food_id, toppings, extras, quantity)

        fooditem = Food.objects.get(pk=food_id)
        result = {
            'food_id': fooditem.id,
            'food_type': fooditem.food_type.name,
            'food_name': fooditem.name,
            'food_size': fooditem.size.name,
            'food_price': fooditem.price,
            'qty': quantity,
            'total': total_price,
            'id': ordertofood_id
        }
        response = JsonResponse(result)
        return response
    
    else:
        types = FoodType.objects.values_list('name', flat=True).order_by("-pk")
        dict_food = {i: list(Food.objects.filter(food_type__name=i).order_by('size')) for i in types}
        toppings = Topping.objects.values_list('name', flat=True).order_by("-pk")
        extras = list(ExtraForSub.objects.all().order_by("-pk"))
        form = ContactForm()
        if request.user.is_authenticated:
            user_id = request.user.id
            current_cart = check_cart(user_id)
            if current_cart != None:
                order = get_order(user_id)
                qty = get_total_qty(current_cart)
                context = {
                    "types": types,
                    "dictfood": dict_food,
                    "toppings": toppings,
                    "extras": extras,
                    'cart': current_cart,
                    'total': order.total,
                    'no_items': qty,
                    'cform': form,
                }
                return render(request, 'orders/menu.html', context)
        
        context = {
            "types": types,
            "dictfood": dict_food,
            "toppings": toppings,
            "extras": extras,
            'cform': form,
        }
        return render(request, 'orders/menu.html', context)

@login_required(login_url="login")
def cart(request):
    if request.user.address.email_confirmed == False:
        messages.warning(request, "Your email address is NOT confirmed yet. You CANNOT place an order until you do. Please check your inbox and/or spam folder.")
    form = ContactForm()
    DetailsForm = CheckoutDetailsForm(initial={
        'first_name': request.user.first_name, 
        'last_name': request.user.last_name, 
        'email': request.user.email, 
        'street_address_1': request.user.address.street_address_1, 
        'street_address_2': request.user.address.street_address_2,
        'city': request.user.address.city, 
        'post_code': request.user.address.post_code,
        'tel': request.user.address.tel
    })
    DeliveryForm = CheckoutDeliveryForm()

    PaymentTypeForm = CheckoutPaymentForm()
    
    user_id = request.user.id
    current_cart = check_cart(user_id)
    if current_cart != None:
        order = get_order(user_id)
        qty = get_total_qty(current_cart)
        context = {
            'cart': current_cart,
            'total': order.total,
            'no_items': qty,
            'toppings': Topping.objects.values_list('name', flat=True).order_by("-pk"),
            'extras': list(ExtraForSub.objects.all().order_by("-pk")),
            'DetailsForm': DetailsForm,
            'DeliveryForm': DeliveryForm,
            'PaymentTypeForm': PaymentTypeForm,
            'cform': form,
        }
        return render(request, 'orders/cart.html', context)
    return render(request, 'orders/cart.html', {
        'DetailsForm': DetailsForm,
        'DeliveryForm': DeliveryForm,
        'PaymentTypeForm': PaymentTypeForm,
        'cform': form,
    })

@login_required(login_url="login")
def update_cart(request):
    if request.method == 'POST':
        user_id = request.user.id
        OrderToFood_id = request.POST['OrderToFood_id']
        extras = request.POST.getlist("extras[]")
        toppings = request.POST.getlist("toppings[]")
        quantity = int(request.POST['quantity'])
        print(extras)
        
        updated_total = update_total(user_id, OrderToFood_id, extras, quantity)
        item = update_item(OrderToFood_id, extras, toppings, quantity)
        current_cart = check_cart(user_id)
        if current_cart != None:
            qty = get_total_qty(current_cart)
        else:
            qty = 0
        
        result = {
            'total': updated_total,
            'item': item.__str__(),
            'extras': item.get_extra(),
            'toppings': item.get_toppings(),
            'overall_price': item.get_overall_price(),
            'type': item.getfood_type(),
            'quantity': item.quantity,
            'id': item.id,
            'total_qty': qty,
        }
        response = JsonResponse(result)
        return response
    
    return redirect('cart')

@login_required(login_url='login')
def delete_item_cart(request):
    if request.method == 'POST':
        OrderToFood_id = request.POST['OrderToFood_id']
        item = OrderToFood.objects.get(pk=OrderToFood_id)
        old_price = item.get_overall_price()
        order_id = item.order.id
        order = Order.objects.get(pk=order_id)
        old_total = order.total
        new_total = old_total - old_price
        order.total = new_total
        order.save()
        item.delete()

        current_cart = check_cart(request.user.id)
        if current_cart != None:
            qty = get_total_qty(current_cart)
        else:
            qty = 0

        result = {
            'total': new_total,
            'id': OrderToFood_id,
            'total_qty': qty,
        }
        response = JsonResponse(result)
        return response
    
    return redirect('cart')

@login_required(login_url="login")
def cash(request):
    if request.method == 'POST':
        details_form = CheckoutDetailsForm(request.POST, instance=request.user)
        order = get_order(request.user.id)
        delivery_form = CheckoutDeliveryForm(request.POST, instance=order)
        payment_form = CheckoutPaymentForm(request.POST, instance=order)
        if details_form.is_valid() and delivery_form.is_valid() and payment_form.is_valid():
            user = details_form.save()
            user.refresh_from_db()  # load the address instance created by the signal
            user.address.street_address_1 = details_form.cleaned_data.get('street_address_1')
            user.address.street_address_2 = details_form.cleaned_data.get('street_address_2')
            user.address.city = details_form.cleaned_data.get('city')
            user.address.post_code = details_form.cleaned_data.get('post_code')
            user.address.tel = details_form.cleaned_data.get('tel')
            user.save()
            delivery_form.save()
            payment_form.save()
            order = get_order(request.user.id)
            order.status = 'confirmed'
            order.timestamp = datetime.utcnow()
            order.save()
            subject = 'Order Confirmed'
            message = render_to_string('orders/confirmation_email.html', {
                'order': order,
                'user': request.user,
            })
            request.user.email_user(subject, message)
            messages.success(request, "Order placed and confirmed")
            return redirect('/account#order-confirmed')
        else:
            messages.error(request, 'There was error and order is NOT confirmed. Please try again or contact us.')
    
    return redirect('cart')

@login_required(login_url="login")
def card(request):
    if request.method == 'POST':
        details_form = CheckoutDetailsForm(request.POST, instance=request.user)
        order = get_order(request.user.id)
        delivery_form = CheckoutDeliveryForm(request.POST, instance=order)
        payment_form = CheckoutPaymentForm(request.POST, instance=order)
        if details_form.is_valid() and delivery_form.is_valid() and payment_form.is_valid():
            user = details_form.save()
            user.refresh_from_db()  # load the address instance created by the signal
            user.address.street_address_1 = details_form.cleaned_data.get('street_address_1')
            user.address.street_address_2 = details_form.cleaned_data.get('street_address_2')
            user.address.city = details_form.cleaned_data.get('city')
            user.address.post_code = details_form.cleaned_data.get('post_code')
            user.address.tel = details_form.cleaned_data.get('tel')
            user.save()
            delivery_form.save()
            payment_form.save()
            
            user_id = request.user.id
            order = get_order(request.user.id)
            current_cart_items = check_cart(user_id)
            qty = get_total_qty(current_cart_items)
            context = {
                'cart': current_cart_items,
                'total': order.total,
                'no_items': qty,
            }
            return render(request, 'orders/card.html', context)
        else:
            messages.error(request, 'There was error and order is NOT confirmed. Please try again or contact us.')
    
    return redirect('cart')

@login_required(login_url="login")
def charge(request):
    if request.method == 'POST':
        try:
            customer = stripe.Customer.retrieve(str(request.user.id))
        except stripe.error.InvalidRequestError:
            customer = stripe.Customer.create(
                id = request.user.id,
                name = request.user.get_full_name(),
                email = request.user.email,
                address = {
                    'line1': request.user.address.street_address_1,
                    'line2': request.user.address.street_address_2,
                    'city': request.user.address.city,
                    'postal_code': request.user.address.post_code
                },
                phone = request.user.address.tel,
                source = request.POST['stripeToken']
            )
        order = get_order(request.user.id)
        amount = int(order.total * 100)
        charge = stripe.Charge.create(
            customer = customer,
            amount = amount,
            currency = 'usd',
            description = 'Food Order',
        )

        order.status = 'confirmed'
        order.timestamp = datetime.utcnow()
        order.save()
        subject = 'Order Confirmed'
        message = render_to_string('orders/confirmation_email.html', {
            'order': order,
            'user': request.user,
        })
        request.user.email_user(subject, message)
        messages.success(request, "Order placed and confirmed")
        return redirect('/account#order-confirmed')

    return redirect('cart') 

@login_required(login_url="login")
def account(request):
    if request.user.address.email_confirmed == False:
        messages.warning(request, "Your email address is NOT confirmed yet. You CANNOT place an order until you do. Please check your inbox and/or spam folder.")
    form = ContactForm()
    user_id = request.user.id
    a = False
    b = False
    c = False

    current_order = check_order(user_id)
    print(current_order)
    contexta={}
    if current_order != None:
        current_order_food = get_order_food(current_order)
        timestamp = current_order.timestamp
        timestamp = timestamp.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        contexta = {
            'order': current_order,
            'timestamp': timestamp,
            'orderfood': current_order_food
        }
        print(contexta)
        a = True

    contextb = {}
    current_cart = check_cart(user_id)
    if current_cart != None:
        order = get_order(user_id)
        qty = get_total_qty(current_cart)
        contextb = {
            'cart': current_cart,
            'total': order.total,
            'no_items': qty
        }
        b = True
    
    prev_orders_list = []
    prev_orders = list(Order.objects.filter(status='completed').filter(user=user_id).order_by('pk'))
    print(prev_orders)
    for order in prev_orders:
        order_items = list(OrderToFood.objects.filter(order=order))
        timestamp = order.timestamp
        timestamp = timestamp.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        order_dict = {
            'porder': order,
            'porderFood': order_items,
            'ptimestamp': timestamp
        }
        prev_orders_list.append(order_dict)
    
    context={}
    if a == True and b == True:
        context.update(contexta)
        context.update(contextb)
    elif a == True and b == False:
        context.update(contexta)
    else:
        context.update(contextb)
   
    context.update({
        'prev_orders': prev_orders_list,
        'cform': form,
    }) 
    
    return render(request, 'orders/account.html', context)

class myPasswordContextMixin:
    extra_context = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = ContactForm()
        if self.request.user.is_authenticated:
            user_id = self.request.user.id
            current_cart = check_cart(user_id)
            if current_cart != None:
                order = get_order(user_id)
                qty = get_total_qty(current_cart)
                context.update({
                    'cart': current_cart,
                    'total': order.total,
                    'no_items': qty,
                    'title': self.title,
                    'cform': form,
                    **(self.extra_context or {})
                })
                return context
        
        context.update({
            'cform': form,
            'title': self.title,
            **(self.extra_context or {})
        })
        return context

class myPasswordChangeView(myPasswordContextMixin, FormView):
    form_class = PasswordChangeForm
    success_url = reverse_lazy('password_change_done')
    template_name = 'registration/password_change_form.html'
    title = _('Password change')

    @method_decorator(sensitive_post_parameters())
    @method_decorator(csrf_protect)
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        # Updating the password logs out all other sessions for the user
        # except the current one.
        update_session_auth_hash(self.request, form.user)
        return super().form_valid(form)

@login_required(login_url="login")
def password_change_done(request):
    messages.info(request, "Your password has been updated.")
    return redirect('account')

def password_reset_complete(request):
    messages.info(request, "Your password has been reset.")
    return redirect('login')

def register(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()  # load the address instance created by the signal
            user.address.street_address_1 = form.cleaned_data.get('street_address_1')
            user.address.street_address_2 = form.cleaned_data.get('street_address_2')
            user.address.city = form.cleaned_data.get('city')
            user.address.post_code = form.cleaned_data.get('post_code')
            user.save()

            current_site = get_current_site(request)
            subject = 'Activate Your Account'
            message = render_to_string('registration/account_activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            user.email_user(subject, message)
            messages.info(request, "Please confirm your email address to complete the registration.")
            return render(request, 'orders/index.html')
        else:
            for msg in form.error_messages:
                print(form.error_messages[msg])
    else:
        form = SignUpForm()

    
    form1 = ContactForm()
    
    context= {
        'cform': form1,
        'form': form,
    }
    return render(request, 'registration/register.html', context)



def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.address.email_confirmed = True
        user.save()
        login(request, user)
        messages.info(request, f"Hello { user.username }! You are ready to order some delicious pizza!")
        return redirect('index')
        
    else:
        messages.error(request, "The confirmation link was invalid, possibly because it has already been used.")
        return redirect('index')

@staff_member_required(login_url='login')
def staff(request):
    if request.method == 'POST':
        order_id = request.POST['order_id']
        status = request.POST['status']

        order = Order.objects.get(pk=order_id)
        order.status = status
        order.save()

        result = {
            'id': order.id,
            'status': order.status
        }
        return JsonResponse(result)
    
    
    orders=[]
    order_objects = list(Order.objects.exclude(status='checkout').exclude(status='completed').order_by('pk'))
    for order in order_objects:
        user = User.objects.get(pk=order.user.id)
        order_items = list(OrderToFood.objects.filter(order=order))
        timestamp = order.timestamp
        timestamp = timestamp.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        order_dict = {
            'id': order.id,
            'name': user.get_full_name,
            'email': user.email,
            'tel': user.address.tel,
            'address_street_1': user.address.street_address_1,
            'address_street_2': user.address.street_address_2,
            'city': user.address.city,
            'post_code': user.address.post_code,
            'delivery_type': order.delivery_type,
            'delivery_instructions': order.delivery_intructions,
            'status': order.status,
            'payment': order.payment,
            'total': order.total,
            'timestamp': timestamp,
            'orderfood': order_items,
        }
        orders.append(order_dict)
    
    changeStatusForm = ChangeStatusForm(initial={
        'status': 'confirmed',
    })

    form = ContactForm()
    
    user_id = request.user.id
    current_cart = check_cart(user_id)
    if current_cart != None:
        order = get_order(user_id)
        qty = get_total_qty(current_cart)
        context = {
            'cart': current_cart,
            'total': order.total,
            'no_items': qty,
            'orders': orders,
            'ChangeStatusForm': changeStatusForm,
            'cform': form,
        }
        return render(request, 'orders/staff.html', context)
     
    context = {
        'orders': orders,
        'ChangeStatusForm': changeStatusForm,
        'cform': form,
    }
    return render(request, 'orders/staff.html', context)

class SuccessURLAllowedHostsMixin:
    success_url_allowed_hosts = set()

    def get_success_url_allowed_hosts(self):
        return {self.request.get_host(), *self.success_url_allowed_hosts}

class myLoginView(SuccessURLAllowedHostsMixin, FormView):
    """
    Display the login form and handle the login action.
    """
    form_class = AuthenticationForm
    authentication_form = None
    redirect_field_name = REDIRECT_FIELD_NAME
    template_name = 'registration/login.html'
    redirect_authenticated_user = False
    extra_context = None

    @method_decorator(sensitive_post_parameters())
    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        if self.redirect_authenticated_user and self.request.user.is_authenticated:
            redirect_to = self.get_success_url()
            if redirect_to == self.request.path:
                raise ValueError(
                    "Redirection loop for authenticated user detected. Check that "
                    "your LOGIN_REDIRECT_URL doesn't point to a login page."
                )
            return HttpResponseRedirect(redirect_to)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        url = self.get_redirect_url()
        return url or resolve_url(settings.LOGIN_REDIRECT_URL)

    def get_redirect_url(self):
        """Return the user-originating redirect URL if it's safe."""
        redirect_to = self.request.POST.get(
            self.redirect_field_name,
            self.request.GET.get(self.redirect_field_name, '')
        )
        url_is_safe = url_has_allowed_host_and_scheme(
            url=redirect_to,
            allowed_hosts=self.get_success_url_allowed_hosts(),
            require_https=self.request.is_secure(),
        )
        return redirect_to if url_is_safe else ''

    def get_form_class(self):
        return self.authentication_form or self.form_class

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        """Security check complete. Log the user in."""
        auth_login(self.request, form.get_user())
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_site = get_current_site(self.request)
        cform = ContactForm()
        context.update({
            self.redirect_field_name: self.get_redirect_url(),
            'site': current_site,
            'site_name': current_site.name,
            'cform': cform,
            **(self.extra_context or {})
        })
        return context