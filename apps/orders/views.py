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
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .serializers import OrderDetailSerializer
from apps.cart.models import CartItem
from apps.checkout.models import Shipping
from apps.products.models import Products
from apps.orders.models import Order, OrderItem
from apps.coupons.models import Coupon, CouponRedemption
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



class PlaceOrderView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        user = request.user
        shipping_id = request.data.get("shipping_id")
        cart_item_ids = request.data.get("cart_item_ids", [])
        coupon_code = request.data.get("coupon_code")
        payment_method = request.data.get("payment_method", "COD")

        if not shipping_id or not cart_item_ids:
            return Response({"error": "shipping_id and cart_item_ids are required"}, status=400)

        shipping = get_object_or_404(Shipping, id=shipping_id, user=user)
        cart_items = CartItem.objects.filter(user=user, id__in=cart_item_ids).select_related("product")
        if not cart_items.exists():
            return Response({"error": "Selected cart items not found"}, status=400)

        # Step 1: Create order (empty amounts first)
        order = Order.objects.create(
            user=user,
            shipping_address=shipping,
            total_amount=Decimal("0.00"),
            discounted_amount=Decimal("0.00"),
            final_amount=Decimal("0.00"),
            payment_status="pending",
            order_status="PENDING",
            payment_method=payment_method
        )

        total_amount = Decimal("0.00")
        discounted_amount = Decimal("0.00")

        # Step 2: Calculate totals & create items
        for item in cart_items:
            product = item.product
            quantity = item.quantity

            if quantity > product.available_stock:
                transaction.set_rollback(True)
                return Response({"error": f"Only {product.available_stock} items available for {product.title}."}, status=400)

            # 🟩 Use discounted price if exists, else regular
            product_price = Decimal(str(getattr(product, "discounted_price", product.price)))

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=product_price
            )

            total_amount += Decimal(str(product.price)) * quantity
            discounted_amount += product_price * quantity

            # Reduce stock
            product.available_stock -= quantity
            product.save(update_fields=["available_stock"])

        # 🟩 Step 3: Calculate base final amount (without coupon)
        final_amount = discounted_amount

        # 🟩 Step 4: Apply coupon if provided
        coupon = None
        if coupon_code:
            try:
                coupon = Coupon.objects.get(code=coupon_code, active=True)
                now = timezone.now()

                if coupon.valid_from and coupon.valid_from > now:
                    return Response({"error": "Coupon is not yet valid"}, status=400)
                if coupon.valid_to and coupon.valid_to < now:
                    return Response({"error": "Coupon has expired"}, status=400)

                # 🟩 FIX: Apply coupon correctly (same logic as ApplyCouponView)
                if coupon.discount_type == "percentage":
                    discount_value = (discounted_amount * Decimal(coupon.discount_value)) / Decimal("100")
                else:
                    discount_value = Decimal(coupon.discount_value)

                final_amount = max(discounted_amount - discount_value, Decimal("0.00"))

                # Mark coupon as redeemed for this user
                CouponRedemption.objects.get_or_create(coupon=coupon, user=user)

            except Coupon.DoesNotExist:
                return Response({"error": "Invalid coupon code"}, status=400)

        if final_amount <= 0:
            return Response({"error": "Final order amount is 0 or negative, cannot proceed"}, status=400)

        # 🟩 Step 5: Save totals to order
        order.total_amount = total_amount
        order.discounted_amount = discounted_amount
        order.final_amount = final_amount
        order.coupon = coupon

        # COD handling
        if payment_method == "COD":
            order.is_paid = False
            order.payment_status = "pending"
            order.order_status = OrderStatus.PENDING

        order.save(update_fields=["total_amount", "discounted_amount", "final_amount", "coupon", "is_paid", "payment_status", "order_status"])

        # 🟩 Step 6: Clear cart after successful order
        cart_items.delete()

        # 🟩 Step 7: Send confirmation email
        send_mail(
            subject=f"Order Confirmation - {order.order_number}",
            message=(
                f"Hello {user.email},\n\n"
                f"Your order {order.order_number} has been confirmed.\n"
                f"Final Amount: {order.final_amount}\n\n"
                "Thank you for shopping with us!"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

        # ✅ Return final correct response
        return Response({
            "success": "Order placed successfully",
            "order_id": order.id,
            "order_number": order.order_number,
            "total_amount": str(total_amount),
            "discounted_amount": str(discounted_amount),
            "final_amount": str(final_amount),
            "coupon_code": coupon.code if coupon else None,
        }, status=201)


# order details views
class OrderDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderDetailSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related("items__product")
 


class OrderListFilter(generics.ListAPIView):
    queryset = Order.objects.select_related('user', 'shipping_address').all().order_by('-created_at')
    serializer_class = OrderDetailSerializer
    permission_classes = [IsAdminUser]

    # ✅ Default pagination will automatically apply from settings.py

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['order_status']

    search_fields = [
        'order_number',
        'user__email',
        'user__name',
        'shipping_address__full_name',
        'shipping_address__email'
    ]

    ordering_fields = ['created_at', 'total_amount']
    ordering = ['-created_at']

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        if not queryset.exists():
            return Response(
                {"message": "No orders found for the given search or filters."},
                status=status.HTTP_404_NOT_FOUND
            )

        # ✅ DRF will automatically paginate if pagination is set in settings.py
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)





# ------------------- Admin: Update Order Status -------------------
class AdminUpdateOrderStatusView(generics.UpdateAPIView):
    serializer_class = AdminOrderStatusUpdateSerializer
    permission_classes = [permissions.IsAdminUser]
    parser_classes = [JSONParser, FormParser, MultiPartParser] 
    queryset = Order.objects.all()
    lookup_field = "id"

    def update(self, request, *args, **kwargs):
        order = self.get_object()
        old_status = order.order_status  # Save previous status

        serializer = self.get_serializer(order, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # ✅ Create tracking entry automatically when status changes

        return Response({  
            "message": f"Order {order.order_number} status updated successfully.",
            "order_id": order.id,
            "new_status": order.order_status
        }, status=status.HTTP_200_OK)




class BuyNowView(generics.CreateAPIView):
    serializer_class = BuyNowSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()

        if order.payment_method == "ONLINE":
            return Response({
                "order_id": order.id,
                "final_amount": str(order.final_amount),
                "message": "Order created. Please complete payment via Stripe."
            }, status=status.HTTP_201_CREATED)

        return Response({
            "order_id": order.id,
            "final_amount": str(order.final_amount),
            "message": "Order placed successfully (COD)"
        }, status=status.HTTP_201_CREATED)



class AdminOrderListView(generics.ListAPIView):
    """
    Admin view to list all orders with search, filter, and ordering.
    """
    serializer_class = OrderDetailSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["order_status", "payment_status", "payment_method", "is_paid"]
    search_fields = ["order_number", "user__email", "items__product__title"]
    ordering_fields = ["created_at", "total_amount"]

    def get_queryset(self):
        user = self.request.user
        if not user.is_staff:
            return Order.objects.none()  # non-admin cannot access
        # Use select_related and prefetch_related for performance
        return Order.objects.select_related("shipping_address", "user") \
                            .prefetch_related("items__product", "tracking_history") \
                            .order_by("-created_at")

# delete order 
class OrderDeleteView(generics.DestroyAPIView):
    """
    Delete an order by ID (Admin only).
    """
    queryset = Order.objects.all()
    permission_classes = [permissions.IsAdminUser]

    def delete(self, request, *args, **kwargs):
        order_id = kwargs.get('pk')
        try:
            order = self.get_queryset().get(pk=order_id)
            order.delete()
            return Response(
                {"message": f"Order #{order_id} deleted successfully."},
                status=status.HTTP_204_NO_CONTENT
            )
        except Order.DoesNotExist:
            return Response(
                {"error": "Order not found."},
                status=status.HTTP_404_NOT_FOUND
            )



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
        user = self.request.user
        product_id = self.request.query_params.get("product_id")
        print("product id",product_id)

        queryset = Order.objects.filter(user=user).order_by("-created_at")

        if product_id:
            # Filter orders that include this product
            queryset = queryset.filter(items__product_id=product_id).distinct()

        return queryset



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

        # Allow cancel if status is PENDING or PROCESSING
        if order.order_status not in ["PENDING", "PROCESSING"]:
            return Response(
                {"error": f"Order cannot be canceled. Current status: {order.order_status}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        order.order_status = "CANCELED"  # Use correct field
        order.save()
        return Response({
            "message": f"Order {order.order_number} has been canceled successfully.",
            "order_id": order.id,
            "new_status": order.order_status
        }, status=status.HTTP_200_OK)

