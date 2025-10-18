from decimal import Decimal
from rest_framework import serializers
from .models import Order, OrderItem
# from apps.products.serializers import ProductSerializer
from decimal import Decimal
from rest_framework import serializers
from django.db import transaction
from django.shortcuts import get_object_or_404
from apps.products.models import Product
from .models import Order, OrderItem
from apps.checkout.models import Shipping
from apps.accounts.models import User
from .enums import PaymentMethod, OrderStatus, PaymentStatus
from apps.checkout.serializers import ShippingSerializer
from apps.orders.models import OrderStatus

# Simple serializer for OrderItem
from rest_framework import serializers
from decimal import Decimal
from apps.orders.models import OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    """
    Serializer for individual order items.
    Includes computed line total, discount, and product image handling.
    """
    product_name = serializers.CharField(source="product.title", read_only=True)
    product_image = serializers.SerializerMethodField()
    product_discount = serializers.SerializerMethodField()
    line_total = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "product_name",
            "product_image",
            "quantity",
            "price_at_time",
            "product_discount",
            "line_total",
        ]
        read_only_fields = [
            "id",
            "product_name",
            "product_image",
            "line_total",
            "product_discount",
        ]

    # --------------------------
    # ✅ Product image (Cloudinary / Local)
    # --------------------------
    def get_product_image(self, obj):
        """
        Handles product image(s) — supports JSONField (multiple images)
        or FileField (single image).
        """
        request = self.context.get("request")
        product = getattr(obj, "product", None)

        if not product:
            return []

        try:
            # If product has multiple images (JSON list)
            if getattr(product, "images", None):
                return [
                    request.build_absolute_uri(img) if request else img
                    for img in product.images
                ]

            # If product has single image field
            if getattr(product, "image", None):
                url = (
                    request.build_absolute_uri(product.image.url)
                    if request
                    else product.image.url
                )
                return [url]
        except Exception:
            return []

        return []


    # --------------------------
    # ✅ Product discount
    # --------------------------
    def get_product_discount(self, obj):
        """
        Returns the product discount percentage, defaults to 0 if missing.
        """
        try:
            return Decimal(getattr(obj.product, "discount", 0) or 0)
        except Exception:
            return Decimal("0.00")

    # --------------------------
    # ✅ Line total computation
    # --------------------------
    def get_line_total(self, obj):
        """
        Calculates the total for the line (with discount applied).
        """
        try:
            price = Decimal(obj.price_at_time or 0)
            qty = Decimal(obj.quantity or 0)
            discount = self.get_product_discount(obj)

            discounted_price = price - (price * discount / Decimal("100"))
            total = discounted_price * qty

            return round(total, 2)
        except Exception:
            return Decimal("0.00")


# Serializer for order list view
class OrderListSerializer(serializers.ModelSerializer):
    """
    Optimized serializer for listing orders for both admin and users.
    Includes order items and computed total.
    """
    user_email = serializers.EmailField(source="user.email", read_only=True)
    order_items = serializers.SerializerMethodField()
    payment_status_display = serializers.CharField(source="get_payment_status_display", read_only=True)
    order_status_display = serializers.CharField(source="get_order_status_display", read_only=True)
    total_amount = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "id",
            "order_number",
            "user_email",
            "payment_method",
            "payment_status",
            "payment_status_display",
            "order_status",
            "order_status_display",
            "is_paid",
            "total_amount",
            "created_at",
            "order_items",
        ]

    def get_order_items(self, obj):
        """
        Fetch related order items with safe fallback.
        """
        try:
            items = obj.items.select_related("product").all()
            return [
                {
                    "product": item.product.title if item.product else "Deleted Product",
                    "quantity": item.quantity,
                    "price": float(item.price_at_time or 0),
                }
                for item in items
            ]
        except Exception:
            return []

    def get_total_amount(self, obj):
        """
        Compute total dynamically from related order items.
        """
        try:
            total = sum(
                (item.price_at_time or Decimal("0.00")) * item.quantity
                for item in obj.items.all()
            )
            return float(total)
        except Exception:
            return float(obj.total_amount or 0)



# Detailed serializer for a single order
class OrderDetailSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    shipping_address = ShippingSerializer(read_only=True)
    user_email = serializers.EmailField(source="user.email", read_only=True)
    total_amount = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "id",
            "order_number",
            "user_email",
            "shipping_address",
            "items",
            "total_amount",
            "is_paid",
            "payment_method",
            "status",
            "paid_at",
            "created",
            "modified",
        ]
        read_only_fields = fields  # All fields are read-only in detail view

    def get_total_amount(self, obj):
        try:
            total = sum([item.line_total for item in obj.items.all()])
            return round(total, 2)
        except Exception:
            return Decimal("0.00")



class AdminOrderStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["order_status"]

    def validate_order_status(self, value):
        if value not in OrderStatus.values:
            raise serializers.ValidationError("Invalid order status.")
        return value



class BuyNowSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(default=1)
    payment_method = serializers.ChoiceField(choices=[("COD", "Cash on Delivery"), ("ONLINE", "Online Payment")])
    shipping_id = serializers.IntegerField(required=False)

    # Shipping fields if no shipping_id provided
    full_name = serializers.CharField(required=False)
    phone_no = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    street_address = serializers.CharField(required=False)
    apartment = serializers.CharField(required=False, allow_blank=True)
    floor = serializers.CharField(required=False, allow_blank=True)
    city = serializers.CharField(required=False)
    zipcode = serializers.CharField(required=False)

    def validate_product_id(self, value):
        if not Product.objects.filter(id=value).exists():
            raise serializers.ValidationError("Product does not exist.")
        return value

    @transaction.atomic
    def create(self, validated_data):
        request = self.context.get("request")
        user = request.user

        # Fetch product and validate stock
        product = Product.objects.select_for_update().get(id=validated_data["product_id"])
        quantity = validated_data.get("quantity", 1)

        if quantity > product.available_stock:
            raise serializers.ValidationError(f"Only {product.available_stock} items available.")

        # Handle shipping
        shipping_id = validated_data.get("shipping_id")
        if shipping_id:
            shipping = get_object_or_404(Shipping, id=shipping_id, user=user)
        else:
            shipping = Shipping.objects.create(
                user=user,
                full_name=validated_data.get("full_name", ""),
                phone_no=validated_data.get("phone_no", ""),
                email=validated_data.get("email", ""),
                street_address=validated_data.get("street_address", ""),
                apartment=validated_data.get("apartment", ""),
                floor=validated_data.get("floor", ""),
                city=validated_data.get("city", ""),
                zipcode=validated_data.get("zipcode", ""),
            )

        # Determine product price (no coupon/discount logic)
        product_price = getattr(product, "discounted_price", product.price)
        total_amount = Decimal(product_price) * quantity

        # Determine payment/order status
        payment_method = validated_data["payment_method"]
        if payment_method == "ONLINE":
            is_paid = False
            payment_status = PaymentStatus.PENDING
            order_status = OrderStatus.PENDING
        else:
            is_paid = False
            payment_status = PaymentStatus.PENDING
            order_status = OrderStatus.PROCESSING

        # Create Order
        order = Order.objects.create(
            user=user,
            shipping_address=shipping,
            total_amount=total_amount,
            payment_method=payment_method,
            is_paid=is_paid,
            payment_status=payment_status,
            order_status=order_status,
        )

        # Create OrderItem
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            price_at_time=product_price,
        )

        # Reduce stock
        product.available_stock -= quantity
        product.save(update_fields=["available_stock"])


