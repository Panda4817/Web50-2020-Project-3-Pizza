from django.urls import path
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

from . import views


# All url routes for views
urlpatterns = [
    path("", views.index, name="index"),
    path("account", views.account, name="account"),
    path("menu", views.menu, name="menu"),
    path("cart", views.cart, name="cart"),
    path("update_cart", views.update_cart, name="update_cart"),
    path("delete_item_cart", views.delete_item_cart, name="delete_item_cart"),
    path("cash", views.cash, name="cash"),
    path("card", views.card, name="card"),
    path("charge", views.charge, name="charge"),
    path("staff", views.staff, name="staff"),
    path("register", views.register, name="register"),
    path("activate/<uidb64>/<token>", views.activate, name='activate'),
    path("login", views.myLoginView.as_view(), name="login"),
    path("logout", auth_views.LogoutView.as_view(), name="logout"),
    path("password_reset", views.myPasswordResetView.as_view(),
         name="password_reset"),
    path("password_reset/done", views.myPasswordResetDoneView.as_view(),
         name="password_reset_done"),
    path("reset/<uidb64>/<token>", views.myPasswordResetConfirmView.as_view(),
         name="password_reset_confirm"),
    path("reset/done", views.password_reset_complete,
         name="password_reset_complete"),
    path("password_change", views.myPasswordChangeView.as_view(),
         name="password_change"),
    path("password_change/done", views.password_change_done,
         name="password_change_done"),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
