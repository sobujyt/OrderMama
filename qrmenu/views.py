import json
from functools import wraps
from io import BytesIO

import qrcode
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from django.db.models import Count, Max, Prefetch, Sum
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST

from .forms import CategoryForm, ItemForm, NewRestaurantForm, RestaurantForm
from .models import Category, MenuItem, Order, OrderItem, Restaurant, Table

ACTIVE_STATUSES = [Order.PENDING, Order.PREPARING, Order.READY]


# ---------------------------------------------------------------- helpers
def owner_required(view):
    @login_required
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        restaurant = getattr(request.user, "restaurant", None)
        if restaurant is None:
            if request.user.is_superuser:
                return redirect("super_dashboard")
            return HttpResponse("No restaurant is linked to this account.", status=403)
        request.restaurant = restaurant
        return view(request, *args, **kwargs)
    return wrapper


superuser_required = user_passes_test(lambda u: u.is_active and u.is_superuser, login_url="/login/")


def order_json(o):
    return {
        "id": o.id,
        "table": o.table.number if o.table_id else None,
        "name": o.customer_name,
        "phone": o.customer_phone,
        "note": o.note,
        "total": float(o.total),
        "status": o.status,
        "time": timezone.localtime(o.created_at).strftime("%H:%M"),
        "items": [{"name": i.name, "qty": i.quantity} for i in o.items.all()],
    }


# ---------------------------------------------------------------- public
def index(request):
    restaurants = Restaurant.objects.filter(is_active=True).order_by("name")
    return render(request, "qrmenu/index.html", {"restaurants": restaurants})


@login_required
def after_login(request):
    return redirect("super_dashboard" if request.user.is_superuser else "dash_orders")


# ---------------------------------------------------------------- 1) customer
@ensure_csrf_cookie
def menu(request, slug):
    restaurant = get_object_or_404(Restaurant, slug=slug, is_active=True)
    categories = restaurant.categories.prefetch_related(
        Prefetch("items", queryset=MenuItem.objects.filter(is_available=True))
    )
    categories = [c for c in categories if c.items.all()]
    table = request.GET.get("table", "")
    table = table if table.isdigit() else ""
    return render(request, "qrmenu/menu.html", {"restaurant": restaurant, "categories": categories, "table": table})


@require_POST
def place_order(request, slug):
    restaurant = get_object_or_404(Restaurant, slug=slug, is_active=True)
    try:
        data = json.loads(request.body)
        name = str(data.get("name", "")).strip()[:80]
        phone = str(data.get("phone", "")).strip()[:20]
        note = str(data.get("note", "")).strip()[:300]
        lines = data.get("items") or []
        table_no = str(data.get("table", "")).strip()
    except (ValueError, AttributeError, TypeError):
        return JsonResponse({"error": "bad_request"}, status=400)
    if not name:
        return JsonResponse({"error": "name_required"}, status=400)

    wanted = {}
    for line in lines if isinstance(lines, list) else []:
        try:
            item_id, qty = int(line["id"]), int(line["qty"])
        except (KeyError, TypeError, ValueError):
            continue
        if 1 <= qty <= 50:
            wanted[item_id] = wanted.get(item_id, 0) + qty
    items = MenuItem.objects.filter(restaurant=restaurant, is_available=True, id__in=wanted.keys())
    if not items:
        return JsonResponse({"error": "empty_cart"}, status=400)

    table = restaurant.tables.filter(number=int(table_no)).first() if table_no.isdigit() else None
    with transaction.atomic():
        order = Order.objects.create(
            restaurant=restaurant, table=table, customer_name=name, customer_phone=phone, note=note,
            total=sum(i.price * min(wanted[i.id], 50) for i in items),
        )
        OrderItem.objects.bulk_create([
            OrderItem(order=order, menu_item=i, name=i.name, name_bn=i.name_bn, price=i.price, quantity=wanted[i.id])
            for i in items
        ])
    return JsonResponse({"url": reverse("order_status", args=[slug, order.public_id])})


def order_status(request, slug, public_id):
    order = get_object_or_404(Order.objects.select_related("restaurant", "table"), public_id=public_id, restaurant__slug=slug)
    return render(request, "qrmenu/order_status.html", {"order": order})


def order_status_api(request, slug, public_id):
    order = get_object_or_404(Order, public_id=public_id, restaurant__slug=slug)
    return JsonResponse({"status": order.status})


# ---------------------------------------------------------------- 2) restaurant dashboard
@owner_required
@ensure_csrf_cookie
def dash_orders(request):
    return render(request, "qrmenu/dash_orders.html", {"restaurant": request.restaurant})


@owner_required
def api_orders(request):
    qs = (request.restaurant.orders.filter(status__in=ACTIVE_STATUSES)
          .select_related("table").prefetch_related("items").order_by("id"))
    return JsonResponse({"orders": [order_json(o) for o in qs]})


@owner_required
@require_POST
def update_status(request, pk):
    order = get_object_or_404(Order, pk=pk, restaurant=request.restaurant)
    status = request.POST.get("status")
    if status not in dict(Order.STATUS):
        return JsonResponse({"error": "bad_status"}, status=400)
    order.status = status
    order.save(update_fields=["status"])
    return JsonResponse({"ok": True})


@owner_required
def dash_history(request):
    r = request.restaurant
    revenue = r.orders.filter(status=Order.SERVED, created_at__date=timezone.localdate()).aggregate(s=Sum("total"))["s"] or 0
    orders = r.orders.select_related("table")[:100]
    return render(request, "qrmenu/dash_history.html", {"restaurant": r, "orders": orders, "revenue": revenue})


@owner_required
def menu_manage(request):
    r = request.restaurant
    form = CategoryForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        c = form.save(commit=False)
        c.restaurant = r
        c.save()
        return redirect("dash_menu")
    categories = r.categories.prefetch_related("items")
    return render(request, "qrmenu/dash_menu.html", {"restaurant": r, "categories": categories, "form": form})


@owner_required
@require_POST
def category_delete(request, pk):
    get_object_or_404(Category, pk=pk, restaurant=request.restaurant).delete()
    return redirect("dash_menu")


@owner_required
def item_form(request, pk=None):
    r = request.restaurant
    item = get_object_or_404(MenuItem, pk=pk, restaurant=r) if pk else None
    form = ItemForm(request.POST or None, request.FILES or None, instance=item, restaurant=r)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.restaurant = r
        obj.save()
        return redirect("dash_menu")
    if not r.categories.exists():
        messages.warning(request, "Create a category first. / আগে একটি ক্যাটাগরি তৈরি করুন।")
        return redirect("dash_menu")
    return render(request, "qrmenu/dash_form.html", {"restaurant": r, "form": form, "title_key": "add_item"})


@owner_required
@require_POST
def item_toggle(request, pk):
    item = get_object_or_404(MenuItem, pk=pk, restaurant=request.restaurant)
    item.is_available = not item.is_available
    item.save(update_fields=["is_available"])
    return redirect("dash_menu")


@owner_required
@require_POST
def item_delete(request, pk):
    get_object_or_404(MenuItem, pk=pk, restaurant=request.restaurant).delete()
    return redirect("dash_menu")


@owner_required
def tables_view(request):
    r = request.restaurant
    if request.method == "POST":
        try:
            count = max(1, min(int(request.POST.get("count", 1)), 50))
        except ValueError:
            count = 1
        last = r.tables.aggregate(m=Max("number"))["m"] or 0
        Table.objects.bulk_create([Table(restaurant=r, number=last + i) for i in range(1, count + 1)])
        return redirect("dash_tables")
    return render(request, "qrmenu/dash_tables.html", {"restaurant": r, "tables": r.tables.all()})


@owner_required
@require_POST
def table_delete(request, pk):
    get_object_or_404(Table, pk=pk, restaurant=request.restaurant).delete()
    return redirect("dash_tables")


@owner_required
def qr_png(request):
    base = settings.SITE_URL or request.build_absolute_uri("/").rstrip("/")
    url = base + reverse("menu", args=[request.restaurant.slug])
    table = request.GET.get("table", "")
    if table.isdigit():
        url += f"?table={table}"
    buf = BytesIO()
    qrcode.make(url, box_size=8, border=2).save(buf, "PNG")
    return HttpResponse(buf.getvalue(), content_type="image/png")


@owner_required
def dash_settings(request):
    r = request.restaurant
    form = RestaurantForm(request.POST or None, request.FILES or None, instance=r)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Saved. / সেভ হয়েছে।")
        return redirect("dash_settings")
    return render(request, "qrmenu/dash_form.html", {"restaurant": r, "form": form, "title_key": "settings"})


# ---------------------------------------------------------------- 3) super admin
@superuser_required
def super_dashboard(request):
    restaurants = Restaurant.objects.select_related("owner").annotate(order_count=Count("orders")).order_by("-id")
    stats = {
        "restaurants": restaurants.count(),
        "active": restaurants.filter(is_active=True).count(),
        "orders": Order.objects.count(),
        "today": Order.objects.filter(created_at__date=timezone.localdate()).count(),
    }
    return render(request, "qrmenu/super_dashboard.html", {"restaurants": restaurants, "stats": stats})


@superuser_required
def super_create(request):
    form = NewRestaurantForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Restaurant created. / রেস্টুরেন্ট তৈরি হয়েছে।")
        return redirect("super_dashboard")
    return render(request, "qrmenu/super_form.html", {"form": form})


@superuser_required
@require_POST
def super_toggle(request, pk):
    r = get_object_or_404(Restaurant, pk=pk)
    r.is_active = not r.is_active
    r.save(update_fields=["is_active"])
    return redirect("super_dashboard")
