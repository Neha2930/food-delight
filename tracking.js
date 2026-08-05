/* FoodDelight - Live Order Tracking Simulator */

class OrderTracker {
  constructor(orderId = 'FD-98421') {
    this.orderId = orderId;
    this.currentStep = 3; // 1: Confirmed, 2: Preparing, 3: Ready, 4: Out for Delivery, 5: Delivered
    this.etaMinutes = 18;
    this.init();
  }

  init() {
    this.renderStatus();
    this.startSimulation();
  }

  renderStatus() {
    const steps = ['CONFIRMED', 'PREPARING', 'READY', 'OUT_FOR_DELIVERY', 'DELIVERED'];

    document.querySelectorAll('.timeline-step').forEach((stepEl, idx) => {
      const stepNum = idx + 1;
      stepEl.classList.remove('completed', 'active');
      if (stepNum < this.currentStep) {
        stepEl.classList.add('completed');
      } else if (stepNum === this.currentStep) {
        stepEl.classList.add('active');
      }
    });

    const progressPercent = ((this.currentStep - 1) / (steps.length - 1)) * 100;
    const progressBar = document.getElementById('trackingProgress');
    if (progressBar) {
      progressBar.style.width = `${progressPercent}%`;
    }

    const etaEl = document.getElementById('trackingETA');
    if (etaEl) {
      etaEl.textContent = this.currentStep === 5 ? 'Delivered!' : `${this.etaMinutes} Mins`;
    }

    const driverMarker = document.getElementById('driverMarker');
    if (driverMarker) {
      driverMarker.style.left = `${10 + (progressPercent * 0.8)}%`;
    }
  }

  startSimulation() {
    // Automatically advance order stage every 12 seconds for interactive demo
    this.timer = setInterval(() => {
      if (this.currentStep < 5) {
        this.currentStep += 1;
        this.etaMinutes = Math.max(0, this.etaMinutes - 5);
        this.renderStatus();

        if (window.app) {
          const stepNames = ['Confirmed', 'Food is being Prepared', 'Ready for Pickup', 'Out for Delivery', 'Delivered! Enjoy your meal'];
          window.app.showToast(`Order Status Update: ${stepNames[this.currentStep - 1]}`, 'info');
        }
      } else {
        clearInterval(this.timer);
      }
    }, 12000);
  }
}

document.addEventListener('DOMContentLoaded', () => {
  if (document.getElementById('trackingProgress')) {
    window.orderTracker = new OrderTracker();
  }
});
