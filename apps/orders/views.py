from decimal import Decimal
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, filters, status, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
# b2c/orders/views.py
from rest_framework import generics, permissions, status
from .models import Order
from .serializers import AdminOrderStatusUpdateSerializer
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAdminUser
from .serializers import OrderListSerializer
# Models
from rest_framework.permissions import IsAuthenticated
from .serializers import OrderDetailSerializer
from apps.cart.models import CartItem
from apps.checkout.models import Shipping
from apps.products.models import Products
from apps.orders.models import Order, OrderItem

from .enums import OrderStatus, PaymentStatus, PaymentMethod
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from decimal import Decimal
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from datetime import timedelta
from rest_framework import generics, filters, status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAdminUser
from .models import Order
from .serializers import OrderListSerializer
from apps.orders.serializers import (
    OrderItemSerializer,
    OrderDetailSerializer,
    BuyNowSerializer,
)
from .enums import OrderStatus
User = get_user_model()


class OrderListView(generics.ListAPIView):
    serializer_class = OrderDetailSerializer
    permission_classes = [IsAdminUser] 
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["order_status", "payment_status"]
    search_fields = ["order_number", "items__product__title"]
    ordering_fields = ["created_at", "total_amount"]

    def get_queryset(self):
        return Order.objects.all().select_related("shipping_address").prefetch_related("items__product").order_by("-created_at")





# ------------------------------
# Place Order (from Cart)
# ------------------------------
class PlaceOrderView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        user = request.user
        shipping_id = request.data.get("shipping_id")
        cart_item_ids = request.data.get("cart_item_ids", [])
        payment_method = request.data.get("payment_method", "COD")

        if not shipping_id or not cart_item_ids:
            return Response({"error": "shipping_id and cart_item_ids are required"}, status=400)

        shipping = get_object_or_404(Shipping, id=shipping_id, user=user)
        cart_items = CartItem.objects.filter(user=user, id__in=cart_item_ids).select_related("product")
        if not cart_items.exists():
            return Response({"error": "Selected cart items not found"}, status=400)

        order = Order.objects.create(
            user=user,
            shipping_address=shipping,
            total_amount=Decimal("0.00"),
            payment_method=payment_method,
            payment_status=PaymentStatus.PENDING,
            order_status=OrderStatus.PENDING,
            is_paid=False
        )

        total_amount = Decimal("0.00")

        for item in cart_items:
            product = item.product
            quantity = item.quantity

            if quantity > product.available_stock:
                transaction.set_rollback(True)
                return Response(
                    {"error": f"Only {product.available_stock} items available for {product.title}."},
                    status=400
                )

            product_price = Decimal(str(getattr(product, "discounted_price", product.price)))

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price_at_time=product_price
            )

            total_amount += product_price * quantity

            # Reduce stock
            product.available_stock -= quantity
            product.save(update_fields=["available_stock"])

        order.total_amount = total_amount
        
        order.save(update_fields=["total_amount", "is_paid", "payment_status", "order_status"])

        cart_items.delete()  # Clear cart

        # Send confirmation email
        send_mail(
            subject=f"Order Confirmation - {order.order_number}",
            message=f"Hello {user.email},\n\nYour order {order.order_number} has been confirmed.\n"
                    f"Total Amount: {order.total_amount}\n\nThank you for shopping with us!",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

        return Response({
            "success": "Order placed successfully",
            "order_id": order.id,
            "order_number": order.order_number,
            "total_amount": str(order.total_amount),
           
        }, status=201)


# ------------------------------
# Buy Now
# ------------------------------
class BuyNowView(generics.CreateAPIView):
    serializer_class = BuyNowSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()

        return Response({
            "order_id": order.id,
            "total_amount": str(order.total_amount),
            "message": "Order placed successfully" if order.payment_method == "COD" else "Order created. Please complete payment online."
        }, status=201)


# ------------------------------
# User Order Details
# ------------------------------
class OrderDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderDetailSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related("items__product")


# ------------------------------
# User Order History
# ------------------------------
class UserOrderHistoryView(generics.ListAPIView):
    serializer_class = OrderDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)\
            .select_related("shipping_address")\
            .prefetch_related("items__product")\
            .order_by("-created_at")


# ------------------------------
# Admin: List Orders
# ------------------------------
class AdminOrderListView(generics.ListAPIView):
    serializer_class = OrderDetailSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["order_status", "payment_status", "payment_method", "is_paid"]
    search_fields = ["order_number", "user__email", "items__product__title"]
    ordering_fields = ["created_at", "total_amount"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return Order.objects.select_related("shipping_address", "user")\
                            .prefetch_related("items__product")\
                            .order_by("-created_at")


# ------------------------------
# Admin: Update Order Status
# ------------------------------
class AdminUpdateOrderStatusView(generics.UpdateAPIView):
    serializer_class = AdminOrderStatusUpdateSerializer
    permission_classes = [IsAdminUser]
    queryset = Order.objects.all()
    lookup_field = "id"

    def update(self, request, *args, **kwargs):
        order = self.get_object()
        serializer = self.get_serializer(order, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Notify user
        Notification.objects.create(
            user=order.user,
            title=f"Order {order.order_number} status updated",
            message=f"Your order status has been updated to '{order.order_status}'."
        )

        return Response({
            "message": f"Order {order.order_number} status updated successfully.",
            "order_id": order.id,
            "new_status": order.order_status
        }, status=200)


# ------------------------------
# Admin: Delete Order
# ------------------------------
class OrderDeleteView(generics.DestroyAPIView):
    queryset = Order.objects.all()
    permission_classes = [IsAdminUser]

    def delete(self, request, *args, **kwargs):
        order_id = kwargs.get('pk')
        try:
            order = self.get_queryset().get(pk=order_id)
            order.delete()
            return Response({"message": f"Order #{order_id} deleted successfully."}, status=204)
        except Order.DoesNotExist:
            return Response({"error": "Order not found."}, status=404)

# ------------------ User Order History & Detail Views ------------------ #

# List all orders for a logged-in user
class UserOrderHistoryView(generics.ListAPIView):
    serializer_class = OrderListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by("-created")


# Retrieve single order detail
class UserOrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


# Cancel an order
class CancelOrderView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            return Response({"error": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

        # Only allow cancel if status is PROCESSING (not shipped or completed)
        if order.status not in ["PROCESSING"]:
            return Response(
                {"error": f"Order cannot be canceled. Current status: {order.status}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        order.status = "CANCELED"
        order.save()
        return Response({"message": f"Order {order.order_number} has been canceled successfully."})

