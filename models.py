from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=50, help_text="FontAwesome or emoji icon class")
    image = models.URLField(max_length=500, blank=True, null=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"

class Restaurant(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    image = models.URLField(max_length=500)
    banner_image = models.URLField(max_length=500, blank=True, null=True)
    rating = models.FloatField(default=4.5)
    reviews_count = models.IntegerField(default=120)
    cuisine = models.CharField(max_length=200, help_text="Comma-separated cuisines")
    delivery_time = models.CharField(max_length=50, default="25-35 min")
    delivery_fee = models.DecimalField(max_digits=6, decimal_places=2, default=30.00)
    price_for_two = models.DecimalField(max_digits=8, decimal_places=2, default=400.00)
    address = models.TextField(default="Downtown Central Market")
    is_featured = models.BooleanField(default=True)
    is_open = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class MenuItem(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='menu_items')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='menu_items')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    is_veg = models.BooleanField(default=True)
    is_vegan = models.BooleanField(default=False)
    is_bestseller = models.BooleanField(default=False)
    rating = models.FloatField(default=4.6)
    prep_time = models.CharField(max_length=50, default="15-20 min")
    image = models.URLField(max_length=500)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - {self.restaurant.name}"

class Address(models.Model):
    ADDRESS_TYPES = (
        ('HOME', 'Home'),
        ('WORK', 'Work'),
        ('OTHER', 'Other'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    title = models.CharField(max_length=50, choices=ADDRESS_TYPES, default='HOME')
    full_address = models.TextField()
    landmark = models.CharField(max_length=200, blank=True)
    lat = models.FloatField(default=28.6139)
    lng = models.FloatField(default=77.2090)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.title}"

class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_percent = models.IntegerField(default=20)
    max_discount = models.DecimalField(max_digits=8, decimal_places=2, default=100.00)
    min_order_value = models.DecimalField(max_digits=8, decimal_places=2, default=299.00)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.code

class Order(models.Model):
    STATUS_CHOICES = (
        ('CONFIRMED', 'Order Confirmed'),
        ('PREPARING', 'Preparing Food'),
        ('READY', 'Ready for Pickup'),
        ('OUT_FOR_DELIVERY', 'Out for Delivery'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    )

    PAYMENT_METHODS = (
        ('UPI', 'UPI Payment'),
        ('CARD', 'Credit/Debit Card'),
        ('NETBANKING', 'Net Banking'),
        ('WALLET', 'Digital Wallet'),
        ('COD', 'Cash on Delivery'),
    )

    order_id = models.CharField(max_length=50, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', null=True, blank=True)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='orders')
    delivery_address = models.TextField()
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='CONFIRMED')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='UPI')
    payment_status = models.BooleanField(default=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_charge = models.DecimalField(max_digits=6, decimal_places=2, default=30.00)
    tax = models.DecimalField(max_digits=8, decimal_places=2, default=25.00)
    discount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    estimated_delivery = models.CharField(max_length=50, default="30 mins")

    def __str__(self):
        return f"Order #{self.order_id} - {self.status}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.quantity}x {self.menu_item.name}"

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='reviews')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.SET_NULL, null=True, blank=True)
    rating = models.IntegerField(default=5)
    comment = models.TextField()
    image = models.URLField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user.username} for {self.restaurant.name}"

class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist')
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, null=True, blank=True)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"Wishlist item for {self.user.username}"
