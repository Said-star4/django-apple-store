from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseNotFound, HttpResponseServerError
from django.db.models import Q, Avg
from django.core.paginator import Paginator
from django.utils.text import slugify
from django.views.decorators.http import require_http_methods
from decimal import Decimal
import json
import uuid

from .models import (
    iPhone, Category, Review, Cart, CartItem, Order, OrderItem,
    Wishlist, News, Comparison
)
from .forms import ReviewForm, OrderForm, SearchForm, FilterForm


def handler404(request, exception):
    """Custom 404 error handler"""
    return render(request, 'store/404.html', status=404)


def handler500(request):
    """Custom 500 error handler"""
    return render(request, 'store/500.html', status=500)


class HomeView(View):
    """Homepage with featured products and news"""
    def get(self, request):
        featured_iphones = iPhone.objects.filter(is_featured=True, is_active=True)[:6]
        new_iphones = iPhone.objects.filter(is_new=True, is_active=True)[:6]
        latest_news = News.objects.filter(is_published=True)[:3]
        
        context = {
            'featured_iphones': featured_iphones,
            'new_iphones': new_iphones,
            'latest_news': latest_news,
        }
        return render(request, 'store/index.html', context)


class CatalogView(View):
    """iPhone catalog with filtering and searching"""
    def get(self, request):
        iphones = iPhone.objects.filter(is_active=True)
        categories = Category.objects.all()
        
        # Search
        search_query = request.GET.get('search', '')
        if search_query:
            iphones = iphones.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        
        # Category filter
        category_id = request.GET.get('category')
        if category_id:
            iphones = iphones.filter(category_id=category_id)
        
        # Price filter
        min_price = request.GET.get('min_price')
        max_price = request.GET.get('max_price')
        if min_price:
            iphones = iphones.filter(price__gte=min_price)
        if max_price:
            iphones = iphones.filter(price__lte=max_price)
        
        # Storage filter
        storage = request.GET.getlist('storage')
        if storage:
            q = Q()
            for s in storage:
                q |= Q(storage_options__icontains=s)
            iphones = iphones.filter(q)
        
        # Color filter
        color = request.GET.getlist('color')
        if color:
            q = Q()
            for c in color:
                q |= Q(color_options__icontains=c)
            iphones = iphones.filter(q)
        
        # Sorting
        sort_by = request.GET.get('sort', '-created_at')
        if sort_by == 'price_asc':
            iphones = iphones.order_by('price')
        elif sort_by == 'price_desc':
            iphones = iphones.order_by('-price')
        elif sort_by == 'rating':
            iphones = iphones.order_by('-rating')
        else:
            iphones = iphones.order_by('-created_at')
        
        # Pagination
        paginator = Paginator(iphones, 12)
        page_num = request.GET.get('page', 1)
        page = paginator.get_page(page_num)
        
        context = {
            'page': page,
            'categories': categories,
            'search_query': search_query,
            'sort_by': sort_by,
        }
        return render(request, 'store/catalog.html', context)


class ProductDetailView(View):
    """Detailed product page"""
    def get(self, request, slug):
        iphone = get_object_or_404(iPhone, slug=slug)
        reviews = iphone.reviews.all()
        avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
        
        # Related products
        related = iPhone.objects.filter(
            category=iphone.category,
            is_active=True
        ).exclude(id=iphone.id)[:4]
        
        form = ReviewForm()
        
        context = {
            'iphone': iphone,
            'reviews': reviews,
            'avg_rating': avg_rating,
            'related': related,
            'form': form,
            'storage_options': iphone.storage_options.split(','),
            'color_options': iphone.color_options.split(','),
        }
        return render(request, 'store/product_detail.html', context)


class ComparisonView(View):
    """iPhone comparison page"""
    def get(self, request):
        comparison_ids = request.session.get('comparison_ids', [])
        iphones = iPhone.objects.filter(id__in=comparison_ids)
        
        context = {
            'iphones': iphones,
        }
        return render(request, 'store/comparison.html', context)


class AccessoriesView(View):
    """Accessories page (placeholder)"""
    def get(self, request):
        return render(request, 'store/accessories.html')


class NewsListView(View):
    """News/Blog listing"""
    def get(self, request):
        news = News.objects.filter(is_published=True).order_by('-published_at')
        
        paginator = Paginator(news, 9)
        page_num = request.GET.get('page', 1)
        page = paginator.get_page(page_num)
        
        context = {
            'page': page,
        }
        return render(request, 'store/news_list.html', context)


class NewsDetailView(View):
    """News/Blog detail page"""
    def get(self, request, slug):
        news = get_object_or_404(News, slug=slug)
        related_news = News.objects.filter(
            is_published=True
        ).exclude(id=news.id)[:3]
        
        context = {
            'news': news,
            'related_news': related_news,
        }
        return render(request, 'store/news_detail.html', context)


class FAQView(View):
    """FAQ page"""
    def get(self, request):
        return render(request, 'store/faq.html')


class ContactsView(View):
    """Contacts page"""
    def get(self, request):
        return render(request, 'store/contacts.html')


class AboutView(View):
    """About page"""
    def get(self, request):
        return render(request, 'store/about.html')


@login_required
def cart_view(request):
    """Shopping cart view"""
    try:
        cart = request.user.cart
    except Cart.DoesNotExist:
        cart = Cart.objects.create(user=request.user)
    
    context = {
        'cart': cart,
    }
    return render(request, 'store/cart.html', context)


@login_required
@require_http_methods(["POST"])
def add_to_cart(request):
    """AJAX endpoint to add item to cart"""
    try:
        cart = request.user.cart
    except Cart.DoesNotExist:
        cart = Cart.objects.create(user=request.user)
    
    data = json.loads(request.body)
    iphone_id = data.get('iphone_id')
    quantity = int(data.get('quantity', 1))
    storage = data.get('storage', '128GB')
    color = data.get('color', 'Black')
    
    iphone = get_object_or_404(iPhone, id=iphone_id)
    price = iphone.get_current_price
    
    item, created = CartItem.objects.get_or_create(
        cart=cart,
        iphone=iphone,
        storage=storage,
        color=color,
        defaults={'price': price, 'quantity': quantity}
    )
    
    if not created:
        item.quantity += quantity
        item.save()
    
    return JsonResponse({
        'success': True,
        'message': 'Item added to cart',
        'cart_count': cart.get_total_items,
    })


@login_required
@require_http_methods(["POST"])
def remove_from_cart(request, item_id):
    """Remove item from cart"""
    try:
        cart = request.user.cart
        item = cart.items.get(id=item_id)
        item.delete()
        return JsonResponse({
            'success': True,
            'cart_count': cart.get_total_items,
        })
    except:
        return JsonResponse({'success': False}, status=400)


@login_required
@require_http_methods(["POST"])
def update_cart_item(request, item_id):
    """Update cart item quantity"""
    try:
        cart = request.user.cart
        item = cart.items.get(id=item_id)
        quantity = int(request.POST.get('quantity', 1))
        
        if quantity > 0:
            item.quantity = quantity
            item.save()
        else:
            item.delete()
        
        return JsonResponse({
            'success': True,
            'cart_total': str(cart.get_total_price),
        })
    except:
        return JsonResponse({'success': False}, status=400)


@login_required
def checkout_view(request):
    """Checkout page"""
    try:
        cart = request.user.cart
    except Cart.DoesNotExist:
        return redirect('store:cart')
    
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
            order.total_price = cart.get_total_price
            order.save()
            
            # Create order items
            for cart_item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    iphone=cart_item.iphone,
                    storage=cart_item.storage,
                    color=cart_item.color,
                    quantity=cart_item.quantity,
                    price=cart_item.price,
                )
            
            # Clear cart
            cart.items.all().delete()
            
            return redirect('store:order_confirmation', order_id=order.id)
    else:
        form = OrderForm()
    
    context = {
        'cart': cart,
        'form': form,
    }
    return render(request, 'store/checkout.html', context)


@login_required
def order_confirmation(request, order_id):
    """Order confirmation page"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    context = {'order': order}
    return render(request, 'store/order_confirmation.html', context)


@login_required
def orders_list(request):
    """User orders history"""
    orders = request.user.orders.all()
    
    paginator = Paginator(orders, 10)
    page_num = request.GET.get('page', 1)
    page = paginator.get_page(page_num)
    
    context = {'page': page}
    return render(request, 'store/orders_list.html', context)


@login_required
def order_detail(request, order_id):
    """Order detail page"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    context = {'order': order}
    return render(request, 'store/order_detail.html', context)


@login_required
def wishlist_view(request):
    """User wishlist"""
    try:
        wishlist = request.user.wishlist
    except Wishlist.DoesNotExist:
        wishlist = Wishlist.objects.create(user=request.user)
    
    context = {'wishlist': wishlist}
    return render(request, 'store/wishlist.html', context)


@login_required
@require_http_methods(["POST"])
def add_to_wishlist(request):
    """AJAX endpoint to add item to wishlist"""
    try:
        wishlist = request.user.wishlist
    except Wishlist.DoesNotExist:
        wishlist = Wishlist.objects.create(user=request.user)
    
    data = json.loads(request.body)
    iphone_id = data.get('iphone_id')
    iphone = get_object_or_404(iPhone, id=iphone_id)
    
    wishlist.iphones.add(iphone)
    
    return JsonResponse({
        'success': True,
        'message': 'Added to wishlist',
        'is_in_wishlist': True,
    })


@login_required
@require_http_methods(["POST"])
def remove_from_wishlist(request):
    """Remove from wishlist"""
    try:
        wishlist = request.user.wishlist
        data = json.loads(request.body)
        iphone_id = data.get('iphone_id')
        iphone = get_object_or_404(iPhone, id=iphone_id)
        wishlist.iphones.remove(iphone)
        
        return JsonResponse({
            'success': True,
            'is_in_wishlist': False,
        })
    except:
        return JsonResponse({'success': False}, status=400)


@login_required
@require_http_methods(["POST"])
def add_review(request, product_id):
    """Add product review"""
    iphone = get_object_or_404(iPhone, id=product_id)
    form = ReviewForm(request.POST)
    
    if form.is_valid():
        review = form.save(commit=False)
        review.user = request.user
        review.iphone = iphone
        review.save()
        
        # Update iPhone rating
        reviews = iphone.reviews.all()
        avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
        iphone.rating = avg_rating
        iphone.num_reviews = reviews.count()
        iphone.save()
        
        return redirect('store:product_detail', slug=iphone.slug)
    
    return redirect('store:product_detail', slug=iphone.slug)
