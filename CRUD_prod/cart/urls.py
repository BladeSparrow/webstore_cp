from django.urls import path
from .views import (
    CartCreateView, CartCloseView, CartPurchaseView,
    CartItemsView, CartItemDetailView, CartClearView
)

urlpatterns = [
    path('create/', CartCreateView.as_view(), name='cart-create'),
    path('close/', CartCloseView.as_view(), name='cart-close'),
    path('purchase/', CartPurchaseView.as_view(), name='cart-purchase'),

    
    path('items/', CartItemsView.as_view(), name='cart-items'),
    path('items/<int:itemId>/', CartItemDetailView.as_view(), name='cart-item-detail'),
    path('clear/', CartClearView.as_view(), name='cart-clear'),
]