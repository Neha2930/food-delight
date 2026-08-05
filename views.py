import json
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from .models import Category, Restaurant, MenuItem, Address, Coupon, Order, OrderItem, Review, Wishlist

def index_view(request):
    categories = Category.objects.all()
    featured_restaurants = Restaurant.objects.filter(is_featured=True)[:6]
    popular_dishes = MenuItem.objects.filter(is_bestseller=True)[:8]
    coupons = Coupon.objects.filter(is_active=True)

    context = {
        'categories': categories,
        'featured_restaurants': featured_restaurants,
        'popular_dishes': popular_dishes,
        'coupons': coupons,
    }
    return render(request, 'index.html', context)

def restaurant_detail_view(request, slug):
    restaurant = get_object_or_404(Restaurant, slug=slug)
    categories = Category.objects.all()
    menu_items = MenuItem.objects.filter(restaurant=restaurant)

    veg_only = request.GET.get('veg', None)
    bestseller_only = request.GET.get('bestseller', None)
    search_query = request.GET.get('q', None)

    if veg_only == 'true':
        menu_items = menu_items.filter(is_veg=True)
    if bestseller_only == 'true':
        menu_items = menu_items.filter(is_bestseller=True)
    if search_query:
        menu_items = menu_items.filter(Q(name__icontains=search_query) | Q(description__icontains=search_query))

    reviews = Review.objects.filter(restaurant=restaurant).order_by('-created_at')[:5]

    context = {
        'restaurant': restaurant,
        'categories': categories,
        'menu_items': menu_items,
        'reviews': reviews,
    }
    return render(request, 'restaurant.html', context)

def cart_checkout_view(request):
    coupons = Coupon.objects.filter(is_active=True)
    addresses = Address.objects.filter(user=request.user) if request.user.is_authenticated else []
    return render(request, 'cart_checkout.html', {'coupons': coupons, 'addresses': addresses})

def tracking_view(request, order_id=None):
    order = None
    if order_id:
        order = Order.objects.filter(order_id=order_id).first()
    context = {'order': order, 'order_id': order_id or "FD-98421"}
    return render(request, 'tracking.html', context)

def profile_view(request):
    user = request.user
    orders = Order.objects.filter(user=user).order_by('-created_at') if user.is_authenticated else []
    addresses = Address.objects.filter(user=user) if user.is_authenticated else []
    wishlist_items = Wishlist.objects.filter(user=user) if user.is_authenticated else []

    context = {
        'user_obj': user,
        'orders': orders,
        'addresses': addresses,
        'wishlist_items': wishlist_items,
    }
    return render(request, 'profile.html', context)

def admin_dashboard_view(request):
    total_orders = Order.objects.count()
    total_sales = sum([order.total_amount for order in Order.objects.all()]) if total_orders > 0 else 0
    total_restaurants = Restaurant.objects.count()
    total_items = MenuItem.objects.count()

    recent_orders = Order.objects.order_by('-created_at')[:10]
    restaurants = Restaurant.objects.all()
    menu_items = MenuItem.objects.all()[:20]
    coupons = Coupon.objects.all()

    context = {
        'total_orders': total_orders,
        'total_sales': total_sales,
        'total_restaurants': total_restaurants,
        'total_items': total_items,
        'recent_orders': recent_orders,
        'restaurants': restaurants,
        'menu_items': menu_items,
        'coupons': coupons,
    }
    return render(request, 'admin_dashboard.html', context)

# API ENDPOINTS
def api_restaurants(request):
    query = request.GET.get('q', '')
    cuisine = request.GET.get('cuisine', '')

    restaurants = Restaurant.objects.filter(is_open=True)
    if query:
        restaurants = restaurants.filter(Q(name__icontains=query) | Q(cuisine__icontains=query))
    if cuisine:
        restaurants = restaurants.filter(cuisine__icontains=cuisine)

    data = []
    for r in restaurants:
        data.append({
            'id': r.id,
            'name': r.name,
            'slug': r.slug,
            'image': r.image,
            'rating': r.rating,
            'reviews_count': r.reviews_count,
            'cuisine': r.cuisine,
            'delivery_time': r.delivery_time,
            'delivery_fee': float(r.delivery_fee),
            'price_for_two': float(r.price_for_two),
        })
    return JsonResponse({'status': 'success', 'restaurants': data})

def api_menu_items(request):
    query = request.GET.get('q', '')
    category_slug = request.GET.get('category', '')
    veg = request.GET.get('veg', '')
    bestseller = request.GET.get('bestseller', '')
    sort_by = request.GET.get('sort', '')

    items = MenuItem.objects.filter(is_available=True)

    if query:
        items = items.filter(Q(name__icontains=query) | Q(description__icontains=query))
    if category_slug:
        items = items.filter(category__slug=category_slug)
    if veg == 'true':
        items = items.filter(is_veg=True)
    if bestseller == 'true':
        items = items.filter(is_bestseller=True)

    if sort_by == 'price_low':
        items = items.order_by('price')
    elif sort_by == 'price_high':
        items = items.order_by('-price')
    elif sort_by == 'rating':
        items = items.order_by('-rating')

    data = []
    for item in items:
        data.append({
            'id': item.id,
            'name': item.name,
            'restaurant_id': item.restaurant.id,
            'restaurant_name': item.restaurant.name,
            'category': item.category.name,
            'price': float(item.price),
            'description': item.description,
            'is_veg': item.is_veg,
            'is_bestseller': item.is_bestseller,
            'rating': item.rating,
            'prep_time': item.prep_time,
            'image': item.image,
        })
    return JsonResponse({'status': 'success', 'items': data})

@csrf_exempt
def api_create_order(request):
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            items = body.get('items', [])
            address = body.get('address', '123 Main St, Central City')
            payment_method = body.get('payment_method', 'UPI')
            coupon_code = body.get('coupon', '')

            if not items:
                return JsonResponse({'status': 'error', 'message': 'Cart is empty'}, status=400)

            # Get restaurant from first item
            first_item = MenuItem.objects.get(id=items[0]['id'])
            restaurant = first_item.restaurant

            subtotal = sum([item['price'] * item['quantity'] for item in items])
            delivery_charge = 30.00
            tax = round(subtotal * 0.05, 2)
            discount = 0.00

            if coupon_code:
                coupon = Coupon.objects.filter(code=coupon_code, is_active=True).first()
                if coupon and subtotal >= float(coupon.min_order_value):
                    discount = min((subtotal * (coupon.discount_percent / 100.0)), float(coupon.max_discount))

            grand_total = subtotal + delivery_charge + tax - discount

            import random
            order_id = f"FD-{random.randint(10000, 99999)}"

            order = Order.objects.create(
                order_id=order_id,
                user=request.user if request.user.is_authenticated else None,
                restaurant=restaurant,
                delivery_address=address,
                payment_method=payment_method,
                subtotal=subtotal,
                delivery_charge=delivery_charge,
                tax=tax,
                discount=discount,
                total_amount=grand_total,
                status='CONFIRMED',
                estimated_delivery="30 mins"
            )

            for item_data in items:
                menu_item = MenuItem.objects.get(id=item_data['id'])
                OrderItem.objects.create(
                    order=order,
                    menu_item=menu_item,
                    quantity=item_data['quantity'],
                    price=item_data['price']
                )

            return JsonResponse({
                'status': 'success',
                'order_id': order_id,
                'total_amount': grand_total,
                'message': 'Order placed successfully!'
            })

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

def api_order_status(request, order_id):
    order = Order.objects.filter(order_id=order_id).first()
    if not order:
        return JsonResponse({'status': 'error', 'message': 'Order not found'}, status=404)

    items = [{
        'name': item.menu_item.name,
        'quantity': item.quantity,
        'price': float(item.price)
    } for item in order.items.all()]

    return JsonResponse({
        'status': 'success',
        'order': {
            'order_id': order.order_id,
            'restaurant_name': order.restaurant.name,
            'status': order.status,
            'status_display': order.get_status_display(),
            'total_amount': float(order.total_amount),
            'address': order.delivery_address,
            'payment_method': order.payment_method,
            'created_at': order.created_at.strftime('%Y-%m-%d %H:%M'),
            'estimated_delivery': order.estimated_delivery,
            'items': items
        }
    })

@csrf_exempt
def api_update_order_status(request):
    if request.method == 'POST':
        body = json.loads(request.body)
        order_id = body.get('order_id')
        new_status = body.get('status')

        order = Order.objects.filter(order_id=order_id).first()
        if order:
            order.status = new_status
            order.save()
            return JsonResponse({'status': 'success', 'message': f'Order status updated to {new_status}'})

        return JsonResponse({'status': 'error', 'message': 'Order not found'}, status=404)

@csrf_exempt
def api_apply_coupon(request):
    if request.method == 'POST':
        body = json.loads(request.body)
        code = body.get('code', '').upper()
        subtotal = float(body.get('subtotal', 0))

        coupon = Coupon.objects.filter(code=code, is_active=True).first()
        if not coupon:
            return JsonResponse({'status': 'error', 'message': 'Invalid or expired coupon code'}, status=400)

        if subtotal < float(coupon.min_order_value):
            return JsonResponse({
                'status': 'error',
                'message': f'Minimum order amount for this coupon is ₹{coupon.min_order_value}'
            }, status=400)

        discount = min((subtotal * (coupon.discount_percent / 100.0)), float(coupon.max_discount))

        return JsonResponse({
            'status': 'success',
            'code': coupon.code,
            'discount': discount,
            'message': f'Coupon {coupon.code} applied! Saved ₹{discount}'
        })
