/* FoodDelight - Main Client JavaScript Application */

class FoodDelightApp {
  constructor() {
    this.cart = JSON.parse(localStorage.getItem('fooddelight_cart')) || [];
    this.wishlist = JSON.parse(localStorage.getItem('fooddelight_wishlist')) || [];
    this.darkMode = localStorage.getItem('fooddelight_darkmode') === 'true';
    this.appliedCoupon = JSON.parse(localStorage.getItem('fooddelight_coupon')) || null;
    this.userLocation = localStorage.getItem('fooddelight_location') || 'Flat 402, Sunshine Heights, MG Road';

    this.init();
  }

  init() {
    this.applyTheme();
    this.updateCartBadge();
    this.bindEvents();
    this.renderCartDrawer();
  }

  applyTheme() {
    if (this.darkMode) {
      document.body.classList.add('dark-mode');
      const themeIcon = document.getElementById('themeIcon');
      if (themeIcon) themeIcon.className = 'fas fa-sun';
    } else {
      document.body.classList.remove('dark-mode');
      const themeIcon = document.getElementById('themeIcon');
      if (themeIcon) themeIcon.className = 'fas fa-moon';
    }
  }

  toggleDarkMode() {
    this.darkMode = !this.darkMode;
    localStorage.setItem('fooddelight_darkmode', this.darkMode);
    this.applyTheme();
    this.showToast(this.darkMode ? 'Switched to Dark Mode' : 'Switched to Light Mode', 'info');
  }

  showToast(message, type = 'success') {
    let container = document.getElementById('toastContainer');
    if (!container) {
      container = document.createElement('div');
      container.id = 'toastContainer';
      container.className = 'toast-container';
      document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    let iconClass = type === 'success' ? 'fa-check-circle' : type === 'error' ? 'fa-exclamation-circle' : 'fa-info-circle';
    toast.innerHTML = `<i class="fas ${iconClass}"></i> <span>${message}</span>`;

    container.appendChild(toast);
    setTimeout(() => {
      toast.style.animation = 'slideInRight 0.3s ease reverse forwards';
      setTimeout(() => toast.remove(), 300);
    }, 3000);
  }

  // Cart operations
  addToCart(id, name, price, image, restaurantId = 1) {
    const existing = this.cart.find(item => item.id === id);
    if (existing) {
      existing.quantity += 1;
    } else {
      this.cart.push({ id, name, price: parseFloat(price), image, quantity: 1, restaurantId });
    }
    this.saveCart();
    this.showToast(`Added ${name} to cart!`);
    this.renderCartDrawer();
    this.updateItemButtons();
  }

  updateQuantity(id, delta) {
    const index = this.cart.findIndex(item => item.id === id);
    if (index !== -1) {
      this.cart[index].quantity += delta;
      if (this.cart[index].quantity <= 0) {
        this.cart.splice(index, 1);
      }
      this.saveCart();
      this.renderCartDrawer();
      this.updateItemButtons();
    }
  }

  saveCart() {
    localStorage.setItem('fooddelight_cart', JSON.stringify(this.cart));
    this.updateCartBadge();
  }

  updateCartBadge() {
    const totalCount = this.cart.reduce((sum, item) => sum + item.quantity, 0);
    document.querySelectorAll('.cart-badge-count').forEach(el => {
      el.textContent = totalCount;
      el.style.display = totalCount > 0 ? 'flex' : 'none';
    });
  }

  getCartSubtotal() {
    return this.cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
  }

  getCartTotal() {
    const subtotal = this.getCartSubtotal();
    const delivery = subtotal > 0 ? 30 : 0;
    const tax = roundToTwo(subtotal * 0.05);
    let discount = 0;

    if (this.appliedCoupon) {
      discount = Math.min((subtotal * (this.appliedCoupon.discount_percent / 100)), this.appliedCoupon.max_discount);
    }

    return {
      subtotal,
      delivery,
      tax,
      discount,
      grandTotal: Math.max(0, subtotal + delivery + tax - discount)
    };
  }

  renderCartDrawer() {
    const bodyEl = document.getElementById('cartDrawerItems');
    if (!bodyEl) return;

    if (this.cart.length === 0) {
      bodyEl.innerHTML = `
        <div style="text-align: center; padding: 40px 20px;">
          <i class="fas fa-shopping-basket" style="font-size: 3rem; color: var(--text-muted); margin-bottom: 16px;"></i>
          <h4 style="font-weight: 700;">Your Cart is Empty</h4>
          <p style="color: var(--text-muted); font-size: 0.9rem;">Add delicious food items to get started!</p>
        </div>
      `;
    } else {
      bodyEl.innerHTML = this.cart.map(item => `
        <div class="cart-item">
          <div>
            <div class="cart-item-name">${item.name}</div>
            <div class="cart-item-price">₹${item.price}</div>
          </div>
          <div style="display: flex; align-items: center; gap: 10px;">
            <button onclick="app.updateQuantity(${item.id}, -1)" style="background: var(--bg-main); width: 28px; height: 28px; border-radius: 50%; border: 1px solid var(--border-color); font-weight: bold;">-</button>
            <span style="font-weight: 700;">${item.quantity}</span>
            <button onclick="app.updateQuantity(${item.id}, 1)" style="background: var(--primary); color: #fff; width: 28px; height: 28px; border-radius: 50%; font-weight: bold;">+</button>
          </div>
        </div>
      `).join('');
    }

    const calc = this.getCartTotal();
    const subtotalEl = document.getElementById('cartSubtotal');
    const totalEl = document.getElementById('cartGrandTotal');
    const discountEl = document.getElementById('cartDiscountRow');

    if (subtotalEl) subtotalEl.textContent = `₹${calc.subtotal.toFixed(2)}`;
    if (totalEl) totalEl.textContent = `₹${calc.grandTotal.toFixed(2)}`;
    if (discountEl) {
      if (calc.discount > 0) {
        discountEl.style.display = 'flex';
        document.getElementById('cartDiscountVal').textContent = `-₹${calc.discount.toFixed(2)}`;
      } else {
        discountEl.style.display = 'none';
      }
    }
  }

  updateItemButtons() {
    document.querySelectorAll('.dish-action-area').forEach(container => {
      const id = parseInt(container.dataset.itemId);
      const cartItem = this.cart.find(item => item.id === id);
      if (cartItem) {
        container.innerHTML = `
          <div class="qty-control">
            <button onclick="app.updateQuantity(${id}, -1)">-</button>
            <span>${cartItem.quantity}</span>
            <button onclick="app.updateQuantity(${id}, 1)">+</button>
          </div>
        `;
      } else {
        const name = container.dataset.itemName;
        const price = container.dataset.itemPrice;
        const img = container.dataset.itemImg;
        container.innerHTML = `
          <button class="btn-add-cart" onclick="app.addToCart(${id}, '${escapeQuotes(name)}', ${price}, '${img}')">
            + ADD
          </button>
        `;
      }
    });
  }

  // Wishlist
  toggleWishlist(id, name) {
    const idx = this.wishlist.indexOf(id);
    if (idx !== -1) {
      this.wishlist.splice(idx, 1);
      this.showToast(`Removed ${name} from wishlist`, 'info');
    } else {
      this.wishlist.push(id);
      this.showToast(`Added ${name} to wishlist!`, 'success');
    }
    localStorage.setItem('fooddelight_wishlist', JSON.stringify(this.wishlist));
    this.updateWishlistIcons();
  }

  updateWishlistIcons() {
    document.querySelectorAll('.card-wishlist-btn').forEach(btn => {
      const id = parseInt(btn.dataset.id);
      if (this.wishlist.includes(id)) {
        btn.classList.add('active');
        btn.querySelector('i').className = 'fas fa-heart';
      } else {
        btn.classList.remove('active');
        btn.querySelector('i').className = 'far fa-heart';
      }
    });
  }

  // GPS Location simulator
  detectLocation() {
    this.showToast('Fetching GPS coordinates...', 'info');
    setTimeout(() => {
      const simulatedAddrs = [
        'Flat 402, Sunshine Heights, MG Road',
        'Tower 3, Cyber Tech Park, Sector 62',
        'House 14, Green Glen Layout, Bellandur',
        'Apartment 9B, Horizon View Towers'
      ];
      const randomAddr = simulatedAddrs[Math.floor(Math.random() * simulatedAddrs.length)];
      this.userLocation = randomAddr;
      localStorage.setItem('fooddelight_location', randomAddr);
      document.querySelectorAll('.current-location-text').forEach(el => el.textContent = randomAddr);
      this.showToast('Location updated successfully!');
    }, 1200);
  }

  // Coupon applier
  applyCouponCode(code) {
    if (!code) return;
    const subtotal = this.getCartSubtotal();

    if (code.toUpperCase() === 'WELCOME50') {
      this.appliedCoupon = { code: 'WELCOME50', discount_percent: 50, max_discount: 120 };
      this.showToast('Coupon WELCOME50 applied! Saved 50% up to ₹120');
    } else if (code.toUpperCase() === 'DELIGHT20') {
      this.appliedCoupon = { code: 'DELIGHT20', discount_percent: 20, max_discount: 200 };
      this.showToast('Coupon DELIGHT20 applied! Saved 20%');
    } else {
      this.showToast('Invalid coupon code', 'error');
      return;
    }
    localStorage.setItem('fooddelight_coupon', JSON.stringify(this.appliedCoupon));
    this.renderCartDrawer();
  }

  toggleCartDrawer() {
    const drawer = document.getElementById('cartDrawer');
    const overlay = document.getElementById('cartOverlay');
    if (drawer && overlay) {
      drawer.classList.toggle('open');
      overlay.classList.toggle('open');
    }
  }

  bindEvents() {
    this.updateWishlistIcons();
    this.updateItemButtons();

    // Set initial location text
    document.querySelectorAll('.current-location-text').forEach(el => el.textContent = this.userLocation);
  }
}

function roundToTwo(num) {
  return +(Math.round(num + "e+2")  + "e-2");
}

function escapeQuotes(str) {
  return str.replace(/'/g, "\\'");
}

const app = new FoodDelightApp();
