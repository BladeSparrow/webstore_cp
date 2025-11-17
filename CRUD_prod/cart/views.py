from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.db import transaction
import datetime

from .models import Cart, CartItem, CartStatus, ArchCart, Product
from api.models import Price
from .serializers import CartItemSerializer



def get_status(code):
    return CartStatus.objects.get(code=code)

def get_current_price(product_id):
    product = Product.objects.get(id=product_id)
    price_obj = Price.objects.filter(product=product).order_by('-pdate').first()
    if price_obj:
        return price_obj.pprice
    return 0 

@transaction.atomic
def archive_cart(cart, final_status_code):
    prod_list = []
    cart_items = cart.items.all()
    for item in cart_items:
        prod_list.append({
            "id": item.id_item.id,
            "qtty": item.item_qtty,
            "amount": item.sale_price
        })

    cart_stop_time = timezone.now()

    ArchCart.objects.create(
        session_id=cart.session_id,
        cart_start=cart.cart_start,
        cart_stop=cart_stop_time,
        prod_list=prod_list
    )

    cart.delete()
    
    return Response({"status": "success", "message": f"Cart archived as {final_status_code}"}, status=status.HTTP_200_OK)



class CartCreateView(APIView):
    """
    Створення нового кошику для сесії.
    POST /cart/create
    [cite: 4]
    """
    def post(self, request):
        session_id = request.data.get('session_id')
        if not session_id:
            return Response({"error": "session_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        if Cart.objects.filter(session_id=session_id).exists():
            return Response({"error": "Cart for this session already exists"}, status=status.HTTP_400_BAD_REQUEST)

        new_cart = Cart.objects.create(
            session_id=session_id,
            cart_status=get_status('empty')
        )
        return Response({"status": "success", "cart_id": new_cart.id}, status=status.HTTP_201_CREATED)

class CartCloseView(APIView):
    """
    Видалення (закриття) кошику по завершенню сесії.
    DELETE /cart/close
    [cite: 5]
    """
    def delete(self, request):
        session_id = request.data.get('session_id')
        try:
            cart = Cart.objects.get(session_id=session_id)
        except Cart.DoesNotExist:
            return Response({"error": "Cart not found"}, status=status.HTTP_404_NOT_FOUND)

        if cart.items.exists():
            return archive_cart(cart, 'abandoned')
        else:
            cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

class CartPurchaseView(APIView):
    """
    Перехід к оформленню (покупка).
    PUT /cart/purchase
    [cite: 6]
    """
    def put(self, request):
        session_id = request.data.get('session_id')
        try:
            cart = Cart.objects.get(session_id=session_id)
        except Cart.DoesNotExist:
            return Response({"error": "Cart not found"}, status=status.HTTP_404_NOT_FOUND)

        
        return archive_cart(cart, 'purchased')


class CartItemsView(APIView):
    """
    Перегляд вмісту кошика (GET)
    Додавання товара в корзину (POST)
    GET /cart/items?session_id=... 
    POST /cart/items 
    """
    def get(self, request):
        session_id = request.query_params.get('session_id')
        try:
            cart = Cart.objects.get(session_id=session_id)
        except Cart.DoesNotExist:
            return Response({"error": "Cart not found"}, status=status.HTTP_404_NOT_FOUND)
        
        items = cart.items.all()
        serializer = CartItemSerializer(items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @transaction.atomic
    def post(self, request):
        session_id = request.data.get('session_id')
        item_id = request.data.get('itemId')
        
        try:
            cart = Cart.objects.get(session_id=session_id)
            product = Product.objects.get(id=item_id)
        except Cart.DoesNotExist:
            return Response({"error": "Cart not found"}, status=status.HTTP_404_NOT_FOUND)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

        
        existing_item = CartItem.objects.filter(id_cart=cart, id_item=product).first()
        if existing_item:
            return Response({"error": "Item already in cart. Use PUT to update qtty."}, status=status.HTTP_400_BAD_REQUEST)

        
        current_price = get_current_price(product.id)
        
        
        CartItem.objects.create(
            id_cart=cart,
            id_item=product,
            item_qtty=1,
            sale_price=current_price
        )

        
        if cart.cart_status.code == 'empty':
            cart.cart_status = get_status('have_items')
            cart.save()
            
        return Response({"status": "success", "message": "Item added"}, status=status.HTTP_201_CREATED)


class CartItemDetailView(APIView):
    """
    Оновлення кількості (PUT)
    Видалення товару (DELETE)
    /cart/items/{itemId}
    [cite: 14, 15]
    """
    @transaction.atomic
    def put(self, request, itemId):
        session_id = request.data.get('session_id')
        new_qtty = request.data.get('new_qtty')
        
        try:
            cart = Cart.objects.get(session_id=session_id)
            item = CartItem.objects.get(id_cart=cart, id_item__id=itemId)
        except (Cart.DoesNotExist, CartItem.DoesNotExist):
            return Response({"error": "Cart or Item not found"}, status=status.HTTP_404_NOT_FOUND)

        new_qtty = int(new_qtty)
        if new_qtty <= 0:
            return self.delete(request, itemId)

        
        current_price = get_current_price(item.id_item.id)
        item.item_qtty = new_qtty
        item.sale_price = current_price * new_qtty
        item.save()
        
        return Response({"status": "success", "message": "Quantity updated"}, status=status.HTTP_200_OK)

    @transaction.atomic
    def delete(self, request, itemId):
        session_id = request.data.get('session_id')
        try:
            cart = Cart.objects.get(session_id=session_id)
            item = CartItem.objects.get(id_cart=cart, id_item__id=itemId)
        except (Cart.DoesNotExist, CartItem.DoesNotExist):
            return Response({"error": "Cart or Item not found"}, status=status.HTTP_404_NOT_FOUND)

        
        item.delete()

        
        if not cart.items.exists():
            cart.cart_status = get_status('empty')
            cart.save()
            
        return Response(status=status.HTTP_204_NO_CONTENT)


class CartClearView(APIView):
    """
    Повне очищення корзини.
    DELETE /cart/clear
    [cite: 15]
    """
    @transaction.atomic
    def delete(self, request):
        session_id = request.data.get('session_id')
        try:
            cart = Cart.objects.get(session_id=session_id)
        except Cart.DoesNotExist:
            return Response({"error": "Cart not found"}, status=status.HTTP_404_NOT_FOUND)

        
        cart.items.all().delete()
        
        cart.cart_status = get_status('empty')
        cart.save()
        
        return Response(status=status.HTTP_204_NO_CONTENT)