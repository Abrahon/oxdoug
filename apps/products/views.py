import csv
import json
import logging
import random
import requests
from decimal import Decimal, InvalidOperation
from django.utils.text import slugify
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from django.db.models import Q, Sum, F, Value
from django.db.models.functions import Coalesce

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.pagination import PageNumberPagination

import django_filters
from django_filters.rest_framework import DjangoFilterBackend

from cloudinary.uploader import upload as cloudinary_upload

from .models import Products, Category
from .serializers import ProductSerializer, CategorySerializer
from .enums import ProductStatus
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
logger = logging.getLogger(__name__)



# Admin Views
# 



class AdminCategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAdminUser]
    parser_classes = [JSONParser, MultiPartParser, FormParser]  # ✅ Add this



# List and Create Products - Admin only
class AdminProductListCreateView(generics.ListCreateAPIView):
    queryset = Products.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAdminUser]
    parser_classes = [MultiPartParser, FormParser]

# List products by category for admin
class AdminCategoryProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        category_id = self.kwargs.get("category_id")
        return Products.objects.filter(category_id=category_id)



# Admin Product Retrieve, Update, Delete
class AdminProductCreateUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Products.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAdminUser]
    parser_classes = [MultiPartParser, FormParser]
    lookup_field = "id"
    lookup_url_kwarg = "id"
    http_method_names = ['get', 'patch', 'delete', 'put']  

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)  
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({
            "message": "Product updated successfully",
            "product": serializer.data
        }, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            "message": "Product deleted successfully"
        }, status=status.HTTP_200_OK)



class AdminProductBulkDelete(APIView):
    permission_classes = [permissions.IsAdminUser]

    def delete(self, request, *args, **kwargs):
        ids = request.data.get("ids", [])
        if not ids:
            return Response({"error": "No product IDs provided"}, status=status.HTTP_400_BAD_REQUEST)
        deleted_count, _ = Product.objects.filter(id__in=ids).delete()
        return Response({"message": f"{deleted_count} products deleted successfully"}, status=status.HTTP_200_OK)


# ======================
# User Views
# ======================

class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]



# class UserCategoryProductListView(generics.ListAPIView):
#     """
#     ✅ List all products filtered by a single category.
#     Example:
#         /api/products/by-category/<uuid:category_id>/
#     """
#     serializer_class = ProductSerializer

#     def get_queryset(self):
#         category_id = self.kwargs.get("category_id")
#         queryset = Product.objects.filter(status="active")

#         if category_id:
#             queryset = queryset.filter(category_id=category_id)

#         # Optional search by product title
#         search = self.request.query_params.get("search")
#         if search:
#             queryset = queryset.filter(title__icontains=search)

#         # Optional ordering
#         ordering = self.request.query_params.get("ordering")
#         if ordering:
#             queryset = queryset.order_by(ordering)

#         return queryset






# recommended products
class RecommendedProductsView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, product_id):
        product = get_object_or_404(Products, id=product_id)

        # 1. Active products in same category, exclude current
        recommended_qs = Products.objects.filter(
            category=product.category,
            status=ProductStatus.ACTIVE
        ).exclude(id=product.id).distinct()

        # 2. Parse colors if stored as string
        try:
            product_colors = product.colors
            if isinstance(product_colors, str):
                product_colors = json.loads(product_colors)
        except Exception:
            product_colors = []

        # 3. Filter manually for overlapping colors
        if product_colors:
            filtered = []
            for p in recommended_qs:
                colors = p.colors
                if isinstance(colors, str):
                    try:
                        colors = json.loads(colors)
                    except Exception:
                        colors = []
                if set(product_colors) & set(colors):
                    filtered.append(p)
        else:
            filtered = list(recommended_qs)

        # 4. Shuffle and limit
        random.shuffle(filtered)
        filtered = filtered[:6]

        serializer = ProductSerializer(filtered, many=True, context={'request': request})
        return Response(serializer.data)





# Pagination class
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100

class CategoryProductFilterListView(APIView):
    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination

    def get(self, request, category_id=None):
        try:
            q = request.query_params.get("q", None)
            categories = request.query_params.getlist("category")
            min_price = request.query_params.get("min_price", None)
            max_price = request.query_params.get("max_price", None)
            price_sort = request.query_params.get("price_sort", None)
            name_sort = request.query_params.get("name_sort", None)
            top_filter = request.query_params.get("top", None)
            status_filter = request.query_params.get("status", None)

            products = Products.objects.all()

            # Include category from path
            if category_id:
                categories.append(str(category_id))

            # Clean categories
            categories = [c.strip() for c in categories if c and c.strip()]

            if categories:
                try:
                    # Convert category IDs to integers
                    category_ids = [int(cat) for cat in categories]
                    products = products.filter(category__id__in=category_ids)
                except ValueError:
                    return Response({"error": "Invalid category ID format"}, status=400)


            # Status filter
            if status_filter:
                sf = status_filter.lower()
                if sf not in ["active", "inactive"]:
                    return Response({"error": "Invalid status value"}, status=400)
                products = products.filter(status=sf)

            # Keyword search
            if q:
                products = products.filter(Q(title__icontains=q) | Q(description__icontains=q))

            # Price filters
            if min_price:
                try:
                    products = products.filter(price__gte=Decimal(min_price))
                except InvalidOperation:
                    return Response({"error": "Invalid min_price"}, status=400)
            if max_price:
                try:
                    products = products.filter(price__lte=Decimal(max_price))
                except InvalidOperation:
                    return Response({"error": "Invalid max_price"}, status=400)

            # Top filters
            if top_filter:
                tf = top_filter.lower()
                if tf == "sales":
                    products = products.annotate(total_sold=Coalesce(Sum("order_items__quantity"), Value(0)))
                    products = products.order_by("-total_sold")
                elif tf == "stock":
                    products = products.order_by("-available_stock")
                elif tf == "price" and not price_sort:
                    products = products.order_by("-price")

            # Price and name sorting
            if price_sort:
                products = products.order_by("price" if price_sort.lower() == "asc" else "-price")
            if name_sort:
                products = products.order_by("title" if name_sort.lower() == "asc" else "-title")

            # Remove duplicates
            products = products.distinct()

            # Pagination
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(products, request)
            serializer = ProductSerializer(page, many=True, context={"request": request})
            return paginator.get_paginated_response(serializer.data)

        except Exception as e:
            return Response({"error": str(e)}, status=500)


class ProductFilter(django_filters.FilterSet):
    category = django_filters.CharFilter(field_name="category__id", lookup_expr="exact")

    class Meta:
        model = Products
        fields = ["category"]

class ProductListView(generics.ListAPIView):
    queryset = Products.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter


class ProductDetailView(generics.RetrieveAPIView):
    queryset = Products.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "id"
    lookup_url_kwarg = "id"


# top selling products
