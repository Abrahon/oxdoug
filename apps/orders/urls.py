from django.urls import path
from .views import (
    PlaceOrderView,
    BuyNowView,
    OrderDetailView,
    UserOrderHistoryView,
    AdminOrderListView,
    AdminUpdateOrderStatusView,
    OrderDeleteView,
    OrderListView,
    UserOrderDetailView,
    CancelOrderView
)

urlpatterns = [
    # ---------------- User URLs ----------------
    path("orders/", OrderListView.as_view(), name="order-list"),
    path('order/place/', PlaceOrderView.as_view(), name='place-order'),
    path('buy-now/', BuyNowView.as_view(), name='buy-now'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    # path('orders/history/', UserOrderHistoryView.as_view(), name='user-order-history'),
    path("my-orders/", UserOrderHistoryView.as_view(), name="user-order-history"),
    path("my-orders/<int:id>/", UserOrderDetailView.as_view(), name="user-order-detail"),
    path("my-orders/<int:order_id>/cancel/", CancelOrderView.as_view(), name="cancel-order"),

    # ---------------- Admin URLs ----------------
    path('admin/orders/', AdminOrderListView.as_view(), name='admin-order-list'),
    path('admin/orders/<int:id>/update-status/', AdminUpdateOrderStatusView.as_view(), name='admin-update-order-status'),
    path('admin/orders/<int:pk>/delete/', OrderDeleteView.as_view(), name='admin-delete-order'),
]
