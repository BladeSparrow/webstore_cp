from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse

from .models import Category, Manufacturer, Product, Cart, CartItem, Price

class ModelTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(code="TEST_CAT", name="Test Category")
        self.manufacturer = Manufacturer.objects.create(code="TEST_MAN", name="Test Manufacturer")
        self.product = Product.objects.create(
            code="TEST_PROD",
            name="Test Product",
            category=self.category,
            manufacturer=self.manufacturer,
            short_descr="Short",
            description="Long"
        )

    def test_category_str(self):
        self.assertEqual(str(self.category), "Test Category")

    def test_product_creation(self):
        self.assertEqual(Product.objects.count(), 1)
        self.assertEqual(self.product.category, self.category)


class AuthAPITests(APITestCase):
    def test_register_user(self):
        url = reverse('auth_register')
        data = {
            'username': 'newuser',
            'password': 'securepassword123',
            'email': 'new@example.com',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, 'newuser')


class CartAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='cartuser', password='password123')
        self.client.force_authenticate(user=self.user)

        self.category = Category.objects.create(code="C1", name="C1")
        self.manufacturer = Manufacturer.objects.create(code="M1", name="M1")
        self.product = Product.objects.create(
            code="P1", name="P1", category=self.category, manufacturer=self.manufacturer, short_descr="-", description="-"
        )
        Price.objects.create(product=self.product, pdate="2025-01-01", pprice=100.00, qtty=10)

    def test_add_item_to_cart(self):
        url = reverse('cart-detail')
        data = {
            'product_id': self.product.id,
            'quantity': 2
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            
        cart = Cart.objects.get(user=self.user)
        self.assertEqual(cart.items.count(), 1)
        self.assertEqual(cart.items.first().quantity, 2)

    def test_remove_item_from_cart(self):
        CartItem.objects.create(cart=Cart.objects.create(user=self.user), product=self.product, quantity=1)
        
        cart_item = CartItem.objects.get(product=self.product)
        url = reverse('cart-item-delete', args=[cart_item.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(CartItem.objects.count(), 0)

    def test_clear_cart(self):
         CartItem.objects.create(cart=Cart.objects.create(user=self.user), product=self.product, quantity=1)
         url = reverse('cart-detail')
         response = self.client.delete(url)
         self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
         self.assertEqual(CartItem.objects.count(), 0)


class ProductAPITests(APITestCase):
    def setUp(self):
        self.category1 = Category.objects.create(code="C1", name="Cat 1")
        self.category2 = Category.objects.create(code="C2", name="Cat 2")
        self.manufacturer = Manufacturer.objects.create(code="M1", name="Man 1")
        
        self.product1 = Product.objects.create(
            code="P1", name="Product 1", category=self.category1, manufacturer=self.manufacturer, short_descr="-", description="-"
        )
        self.product2 = Product.objects.create(
            code="P2", name="Product 2", category=self.category2, manufacturer=self.manufacturer, short_descr="-", description="-"
        )

    def test_unauthenticated_can_list_products(self):
        url = reverse('product-list-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_unauthenticated_cannot_create_product(self):
        url = reverse('product-list-create')
        data = {'name': 'Hack'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_filter_by_category(self):
        url = reverse('product-list-by-category', args=[self.category1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Product 1')

