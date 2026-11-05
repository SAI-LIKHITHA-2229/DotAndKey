# ---- Pricing rules (the server is the only place these are decided) ----
DISCOUNT_PERCENT = 20          # store-wide discount
PREPAID_EXTRA_PERCENT = 5      # extra off for card / wallet / netbanking
FREE_SHIPPING_MIN = 1000       # bill needed for free shipping
SHIPPING_FEE = 70              # charged when the bill is below FREE_SHIPPING_MIN
FREE_GIFT_STEP = 1000          # one free gift per this much

FREE_GIFTS = [
    {"name": "Vitamin C Facewash - 15ml", "image": "gift-vitc-facewash.jpg"},
    {"name": "72HR Hydrating Gel Moisturizer - 15ml", "image": "gift-72hr-moisturizer.jpg"},
    {"name": "Barrier Repair Moisturizer - 15ml", "image": "gift-barrier-repair.jpg"},
    {"name": "Strawberry Moisturizer - 15ml", "image": "gift-strawberry-moisturizer.jpg"},
    {"name": "CICA + Niacinamide Oil Free Moisturizer - 15ml", "image": "gift-cica-niacinamide.jpg"},
]

PAYMENT_METHODS = [
    {"id": "cod", "title": "Cash on delivery", "sub": "Pay with cash",
     "prepaid": False, "options": []},
    {"id": "card", "title": "Debit/Credit cards", "sub": "Visa, Mastercard, RuPay & more",
     "prepaid": True, "options": ["Visa", "Mastercard", "RuPay", "American Express"]},
    {"id": "wallet", "title": "Wallets", "sub": "Amazon Pay, PhonePe, Mobikwik & more",
     "prepaid": True, "options": ["Amazon Pay", "PhonePe", "Mobikwik"]},
    {"id": "netbanking", "title": "Netbanking", "sub": "Select from a list of banks",
     "prepaid": True,
     "options": ["HDFC Bank", "ICICI Bank", "State Bank of India", "Axis Bank",
                 "Kotak Mahindra Bank", "Punjab National Bank", "Bank of Baroda",
                 "Yes Bank"]},
    {"id": "paylater", "title": "Pay Later", "sub": "LazyPay, Simpl & more",
     "prepaid": False, "options": ["LazyPay", "Simpl", "ICICI PayLater"]},
]


def percent_of(amount, percent):
    return int(amount * percent / 100 + 0.5)


def price_cart(items):
    subtotal = sum(item["price"] * item["quantity"] for item in items)
    discount = percent_of(subtotal, DISCOUNT_PERCENT)
    return subtotal, discount, subtotal - discount


def max_gifts_for(bill_total):
    return min(bill_total // FREE_GIFT_STEP, len(FREE_GIFTS))


def shipping_for(bill_total):
    # An empty cart has nothing to ship.
    if bill_total == 0 or bill_total >= FREE_SHIPPING_MIN:
        return 0
    return SHIPPING_FEE


def method_total(bill_total, method):
    # The prepaid discount applies to the products only, not to shipping.
    off = percent_of(bill_total, PREPAID_EXTRA_PERCENT) if method["prepaid"] else 0
    return off, bill_total - off + shipping_for(bill_total)


def find_method(method_id):
    for method in PAYMENT_METHODS:
        if method["id"] == method_id:
            return method
    return None
