
from django.contrib import admin
from .models import Category, Restaurant, MenuItem, Address, Coupon, Order, OrderItem, Review, Wishlist

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'icon')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('name', 'cuisine', 'rating', 'delivery_time', 'price_for_two', 'is_open', 'is_featured')
    list_filter = ('is_open', 'is_featured')
    search_fields = ('name', 'cuisine')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'restaurant', 'category', 'price', 'is_veg', 'is_bestseller', 'is_available')
    list_filter = ('is_veg', 'is_vegan', 'is_bestseller', 'is_available', 'category')
    search_fields = ('name', 'restaurant__name')

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_percent', 'max_discount', 'min_order_value', 'is_active')

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'user', 'restaurant', 'status', 'total_amount', 'created_at')
    list_filter = ('status', 'payment_method')
    search_fields = ('order_id', 'user__username', 'restaurant__name')
    inlines = [OrderItemInline]

admin.site.register(Address)
admin.site.register(Review)
admin.site.register(Wishlist)
