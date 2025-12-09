from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Category, Manufacturer, Product, Cart, CartItem

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'  

class ManufacturerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manufacturer
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'email', 'first_name', 'last_name')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data.get('email', ''),
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        return user

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source='product', write_only=True
    )
    price = serializers.DecimalField(max_digits=10, decimal_places=2, source='product.prices.first.pprice', read_only=True) # Simplification: taking first price. In real app logic is complex.

    class Meta:
        model = CartItem
        fields = ('id', 'product', 'product_id', 'quantity', 'price')


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ('id', 'items', 'total_price', 'created_at', 'updated_at')

    def get_total_price(self, obj):
        total = 0
        for item in obj.items.all():
             price = item.product.prices.first()
             if price:
                 total += price.pprice * item.quantity
        return total