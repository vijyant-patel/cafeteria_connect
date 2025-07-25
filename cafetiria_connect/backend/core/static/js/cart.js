function getCSRFToken() {
    // return document.querySelector('[name=csrfmiddlewaretoken]').value;
    var csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
    if (csrfInput) {
        return csrfInput.value;
    }
    if (!csrfInput){
      const name = 'csrftoken';
      const cookies = document.cookie.split(';');
      for (let cookie of cookies) {
          csrfInput = cookie.trim();
          if (csrfInput.startsWith(name + '=')) {
              csrfInput.substring(name.length + 1);
          }
      }
      return '';
    }
    return csrfInput;
}

function addToCart(productId, quantity = 1) {
    fetch('/cart/add/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify({ product_id: productId, quantity: quantity })
    })
    .then(res => res.json())
    .then(data => {
        alert(data.message);
        document.getElementById("cart-count").textContent = data.cart_count;
        if (data.status === 'error') {
            if (confirm("Clear cart to add from a new shop?")) {
                clearCart(() => addToCart(productId, quantity));
            }
        }
    });
}


function clearCart(callback) {
    fetch('/cart/clear/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        }
    })
    .then(res => res.json())
    .then(data => {
        alert(data.message);
        document.getElementById('cart-count').textContent = data.cart_count;

        // ✅ Remove the entire table and action buttons from DOM
        const table = document.querySelector('table');
        if (table) table.remove();

        const actions = document.querySelector('.mt-6');
        if (actions) actions.remove();

        // ✅ Show "Your cart is empty" message
        // const cartContainer = document.querySelector('.max-w-5xl');
        // const emptyMsg = document.createElement('div');
        // emptyMsg.className = 'text-center text-gray-500 text-lg font-medium mt-12';
        // emptyMsg.textContent = '🛍️ Your cart is currently empty.';
        // cartContainer.appendChild(emptyMsg);
        document.getElementById("empty-cart-msg").classList.remove("hidden");
        if (callback) callback();
    });
}


// function placeOrder() {
//     fetch('/cart/place-order/', {
//         method: 'POST',
//         headers: {
//             'Content-Type': 'application/json',
//             'X-CSRFToken': getCSRFToken()
//         }
//     })
//     .then(res => res.json())
//     .then(data => {
//         alert(data.message);
//     });
// }



function placeOrder(shopId) {
    const selectedIds = [...document.querySelectorAll('.product-id')].map(el => el.value);
    const quantities = {};

    selectedIds.forEach(id => {
        quantities[id] = document.getElementById(`quantity_${id}`).value;
    });

    fetch(`/orders/place/${shopId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify({
            product_ids: selectedIds,
            quantities: quantities
        })
    })
    .then(res => res.json())
    .then(data => {
        alert(data.message);
        if (data.status === 'success') {
            window.location.href = `/orders/success/${data.order_id}/`;
        }
    });
}

function updateCartCount() {
    fetch('/cart/count/')
        .then(res => res.json())
        .then(data => {
            document.getElementById("cart-count").textContent = data.count;
        });
}