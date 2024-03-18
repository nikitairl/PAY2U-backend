from django.contrib import admin
from .models import Category, Service


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "login",
        "availability",
        "description",
        "conditions",
        "website",
        "instruction",
        "rules",
        "popularity",
        "category",
    )
