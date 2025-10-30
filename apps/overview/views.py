from datetime import datetime, timedelta, date
from decimal import Decimal
from collections import Counter
from django.utils.timezone import now
from django.db.models import Sum, Count, F, Min, Q
from django.db.models.functions import TruncWeek, TruncMonth, TruncYear
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from apps.accounts.models import User
from apps.orders.models import Order, OrderItem, OrderStatus
from apps.reviews.models import Review
from apps.products.models import Products
from django.db.models import Sum, Count, Avg, DecimalField
from django.db.models.functions import Coalesce, TruncWeek, TruncMonth, TruncYear


class DashboardOverview(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        try:
            period = request.query_params.get("period", "weekly").lower()
            current_time = now()

            # Base Querysets
            orders = Order.objects.all()
            order_items = OrderItem.objects.select_related("product").all()
            users = User.objects.filter(is_staff=False)

            # Total metrics
            total_stock = Products.objects.aggregate(total=Sum("available_stock"))["total"] or 0
            total_sales = order_items.count()
            # total_new_customers = users.count()
            total_orders_pending = orders.filter(order_status=OrderStatus.PENDING).count()
            total_orders_completed = orders.filter(order_status=OrderStatus.DELIVERED).count()

            # Choose truncate function
            if period == "weekly":
                truncate_func = TruncWeek
                periods = 10
            elif period == "monthly":
                truncate_func = TruncMonth
                periods = 12
            elif period == "yearly":
                truncate_func = TruncYear
                periods = 5
            else:
                return Response(
                    {"error": "Invalid period. Use weekly, monthly, or yearly."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Revenue grouped by period
            revenue_data = (
                orders.annotate(period=truncate_func("created_at"))
                .values("period")
                .annotate(total_revenue=Sum("final_amount"))
                .order_by("period")
            )
            revenue_map = {d["period"].date(): d["total_revenue"] for d in revenue_data}

            # Completed orders grouped by period
            completed_data = (
                orders.filter(order_status=OrderStatus.DELIVERED)
                .annotate(period=truncate_func("created_at"))
                .values("period")
                .annotate(completed_orders=Count("id"))
                .order_by("period")
            )
            completed_map = {d["period"].date(): d["completed_orders"] for d in completed_data}

            # --- Build trend lists ---
            revenue_trend = []
           

            for i in range(periods):
                if period == "weekly":
                    bucket_start = current_time - timedelta(days=i * 7)
                    bucket_start = bucket_start - timedelta(days=bucket_start.weekday())
                    display_period = bucket_start.strftime("%Y-%m-%d")

                elif period == "monthly":
                    # ✅ Fixed month/year calculation
                    total_month_index = current_time.year * 12 + (current_time.month - 1) - i
                    year = total_month_index // 12
                    month = (total_month_index % 12) + 1
                    bucket_start = current_time.replace(year=year, month=month, day=1)
                    display_period = bucket_start.strftime("%Y-%m")

                elif period == "yearly":
                    year = current_time.year - i
                    bucket_start = current_time.replace(year=year, month=1, day=1)
                    display_period = str(year)

                key = bucket_start.date()
                revenue_trend.append({
                    "period": display_period,
                    "total_revenue": float(revenue_map.get(key, 0)),
                    "orders_completed": int(completed_map.get(key, 0)),
                })
             
            # Recent activity
            # recent_reviews = Review.objects.order_by("-created_at")[:5].values(
            #     "id", "product__title", "user__name", "user__email", "rating", "comment", "created_at"
            # )
            recent_orders = orders.order_by("-created_at")[:5].values(
                "id", "order_number", "user__name", "user__email", "final_amount", "order_status", "created_at"
            )

            # Best-selling products
            # best_selling_products = (
            #     OrderItem.objects.values("product__id", "product__title")
            #     .annotate(total_sold=Sum("quantity"))
            #     .order_by("-total_sold")[:5]
            # )

            response_data = {
                "total_stock": total_stock,
                "total_order": total_sales,
                "total_orders_pending": total_orders_pending,
                "total_orders_completed": total_orders_completed,
                "revenue_trend": revenue_trend[::-1],
                "recent_activity": {
                    "recent_orders": list(recent_orders),
                },
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
