from django.contrib import admin
from .models import Category, Manufacturer, Product, Order, OrderProduct, Price

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'description')
    search_fields = ('code', 'name')
    ordering = ('name',)


@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'description')
    search_fields = ('code', 'name')
    ordering = ('name',)


class PriceInline(admin.TabularInline):
    model = Price
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'category', 'manufacturer', 'short_descr')
    list_filter = ('category', 'manufacturer')
    search_fields = ('code', 'name')
    inlines = [PriceInline]


class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('number', 'odate', 'orderprice')
    search_fields = ('number',)
    inlines = [OrderProductInline]


@admin.register(Price)
class PriceAdmin(admin.ModelAdmin):
    list_display = ('product', 'pdate', 'pprice', 'qtty')
    list_filter = ('pdate',)
    search_fields = ('product__name',)
