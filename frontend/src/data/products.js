// Product catalog (moved from the old script.js).
// `image` values are file names inside public/images/.
// A product with `variants` shows selectable types/shades; all variants share the price.
 
export const products = [
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