function getCSRFToken() {
    const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
    if (csrfInput) {
        return csrfInput.value;
    }

    // Fallback to cookie
    const name = 'csrftoken';
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        cookie = cookie.trim();
        if (cookie.startsWith(name + '=')) {
            return decodeURIComponent(cookie.substring(name.length + 1));
        }
    }

    return '';
}


// function getCSRFToken() {
//     // return document.querySelector('[name=csrfmiddlewaretoken]').value;
//     var csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
//     if (csrfInput) {
//         return csrfInput.value;
//     }
//     if (!csrfInput){
//       const name = 'csrftoken';
//       const cookies = document.cookie.split(';');
//       for (let cookie of cookies) {
//           csrfInput = cookie.trim();
//           if (csrfInput.startsWith(name + '=')) {
//               csrfInput.substring(name.length + 1);
//           }
//       }
//       return '';
//     }
//     return csrfInput;
// }

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


function clearCart(cartId, callback) {
    fetch(`/cart/clear/${cartId}/`, {
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

        const table = document.querySelector('table');
        if (table) table.remove();

        const actions = document.querySelector('.mt-6');
        if (actions) actions.remove();

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



function placeOrder(cartId) {
    const selectedIds = [...document.querySelectorAll('.product-id')].map(el => el.value);
    const quantities = {};
    const addressId = document.getElementById('addressSelect').value;

    selectedIds.forEach(id => {
        quantities[id] = document.getElementById(`quantity_${id}`).value;
    });

    fetch(`/orders/place/${cartId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify({
            product_ids: selectedIds,
            quantities: quantities,
            address_id: addressId
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


console.log("CSRF Token:", getCSRFToken());

function removeFromCart(productId) {
    fetch(`/cart/remove/${productId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        }
    })
    .then(res => res.json())
    .then(data => {
        alert(data.message);
        location.reload();  // Refresh to reflect changes
    });
}
