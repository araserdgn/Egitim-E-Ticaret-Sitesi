from django.contrib import admin
from .models import*

# Register your models here.

# admin.site.register(Products)
admin.site.register(Category)
admin.site.register(SeriNo)
admin.site.register(AltKategori)
admin.site.register(Odeme)

@admin.register(Basket)
class BasketAdmin(admin.ModelAdmin):
    list_display = ("ekleyen","product","adet","total","odendiMi")
    list_filter = ("odendiMi","product")


@admin.register(Products)
class ProductAdmin(admin.ModelAdmin):
    list_display=("name","category",)
    list_filter = ("category",)

