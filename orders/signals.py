from django.contrib.auth.signals import user_logged_out, user_logged_in
from django.contrib import messages


# Custom signal and message for when user signs out
def show_logout_message(sender, user, request, **kwargs):
    messages.info(request, 'You have been logged out')


# Custom signal and message for when user signs in
def show_login_message(sender, user, request, **kwargs):
    messages.info(request, 'You are logged in')

