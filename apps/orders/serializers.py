from decimal import Decimal
from rest_framework import serializers
from .models import Order, OrderItem
from .enums import  PaymentMethod
from decimal import Decimal
from rest_framework import serializers
from django.db import transaction
from django.shortcuts import get_object_or_404
from apps.products.models import Products
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
from apps.coupons.models import Coupon, CouponRedemption
from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Order, OrderItem
from apps.products.serializers import ProductSerializer
from .enums import OrderStatus, PaymentStatus
from django.utils import timezone




class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_name = serializers.CharField(source="product.title", read_only=True)
    # product_image = serializers.ImageField(source="product.image", read_only=True)
    product_image = serializers.SerializerMethodField() 
    product_discount = serializers.SerializerMethodField()
    coupon_discount = serializers.SerializerMethodField()
    final_price = serializers.SerializerMethodField()
    line_total = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = [
            "id", "product", "product_image", "product_name", "quantity", "price",
            "product_discount", "coupon_discount", "final_price", "line_total"
        ]
        read_only_fields = [
            "id", "product_name", "product_image", "line_total",
            "final_price", "product_discount", "coupon_discount"
        ]
    
    
    def get_product_image(self, obj):
        request = self.context.get("request")
        product = getattr(obj, "product", None)
        if product and getattr(product, "images", None):
            # if images is JSONField
            return [request.build_absolute_uri(img) if request else img for img in product.images]
        elif product and getattr(product, "image", None):
            return [request.build_absolute_uri(product.image.url) if request else product.image.url]
        return []



    def get_product_discount(self, obj):
        return getattr(obj.product, "discount", 0) or 0

    def get_coupon_discount(self, obj):
        coupon = getattr(obj.order, "coupon", None)
        if coupon:        
            return coupon.discount_value
            # return order.coupon.discount_value
        return 0
    

    def get_final_price(self, obj):
        price = Decimal(str(obj.product.discounted_price)) 
        coupon = getattr(obj.order, "coupon", None)
        if coupon:
            if coupon.discount_type == "percentage":
                price -= price * Decimal(str(coupon.discount_value)) / Decimal("100")
            else:
                price -= Decimal(str(coupon.discount_value))
        return round(max(price, Decimal("0.00")), 2)

    def get_line_total(self, obj):
        return round(obj.quantity * self.get_final_price(obj), 2)




class OrderDetailSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    product = ProductSerializer(read_only=True)
    shipping_address = ShippingSerializer(read_only=True)
    user_email = serializers.EmailField(source="user.email", read_only=True)
    
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    discounted_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    final_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'user', 'product', 'user_email', 'shipping_address',
            'items','coupon', 'total_amount', 'discounted_amount','final_amount',
            'is_paid', 'payment_status', 'order_status',
            'stripe_payment_intent', 'stripe_checkout_session_id', 'created_at',
        ]
        read_only_fields = [
            'user', 'order_number', 'items', 'product', 'user_email',
            'total_amount', 'discounted_amount', 'is_paid',
            'payment_status', 'order_status', 'final_amount','stripe_payment_intent',
            'stripe_checkout_session_id', 'created_at',
        ]



# class OrderListSerializer(serializers.ModelSerializer):
#     user_email = serializers.CharField(source="user.email", read_only=True)
#     user_name = serializers.CharField(source="user.username", read_only=True) 
#     shipping_address = serializers.CharField(source="shipping_address.address", read_only=True)
#     order_items = serializers.SerializerMethodField()
#     final_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

#     class Meta:
#         model = Order
#         fields = [
#             "id",
#             "order_number",
#             "user_email",
#             "user_name",
#             "order_status",
#             "total_amount",
#             "created_at",
#             "order_items",
#             "final_amount",
#             "shipping_address",
#         ]



#     def get_order_items(self, obj):

#     # Fetch all items related to this order
#         items = obj.items.all() 
        
#         return [
#             {
#                 "product_id": i.product.id,  
#                 "product": i.product.title,
#                 "quantity": i.quantity,
#                 "price": float(i.price)
#             }
#             for i in items
#         ]



class OrderListSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source="user.email", read_only=True)
    user_name = serializers.CharField(source="user.username", read_only=True)
    shipping_address = serializers.CharField(source="shipping_address.address", read_only=True)
    order_items = serializers.SerializerMethodField()
    final_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "order_number",
            "user_email",
            "user_name",
            "order_status",
            "total_amount",
            "created_at",
            "order_items",
            "final_amount",
            "shipping_address",
        ]

    def get_order_items(self, obj):
        # Fetch all related items safely
        items = obj.items.all()
        return [
            {
                "product_id": item.product.id if item.product else None,
                "product": item.product.title if item.product else None,
                "quantity": item.quantity,
                "price": float(item.price),
            }
            for item in items
        ]

         



# class AdminOrderStatusUpdateSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Order
#         fields = ["order_status"]

#     def validate_order_status(self, value):
#         if value not in OrderStatus.values:
#             raise serializers.ValidationError("Invalid order status.")
#         return value



class AdminOrderStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["order_status"]  # Only the status can be updated
        read_only_fields = []      # Make sure it's not read-only

    def validate_order_status(self, value):
        # Ensure the value is valid
        allowed_statuses = [status for status in OrderStatus.values]  # Example: ['PENDING', 'PROCESSING', 'SHIPPED', 'DELIVERED', 'CANCELLED']
        if value not in allowed_statuses:
            raise serializers.ValidationError(
                f"Invalid order status. Allowed values: {', '.join(allowed_statuses)}"
            )
        return value




# buy now serializers
class BuyNowSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(default=1)
    payment_method = serializers.ChoiceField(choices=[("COD", "Cash on Delivery"), ("ONLINE", "Online Payment")])
    shipping_id = serializers.IntegerField(required=False)
    coupon_code = serializers.CharField(required=False, allow_blank=True)

    # Shipping fields if no shipping_id is provided
    full_name = serializers.CharField(required=False)
    phone_no = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    street_address = serializers.CharField(required=False)
    apartment = serializers.CharField(required=False, allow_blank=True)
    floor = serializers.CharField(required=False, allow_blank=True)
    city = serializers.CharField(required=False)
    zipcode = serializers.CharField(required=False)

    def validate_product_id(self, value):
        if not Products.objects.filter(id=value).exists():
            raise serializers.ValidationError("Product does not exist.")
        return value

    @transaction.atomic

    def create(self, validated_data):
        request = self.context.get("request")
        user = request.user
        product = Products.objects.select_for_update().get(id=validated_data["product_id"])
        quantity = validated_data.get("quantity", 1)

        # Step 0: Validate stock
        if quantity > product.available_stock:
            raise serializers.ValidationError(f"Only {product.available_stock} items available.")

        # Step 1: Handle shipping
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

        # Step 2: Determine product price
        product_price = getattr(product, "discounted_price", product.price)

        total_amount = Decimal(product.price) * quantity         
        discounted_amount = Decimal(product_price) * quantity    
        final_amount = discounted_amount                         

        # Step 3: Apply coupon if provided
        coupon_code = validated_data.get("coupon_code")
        coupon = None
        if coupon_code:
            try:
                coupon = Coupon.objects.get(code=coupon_code, active=True)
                now = timezone.now()
                if coupon.valid_from and coupon.valid_from > now:
                    raise serializers.ValidationError("Coupon is not yet valid.")
                if coupon.valid_to and coupon.valid_to < now:
                    raise serializers.ValidationError("Coupon has expired.")

                # Coupon base amount logic
                base_amount_for_coupon = discounted_amount if getattr(product, "discounted_price", None) else total_amount

                if coupon.discount_type == "percentage":
                    discount_amount = (base_amount_for_coupon * Decimal(coupon.discount_value)) / Decimal("100")
                else:
                    discount_amount = Decimal(coupon.discount_value)

                final_amount = base_amount_for_coupon - discount_amount
                final_amount = max(final_amount, Decimal("0.00"))

                # Record coupon redemption
                CouponRedemption.objects.get_or_create(coupon=coupon, user=user)

            except Coupon.DoesNotExist:
                raise serializers.ValidationError("Invalid coupon code.")

        if final_amount <= 0:
            raise serializers.ValidationError("Final amount is zero or negative. Cannot proceed to checkout.")

        # Step 4: Determine payment and order statuses
        payment_method = validated_data["payment_method"]
        if payment_method == PaymentMethod.ONLINE:
            is_paid = False
            payment_status = PaymentStatus.PENDING
            order_status = OrderStatus.PENDING

        elif payment_method == PaymentMethod.COD:
            is_paid = False
            payment_status = PaymentStatus.PENDING
            order_status = OrderStatus.PROCESSING
        else:
            is_paid = False
            payment_status = "pending"
            order_status = "PENDING"

        # Step 5: Create order
        order = Order.objects.create(
            user=user,
            shipping_address=shipping,
            total_amount=total_amount,
            discounted_amount=discounted_amount,
            final_amount=final_amount,
            payment_method=payment_method,
            is_paid=is_paid,
            payment_status=payment_status,
            order_status=order_status,
            coupon=coupon
        )

        # Step 6: Create OrderItem
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            price=product_price,
        )

        # Step 7: Reduce stock
        product.available_stock -= quantity
        product.save(update_fields=["available_stock"])

        # Step 8: Notifications
        # Notification.objects.create(
        #     user=user,
        #     title="Order Placed",
        #     message=f"Your order {order.order_number} has been placed successfully.",
        # )

        # admins = User.objects.filter(is_staff=True)
        # for admin in admins:
        #     Notification.objects.create(
        #         user=admin,
        #         title="New Order",
        #         message=f"New order {order.order_number} placed by {user.email}.",
        #     )

        return order


