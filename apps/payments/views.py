
import logging
import stripe
from django.conf import settings
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.orders.models import Order
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.permissions import IsAuthenticated
from datetime import timedelta
from django.utils import timezone
# from b2c.orders.models import Order, Notification
# from apps.checkout.models import  ShippingStatusChoices

logger = logging.getLogger(__name__)
stripe.api_key = settings.STRIPE_SECRET_KEY


class CreateCheckoutSessionView(APIView):
    permission_classes = [IsAuthenticated]  # Only authenticated users can pay

    def post(self, request, *args, **kwargs):
        order_id = request.data.get("order_id")
        if not order_id:
            return Response({"error": "order_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

        if not order.total_amount or order.total_amount <= 0:
            return Response({"error": "Order amount must be greater than 0"}, status=status.HTTP_400_BAD_REQUEST)

        amount_cents = int(order.total_amount * 100)
        print("final amount", amount_cents)
        logger.info(f"Stripe Checkout: Creating session for Order {order.order_number} - {order.total_amount} ({amount_cents} cents)")

        try:
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[{
                    "price_data": {
                        "currency": "usd",  
                        "product_data": {
                            "name": f"Order {order.order_number}"
                        },
                        "unit_amount": amount_cents,
                    },
                    "quantity": 1,
                }],
                mode="payment",
                success_url=f"http://localhost:3000/cart?order_id={order_id}&session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=f"http://localhost:3000/cart?order_id={order_id}",

            )

            order.stripe_checkout_session_id = session.id
            order.save(update_fields=["stripe_checkout_session_id"])

            # ✅ Removed final_amount from the response
            return Response({
                "id": session.id,
                "url": session.url,
            }, status=200)

        except Exception as e:
            logger.error(f"Stripe Checkout session creation failed: {str(e)}")
            return Response({"error": "Stripe session creation failed, please try again later."},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)



# webhook
@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(APIView):
    authentication_classes = []  # public webhook
    permission_classes = []

    def post(self, request, *args, **kwargs):
        payload = request.body
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except stripe.error.SignatureVerificationError:
            return HttpResponse(status=400)
        except Exception as e:
            logger.error(f"Stripe webhook error: {str(e)}")
            return HttpResponse(status=400)

        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            session_id = session.get("id")

            try:
                order = Order.objects.get(stripe_checkout_session_id=session_id)

                
                 # ✅ Avoid double processing
                if not order.is_paid:
                    order.is_paid = True
                    order.payment_status = "paid"          
                    order.order_status = "PROCESSING"      

                    # ✅ Save everything in one call
                    order.save(
                        update_fields=[
                            "is_paid",
                            "payment_status",
                            "order_status",
                            # "status",
                            "estimated_delivery",
                        ]
                    )

                 
                    # logger.info(f"✅ Order {order.id} marked as SHIPPED after payment.")

            except Order.DoesNotExist:
                logger.error(f"Stripe session ID {session_id} not linked to any order")

        return HttpResponse(status=200)
