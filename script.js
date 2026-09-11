// -----------------------------------------------------------------------------
// PRODUCT CATALOG
// Add a `variants` array to any product to show pill selectors (types / shades).
// All variants share the product's price. Leave `variants` off for single items.
// The values below are placeholders — edit them to the real types / shades.
// -----------------------------------------------------------------------------
const products = [
    { id: 1, name: "Moisturizer", category: "Moisturizer", price: 499, image: "moisturizer.jpg",
      variants: [
          { label: "Watermelon Cooling Gel", image: "moisturizer.jpg" },
          { label: "Vitamin C + E Super Bright Gel Moisturizer for Face", image: "moist-vitce-superbright.jpg" },
          { label: "Barrier Repair Moisturizer (Hyaluronic + Ceramides)", image: "moist-barrier-repair.jpg" },
          { label: "72HR Gel Moisturizer + Probiotics for Face", image: "moist-72hr-probiotics.jpg" },
          { label: "Dragon Fruit Bounce Jelly Moisturizer With Plant PDRN", image: "moist-dragonfruit-jelly.jpg" }
      ] },
    { id: 2, name: "Sunscreen", category: "Sunscreen", price: 549, image: "sunscreen.jpg",
      variants: [
          { label: "Vitamin C + E Sunscreen SPF 50+ PA++++ With New-Age UV Filters", image: "sunscreen.jpg" },
          { label: "Barrier Repair Sunscreen, In-Vivo Tested SPF 50+ PA++++", image: "sunscreen-barrier-repair.jpg" },
          { label: "Watermelon Cooling Sunscreen SPF 50+ PA++++ With New-Age UV Filters", image: "sunscreen-watermelon.jpg" },
          { label: "Cica + Niacinamide Sunscreen, In-Vivo Tested SPF 50+ PA++++", image: "sunscreen-cica-niacinamide.jpg" },
          { label: "Dragon Fruit Bounce Gel Sunscreen SPF 50+ PA++++, With New-Age UV Filters", image: "sunscreen-dragonfruit.jpg" }
      ] },
    { id: 13, name: "Strawberry Dew Tinted Sunscreen SPF 50+ PA++++ With New-Age UV Filters", category: "Tinted Sunscreen", price: 599, image: "sunscreen-strawberrydew.jpg",
      variants: [
          { label: "Peony - 00 Very Light with Cool Undertone", color: "#f2d8cf", image: "sunscreen-strawberrydew.jpg" },
          { label: "Porcelain - 01 Very Light with Warm Undertone", color: "#f3d9c0", image: "sunscreen-strawberrydew-porcelain.jpg" },
          { label: "Rose - 01A Light with Neutral Undertone", color: "#eccbb4", image: "sunscreen-strawberrydew-rose.jpg" },
          { label: "Warm Ivory - 02 Light with Warm Undertone", color: "#e6c1a0", image: "sunscreen-strawberrydew-warm-ivory.jpg" },
          { label: "Peach - 02A Light with Neutral Undertone", color: "#e5c0a2", image: "sunscreen-strawberrydew-peach.jpg" },
          { label: "Sand - 03 Light Medium with Warm Undertone", color: "#d3a578", image: "sunscreen-strawberrydew-sand.jpg" },
          { label: "Honey - 03A Light Medium with Warm Undertone", color: "#c99866", image: "sunscreen-strawberrydew-honey.jpg" },
          { label: "Almond - 04 Medium with Cool Undertone", color: "#bd8a5f", image: "sunscreen-strawberrydew-almond.jpg" },
          { label: "Beige - 05 Medium with Warm Undertone", color: "#b17d50", image: "sunscreen-strawberrydew-beige.jpg" },
          { label: "Cinnamon - 06 Medium with Neutral Undertone", color: "#a06b43", image: "sunscreen-strawberrydew-cinnamon.jpg" },
          { label: "Caramel - 07 Rich with Warm Undertone", color: "#8c5a37", image: "sunscreen-strawberrydew-caramel.jpg" },
          { label: "Hazelnut - 08 Rich with Neutral Undertone", color: "#7a4c2f", image: "sunscreen-strawberrydew-hazelnut.jpg" },
          { label: "Mocha - 08A Rich with Warm Undertone", color: "#6a4028", image: "sunscreen-strawberrydew-mocha.jpg" },
          { label: "Fudge - 09 Very Rich with Warm Undertone", color: "#563322", image: "sunscreen-strawberrydew-fudge.jpg" },
          { label: "Espresso - 10 Very Rich with Cool Undertone", color: "#43281c", image: "sunscreen-strawberrydew-espresso.jpg" }
      ] },
    { id: 3, name: "Face Serum", category: "Face Serum", price: 599, image: "serum.jpg",
      variants: [
          { label: "10% Vitamin C + E Face Serum with 5% Niacinamide", image: "serum.jpg" },
          { label: "Strawberry Bright 10% Niacinamide Face Serum", image: "serum-strawberry-bright.jpg" },
          { label: "12% Barrier Boost Serum (Hyaluronic + Ceramides)", image: "serum-barrier-boost.jpg" },
          { label: "Cica + 10% Niacinamide Face Serum for Oily Skin", image: "serum-cica-niacinamide.jpg" },
          { label: "Pomegranate Youth 0.2% Retinol Complex Face Serum", image: "serum-pomegranate-retinol.jpg" }
      ] },
    { id: 4, name: "Face Wash", category: "Face Wash", price: 399, image: "facewash.jpg",
      variants: [
          { label: "Vitamin C Foaming Face Wash", image: "facewash.jpg" },
          { label: "Watermelon Gel Face Wash", image: "facewash-watermelon.jpg" },
          { label: "Cica + Salicylic Acid Face Wash for Oily Skin", image: "facewash-cica-salicylic.jpg" },
          { label: "Barrier Repair Gentle Hydrating Face Wash", image: "facewash-barrier-repair.jpg" },
          { label: "Strawberry Dew Micellar Face Wash", image: "facewash-strawberry-micellar.jpg" }
      ] },
    { id: 5, name: "Face Mask", category: "Face Mask", price: 449, image: "facemask.jpg",
      variants: [
          { label: "Watermelon Cool Icy Plunge Clay Mask", image: "facemask.jpg" },
          { label: "Cica & Salicylic French Green Clay Face Mask", image: "facemask-cica-greenclay.jpg" },
          { label: "Mango Detan Clay Mask", image: "facemask-mango-detan.jpg" },
          { label: "Vitamin C Pink Clay Mask", image: "facemask-vitc-pinkclay.jpg" }
      ] },
    { id: 7, name: "Face Toner", category: "Face Toner", price: 449, image: "toner.jpg",
      variants: [
          { label: "Blueberry Hydrate Barrier Repair Rice Water Toner", image: "toner.jpg" },
          { label: "Watermelon + Glycolic Acid Pore Tightening Toner", image: "toner-watermelon-glycolic.jpg" },
          { label: "Cica + Niacinamide Toner with Green Tea", image: "toner-cica-niacinamide.jpg" },
          { label: "Blueberry Hydrate Barrier Repair Milk Face Toner", image: "toner-blueberry-milk.jpg" }
      ] },
    { id: 8, name: "Hair Care", category: "Hair Care", price: 499, image: "haircare.jpg",
      variants: [
          { label: "Moringa & Argan Oil Hair Fall Control Shampoo", image: "haircare.jpg" },
          { label: "Hair Mask with Moringa + Argan Oil", image: "haircare-hair-mask.jpg" },
          { label: "Moringa & Argan Frizz Control Hair Conditioner", image: "haircare-conditioner.jpg" }
      ] },
    { id: 9, name: "Meltie Lip Balm In-Vivo Tested SPF 50+ PA+++", category: "Lip Balm", price: 349, image: "lipbalm-meltie.jpg",
      variants: [
          { label: "Strawberry Glaze", color: "#e64b6e", image: "lipbalm-meltie.jpg" },
          { label: "Cocoa Crème", color: "#6e4b3a", image: "lipbalm-meltie-cocoa-creme.jpg" },
          { label: "Berry Crumble", color: "#7c2f45", image: "lipbalm-meltie-berry-crumble.jpg" }
      ] },
    { id: 10, name: "Barrier Repair Hydrating Lip Balm In-Vivo Tested SPF 50+ PA+++", category: "Lip Balm", price: 349, image: "lipbalm-barrier.jpg",
      variants: [
          { label: "Strawberry Red - High Tinted", color: "#d81f3a", image: "lipbalm-barrier.jpg" },
          { label: "Cherry Crimson - High Tinted", color: "#8f1d2e", image: "lipbalm-barrier-cherry-crimson.jpg" },
          { label: "Cocoa Nude - Medium Tinted", color: "#a9615a", image: "lipbalm-barrier-cocoa-nude.jpg" }
      ] },
    { id: 11, name: "Ceramide + Peptide Lip Balm In-Vivo Tested SPF 50+ PA+++", category: "Lip Balm", price: 349, image: "lipbalm-ceramide.jpg",
      variants: [
          { label: "Warm Nude", color: "#c08a72", image: "lipbalm-ceramide.jpg" },
          { label: "Plush Pink", color: "#e87ba0", image: "lipbalm-ceramide-plush-pink.jpg" },
          { label: "Red Romance", color: "#c02234", image: "lipbalm-ceramide-red-romance.jpg" }
      ] },
    { id: 12, name: "Vitamin C + E Gloss Boss Lip Balm In-Vivo Tested SPF 50+ PA+++", category: "Lip Balm", price: 349, image: "lipbalm-glossboss.jpg",
      variants: [
          { label: "Strawberry Crush High Tinted", color: "#e33c5a", image: "lipbalm-glossboss.jpg" },
          { label: "Cherry Pop Medium Tinted", color: "#c0304a", image: "lipbalm-glossboss-cherry-pop.jpg" },
          { label: "Watermelon Cool Medium Tinted", color: "#f2678a", image: "lipbalm-glossboss-watermelon-cool.jpg" },
          { label: "Cocoa Mint Low Tinted", color: "#a56b5c", image: "lipbalm-glossboss-cocoa-mint.jpg" }
      ] },
    { id: 15, name: "Body Care", category: "Body Care", price: 545, image: "bodycare.jpg",
      variants: [
          { label: "Barrier Repair Hyaluronic Acid Body Lotion", image: "bodycare.jpg" },
          { label: "Vitamin C + E Body Lotion for Glowing Skin", image: "bodycare-vitce-lotion.jpg" },
          { label: "Cica + 1% Salicylic Acid Exfoliating Shower Gel", image: "bodycare-cica-showergel.jpg" },
          { label: "Watermelon Cooling Glycolic Acid Shower Gel", image: "bodycare-watermelon-showergel.jpg" },
          { label: "Watermelon Cooling Sunscreen Body Spray In-Vivo Tested SPF 50+ PA+++", image: "bodycare-watermelon-sunscreen-spray.jpg" }
      ] },
    { id: 16, name: "Combos", category: "Combos", price: 999, image: "combos.jpg",
      variants: [
          { label: "Glow+ Protect Vitamin C Duo", image: "combos.jpg" },
          { label: "Super Cica & Salicylic Anti Acne Routine", image: "combos-cica-acne-routine.jpg" },
          { label: "SPF 50+ Barrier Repair Hydrating Lip Balm - Pack of 2", image: "combos-lipbalm-pack2.jpg" },
          { label: "SPF 50+ Ultra Light Sunscreen Duo", image: "combos-sunscreen-duo.jpg" },
          { label: "Moisturize & Protect Power Duo", image: "combos-moisturize-protect-duo.jpg" }
      ] },
    { id: 14, name: "Eye Care", category: "Eye Care", price: 595, image: "eyecare.jpg",
      variants: [
          { label: "Watermelon Hydrogel Under-eye Patches", image: "eyecare.jpg" },
          { label: "Pomegranate + Retinol Eye Cream for Dark Circles", image: "eyecare-pomegranate-retinol.jpg" }
      ] },
    { id: 6, name: "Lip Mask", category: "Lip Mask", price: 399, image: "lipmask.jpg" }
        ];

const productModal = document.querySelector("#productModal");
const modalImage = document.querySelector("#modalImage");
const modalName = document.querySelector("#modalName");
const modalPrice = document.querySelector("#modalPrice");
const modalAddToCart = document.querySelector("#modalAddToCart");
const closeModal = document.querySelector("#closeModal");

if (closeModal) {
    closeModal.addEventListener("click", function() {
        productModal.classList.remove("active");
    });
}

// Navbar icons: soft enlarge on click, easing slowly back before navigating.
document.querySelectorAll(".nav-link").forEach(function(link) {
    link.addEventListener("animationend", function() {
        link.classList.remove("nav-pop");
    });
    link.addEventListener("click", function(e) {
        link.classList.remove("nav-pop");
        void link.offsetWidth;          // restart the animation
        link.classList.add("nav-pop");

        if (link.pathname === window.location.pathname) return; // current page: just animate
        e.preventDefault();
        setTimeout(function() { window.location.href = link.href; }, 280);
    });
});

// A variant is either a plain string, or { label, image, color }.
// `color` present -> render as a shade dot instead of a text pill.
function variantLabel(v) { return typeof v === "string" ? v : v.label; }
function variantImage(v, product) {
    return (v && typeof v === "object" && v.image) ? v.image : product.image;
}
function variantColor(v) { return (v && typeof v === "object") ? v.color : null; }

// Cart line-item name, with the chosen variant in parentheses.
function cartName(product, variant) {
    return variant ? product.name + " (" + variant + ")" : product.name;
}

// Point an <img> at a product image, falling back to the base image if missing.
function setProductImage(imgEl, product, file) {
    imgEl.onerror = function() {
        imgEl.onerror = null;
        imgEl.src = "images/" + product.image;
    };
    imgEl.src = "images/" + file;
}

// Build the variant selector. If the variants carry `color` it renders as shade
// dots with the selected shade's name above them; otherwise as text pills.
// `onSelect(imageFile)` fires on change so the caller can swap its picture.
// `initialLabel` pre-selects a specific variant (defaults to the first).
function buildVariantList(product, onSelect, initialLabel) {
    const variants = product.variants || [];
    let initialIndex = 0;
    if (initialLabel != null) {
        const found = variants.findIndex(function(v) { return variantLabel(v) === initialLabel; });
        if (found >= 0) initialIndex = found;
    }
    let selected = variants[initialIndex] || null;
    const swatchMode = variants.length > 0 && variantColor(variants[0]);

    const wrap = document.createElement("div");
    wrap.className = swatchMode ? "variant-swatches" : "variant-list";

    function choose(value) {
        selected = value;
        if (onSelect) onSelect(variantImage(value, product));
    }

    if (swatchMode) {
        const nameEl = document.createElement("span");
        nameEl.className = "swatch-name";
        nameEl.textContent = variantLabel(selected);

        const dots = document.createElement("div");
        dots.className = "swatch-dots";

        variants.forEach(function(value, index) {
            const dot = document.createElement("button");
            dot.type = "button";
            dot.className = "swatch-dot" + (index === initialIndex ? " selected" : "");
            dot.style.backgroundColor = variantColor(value) || "#ccc";
            dot.title = variantLabel(value);
            dot.setAttribute("aria-label", variantLabel(value));
            dot.addEventListener("click", function() {
                dots.querySelectorAll(".swatch-dot").forEach(function(d) {
                    d.classList.remove("selected");
                });
                dot.classList.add("selected");
                nameEl.textContent = variantLabel(value);
                choose(value);
            });
            dots.appendChild(dot);
        });

        wrap.appendChild(nameEl);
        wrap.appendChild(dots);
    } else {
        variants.forEach(function(value, index) {
            const pill = document.createElement("button");
            pill.type = "button";
            pill.className = "variant-pill" + (index === initialIndex ? " selected" : "");
            pill.textContent = variantLabel(value);
            pill.addEventListener("click", function() {
                wrap.querySelectorAll(".variant-pill").forEach(function(p) {
                    p.classList.remove("selected");
                });
                pill.classList.add("selected");
                choose(value);
            });
            wrap.appendChild(pill);
        });
    }

    return {
        el: wrap,
        getSelected: function() { return selected ? variantLabel(selected) : null; },
        getImage: function() { return variantImage(selected, product); }
    };
}

// ---- Add-to-cart feedback: pleasant sound + button animation --------------
let audioCtx = null;

// Create/resume the audio context inside a user gesture so playback is allowed.
function primeAudio() {
    try {
        const AC = window.AudioContext || window.webkitAudioContext;
        if (!AC) return;
        if (!audioCtx) audioCtx = new AC();
        if (audioCtx.state === "suspended") audioCtx.resume();
    } catch (e) { /* audio is not critical */ }
}

// Soft "pop" transient + a gentle rising two-note chime.
function playAddToCartSound() {
    primeAudio();
    if (!audioCtx) return;
    try {
        const now = audioCtx.currentTime;
        const master = audioCtx.createGain();
        master.gain.value = 0.14;
        master.connect(audioCtx.destination);

        const pop = audioCtx.createOscillator();
        const popGain = audioCtx.createGain();
        pop.type = "sine";
        pop.frequency.setValueAtTime(180, now);
        pop.frequency.exponentialRampToValueAtTime(520, now + 0.06);
        popGain.gain.setValueAtTime(0.0001, now);
        popGain.gain.exponentialRampToValueAtTime(0.9, now + 0.012);
        popGain.gain.exponentialRampToValueAtTime(0.0001, now + 0.12);
        pop.connect(popGain).connect(master);
        pop.start(now);
        pop.stop(now + 0.14);

        [{ f: 880.0, t: 0.04, d: 0.28 }, { f: 1174.7, t: 0.15, d: 0.34 }].forEach(function(n) {
            const osc = audioCtx.createOscillator();
            const g = audioCtx.createGain();
            osc.type = "triangle";
            osc.frequency.value = n.f;
            const s = now + n.t;
            g.gain.setValueAtTime(0.0001, s);
            g.gain.exponentialRampToValueAtTime(0.6, s + 0.02);
            g.gain.exponentialRampToValueAtTime(0.0001, s + n.d);
            osc.connect(g).connect(master);
            osc.start(s);
            osc.stop(s + n.d + 0.02);
        });
    } catch (e) { /* ignore */ }
}

// Instant "pop" (enlarge then settle) — fire this synchronously on click so it
// happens immediately, regardless of the network round-trip.
function popButton(btn) {
    btn.classList.remove("atc-pop");
    void btn.offsetWidth;            // restart the animation
    btn.classList.add("atc-pop");
}

function flashAdded(btn) {
    if (!btn.dataset.label) btn.dataset.label = btn.textContent;
    btn.textContent = "Added ✓";
    btn.classList.add("atc-added");
    popButton(btn);

    const ring = document.createElement("span");
    ring.className = "btn-ring";
    ring.setAttribute("aria-hidden", "true");
    btn.appendChild(ring);
    setTimeout(function() { if (ring.parentNode) ring.remove(); }, 650);

    clearTimeout(btn._restore);
    btn._restore = setTimeout(function() {
        btn.textContent = btn.dataset.label;
        btn.classList.remove("atc-added", "atc-pop");
    }, 1300);
}

function flashError(btn) {
    if (!btn.dataset.label) btn.dataset.label = btn.textContent;
    btn.textContent = "Try again";
    btn.classList.remove("atc-shake");
    void btn.offsetWidth;
    btn.classList.add("atc-shake");
    clearTimeout(btn._restore);
    btn._restore = setTimeout(function() {
        btn.textContent = btn.dataset.label;
        btn.classList.remove("atc-shake");
    }, 1400);
}

function addToCart(product, variant, image) {
    return fetch("http://127.0.0.1:5001/cart", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            product_name: cartName(product, variant),
            price: product.price,
            image: image || product.image
        })
    })
    .then(function(response) {
        if (!response.ok) throw new Error("HTTP " + response.status);
        return response.json();
    });
}

function openModal(product, initialLabel) {
    if (!productModal || !modalImage) return;   // page has no modal (e.g. cart)
    modalImage.src = "images/" + product.image;
    modalImage.alt = product.name;
    modalName.textContent = product.name;
    modalPrice.textContent = "₹" + product.price;

    const existing = document.querySelector("#modalVariants");
    if (existing) existing.remove();

    let modalVariants = null;
    if (product.variants && product.variants.length > 0) {
        modalVariants = buildVariantList(product, function(file) {
            setProductImage(modalImage, product, file);
        }, initialLabel);
        modalVariants.el.id = "modalVariants";
        modalPrice.insertAdjacentElement("afterend", modalVariants.el);
        setProductImage(modalImage, product, modalVariants.getImage());
    }

    modalAddToCart.textContent = "Add to Cart";
    modalAddToCart.classList.remove("atc-added", "atc-pop", "atc-shake");

    modalAddToCart.onclick = function() {
        popButton(modalAddToCart);           // immediate feedback, every click
        const variant = modalVariants ? modalVariants.getSelected() : null;
        const image = modalVariants ? modalVariants.getImage() : product.image;
        primeAudio();
        addToCart(product, variant, image)
            .then(function() {
                playAddToCartSound();
                flashAdded(modalAddToCart);
                setTimeout(function() { productModal.classList.remove("active"); }, 600);
            })
            .catch(function(err) {
                console.error("Add to cart failed:", err);
                flashError(modalAddToCart);
            });
    };

    productModal.classList.add("active");
}

function renderProduct(product, container) {
    const card = document.createElement("div");
    card.classList.add("product-card");

    card.innerHTML = `
    <img src="images/${product.image}" alt="${product.name}" class="product-image">
    <h3>${product.name}</h3>
    <p class="price">₹${product.price}</p>
`;

    const productImage = card.querySelector(".product-image");

    let cardVariants = null;
    if (product.variants && product.variants.length > 0) {
        cardVariants = buildVariantList(product, function(file) {
            setProductImage(productImage, product, file);
        });
        card.appendChild(cardVariants.el);
        setProductImage(productImage, product, cardVariants.getImage());
    }

    const addToCartBtn = document.createElement("button");
    addToCartBtn.className = "add-to-cart-btn";
    addToCartBtn.textContent = "Add to Cart";
    card.appendChild(addToCartBtn);

    addToCartBtn.addEventListener("click", function() {
        popButton(addToCartBtn);             // immediate feedback, every click
        const variant = cardVariants ? cardVariants.getSelected() : null;
        const image = cardVariants ? cardVariants.getImage() : product.image;
        primeAudio();
        addToCart(product, variant, image)
            .then(function() {
                playAddToCartSound();
                flashAdded(addToCartBtn);
            })
            .catch(function(err) {
                console.error("Add to cart failed:", err);
                flashError(addToCartBtn);
            });
    });

    productImage.addEventListener("click", function() {
        openModal(product, cardVariants ? cardVariants.getSelected() : null);
    });

    container.appendChild(card);
}


// One free 15ml gift for every ₹1000 in the cart (pick from this list).
const FREE_GIFTS = [
    { name: "Vitamin C Facewash - 15ml", image: "gift-vitc-facewash.jpg" },
    { name: "72HR Hydrating Gel Moisturizer - 15ml", image: "gift-72hr-moisturizer.jpg" },
    { name: "Barrier Repair Moisturizer - 15ml", image: "gift-barrier-repair.jpg" },
    { name: "Strawberry Moisturizer - 15ml", image: "gift-strawberry-moisturizer.jpg" },
    { name: "CICA + Niacinamide Oil Free Moisturizer - 15ml", image: "gift-cica-niacinamide.jpg" }
];
const FREE_GIFT_STEP = 1000;

function giftByName(name) {
    return FREE_GIFTS.filter(function(g) { return g.name === name; })[0] || null;
}

const RECOMMENDED_NAMES = [
    "Sunscreen",
    "Face Toner",
    "Body Care",
    "Moisturizer",
    "Face Serum",
    "Face Wash",
    "Face Mask",
    "Strawberry Dew Tinted Sunscreen SPF 50+ PA++++ With New-Age UV Filters"
];

function renderRecommended(container) {
    products
        .filter(function(product) { return RECOMMENDED_NAMES.includes(product.name); })
        .forEach(function(product) { renderProduct(product, container); });
}

const recommendedGrid = document.querySelector("#recommendedGrid");
if (recommendedGrid) {
    renderRecommended(recommendedGrid);
}

const shopGrid = document.querySelector("#shopGrid");

if (shopGrid) {
    products.forEach(function(product) {
        renderProduct(product, shopGrid);
    });
}

const cartItemsContainer = document.querySelector("#cartItems");
const cartTotalDisplay = document.querySelector("#cartTotal");

if (cartItemsContainer) {
    // Always show "You may also like" on the cart page.
    const cartRecs = document.querySelector("#cartRecommendGrid");
    if (cartRecs) {
        cartRecs.innerHTML = "";
        renderRecommended(cartRecs);
    }

    fetch("http://127.0.0.1:5001/cart")
        .then(response => response.json())
        .then(data => {
            if (!data || data.length === 0) {
                showEmptyCart();
                return;
            }

            let total = 0;

                        data.forEach(function(item) {
                const itemRow = document.createElement("div");
                itemRow.classList.add("cart-item");

                itemRow.innerHTML = `
    <span>${item.product_name}</span>
    <img src="images/${item.image}" alt="${item.product_name}" class="cart-item-image">
    <span>₹${item.price} x ${item.quantity}</span>
    <button class="decrease-btn">−</button>
    <button class="increase-btn">+</button>
    <button class="remove-btn">Remove</button>
`;

const removeBtn = itemRow.querySelector(".remove-btn");
removeBtn.addEventListener("click", function() {
    fetch("http://127.0.0.1:5001/cart/" + item.id, {
        method: "DELETE"
    })
    .then(() => {
        itemRow.remove();
    });
});

const decreaseBtn = itemRow.querySelector(".decrease-btn");
decreaseBtn.addEventListener("click", function() {
    fetch("http://127.0.0.1:5001/cart/" + item.id + "/decrease", {
        method: "PUT"
    })
    .then(() => {
        location.reload();
    });
});

const increaseBtn = itemRow.querySelector(".increase-btn");
increaseBtn.addEventListener("click", function() {
    fetch("http://127.0.0.1:5001/cart/" + item.id + "/increase", {
        method: "PUT"
    })
    .then(() => {
        location.reload();
    });
});

                cartItemsContainer.appendChild(itemRow);

                total = total + (item.price * item.quantity);
            });

            // Store-wide 20% off, shown as a before/after breakdown.
            const SITE_DISCOUNT_PCT = 20;
            const subtotal = total;
            const discountAmt = Math.round(subtotal * SITE_DISCOUNT_PCT / 100);
            const billTotal = subtotal - discountAmt;

            cartTotalDisplay.innerHTML =
                '<span class="bill-row"><span>Subtotal</span><span>₹' + subtotal + '</span></span>' +
                '<span class="bill-row bill-discount"><span>Discount (' + SITE_DISCOUNT_PCT + '% off)</span><span>&minus; ₹' + discountAmt + '</span></span>' +
                '<span class="bill-row bill-grand"><span>Total payable</span><span>₹' + billTotal + '</span></span>' +
                '<span class="bill-note">🎉 You save ₹' + discountAmt + ' (' + SITE_DISCOUNT_PCT + '% off) on this order.</span>';

            setupCheckout(billTotal, data);
        })
        .catch(function(err) {
            console.error("Couldn't load the cart:", err);
            showEmptyCart();
        });
}

// Empty cart (e.g. right after an order is placed): hide the bill/checkout
// and show a friendly note. Recommendations are rendered separately, always.
function showEmptyCart() {
    if (cartTotalDisplay) cartTotalDisplay.hidden = true;

    ["#freeShipping", "#freeGifts", "#prepaidNote", "#checkoutBtn", "#paymentOptions"].forEach(function(sel) {
        const el = document.querySelector(sel);
        if (el) el.hidden = true;
    });

    const msg = document.querySelector("#cartEmptyMsg");
    if (msg) msg.hidden = false;
}

// Checkout section: free-shipping note + payment-method options with the
// standard 5%-off-on-prepaid pricing. `cartItems` is the raw server cart.
function setupCheckout(total, cartItems) {
    const freeShipping = document.querySelector("#freeShipping");
    const prepaidNote = document.querySelector("#prepaidNote");
    const checkoutBtn = document.querySelector("#checkoutBtn");
    const panel = document.querySelector("#paymentOptions");
    if (!checkoutBtn || !panel) return;

    const FREE_SHIP_MIN = 1000;
    if (freeShipping) {
        freeShipping.hidden = false;
        const msg = freeShipping.querySelector("span:last-child");
        if (total >= FREE_SHIP_MIN) {
            freeShipping.classList.remove("locked");
            if (msg) msg.innerHTML = "Woohoo! <strong>Free shipping</strong> on this order";
        } else {
            freeShipping.classList.add("locked");
            const need = FREE_SHIP_MIN - total;
            if (msg) msg.innerHTML = "Add <strong>₹" + need + "</strong> more to unlock <strong>free shipping</strong>";
        }
    }
    checkoutBtn.hidden = false;

    // ---- Free gifts: one per ₹1000, pick from FREE_GIFTS ----
    const giftsWrap = document.querySelector("#freeGifts");
    const giftsHead = document.querySelector("#freeGiftsHead");
    const giftsListEl = document.querySelector("#freeGiftsList");
    const maxGifts = Math.min(Math.floor(total / FREE_GIFT_STEP), FREE_GIFTS.length);
    const allGiftsUnlocked = maxGifts >= FREE_GIFTS.length;
    let chosenGifts = FREE_GIFTS.slice(0, maxGifts).map(function(g) { return g.name; });

    if (giftsWrap && giftsHead && giftsListEl) {
        giftsWrap.hidden = false;
        giftsListEl.innerHTML = "";

        if (maxGifts === 0) {
            giftsHead.textContent = "🎁 Add ₹" + (FREE_GIFT_STEP - total) + " more to unlock a free gift";
        } else if (maxGifts >= FREE_GIFTS.length) {
            giftsHead.textContent = "🎁 All " + FREE_GIFTS.length + " free gifts are yours!";
        } else {
            const toNext = FREE_GIFT_STEP - (total % FREE_GIFT_STEP);
            giftsHead.textContent = "🎁 You've unlocked " + maxGifts + " free gift" +
                (maxGifts > 1 ? "s" : "") + " — pick " + maxGifts +
                " (add ₹" + toNext + " more for another)";
        }

        FREE_GIFTS.forEach(function(gift) {
            const name = gift.name;
            const pill = document.createElement("button");
            pill.type = "button";
            pill.className = "gift-pill";
            pill.dataset.gift = name;
            pill.innerHTML =
                '<img src="images/' + gift.image + '" alt="" onerror="this.remove()">' +
                '<span class="gift-name">' + name + '</span>' +
                '<span class="gift-free">FREE</span>';
            if (chosenGifts.indexOf(name) !== -1) pill.classList.add("selected");
            if (maxGifts === 0) pill.disabled = true;
            if (allGiftsUnlocked) pill.classList.add("locked");   // all 5 free, no choosing

            pill.addEventListener("click", function() {
                if (maxGifts === 0 || allGiftsUnlocked) return;
                const at = chosenGifts.indexOf(name);
                if (at !== -1) {
                    chosenGifts.splice(at, 1);
                    pill.classList.remove("selected");
                } else {
                    if (chosenGifts.length >= maxGifts) {
                        const dropped = chosenGifts.shift();   // swap out the oldest pick
                        const old = giftsListEl.querySelector('.gift-pill[data-gift="' + dropped.replace(/"/g, '\\"') + '"]');
                        if (old) old.classList.remove("selected");
                    }
                    chosenGifts.push(name);
                    pill.classList.add("selected");
                }
            });
            giftsListEl.appendChild(pill);
        });
    }

    function giftOrderItems() {
        return chosenGifts.map(function(nm) {
            const g = giftByName(nm);
            return { product_name: nm + " (Free gift)", price: 0, quantity: 1, image: g ? g.image : "" };
        });
    }

    const discount = Math.round(total * 0.05 * 100) / 100;
    const full = total.toFixed(2);
    const discounted = (total - discount).toFixed(2);
    const off = discount.toFixed(2);

    if (prepaidNote) {
        prepaidNote.hidden = false;
        prepaidNote.textContent = "✨ Extra 5% off on prepaid payment — save ₹" + off + " (pay by UPI, card, wallet or netbanking)";
    }

    const methods = [
        { id: "cod", title: "Cash on delivery", sub: "Pay with cash", price: full },
        { id: "card", title: "Debit/Credit cards", sub: "Visa, Mastercard, RuPay & more", off: off, price: discounted,
          options: ["Visa", "Mastercard", "RuPay", "American Express"] },
        { id: "wallet", title: "Wallets", sub: "Amazon Pay, PhonePe, Mobikwik & more", off: off, price: discounted,
          options: ["Amazon Pay", "PhonePe", "Mobikwik"] },
        { id: "netbanking", title: "Netbanking", sub: "Select from a list of banks", off: off, price: discounted,
          options: ["HDFC Bank", "ICICI Bank", "State Bank of India", "Axis Bank", "Kotak Mahindra Bank", "Punjab National Bank", "Bank of Baroda", "Yes Bank"] },
        { id: "paylater", title: "Pay Later", sub: "LazyPay, Simpl & more", price: full,
          options: ["LazyPay", "Simpl", "ICICI PayLater"] }
    ];

    function optionsMarkup(m) {
        if (!m.options) return "";
        return '<select class="pay-select" data-for="' + m.id + '" hidden>' +
            m.options.map(function(o) { return '<option>' + o + '</option>'; }).join("") +
            '</select>';
    }

    panel.innerHTML =
        '<h3>Choose a payment method</h3>' +
        methods.map(function(m, i) {
            return '<label class="pay-option">' +
                '<input type="radio" name="pay" value="' + m.id + '"' + (i === 0 ? ' checked' : '') + '>' +
                '<span class="pay-body">' +
                    '<span class="pay-title">' + m.title + '</span>' +
                    '<span class="pay-sub">' + m.sub + '</span>' +
                    (m.off ? '<span class="pay-off">Extra 5% off · Save ₹' + m.off + '</span>' : '') +
                    optionsMarkup(m) +
                '</span>' +
                '<span class="pay-price">₹' + m.price + '</span>' +
            '</label>';
        }).join('') +
        '<button class="pay-btn" id="payBtn" type="button">Place Order</button>';

    const payBtn = panel.querySelector("#payBtn");

    function payBtnLabel(m) {
        return m.id === "cod" ? "Place Order" : "Pay ₹" + m.price;
    }

    function syncSelects(methodId) {
        panel.querySelectorAll(".pay-select").forEach(function(sel) {
            sel.hidden = (sel.dataset.for !== methodId);
        });
    }

    panel.querySelectorAll('input[name="pay"]').forEach(function(radio) {
        radio.addEventListener("change", function() {
            const m = methods.filter(function(x) { return x.id === radio.value; })[0];
            payBtn.textContent = payBtnLabel(m);
            syncSelects(radio.value);
        });
    });
    syncSelects("cod");
    payBtn.addEventListener("click", function() {
        const checked = panel.querySelector('input[name="pay"]:checked');
        const m = methods.filter(function(x) { return x.id === checked.value; })[0];

        const sel = panel.querySelector('.pay-select[data-for="' + m.id + '"]');
        const subLabel = (sel && !sel.hidden && sel.value) ? sel.value : "";
        const methodText = m.title + (subLabel ? " · " + subLabel : "");

        // Order = the paid cart items + any free gifts (₹0).
        const orderItems = (cartItems || []).concat(giftOrderItems());

        // Snapshot the exact items being ordered so the order is recorded
        // reliably, independent of the backend being reachable later.
        try {
            localStorage.setItem("dk_pending_order", JSON.stringify({
                items: orderItems,
                amount: m.price,
                method: methodText
            }));
        } catch (e) { /* storage unavailable */ }

        if (m.id === "cod") {
            saveOrder(orderItems, m.price, methodText);
            (cartItems || []).forEach(function(it) {
                fetch("http://127.0.0.1:5001/cart/" + it.id, { method: "DELETE" }).catch(function() {});
            });
            try { localStorage.removeItem("dk_pending_order"); } catch (e) {}
            payBtn.disabled = true;
            const success = document.querySelector("#orderSuccess");
            if (success) success.hidden = false;   // "Order Placed!" popup
            return;
        }

        // Prepaid: go to the PIN payment page with the amount + chosen method.
        window.location.href = "payment.html?amount=" + encodeURIComponent(m.price) +
            "&method=" + encodeURIComponent(methodText);
    });

    checkoutBtn.addEventListener("click", function() {
        panel.hidden = !panel.hidden;
        checkoutBtn.textContent = panel.hidden ? "Checkout" : "Hide payment options";
        if (!panel.hidden) {
            panel.scrollIntoView({ behavior: "smooth", block: "nearest" });
        }
    });
}

// ---- Payment page: PIN entry -> tick animation -> "Order Placed" popup ----
const pinForm = document.querySelector("#pinForm");
if (pinForm) {
    const params = new URLSearchParams(window.location.search);
    const amount = params.get("amount") || "0.00";
    const method = params.get("method") || "Prepaid payment";

    document.querySelectorAll("#payAmount, #payAmount2").forEach(function(el) {
        el.textContent = amount;
    });
    const methodLabel = document.querySelector("#payMethodLabel");
    if (methodLabel) methodLabel.textContent = method;

    const boxes = Array.prototype.slice.call(document.querySelectorAll(".pin-box"));
    const pinError = document.querySelector("#pinError");

    boxes.forEach(function(box, i) {
        box.addEventListener("input", function() {
            box.value = box.value.replace(/\D/g, "").slice(0, 1);
            if (pinError) pinError.hidden = true;
            if (box.value && i < boxes.length - 1) boxes[i + 1].focus();
        });
        box.addEventListener("keydown", function(e) {
            if (e.key === "Backspace" && !box.value && i > 0) boxes[i - 1].focus();
        });
    });
    if (boxes[0]) boxes[0].focus();

    pinForm.addEventListener("submit", function(e) {
        e.preventDefault();
        const pin = boxes.map(function(b) { return b.value; }).join("");
        if (pin.length < boxes.length) {
            if (pinError) pinError.hidden = false;
            return;
        }
        const btn = pinForm.querySelector("button");
        btn.classList.remove("atc-pop");
        void btn.offsetWidth;                // restart the pop animation
        btn.classList.add("atc-pop");
        btn.disabled = true;
        setTimeout(placeOrderAndShowSuccess, 260);
    });
}

function placeOrderAndShowSuccess() {
    const success = document.querySelector("#orderSuccess");
    if (success) success.hidden = false;     // CSS animates it in on display change

    const params = new URLSearchParams(window.location.search);
    let amount = params.get("amount") || "0.00";
    let method = params.get("method") || "Prepaid payment";
    let items = [];

    // Prefer the snapshot taken on the cart page (reliable even if the
    // backend is down); fall back to the URL params.
    try {
        const pending = JSON.parse(localStorage.getItem("dk_pending_order") || "null");
        if (pending) {
            if (Array.isArray(pending.items)) items = pending.items;
            if (pending.amount) amount = pending.amount;
            if (pending.method) method = pending.method;
        }
    } catch (e) { /* ignore */ }

    saveOrder(items, amount, method);
    try { localStorage.removeItem("dk_pending_order"); } catch (e) {}

    // Best-effort: empty the server-side cart.
    items.forEach(function(it) {
        if (it && it.id != null) {
            fetch("http://127.0.0.1:5001/cart/" + it.id, { method: "DELETE" }).catch(function() {});
        }
    });
}

// Persist a placed order to localStorage so the Account page can list it.
function saveOrder(items, amount, method) {
    try {
        const orders = JSON.parse(localStorage.getItem("dk_orders") || "[]");
        orders.push({
            id: "DK" + String(Date.now()).slice(-8),
            date: new Date().toISOString(),
            amount: amount,
            method: method,
            items: (items || []).map(function(it) {
                return { name: it.product_name, price: it.price, qty: it.quantity, image: it.image };
            })
        });
        localStorage.setItem("dk_orders", JSON.stringify(orders));
    } catch (e) { /* storage unavailable */ }
}

// ---- Login / Create account page (credentials kept in localStorage) ----
const authForm = document.querySelector("#authForm");
if (authForm && localStorage.getItem("dk_current_user")) {
    // Already signed in — skip the login screen.
    window.location.replace("index.html");
} else if (authForm) {
    const el = {
        title: document.querySelector("#authTitle"),
        sub: document.querySelector("#authSub"),
        user: document.querySelector("#authUser"),
        pass: document.querySelector("#authPass"),
        confirmField: document.querySelector("#authConfirmField"),
        confirm: document.querySelector("#authConfirm"),
        error: document.querySelector("#authError"),
        btn: document.querySelector("#authBtn"),
        togglePrompt: document.querySelector("#authTogglePrompt"),
        toggle: document.querySelector("#authToggle"),
        userReqs: document.querySelector("#userReqs"),
        passReqs: document.querySelector("#passReqs")
    };

    // Sign-up requirement checks, keyed to the data-rule attrs in the HTML lists.
    const RULES = {
        ulen: function(u) { return u.length >= 8 && u.length <= 20; },
        plen: function(u, p) { return p.length >= 8; },
        upper: function(u, p) { return /[A-Z]/.test(p); },
        lower: function(u, p) { return /[a-z]/.test(p); },
        digit: function(u, p) { return /[0-9]/.test(p); },
        special: function(u, p) { return /[^A-Za-z0-9]/.test(p); }
    };

    function refreshReqs() {
        const u = el.user.value.trim();
        const p = el.pass.value;
        document.querySelectorAll(".req-list li[data-rule]").forEach(function(li) {
            li.classList.toggle("met", !!RULES[li.dataset.rule](u, p));
        });
    }

    function allReqsMet() {
        const u = el.user.value.trim();
        const p = el.pass.value;
        return Object.keys(RULES).every(function(k) { return RULES[k](u, p); });
    }

    function getUsers() {
        try {
            const u = JSON.parse(localStorage.getItem("dk_users") || "{}");
            return (u && typeof u === "object" && !Array.isArray(u)) ? u : {};
        } catch (e) {
            return {};
        }
    }

    // No accounts yet -> start in "create account" mode.
    let signupMode = Object.keys(getUsers()).length === 0;

    function render() {
        el.error.hidden = true;
        el.confirmField.hidden = !signupMode;
        if (el.userReqs) el.userReqs.hidden = !signupMode;
        if (el.passReqs) el.passReqs.hidden = !signupMode;
        el.title.textContent = signupMode ? "Create Account" : "Sign In";
        el.sub.textContent = signupMode
            ? "Join Dot & Key in a few seconds"
            : "Welcome back to Dot & Key";
        el.btn.textContent = signupMode ? "Create Account" : "Sign In";
        el.togglePrompt.textContent = signupMode ? "Already have an account?" : "New to Dot & Key?";
        el.toggle.textContent = signupMode ? "Sign in" : "Create an account";
        el.pass.setAttribute("autocomplete", signupMode ? "new-password" : "current-password");
        if (signupMode) refreshReqs();
    }
    render();

    el.toggle.addEventListener("click", function(e) {
        e.preventDefault();
        signupMode = !signupMode;
        render();
    });

    el.user.addEventListener("input", refreshReqs);
    el.pass.addEventListener("input", refreshReqs);

    function fail(msg) {
        el.error.textContent = msg;
        el.error.hidden = false;
        el.error.classList.remove("shake");
        void el.error.offsetWidth;          // restart the shake
        el.error.classList.add("shake");
    }

    // Find the stored username that matches `typed` ignoring case; null if none.
    function matchUsername(users, typed) {
        const lower = typed.toLowerCase();
        return Object.keys(users).find(function(k) {
            return k.toLowerCase() === lower;
        }) || null;
    }

    authForm.addEventListener("submit", function(e) {
        e.preventDefault();
        const typed = el.user.value.trim();
        const p = el.pass.value;
        if (!typed || !p) { fail("Please enter your username and password to continue."); return; }

        const users = getUsers();
        const existingKey = matchUsername(users, typed);   // works for any casing

        let sessionUser;

        if (signupMode) {
            if (existingKey) {
                fail("An account with this username already exists. Please sign in instead.");
                return;
            }
            if (!allReqsMet()) {
                fail("Please make sure your username and password meet all the requirements listed below.");
                refreshReqs();
                return;
            }
            if (p !== el.confirm.value) {
                fail("Those passwords don't match. Please re-enter your password.");
                return;
            }
            users[typed] = p;
            try { localStorage.setItem("dk_users", JSON.stringify(users)); } catch (err) {}
            sessionUser = typed;
        } else {
            if (!existingKey) {
                fail("We couldn't find an account with that username. Please check it, or create a new account.");
                return;
            }
            if (users[existingKey] !== p) {
                fail("The password you entered is incorrect. Please try again.");
                return;
            }
            sessionUser = existingKey;
        }

        try {
            localStorage.setItem("dk_current_user", sessionUser);
            localStorage.setItem("dk_welcome", "1");   // one-shot flag for the home greeting
        } catch (err) {}
        window.location.href = "index.html";
    });
}

// ---- Home page: one-shot "Welcome back" greeting right after sign-in ----
const welcomeToast = document.querySelector("#welcomeToast");
if (welcomeToast) {
    let justLoggedIn = false;
    let user = null;
    try {
        user = localStorage.getItem("dk_current_user");
        if (localStorage.getItem("dk_welcome")) {
            localStorage.removeItem("dk_welcome");
            justLoggedIn = true;
        }
    } catch (e) { /* ignore */ }

    if (justLoggedIn && user) {
        welcomeToast.textContent = "👋 Welcome back, " + user + "!";
        welcomeToast.hidden = false;
        setTimeout(function() { welcomeToast.classList.add("fade-out"); }, 4000);
        setTimeout(function() {
            welcomeToast.hidden = true;
            welcomeToast.classList.remove("fade-out");
        }, 4600);
    }
}

// ---- Account page: list previous orders (requires sign-in) ----
const ordersList = document.querySelector("#ordersList");
if (ordersList && !localStorage.getItem("dk_current_user")) {
    window.location.replace("login.html");
} else if (ordersList) {
    const nameEl = document.querySelector("#accountUser");
    if (nameEl) nameEl.textContent = localStorage.getItem("dk_current_user");
    const logout = document.querySelector("#logoutLink");
    if (logout) {
        logout.addEventListener("click", function(e) {
            e.preventDefault();
            localStorage.removeItem("dk_current_user");
            window.location.href = "login.html";
        });
    }

    let orders = [];
    try { orders = JSON.parse(localStorage.getItem("dk_orders") || "[]"); } catch (e) {}
    orders = orders.slice().reverse();   // newest first

    if (orders.length === 0) {
        const empty = document.querySelector("#ordersEmpty");
        if (empty) empty.hidden = false;
    } else {
        orders.forEach(function(o) {
            const d = new Date(o.date);
            const orderedOn = d.toLocaleDateString("en-IN", { weekday: "short", day: "numeric", month: "long", year: "numeric" });
            const ageDays = (Date.now() - d.getTime()) / 86400000;
            const status = ageDays > 6 ? "Delivered" : (ageDays > 2 ? "Out for delivery" : "Order confirmed");

            const card = document.createElement("div");
            card.className = "order-card";
            card.innerHTML =
                '<div class="order-head">' +
                    '<div>' +
                        '<span class="order-id">Order ' + o.id + '</span>' +
                        '<span class="order-month">Ordered on ' + orderedOn + '</span>' +
                    '</div>' +
                    '<span class="order-status' + (status === "Delivered" ? " is-delivered" : "") + '">' + status + '</span>' +
                '</div>' +
                '<p class="order-items-label">Previous order items</p>' +
                '<div class="order-items">' +
                    (o.items && o.items.length ? o.items.map(function(it) {
                        return '<div class="order-item">' +
                            '<img src="images/' + it.image + '" alt="" onerror="this.remove()">' +
                            '<span class="order-item-name">' + it.name + '</span>' +
                            '<span class="order-item-qty">₹' + it.price + ' × ' + it.qty + '</span>' +
                        '</div>';
                    }).join("") : '<div class="order-item"><span class="order-item-name">Items not recorded for this order</span></div>') +
                '</div>' +
                '<div class="order-foot">' +
                    '<span>Paid via ' + o.method + '</span>' +
                    '<span class="order-total">Total &#8377;' + o.amount + '</span>' +
                '</div>';
            ordersList.appendChild(card);
        });
    }
}
