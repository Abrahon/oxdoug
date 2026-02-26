# apps/cart/utils.py
from .models import CartItem

def merge_cart_on_login(user, session_key):
    """
    Merge guest cart items into user's cart after login.

    - `user` : authenticated user object
    - `session_key` : session key of the guest cart
    """
    guest_items = CartItem.objects.filter(session_key=session_key, user__isnull=True)
    for item in guest_items:
        cart_item, created = CartItem.objects.get_or_create(
            user=user,
            product=item.product,
            defaults={'quantity': item.quantity}
        )
        if not created:
            # Add quantities, but do not exceed available stock
            cart_item.quantity = min(cart_item.quantity + item.quantity, item.product.available_stock)
            cart_item.save()
        # Delete guest cart item
        item.delete()