def cart_context(request):
    """Context processor for cart data"""
    if request.user.is_authenticated:
        try:
            cart = request.user.cart
            return {'cart': cart}
        except:
            return {'cart': None}
    return {'cart': None}


def wishlist_context(request):
    """Context processor for wishlist data"""
    if request.user.is_authenticated:
        try:
            wishlist = request.user.wishlist
            return {'wishlist': wishlist}
        except:
            return {'wishlist': None}
    return {'wishlist': None}
