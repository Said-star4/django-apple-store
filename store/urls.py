from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    # Main pages
    path('', views.HomeView.as_view(), name='home'),
    path('catalog/', views.CatalogView.as_view(), name='catalog'),
    path('product/<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('comparison/', views.ComparisonView.as_view(), name='comparison'),
    path('accessories/', views.AccessoriesView.as_view(), name='accessories'),
    path('news/', views.NewsListView.as_view(), name='news_list'),
    path('news/<slug:slug>/', views.NewsDetailView.as_view(), name='news_detail'),
    path('faq/', views.FAQView.as_view(), name='faq'),
    path('contacts/', views.ContactsView.as_view(), name='contacts'),
    path('about/', views.AboutView.as_view(), name='about'),
    
    # Cart
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:item_id>/', views.update_cart_item, name='update_cart'),
    
    # Checkout and Orders
    path('checkout/', views.checkout_view, name='checkout'),
    path('order-confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
    path('orders/', views.orders_list, name='orders_list'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    
    # Wishlist
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('wishlist/add/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/', views.remove_from_wishlist, name='remove_from_wishlist'),
    
    # Reviews
    path('product/<int:product_id>/review/', views.add_review, name='add_review'),
]
