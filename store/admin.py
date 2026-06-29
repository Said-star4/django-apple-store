from django.contrib import admin
from .models import (
    Category, iPhone, iPhone_Image, Review, Cart, CartItem,
    Order, OrderItem, Wishlist, News, Comparison
)


class iPhone_ImageInline(admin.TabularInline):
    model = iPhone_Image
    extra = 1
    fields = ['image', 'alt_text', 'is_main', 'order']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(iPhone)
class iPhoneAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'discount_price', 'stock_quantity', 'is_active', 'is_featured', 'rating']
    list_filter = ['is_active', 'is_featured', 'is_new', 'category', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [iPhone_ImageInline]
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'slug', 'category', 'description', 'short_description')
        }),
        ('Цены и склад', {
            'fields': ('price', 'discount_price', 'stock_quantity')
        }),
        ('Конфигурации', {
            'fields': ('storage_options', 'default_storage', 'color_options', 'default_color')
        }),
        ('Технические характеристики', {
            'fields': (
                'processor', 'screen_size', 'screen_resolution', 'rear_camera',
                'front_camera', 'battery_capacity', 'ram', 'operating_system'
            )
        }),
        ('Физические характеристики', {
            'fields': ('weight', 'dimensions', 'water_resistance', 'features')
        }),
        ('Изображения', {
            'fields': ('main_image',)
        }),
        ('Отзывы и рейтинг', {
            'fields': ('rating', 'num_reviews')
        }),
        ('Статус', {
            'fields': ('is_active', 'is_featured', 'is_new')
        }),
    )


@admin.register(iPhone_Image)
class iPhoneImageAdmin(admin.ModelAdmin):
    list_display = ['iphone', 'is_main', 'order']
    list_filter = ['iphone', 'is_main']
    search_fields = ['iphone__name']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'iphone', 'rating', 'created_at']
    list_filter = ['rating', 'created_at', 'iphone']
    search_fields = ['user__username', 'iphone__name', 'title']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at', 'updated_at']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['cart', 'iphone', 'quantity', 'storage', 'color']
    list_filter = ['cart', 'storage', 'color']
    search_fields = ['iphone__name', 'cart__user__username']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'total_price', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['order_number', 'user__username', 'email']
    readonly_fields = ['order_number', 'created_at', 'updated_at']
    fieldsets = (
        ('Основная информация', {
            'fields': ('order_number', 'user', 'status')
        }),
        ('Информация о доставке', {
            'fields': ('first_name', 'last_name', 'email', 'phone', 'address', 'city', 'zip_code', 'country')
        }),
        ('Финансовая информация', {
            'fields': ('total_price', 'shipping_cost')
        }),
        ('Сроки', {
            'fields': ('created_at', 'updated_at', 'shipped_at', 'delivered_at')
        }),
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'iphone', 'quantity', 'storage', 'color']
    list_filter = ['order', 'storage', 'color']
    search_fields = ['iphone__name', 'order__order_number']


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'is_published', 'published_at']
    list_filter = ['is_published', 'published_at']
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Comparison)
class ComparisonAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username']
