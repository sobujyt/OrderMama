from django import forms
from django.contrib.auth import get_user_model
from django.db import transaction

from .models import Category, MenuItem, Restaurant


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "name_bn", "position"]
        labels = {"name": "Name / নাম", "name_bn": "Name in Bangla / বাংলা নাম", "position": "Order / ক্রম"}


class ItemForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = ["category", "name", "name_bn", "description", "description_bn", "price", "image", "is_available"]
        labels = {
            "category": "Category / ক্যাটাগরি", "name": "Name / নাম", "name_bn": "Name in Bangla / বাংলা নাম",
            "description": "Description / বিবরণ", "description_bn": "Description in Bangla / বাংলা বিবরণ",
            "price": "Price (৳) / দাম", "image": "Photo / ছবি", "is_available": "Available / পাওয়া যাচ্ছে",
        }

    def __init__(self, *args, restaurant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if restaurant is not None:
            self.fields["category"].queryset = restaurant.categories.all()

    def clean_price(self):
        price = self.cleaned_data["price"]
        if price < 0:
            raise forms.ValidationError("Price cannot be negative.")
        return price


class RestaurantForm(forms.ModelForm):
    class Meta:
        model = Restaurant
        fields = ["name", "name_bn", "phone", "address", "logo"]
        labels = {"name": "Name / নাম", "name_bn": "Name in Bangla / বাংলা নাম", "phone": "Phone / ফোন",
                  "address": "Address / ঠিকানা", "logo": "Logo / লোগো"}


class NewRestaurantForm(forms.Form):
    name = forms.CharField(max_length=120, label="Restaurant name / নাম")
    name_bn = forms.CharField(max_length=120, required=False, label="Name in Bangla / বাংলা নাম")
    slug = forms.SlugField(label="Unique link name (a-z, 0-9, -) / লিংক", help_text="Menu URL will be /r/<this>/")
    phone = forms.CharField(max_length=20, required=False, label="Phone / ফোন")
    username = forms.CharField(max_length=150, label="Owner username / ইউজারনেম")
    password = forms.CharField(min_length=6, widget=forms.PasswordInput, label="Owner password / পাসওয়ার্ড")

    def clean_slug(self):
        slug = self.cleaned_data["slug"].lower()
        if Restaurant.objects.filter(slug=slug).exists():
            raise forms.ValidationError("This link name is already taken.")
        return slug

    def clean_username(self):
        username = self.cleaned_data["username"]
        if get_user_model().objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username

    @transaction.atomic
    def save(self):
        d = self.cleaned_data
        user = get_user_model().objects.create_user(username=d["username"], password=d["password"])
        return Restaurant.objects.create(owner=user, name=d["name"], name_bn=d["name_bn"], slug=d["slug"], phone=d["phone"])
