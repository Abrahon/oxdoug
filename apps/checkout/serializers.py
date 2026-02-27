

from rest_framework import serializers
from .models import Shipping
from apps.orders.models import Order

class ShippingSerializer(serializers.ModelSerializer):
    shipping_id = serializers.IntegerField(source='id', read_only=True)
    order_id = serializers.PrimaryKeyRelatedField(
        queryset=Order.objects.all(),
        source='order',
        write_only=True,
        required=False
    )

    class Meta:
        model = Shipping
        fields = [
            'shipping_id', 'user', 'session_key', 'full_name', 'phone_no', 'email', 'street_address',
            'apartment', 'floor', 'city', 'zipcode', 'order_id', 'order', 'is_default', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'session_key', 'order', 'created_at', 'updated_at']

    def create(self, validated_data):
        request = self.context['request']
        if request.user.is_authenticated:
            # Authenticated user
            return Shipping.objects.create(user=request.user, **validated_data)
        else:
            # Guest user
            session_key = request.session.session_key
            if not session_key:
                request.session.create()
                session_key = request.session.session_key
            return Shipping.objects.create(session_key=session_key, **validated_data)
