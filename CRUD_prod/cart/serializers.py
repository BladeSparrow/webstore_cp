from rest_framework import serializers
from .models import CartItem

class CartItemSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source='id_item.name', read_only=True)
    item_id = serializers.IntegerField(source='id_item.id', read_only=True)

    class Meta:
        model = CartItem
        fields = ('item_id', 'item_name', 'item_qtty', 'sale_price')