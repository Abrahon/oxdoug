from django.urls import path
from .views import (
    # Admin Views
    AdminCategoryListCreateView,
    AdminProductListCreateView,
    AdminCategoryProductListView,
    AdminProductCreateUpdateDeleteView,
    AdminProductBulkDelete,

    # User Views
    CategoryListView,
    CategoryProductFilterListView,
    ProductListView,
    ProductDetailView,
    TopSellingProductsView,
    RecommendedProductsView,
)

urlpatterns = [
    # ----------------- Admin URLs -----------------
    path('admin/categories/', AdminCategoryListCreateView.as_view(), name='admin-category-list-create'),
    path('admin/products/', AdminProductListCreateView.as_view(), name='admin-product-list-create'),
    path('admin/products/<int:id>/', AdminProductCreateUpdateDeleteView.as_view(), name='admin-product-detail'),
    path('admin/categories/<int:category_id>/products/', AdminCategoryProductListView.as_view(), name='admin-category-products'),
    path('admin/products/bulk-delete/', AdminProductBulkDelete.as_view(), name='admin-product-bulk-delete'),
   
    # ----------------- User URLs -----------------
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('products/', ProductListView.as_view(), name='product-list'),
    path('products/<int:id>/', ProductDetailView.as_view(), name='product-detail'),
    path('products/recommended/<int:product_id>/', RecommendedProductsView.as_view(), name='recommended-products'),
    path("top-products/", TopSellingProductsView.as_view(), name="top-selling-products"),
    path('products/category/', CategoryProductFilterListView.as_view(), name='single-category-products'),
]


