const template = Handlebars.compile(document.querySelector('#navcart').innerHTML)
const yOffset = -200;

// Avoid divs behind fixed navbar by adding an offset
function addMargin() {
    window.scrollTo(0, window.pageYOffset - 200);
}
window.addEventListener('hashchange', addMargin);


// Check if anything in cart, if so, show checkout btn
function checkNavCart() {
    var current_cart = document.querySelector('#orderbody').children;
    if (current_cart.length == 0) {
        document.getElementById('navCartbtn').style.display = 'none';
    }
}


// Menu header chevrons control if you can see that section
function myShow(data) {
    var x = document.getElementById('row' + data);
    var y = document.getElementById('btn' + data);
    if (x.style.display === "none") {
        x.style.display = "flex";
        y.classList.remove("fa-chevron-right");
        y.classList.add("fa-chevron-down");
    } else {
        x.style.display = "none";
        y.classList.remove("fa-chevron-down");
        y.classList.add("fa-chevron-right");
    }
}


// Control selecting quantity, plus adds 1
function minusQuantity(data) {
    data.parentNode.querySelector('input[type=number]').stepDown();
}

// minus takes 1 away
function addQuantity(data) {
    data.parentNode.querySelector('input[type=number]').stepUp();
}

// When mouse is over cart icon, show cart
function showOrderdetails() {
    document.getElementById('order').style.display = "block";
    setTimeout(() => {
        document.getElementById('order').style.display = "none";
    }, 3000);
}


// When food is added to cart, update navcart div
function addToNavbarcart(data) {
    $('#food' + data.food_id).modal('hide');
    current_no = parseInt(document.getElementById('items').innerHTML, 10)
    if (current_no == 0) {
        current_no = data.qty;
    }
    else
        current_no = current_no + data.qty;
    document.getElementById('items').innerHTML = current_no;

    var current_cart = document.querySelector('#orderbody').children;
    var i;
    var old_qty = 0;
    var new_qty = data.qty;
    var added = false;
    for (i = 0, len = current_cart.length; i < len; i++) {
        if (current_cart[i].id == 'navcart' + data.id) {
            old_qty = parseInt(document.querySelector('#qty' + data.id).innerHTML);
            new_qty += old_qty;
            document.querySelector('#qty' + data.id).innerHTML = new_qty;
            added = true;
        }
    }

    if (added == false) {
        const content = template({
            'id': data.id,
            'type': data.food_type,
            'size': data.food_size,
            'name': data.food_name,
            'qty': new_qty,
            'price': data.food_price,
        });
        document.querySelector('#orderbody').innerHTML += content;
    }
    document.querySelector('#total').innerHTML = '$' + data.total;
    document.getElementById('navCartbtn').style.display = 'block';

    $('#order').fadeIn(500, function () {
        $(this).animate({ scrollTop: $(this).prop('scrollHeight') });
        $(this).delay(2000).fadeOut(500);
    });

}

// When add to cart is clicked, ajax call made
function cartFunction(data) {
    var topping1 = document.getElementById('topping1' + data);
    var topping2 = document.getElementById('topping2' + data);
    var topping3 = document.getElementById('topping3' + data);
    var toppings = [];
    if (topping1 != null) {
        var topping_1 = topping1.value;
        toppings.push(topping_1);
        if (topping2 != null) {
            var topping_2 = topping2.value;
            toppings.push(topping_2);
            if (topping3 != null) {
                var topping_3 = topping3.value;
                toppings.push(topping_3);
            }
        }
    }

    var extra = document.forms['form' + data].elements['extra' + data + '[]'];
    var extras = [];
    if (extra != null) {
        var len = extra.length;
        if (len == undefined) {
            if (extra.checked)
                extras.push(extra.value);
        }
        else {
            var i;
            for (i = 0; i < len; i++) {
                if (extra[i].checked) {
                    extras.push(extra[i].value);
                }
            }
        }
    }

    var quantity = document.getElementById('quantity' + data).value;

    var csrftoken = document.getElementById('form' + data).firstElementChild.value;
    console.log(csrftoken);

    $.ajax({
        type: "POST",
        url: '/menu',
        data: {
            'food_id': data,
            'toppings': toppings,
            'extras': extras,
            'quantity': quantity
        },
        headers: {
            'X-CSRFToken': csrftoken
        },
    }).done(function (data) {
        addToNavbarcart(data);
    })

}


// When checkout clicked on cart page
function showPlaceOrder() {
    document.getElementById('checkout').style.display = 'block';
    y = document.getElementById('checkout').getBoundingClientRect().top + window.pageYOffset + yOffset;
    window.scrollTo({ top: y, behavior: 'smooth' });
}


// When proceed clicked suring checkout process
function showTakeawayDiv(data) {
    document.getElementById('takeaway').style.display = 'block';
    document.getElementById('btakeaway').classList.add('active');
    document.getElementById('bdetails').classList.remove('active');
    data.classList.add('clicked');
    y = document.getElementById('takeaway').getBoundingClientRect().top + window.pageYOffset + yOffset;
    window.scrollTo({ top: y, behavior: 'smooth' });
}

// When proceed clicked during checkout process
function showPaymentDiv(data) {
    document.getElementById('btakeaway').classList.remove('active');
    document.getElementById('bpayment').classList.add('active');
    document.getElementById('payment').style.display = 'block';
    data.classList.add('clicked');
    y = document.getElementById('payment').getBoundingClientRect().top + window.pageYOffset + yOffset;
    window.scrollTo({ top: y, behavior: 'smooth' });
}

// Control which notes are shown during checkout process
function showPdiv() {
    if (document.getElementById('deliveryType').value == 'delivery') {
        document.getElementById('collection').style.display = 'none';
        document.getElementById('delivery').style.display = 'block';

    }
    else if (document.getElementById('deliveryType').value == 'collection') {
        document.getElementById('delivery').style.display = 'none';
        document.getElementById('collection').style.display = 'block';
    }
    else {
        document.getElementById('collection').style.display = 'none';
        document.getElementById('delivery').style.display = 'none';
    }
}

// Control which button is shown depending on which payment method is selected
function checkSelectedPay(data) {
    if (data.value == 'cash') {
        document.getElementById('card').style.display = 'none';
        document.getElementById('cash').style.display = 'block';

    }
    else if (data.value == 'card') {
        document.getElementById('cash').style.display = 'none';
        document.getElementById('card').style.display = 'block';
    }
    else {
        document.getElementById('card').style.display = 'none';
        document.getElementById('cash').style.display = 'none';
    }
}

// When on card page, stripe elements are set up
if (location.pathname == '/card') {
    // Create a Stripe client.
    var stripe = Stripe('pk_test_dgZg6jji56E8WVtZhzuBUsIg000U0ay2yZ');

    // Create an instance of Elements.
    var elements = stripe.elements();

    // Custom styling can be passed to options when creating an Element.
    // (Note that this demo uses a wider set of styles than the guide below.)
    var style = {
        base: {
            color: '#32325d',
            fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
            fontSmoothing: 'antialiased',
            fontSize: '16px',
            '::placeholder': {
                color: 'grey',
            }
        },
        invalid: {
            color: 'red',
            iconColor: 'red'
        }
    };

    // Create an instance of the card Element.
    var card = elements.create('card', { style: style });

    // Add an instance of the card Element into the `card-element` <div>.
    card.mount('#card-element');

    // Handle real-time validation errors from the card Element.
    card.on('change', function (event) {
        var displayError = document.getElementById('card-errors');
        if (event.error) {
            displayError.textContent = event.error.message;
        } else {
            displayError.textContent = '';
        }
    });

    // Handle form submission.
    var form = document.getElementById('payment-form');
    form.addEventListener('submit', function (event) {
        event.preventDefault();

        stripe.createToken(card).then(function (result) {
            if (result.error) {
                // Inform the user if there was an error.
                var errorElement = document.getElementById('card-errors');
                errorElement.textContent = result.error.message;
            } else {
                // Send the token to your server.
                stripeTokenHandler(result.token);
            }
        });
    });

    // Submit the form with the token ID.
    function stripeTokenHandler(token) {
        // Insert the token ID into the form so it gets submitted to the server
        var form = document.getElementById('payment-form');
        var hiddenInput = document.createElement('input');
        hiddenInput.setAttribute('type', 'hidden');
        hiddenInput.setAttribute('name', 'stripeToken');
        hiddenInput.setAttribute('value', token.id);
        form.appendChild(hiddenInput);

        // Submit the form
        form.submit();
    }
}


// On staff page, when customer information is clicked, customent div is shown
function customer(data) {
    var cus_div = document.getElementById('customer' + data);
    if (cus_div.style.display === "none") {
        cus_div.style.display = "block";
    } else {
        cus_div.style.display = "none";
    }
}

// On staff page, when order info is clicked, order info div is shown
function orderInfo(data) {
    var odiv = document.getElementById('orderInfo' + data);
    if (odiv.style.display === "none") {
        odiv.style.display = "block";
    } else {
        odiv.style.display = "none";
    }
}

// General function to titleCase string
function titleCase(str) {
    str = str.toLowerCase().split(' ');
    for (var i = 0; i < str.length; i++) {
        str[i] = str[i].charAt(0).toUpperCase() + str[i].slice(1);
    }
    return str.join(' ');
}


// When staff update status, ajax call made
function changeStatus(data) {
    var status = document.getElementById('form' + data).querySelector('select[name="status"]').value;

    var csrftoken = document.getElementById('form' + data).firstElementChild.value;
    console.log(csrftoken);

    $.ajax({
        type: "POST",
        url: '/staff',
        data: {
            'order_id': data,
            'status': status,
        },
        headers: {
            'X-CSRFToken': csrftoken
        },
    }).done(function (data) {
        var x = document.getElementById('status' + data.id);
        x.innerHTML = titleCase(data.status);
    })

}

// A way to hide orders that are completed
function closeOrder(data) {
    var div = document.getElementById('toggle' + data);
    var btn = document.getElementById('orderBtn' + data);
    var header = document.getElementById('header' + data)
    if (div.style.display === "none") {
        div.style.display = "block";
        btn.innerHTML = '&times;';
        header.innerHTML = 'Order no: <span class="text-primary">' + data + '</span>';
    } else {
        div.style.display = "none";
        btn.innerHTML = 'open';
        header.innerHTML = '<span class="text-primary">' + data + '</span>';
    }
}

// Progress bar that changes status
function progress(data) {
    if (data == 'confirmed') {
        document.getElementById('confirmed').style.visibility = 'visible';
        document.getElementById('confirmed-text').style.visibility = 'visible';
        document.getElementById('confirmed').querySelector('i').classList.add('font-big');
        document.getElementById('confirmed-text').querySelector('p').classList.add('font-big');
    }
    else if (data == 'preparing') {
        document.getElementById('confirmed').style.visibility = 'visible';
        document.getElementById('confirmed').querySelector('i').classList.add('text-white');
        document.getElementById('confirmed-text').querySelector('p').classList.add('text-white');
        document.getElementById('confirmed-text').style.visibility = 'visible'
        document.getElementById('confirmed').querySelector('i').classList.remove('font-big');
        document.getElementById('confirmed-text').querySelector('p').classList.remove('font-big');
        document.getElementById('preparing1').style.visibility = 'visible';
        document.getElementById('prep1-text').style.visibility = 'visible';
        document.getElementById('preparing1').querySelector('span').classList.add('font-big');
        document.getElementById('prep1-text').querySelector('p').classList.add('font-big');
        setTimeout(() => {
            document.getElementById('preparing1').querySelector('span').classList.remove('font-big');
            document.getElementById('prep1-text').querySelector('p').classList.remove('font-big');
            document.getElementById('preparing1').querySelector('span').classList.add('text-white');
            document.getElementById('prep1-text').querySelector('p').classList.add('text-white');
            document.getElementById('preparing2').style.visibility = 'visible';
            document.getElementById('prep2-text').style.visibility = 'visible';
            document.getElementById('preparing2').querySelector('i').classList.add('font-big');
            document.getElementById('prep2-text').querySelector('p').classList.add('font-big');
            setTimeout(() => {
                document.getElementById('preparing2').querySelector('i').classList.remove('font-big');
                document.getElementById('prep2-text').querySelector('p').classList.remove('font-big');
                document.getElementById('preparing2').querySelector('i').classList.add('text-white');
                document.getElementById('prep2-text').querySelector('p').classList.add('text-white');
                document.getElementById('preparing3').style.visibility = 'visible';
                document.getElementById('prep3-text').style.visibility = 'visible';
                document.getElementById('preparing3').querySelector('i').classList.add('font-big');
                document.getElementById('prep3-text').querySelector('p').classList.add('font-big');
            }, 300000);
            setTimeout(() => {
                document.getElementById('preparing3').querySelector('i').classList.remove('font-big');
                document.getElementById('prep3-text').querySelector('p').classList.remove('font-big');
                document.getElementById('preparing3').querySelector('i').classList.add('text-white');
                document.getElementById('prep3-text').querySelector('p').classList.add('text-white');
                document.getElementById('preparing4').style.visibility = 'visible';
                document.getElementById('prep4-text').style.visibility = 'visible';
                document.getElementById('preparing4').querySelector('i').classList.add('font-big');
                document.getElementById('prep4-text').querySelector('p').classList.add('font-big');
            }, 300000);
        }, 300000);


    }
    else if (data == 'out for delivery' || data == 'ready to collect') {
        document.getElementById('confirmed').style.visibility = 'visible';
        document.getElementById('confirmed').querySelector('i').classList.add('text-white');
        document.getElementById('confirmed-text').querySelector('p').classList.add('text-white');
        document.getElementById('confirmed-text').style.visibility = 'visible'
        document.getElementById('preparing1').style.visibility = 'visible';
        document.getElementById('prep1-text').style.visibility = 'visible';
        document.getElementById('preparing1').querySelector('span').classList.add('text-white');
        document.getElementById('prep1-text').querySelector('p').classList.add('text-white');
        document.getElementById('preparing2').style.visibility = 'visible';
        document.getElementById('prep2-text').style.visibility = 'visible';
        document.getElementById('preparing2').querySelector('i').classList.add('text-white');
        document.getElementById('prep2-text').querySelector('p').classList.add('text-white');
        document.getElementById('preparing3').style.visibility = 'visible';
        document.getElementById('prep3-text').style.visibility = 'visible';
        document.getElementById('preparing3').querySelector('i').classList.add('text-white');
        document.getElementById('prep3-text').querySelector('p').classList.add('text-white');
        document.getElementById('preparing4').style.visibility = 'visible';
        document.getElementById('prep4-text').style.visibility = 'visible';
        document.getElementById('preparing4').querySelector('i').classList.add('text-white');
        document.getElementById('prep4-text').querySelector('p').classList.add('text-white');
        document.getElementById('out1').style.visibility = 'visible';
        document.getElementById('out1-text').style.visibility = 'visible';
        document.getElementById('out1').querySelector('i').classList.add('font-big');
        document.getElementById('out1-text').querySelector('p').classList.add('font-big');
        setTimeout(() => {
            document.getElementById('out1').querySelector('i').classList.remove('font-big');
            document.getElementById('out1-text').querySelector('p').classList.remove('font-big');
            document.getElementById('out1').querySelector('i').classList.add('text-white');
            document.getElementById('out1-text').querySelector('p').classList.add('text-white');
            document.getElementById('out2').style.visibility = 'visible';
            document.getElementById('out2-text').style.visibility = 'visible';
            document.getElementById('out2').querySelector('i').classList.add('font-big');
            document.getElementById('out2-text').querySelector('p').classList.add('font-big');
        }, 300000);
    }
    else {
        document.getElementById('confirmed').style.visibility = 'visible';
        document.getElementById('confirmed').querySelector('i').classList.add('text-white');
        document.getElementById('confirmed-text').querySelector('p').classList.add('text-white');
        document.getElementById('confirmed-text').style.visibility = 'visible'
        document.getElementById('preparing1').style.visibility = 'visible';
        document.getElementById('prep1-text').style.visibility = 'visible';
        document.getElementById('preparing1').querySelector('span').classList.add('text-white');
        document.getElementById('prep1-text').querySelector('p').classList.add('text-white');
        document.getElementById('preparing2').style.visibility = 'visible';
        document.getElementById('prep2-text').style.visibility = 'visible';
        document.getElementById('preparing2').querySelector('i').classList.add('text-white');
        document.getElementById('prep2-text').querySelector('p').classList.add('text-white');
        document.getElementById('preparing3').style.visibility = 'visible';
        document.getElementById('prep3-text').style.visibility = 'visible';
        document.getElementById('preparing3').querySelector('i').classList.add('text-white');
        document.getElementById('prep3-text').querySelector('p').classList.add('text-white');
        document.getElementById('preparing4').style.visibility = 'visible';
        document.getElementById('prep4-text').style.visibility = 'visible';
        document.getElementById('preparing4').querySelector('i').classList.add('text-white');
        document.getElementById('prep4-text').querySelector('p').classList.add('text-white');
        document.getElementById('out1').style.visibility = 'visible';
        document.getElementById('out1-text').style.visibility = 'visible';
        document.getElementById('out1').querySelector('i').classList.add('text-white');
        document.getElementById('out1-text').querySelector('p').classList.add('text-white');
        document.getElementById('out2').style.visibility = 'visible';
        document.getElementById('out2-text').style.visibility = 'visible';
        document.getElementById('out2').querySelector('i').classList.add('text-white');
        document.getElementById('out2-text').querySelector('p').classList.add('text-white');
        document.getElementById('done').style.visibility = 'visible';
        document.getElementById('done-text').style.visibility = 'visible';
        document.getElementById('done').querySelector('i').classList.add('font-big');
        document.getElementById('done-text').querySelector('p').classList.add('font-big');

    }
}

// General function convert timestamps into local time and date
function convertLocalTime() {
    var time = document.getElementsByClassName('time text-primary');
    console.log(time);
    var i;
    var len = time.length;
    for (i = 0; i < len; i++) {
        var timestamp = time[i].firstChild.textContent;
        var local = new Date(timestamp);
        var now = new Date();
        if (local.toDateString() == now.toDateString())
            var date = 'Today';
        else if (local.getDate() == (now.getDate() - 1))
            var date = 'Yesterday';
        else
            var date = local.toDateString();
        time[i].innerText = date + ' ' + local.toLocaleTimeString();
    };
}

// When cart edited, update cart and navcart
function updateCartDiv(data) {
    $('#food' + data.id).modal('hide');

    var carttotal = document.getElementById('cartTotal');
    carttotal.innerHTML = '$' + data.total;

    var total = document.getElementById('total');
    total.innerHTML = '$' + data.total;

    var item = document.getElementById('item' + data.id);
    item.innerHTML = data.item;

    var extra = document.getElementById('extra' + data.id);
    if (data.type == 'sub')
        if (data.extras == '')
            extra.innerHTML = 'No extras';
        else
            extra.innerHTML = '-with extra ' + data.extras;
    else
        extra.innerHTML = data.toppings;

    var qty = document.getElementById('qty' + data.id);
    qty.innerHTML = data.quantity;

    var cartqty = document.getElementById('cartqty' + data.id);
    cartqty.innerHTML = data.quantity;

    var price = document.getElementById('price' + data.id);
    price.innerHTML = '$' + data.overall_price;

    document.getElementById('items').innerHTML = data.total_qty;
}

// When cart edited, ajax call made
function updateCart(data) {
    var topping1 = document.getElementById('topping1' + data);
    var topping2 = document.getElementById('topping2' + data);
    var topping3 = document.getElementById('topping3' + data);
    var toppings = [];
    if (topping1 != null) {
        var topping_1 = topping1.value;
        toppings.push(topping_1);
        if (topping2 != null) {
            var topping_2 = topping2.value;
            toppings.push(topping_2);
            if (topping3 != null) {
                var topping_3 = topping3.value;
                toppings.push(topping_3);
            }
        }
    }

    var extra = document.forms['form' + data].elements['extra' + data + '[]'];
    console.log(extra);
    var extras = [];
    if (extra != null) {
        var len = extra.length;
        if (len == undefined) {
            if (extra.checked)
                extras.push(extra.value);
        }
        else {
            var i;
            for (i = 0; i < len; i++) {
                if (extra[i].checked) {
                    extras.push(extra[i].value);
                }
            }
        }

    }
    console.log(extras)

    var quantity = document.getElementById('quantity' + data).value;

    var csrftoken = document.getElementById('form' + data).firstElementChild.value;
    console.log(csrftoken);

    $.ajax({
        type: "POST",
        url: '/update_cart',
        data: {
            'OrderToFood_id': data,
            'toppings': toppings,
            'extras': extras,
            'quantity': quantity
        },
        headers: {
            'X-CSRFToken': csrftoken
        },
    }).done(function (data) {
        updateCartDiv(data);
    })
}







