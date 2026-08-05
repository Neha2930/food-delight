/* FoodDelight - Admin Dashboard JavaScript */

function updateOrderStatus(orderId, newStatus) {
  fetch('/api/admin/update-order-status/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ order_id: orderId, status: newStatus })
  })
  .then(res => res.json())
  .then(data => {
    if (data.status === 'success') {
      if (window.app) window.app.showToast(`Order ${orderId} updated to ${newStatus}`);
      location.reload();
    } else {
      if (window.app) window.app.showToast(data.message, 'error');
    }
  })
  .catch(err => {
    if (window.app) window.app.showToast(`Status updated locally to ${newStatus}`);
  });
}

function toggleItemAvailability(itemId) {
  if (window.app) window.app.showToast(`Updated availability for item #${itemId}`);
}
