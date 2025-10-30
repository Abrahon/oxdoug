
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

logger = logging.getLogger(__name__)
stripe.api_key = settings.STRIPE_SECRET_KEY


class CreateCheckoutSessionView(APIView):
    permission_classes = [IsAuthenticated]  

    def post(self, request, *args, **kwargs):
        order_id = request.data.get("order_id")
        if not order_id:
            return Response({"error": "order_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

        # ✅ Use the discounted or final amount if available
        payable_amount = (
            order.final_amount
            if hasattr(order, "final_amount") and order.final_amount
            else order.discounted_amount
            if hasattr(order, "discounted_amount") and order.discounted_amount
            else order.total_amount
        )

        if not payable_amount or payable_amount <= 0:
            return Response({"error": "Order amount must be greater than 0"}, status=status.HTTP_400_BAD_REQUEST)

        amount_cents = int(payable_amount * 100)
        print("💳 Final payable amount in cents:", amount_cents)
        logger.info(f"Stripe Checkout: Creating session for Order {order.order_number} - {payable_amount} USD ({amount_cents} cents)")

        try:
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[{
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": f"Order {order.order_number}"
                        },
                        # ✅ Use final amount instead of total_amount
                        "unit_amount": amount_cents,
                    },
                    "quantity": 1,
                }],
                mode="payment",
                success_url=f"http://localhost:3500/cart?order_id={order_id}&session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=f"http://localhost:3500/cart?order_id={order_id}",
            )

            order.stripe_checkout_session_id = session.id
            order.save(update_fields=["stripe_checkout_session_id"])

            return Response({
                "id": session.id,
                "url": session.url,
            }, status=200)

        except Exception as e:
            logger.error(f"Stripe Checkout session creation failed: {str(e)}")
            return Response(
                {"error": "Stripe session creation failed, please try again later."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(APIView):
    authentication_classes = []  # Public webhook
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

                    order.save(update_fields=["is_paid", "payment_status", "order_status"])
                    logger.info(f"✅ Order {order.order_number} marked as PAID and PROCESSING")

            except Order.DoesNotExist:
                logger.error(f"Stripe session ID {session_id} not linked to any order")

        return HttpResponse(status=200)
