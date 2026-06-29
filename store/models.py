from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class Category(models.Model):
    """iPhone Model Categories"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class iPhone(models.Model):
    """iPhone Product Model"""
    STORAGE_CHOICES = [
        ('64GB', '64GB'),
        ('128GB', '128GB'),
        ('256GB', '256GB'),
        ('512GB', '512GB'),
        ('1TB', '1TB'),
    ]

    COLOR_CHOICES = [
        ('Black', 'Чёрный'),
        ('White', 'Белый'),
        ('Silver', 'Серебристый'),
        ('Gold', 'Золотой'),
        ('Rose Gold', 'Розовое золото'),
        ('Midnight', 'Полночь'),
        ('Starlight', 'Звёздный свет'),
        ('Deep Purple', 'Глубокий фиолет'),
        ('Blue', 'Синий'),
        ('Green', 'Зелёный'),
        ('Red', 'Красный'),
        ('Titanium Gray', 'Титановый серый'),
        ('Titanium Black', 'Титановый чёрный'),
        ('Titanium White', 'Титановый белый'),
        ('Titanium Natural', 'Титановый естественный'),
    ]

    # Basic info
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='iphones')
    
    # Description
    description = models.TextField()
    short_description = models.CharField(max_length=255)
    
    # Pricing and Stock
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)])
    stock_quantity = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    
    # Specifications
    storage_options = models.CharField(max_length=255, help_text='Comma separated storage options')
    default_storage = models.CharField(max_length=10, choices=STORAGE_CHOICES, default='128GB')
    color_options = models.CharField(max_length=255, help_text='Comma separated color options')
    default_color = models.CharField(max_length=50, choices=COLOR_CHOICES, default='Black')
    
    processor = models.CharField(max_length=100)
    screen_size = models.CharField(max_length=50)
    screen_resolution = models.CharField(max_length=100)
    rear_camera = models.CharField(max_length=100)
    front_camera = models.CharField(max_length=100)
    battery_capacity = models.CharField(max_length=100)
    ram = models.CharField(max_length=50)
    operating_system = models.CharField(max_length=50, default='iOS')
    
    # Features
    features = models.TextField(help_text='Key features separated by newline')
    weight = models.CharField(max_length=50)
    dimensions = models.CharField(max_length=100)
    water_resistance = models.CharField(max_length=50)
    
    # Images
    main_image = models.ImageField(upload_to='iphones/main/')
    
    # Ratings and Reviews
    rating = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(5)])
    num_reviews = models.IntegerField(default=0)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    is_new = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active']),
            models.Index(fields=['price']),
        ]

    def __str__(self):
        return self.name

    @property
    def get_discount_percent(self):
        if self.discount_price:
            return int((1 - self.discount_price / self.price) * 100)
        return 0

    @property
    def get_current_price(self):
        return self.discount_price if self.discount_price else self.price

    @property
    def is_in_stock(self):
        return self.stock_quantity > 0


class iPhone_Image(models.Model):
    """Additional iPhone Images"""
    iphone = models.ForeignKey(iPhone, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='iphones/images/')
    alt_text = models.CharField(max_length=255, blank=True)
    is_main = models.BooleanField(default=False)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.iphone.name} - Image {self.order}"


class Review(models.Model):
    """Product Reviews"""
    iphone = models.ForeignKey(iPhone, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    title = models.CharField(max_length=200)
    text = models.TextField()
    helpful_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('iphone', 'user')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.iphone.name}"


class Cart(models.Model):
    """Shopping Cart"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart - {self.user.username}"

    @property
    def get_total_price(self):
        return sum(item.get_total_price for item in self.items.all())

    @property
    def get_total_items(self):
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    """Items in Shopping Cart"""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    iphone = models.ForeignKey(iPhone, on_delete=models.CASCADE)
    storage = models.CharField(max_length=10, default='128GB')
    color = models.CharField(max_length=50, default='Black')
    quantity = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    price = models.DecimalField(max_digits=10, decimal_places=2)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('cart', 'iphone', 'storage', 'color')

    def __str__(self):
        return f"{self.quantity}x {self.iphone.name}"

    @property
    def get_total_price(self):
        return self.quantity * self.price


class Order(models.Model):
    """Customer Orders"""
    STATUS_CHOICES = [
        ('Pending', 'В ожидании'),
        ('Processing', 'Обработка'),
        ('Shipped', 'Отправлено'),
        ('Delivered', 'Доставлено'),
        ('Cancelled', 'Отменено'),
        ('Returned', 'Возврат'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='orders')
    order_number = models.CharField(max_length=50, unique=True)
    
    # Shipping info
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    
    # Order info
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order {self.order_number}"


class OrderItem(models.Model):
    """Items in an Order"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    iphone = models.ForeignKey(iPhone, on_delete=models.SET_NULL, null=True)
    storage = models.CharField(max_length=10)
    color = models.CharField(max_length=50)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity}x {self.iphone.name} in Order {self.order.order_number}"


class Wishlist(models.Model):
    """User Wishlist"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wishlist')
    iphones = models.ManyToManyField(iPhone, related_name='wishlist_users')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Wishlist - {self.user.username}"


class News(models.Model):
    """Apple News/Blog Posts"""
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    content = models.TextField()
    excerpt = models.CharField(max_length=500)
    featured_image = models.ImageField(upload_to='news/')
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name_plural = 'News'
        ordering = ['-published_at']

    def __str__(self):
        return self.title


class Comparison(models.Model):
    """iPhone Comparison"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comparisons', null=True, blank=True)
    iphones = models.ManyToManyField(iPhone)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Comparisons'

    def __str__(self):
        return f"Comparison {self.id}"
