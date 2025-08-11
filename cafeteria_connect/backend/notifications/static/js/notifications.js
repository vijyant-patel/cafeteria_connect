// Setup WebSocket URL based on protocol (ws/wss) and hostname
const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
// Replace localhost IP with your actual server host if deploying
const socketUrl = `${protocol}://127.0.0.1:8002/ws/notifications/`;

console.log('Connecting to WebSocket:', socketUrl);

const socket = new WebSocket(socketUrl);

// Define current order ID for detail page (set dynamically in your template)
const CURRENT_ORDER_ID = window.CURRENT_ORDER_ID || null;  // e.g. set via <script> tag in template

// Define visible order IDs on list page (set dynamically in template)
const VISIBLE_ORDER_IDS = window.VISIBLE_ORDER_IDS || []; // e.g. array of order IDs
console.log(VISIBLE_ORDER_IDS);
console.log(CURRENT_ORDER_ID);
// Map for user-friendly status text
const STATUS_DISPLAY_MAP = {
    pending: 'Pending',
    confirmed: 'Confirmed',
    cancelled: 'Cancelled',
    preparing: 'Preparing',
    // Add other statuses here
};

// Map for status CSS classes
function getStatusClasses(status) {
    switch(status) {
        case 'pending':
            return ['bg-yellow-100', 'text-yellow-800'];
        case 'confirmed':
            return ['bg-green-100', 'text-green-800'];
        case 'cancelled':
            return ['bg-red-100', 'text-red-800'];
        case 'preparing':
            return ['bg-blue-100', 'text-blue-800'];
        default:
            return ['bg-gray-100', 'text-gray-800'];
    }
}

// Update status badge UI for order detail page
function updateOrderDetailStatus(newStatus) {
    const statusSpan = document.getElementById('order-status-span');
    if (!statusSpan) return;

    // Update the displayed text (you need a mapping STATUS_DISPLAY_MAP somewhere)
    statusSpan.innerText = STATUS_DISPLAY_MAP[newStatus] || newStatus;

    // Reset classes to base classes only
    statusSpan.className = 'px-3 py-1 text-sm rounded-full';

    // Add new color classes
    const classes = getStatusClasses(newStatus);
    classes.forEach(c => statusSpan.classList.add(c));
}

// Update status badge UI for order list page
function updateOrderListStatus(orderId, newStatus) {
    const statusSpan = document.getElementById(`order-status-${orderId}`);
    if (!statusSpan) return;

    statusSpan.innerText = STATUS_DISPLAY_MAP[newStatus] || newStatus;

    statusSpan.className = 'px-3 py-1 text-sm rounded-full';

    const classes = getStatusClasses(newStatus);
    classes.forEach(c => statusSpan.classList.add(c));
}
// Update the progress bar colors and active step dynamically
function updateOrderProgressBar(newStatus, currentIndex) {
    const steps = document.querySelectorAll('[id^="progress-step-"]');

    steps.forEach((step, idx) => {
        const statusValue = step.getAttribute('data-status');

        // Reset all classes first
        step.classList.remove('bg-blue-600', 'bg-green-500', 'bg-gray-300', 'text-white', 'text-gray-600');

        if (statusValue === newStatus) {
            // Active step
            step.classList.add('bg-blue-600', 'text-white');
        } else if (idx < currentIndex) {
            // Completed steps
            step.classList.add('bg-green-500', 'text-white');
        } else {
            // Pending steps
            step.classList.add('bg-gray-300', 'text-gray-600');
        }
    });

    // Also update the connecting lines between steps
    const lines = document.querySelectorAll('.progress-line');
    lines.forEach((line, idx) => {
        if (idx < currentIndex) {
            line.classList.remove('bg-gray-300');
            line.classList.add('bg-green-500');
        } else {
            line.classList.remove('bg-green-500');
            line.classList.add('bg-gray-300');
        }
    });
}


socket.onopen = () => {
    console.log("WebSocket connected");
};

socket.onclose = () => {
    console.log("WebSocket disconnected");
};

socket.onerror = (error) => {
    console.error("WebSocket error:", error);
};

socket.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log("🔔 Notification received:", data);

    // Expected data format: { order_id: 123, new_status: "confirmed" }

    if (CURRENT_ORDER_ID && data.order_id === CURRENT_ORDER_ID) {
        updateOrderDetailStatus(data.new_status);
        updateOrderProgressBar(data.new_status, data.current_index);
    }

    if (VISIBLE_ORDER_IDS.length > 0 && VISIBLE_ORDER_IDS.includes(data.order_id)) {
        updateOrderListStatus(data.order_id, data.new_status);
    }
};
