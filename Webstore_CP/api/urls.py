from django.urls import path
from .views import (
    CategoryListCreateAPIView, CategoryDetailAPIView,
    ManufacturerListCreateAPIView, ManufacturerDetailAPIView,
    ProductListCreateAPIView, ProductDetailAPIView,
    ProductListByCategoryAPIView, ProductListByManufacturerAPIView
)
from . import views

urlpatterns = [
    path('category/', CategoryListCreateAPIView.as_view(), name='category-list-create'),
    path('category/<int:pk>/', CategoryDetailAPIView.as_view(), name='category-detail'),

    path('manufacturers/', ManufacturerListCreateAPIView.as_view(), name='manufacturer-list-create'),
    path('manufacturers/<int:pk>/', ManufacturerDetailAPIView.as_view(), name='manufacturer-detail'),

    path('products/', ProductListCreateAPIView.as_view(), name='product-list-create'),
    path('products/<int:pk>/', ProductDetailAPIView.as_view(), name='product-detail'),

    path('products/cat/<int:category_id>/', ProductListByCategoryAPIView.as_view(), name='product-list-by-category'),
    path('products/man/<int:manufacturer_id>/', ProductListByManufacturerAPIView.as_view(), name='product-list-by-manufacturer'),
    path('', views.product_list, name='product_list'),
    path("novaposhta/cities/", views.cities_view, name="novaposhta_cities"),
    path("novaposhta/warehouses/<str:city_ref>/", views.warehouses_view, name="novaposhta_warehouses"),
]
