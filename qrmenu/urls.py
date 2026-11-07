from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", auth_views.LoginView.as_view(template_name="qrmenu/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("after-login/", views.after_login, name="after_login"),

    # 1) Customer (no login)
    path("r/<slug:slug>/", views.menu, name="menu"),
    path("r/<slug:slug>/order/", views.place_order, name="place_order"),
    path("r/<slug:slug>/order/<uuid:public_id>/", views.order_status, name="order_status"),
    path("r/<slug:slug>/order/<uuid:public_id>/api/", views.order_status_api, name="order_status_api"),

    # 2) Restaurant dashboard
    path("dashboard/", views.dash_orders, name="dash_orders"),
    path("dashboard/api/orders/", views.api_orders, name="api_orders"),
    path("dashboard/orders/<int:pk>/status/", views.update_status, name="update_status"),
    path("dashboard/history/", views.dash_history, name="dash_history"),
    path("dashboard/menu/", views.menu_manage, name="dash_menu"),
    path("dashboard/menu/category/<int:pk>/delete/", views.category_delete, name="category_delete"),
    path("dashboard/menu/item/new/", views.item_form, name="item_new"),
    path("dashboard/menu/item/<int:pk>/edit/", views.item_form, name="item_edit"),
    path("dashboard/menu/item/<int:pk>/toggle/", views.item_toggle, name="item_toggle"),
    path("dashboard/menu/item/<int:pk>/delete/", views.item_delete, name="item_delete"),
    path("dashboard/tables/", views.tables_view, name="dash_tables"),
    path("dashboard/tables/<int:pk>/delete/", views.table_delete, name="table_delete"),
    path("dashboard/qr/", views.qr_png, name="dash_qr"),
    path("dashboard/settings/", views.dash_settings, name="dash_settings"),

    # 3) Super admin
    path("super/", views.super_dashboard, name="super_dashboard"),
    path("super/new/", views.super_create, name="super_create"),
    path("super/<int:pk>/toggle/", views.super_toggle, name="super_toggle"),
]
