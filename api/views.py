from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from django.db.models import ProtectedError
from django.core.mail import send_mail
import uuid

from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from .models import Category, Manufacturer, Product, Cart, CartItem, Order, OrderProduct, Price
from .serializers import (
    CategorySerializer, ManufacturerSerializer, ProductSerializer, UserSerializer,
    CartSerializer, CartItemSerializer
)


def handle_protected_error(instance_name):
    return Response(
        {"error": f"Неможливо видалити. Цей {instance_name} пов'язаний з одним або декількома товарами/замовленнями."},
        status=status.HTTP_400_BAD_REQUEST
    )


class CartAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    def post(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = CartItemSerializer(data=request.data)
        if serializer.is_valid():
            product = serializer.validated_data['product']
            quantity = serializer.validated_data.get('quantity', 1)
            
            cart_item, item_created = CartItem.objects.get_or_create(
                cart=cart, product=product,
                defaults={'quantity': quantity}
            )
            if not item_created:
                cart_item.quantity += quantity
                cart_item.save()
            
            return Response(CartSerializer(cart).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        if pk:
            try:
                item = CartItem.objects.get(pk=pk, cart__user=request.user)
                item.delete()
            except CartItem.DoesNotExist:
                return Response({"error": "Item not found"}, status=status.HTTP_404_NOT_FOUND)
            
            cart = Cart.objects.get(user=request.user)
            return Response(CartSerializer(cart).data)
        else:
            cart = Cart.objects.get(user=request.user)
            cart.items.all().delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


class CheckoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        try:
            cart = Cart.objects.get(user=request.user)
            if not cart.items.exists():
                 return Response({"error": "Кошик порожній"}, status=status.HTTP_400_BAD_REQUEST)
        except Cart.DoesNotExist:
            return Response({"error": "Кошик не знайдено"}, status=status.HTTP_404_NOT_FOUND)

        email = request.data.get('email', request.user.email)
        address = request.data.get('address', '')
        total_price = 0
        order_items_text = ""
        order_number = str(uuid.uuid4())
        order = Order.objects.create(
            number=order_number,
            orderprice=0 
        )

        for item in cart.items.all():
            price_obj = item.product.prices.order_by('-pdate').first()
            price = price_obj.pprice if price_obj else 0
            
            line_total = price * item.quantity
            total_price += line_total

            OrderProduct.objects.create(
                order=order,
                product=item.product,
                qtty=item.quantity
            )
            
            order_items_text += f"- {item.product.name} x {item.quantity} шт. = {line_total} грн.\n"

        order.orderprice = total_price
        order.save()

        cart.items.all().delete()

        subject = f"Підтвердження замовлення №{order_number}"
        message = f"""
Дякуємо за ваше замовлення!

Номер замовлення: {order_number}
Сума замовлення: {total_price} грн.

Склад замовлення:
{order_items_text}

Адреса доставки: {address}

Ми вже почали обробку вашого замовлення.
        """
        
        try:
            send_mail(
                subject,
                message,
                'no-reply@webstore.com',
                [email],
                fail_silently=False,
            )
        except Exception as e:
            print(f"Email sending failed: {e}")

        return Response({
            "message": "Оплата успішна. Замовлення створено.",
            "order_number": order_number
        }, status=status.HTTP_200_OK)


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryListCreateAPIView(APIView):
    def get(self, request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CategoryDetailAPIView(APIView):
    def get_object(self, pk):
        try:
            return Category.objects.get(pk=pk)
        except Category.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        category = self.get_object(pk)
        serializer = CategorySerializer(category)
        return Response(serializer.data)

    def put(self, request, pk):
        category = self.get_object(pk)
        serializer = CategorySerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        category = self.get_object(pk)
        try:
            category.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ProtectedError:
            return handle_protected_error("категорію")



class ManufacturerListCreateAPIView(APIView):
    def get(self, request):
        manufacturers = Manufacturer.objects.all()
        serializer = ManufacturerSerializer(manufacturers, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ManufacturerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ManufacturerDetailAPIView(APIView):
    def get_object(self, pk):
        try:
            return Manufacturer.objects.get(pk=pk)
        except Manufacturer.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        manufacturer = self.get_object(pk)
        serializer = ManufacturerSerializer(manufacturer)
        return Response(serializer.data)

    def put(self, request, pk):
        manufacturer = self.get_object(pk)
        serializer = ManufacturerSerializer(manufacturer, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        manufacturer = self.get_object(pk)
        try:
            manufacturer.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ProtectedError:
            return handle_protected_error("виробника")



class ProductListCreateAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProductDetailAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        try:
            return Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        product = self.get_object(pk)
        serializer = ProductSerializer(product)
        return Response(serializer.data)

    def put(self, request, pk):
        product = self.get_object(pk)
        serializer = ProductSerializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        product = self.get_object(pk)
        try:
            product.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ProtectedError:
            return handle_protected_error("товар")


class ProductListByCategoryAPIView(APIView):
    def get(self, request, category_id):
        products = Product.objects.filter(category__id=category_id)
        if not products.exists():
             return Response({"detail": "Товари у цій категорії не знайдено."}, status=status.HTTP_404_NOT_FOUND)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

class ProductListByManufacturerAPIView(APIView):
    def get(self, request, manufacturer_id):
        products = Product.objects.filter(manufacturer__id=manufacturer_id)
        if not products.exists():
            return Response({"detail": "Товари цього виробика не знайдено."}, status=status.HTTP_404_NOT_FOUND)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)
