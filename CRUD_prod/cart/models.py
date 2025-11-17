from django.db import models
from api.models import Product


class CartStatus(models.Model):
    code = models.CharField(max_length=50, unique=True, verbose_name="Код статуса")

    def __str__(self):
        return self.code


class Cart(models.Model):
    session_id = models.CharField(max_length=255, unique=True, db_index=True, verbose_name="ID сесії")
    cart_start = models.DateTimeField(auto_now_add=True, verbose_name="Дата створення")
    cart_stop = models.DateTimeField(null=True, blank=True, verbose_name="Дата закриття")
    cart_status = models.ForeignKey(CartStatus, on_delete=models.PROTECT, verbose_name="Статус кошика")

    def __str__(self):
        return self.session_id


class CartItem(models.Model):
    id_cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items", verbose_name="Посилання на кошик")
    id_item = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name="Посилання на продукт")
    add_start = models.DateTimeField(auto_now_add=True, verbose_name="Дата додавання")
    item_del = models.DateTimeField(null=True, blank=True, verbose_name="Дата видалення")
    item_qtty = models.PositiveIntegerField(default=1, verbose_name="Кількість")
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Загальна кількість")

    def __str__(self):
        return f"Товар {self.id_item.name} в кошику {self.id_cart.session_id}"


class ArchCart(models.Model):
    session_id = models.CharField(max_length=255, db_index=True, verbose_name="ID сесії")
    cart_start = models.DateTimeField(verbose_name="Дата створення")
    cart_stop = models.DateTimeField(verbose_name="Дата закриття")
    prod_list = models.JSONField(verbose_name="Список товарів")

    def __str__(self):
        return f"Архів {self.session_id}"