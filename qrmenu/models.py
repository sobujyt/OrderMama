import uuid

from django.conf import settings
from django.db import models


class Restaurant(models.Model):
    owner = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="restaurant")
    name = models.CharField(max_length=120)
    name_bn = models.CharField(max_length=120, blank=True)
    slug = models.SlugField(unique=True)
    logo = models.ImageField(upload_to="logos/", blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Table(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="tables")
    number = models.PositiveIntegerField()

    class Meta:
        unique_together = ("restaurant", "number")
        ordering = ["number"]

    def __str__(self):
        return f"{self.restaurant.name} - Table {self.number}"


class Category(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="categories")
    name = models.CharField(max_length=80)
    name_bn = models.CharField(max_length=80, blank=True)
    position = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["position", "id"]
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class MenuItem(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="menu_items")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="items")
    name = models.CharField(max_length=120)
    name_bn = models.CharField(max_length=120, blank=True)
    description = models.CharField(max_length=300, blank=True)
    description_bn = models.CharField(max_length=300, blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.ImageField(upload_to="items/", blank=True)
    is_available = models.BooleanField(default=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.name


class Order(models.Model):
    PENDING, PREPARING, READY, SERVED, CANCELLED = "pending", "preparing", "ready", "served", "cancelled"
    STATUS = [(PENDING, "Pending"), (PREPARING, "Preparing"), (READY, "Ready"), (SERVED, "Served"), (CANCELLED, "Cancelled")]

    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="orders")
    table = models.ForeignKey(Table, on_delete=models.SET_NULL, null=True, blank=True, related_name="orders")
    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    customer_name = models.CharField(max_length=80)
    customer_phone = models.CharField(max_length=20, blank=True)
    note = models.CharField(max_length=300, blank=True)
    status = models.CharField(max_length=12, choices=STATUS, default=PENDING)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-id"]
        indexes = [models.Index(fields=["restaurant", "status"])]

    def __str__(self):
        return f"#{self.pk} {self.customer_name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    menu_item = models.ForeignKey(MenuItem, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=120)
    name_bn = models.CharField(max_length=120, blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    @property
    def subtotal(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.name}"
