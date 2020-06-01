from django.contrib.auth.signals import user_logged_out, user_logged_in
from django.contrib import messages

def show_logout_message(sender, user, request, **kwargs):
    messages.info(request, 'You have been logged out')

def show_login_message(sender, user, request, **kwargs):
    messages.info(request, 'You are logged in')


