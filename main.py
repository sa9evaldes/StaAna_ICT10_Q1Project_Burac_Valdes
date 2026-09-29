

"use strict";
var KEY = "ohare-air-trees-v3";
var products = [];
var orderNo = 0;

var CAT_ORDER = ["Bottle Air", "Tree Types", "Air Accessories"];
var CAT_CODE = { "Bottle Air": "AIR", "Tree Types": "TRE", "Air Accessories": "ACC" };

var SEED = [
    ["Bottle Air", "Sniff Pack (one breath)", 50, 200],
    ["Bottle Air", "Breath Bottle", 120, 100],
    ["Bottle Air", "Lungful Jug", 300, 40],
    ["Bottle Air", "Mount Fuji Air", 180, 60],
    ["Tree Types", "Disco Tree", 2400, 25],
    ["Tree Types", "Decorative Tree", 1500, 12],
    ["Tree Types", "Robo Tree", 3200, 8],
    ["Air Accessories", "Bottle Cap Set", 35, 150]
];

function $(id) { return document.getElementById(id); }
function esc(t) { return String(t).replace(/[&<>"']/g, function (c) { return {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"}[c]; }); }
function peso(n) { return "₱" + Number(n).toLocaleString("en-PH", { minimumFractionDigits: 0, maximumFractionDigits: 2 }); }
function letters(s, n) { return s.replace(/[^a-z0-9]/gi, "").toUpperCase().slice(0, n); }

/* ----- storage (guarded) ----- */
function save() { try { localStorage.setItem(KEY, JSON.stringify({ products: products, orderNo: orderNo })); } catch (e) {} }
function load() {
    try {
        var d = JSON.parse(localStorage.getItem(KEY) || "null");
        if (d && Array.isArray(d.products) && d.products.length) { products = d.products; orderNo = d.orderNo || 0; return; }
    } catch (e) {}
    products = [];
    SEED.forEach(function (s) { addProduct(s[0], s[1], s[2], s[3]); });
}

/* ----- SKU logic ----- */
function makeSKU(category, name) {
    var prefix = (CAT_CODE[category] || letters(category, 3)) + "-" + letters(name, 3);
    var n = 1, sku;
    do { sku = prefix + "-" + String(n).padStart(3, "0"); n++; } while (products.some(function (p) { return p.sku === sku; }));
    return sku;
}
function addProduct(category, name, price, stock) {
    var p = { sku: makeSKU(category, name), category: category, name: name, price: price, stock: stock };
    products.push(p);
    return p;
}

function generate() {
    var out = $("sku_output");
    var category = $("category").value;
    var name = $("product_name").value.trim();
    var price = parseFloat($("price").value);
    var qty = $("quantity").value === "" ? NaN : parseInt($("quantity").value, 10);
    var problem = "";
    if (letters(name, 3).length < 3) problem = "Product name needs at least 3 letters or numbers.";
    else if (isNaN(price) || price <= 0) problem = "Enter a price greater than 0.";
    else if (isNaN(qty) || qty < 0) problem = "Enter a stock quantity of 0 or more.";
    if (problem) { out.innerHTML = '<div class="result-box err">' + esc(problem) + "</div>"; return; }

    var p = addProduct(category, name, price, qty);
    save();
    out.innerHTML = '<div class="result-box"><div class="sku-code sku-big">' + esc(p.sku) + '</div>' +
        '<div class="small">' + esc(p.name) + " · " + peso(p.price) + " · " + p.stock + ' in stock. Now in the checkout catalog.</div></div>';
    $("product_name").value = ""; $("price").value = ""; $("quantity").value = "";
    renderInventory();
}

function removeProduct(sku) {
    products = products.filter(function (p) { return p.sku !== sku; });
    save(); renderInventory();
}

/* ----- rendering ----- */
function renderInventory() {
    var box = $("inventory");
    if (!products.length) { box.innerHTML = '<p class="muted">No products yet.</p>'; return; }
    var rows = products.map(function (p) {
        return "<tr><td class='sku-code'>" + esc(p.sku) + "</td><td>" + esc(p.name) + "</td><td class='r'>" + peso(p.price) +
            "</td><td class='r'>" + p.stock + "</td><td class='r'><button class='linkbtn' type='button' data-remove='" + esc(p.sku) + "'>Remove</button></td></tr>";
    }).join("");
    box.innerHTML = '<div class="tscroll"><table><thead><tr><th>SKU</th><th>Product</th><th class="r">Price</th><th class="r">Stock</th><th></th></tr></thead><tbody>' + rows + "</tbody></table></div>";
}

function menuItemHTML(p, i) {
    var out = p.stock <= 0;
    var stockText = out ? "Sold out" : p.stock + " left";
    return '<div class="menu-item' + (out ? " off" : "") + '">' +
        '<div class="menu-left"><input type="checkbox" id="chk' + i + '" data-sku="' + esc(p.sku) + '"' + (out ? " disabled" : "") + '>' +
        '<div><label for="chk' + i + '">' + esc(p.name) + '</label><span class="sku-code">' + esc(p.sku) + "</span></div></div>" +
        '<div class="menu-right"><input class="qty" type="number" min="1" value="1" aria-label="Quantity for ' + esc(p.name) + '" disabled>' +
        '<div><span class="price">' + peso(p.price) + '</span><span class="stock' + (!out && p.stock <= 5 ? " low" : "") + '">' + stockText + "</span></div></div></div>";
}

function renderMenu() {
    var box = $("menu");
    if (!products.length) { box.innerHTML = '<p class="muted">The catalog is empty. Add products on the SKU Generator tab.</p>'; return; }
    var html = "";
    CAT_ORDER.forEach(function (cat) {
        var items = [];
        products.forEach(function (p, i) { if (p.category === cat) items.push(menuItemHTML(p, i)); });
        if (items.length) html += "<h6>" + esc(cat) + "</h6>" + items.join("");
    });
    box.innerHTML = html;
}

function showView(which) {
    var sku = which === "sku";
    $("skuView").hidden = !sku; $("orderView").hidden = sku;
    if (sku) { $("tabSku").setAttribute("aria-current", "page"); $("tabOrder").removeAttribute("aria-current"); renderInventory(); }
    else { $("tabOrder").setAttribute("aria-current", "page"); $("tabSku").removeAttribute("aria-current"); renderMenu(); }
}

/* ----- order ----- */
function createOrder() {
    var show = $("show");
    var lines = [];
    var errors = [];
    var smog = $("smog").checked;
    var checks = document.querySelectorAll("#menu input[type=checkbox]:checked");
    checks.forEach(function (c) {
        var p = products.find(function (x) { return x.sku === c.getAttribute("data-sku"); });
        var q = parseInt(c.closest(".menu-item").querySelector(".qty").value, 10);
        if (!p) return;
        if (isNaN(q) || q < 1) errors.push("Quantity for " + p.name + " must be at least 1.");
        else if (q > p.stock) errors.push("Only " + p.stock + " " + p.name + " left in stock.");
        else lines.push({ p: p, q: q });
    });
    if (!checks.length) errors.push("Select at least one item.");
    if (errors.length) { show.innerHTML = '<div class="result-box err">' + errors.map(esc).join("<br>") + "</div>"; return; }

    var total = 0, surged = false;
    var rows = lines.map(function (l) {
        var unit = l.p.price;
        if (smog && l.p.category === "Bottle Air") { unit = Math.round(unit * 1.5 * 100) / 100; surged = true; }
        var sub = unit * l.q; total += sub; l.p.stock -= l.q;
        return "<tr><td>" + esc(l.p.name) + "<br><span class='sku-code small'>" + esc(l.p.sku) + "</span></td><td class='r'>" + l.q +
            "</td><td class='r'>" + peso(unit) + "</td><td class='r'>" + peso(sub) + "</td></tr>";
    }).join("");
    orderNo++;
    save();
    show.innerHTML = '<div class="result-box"><strong>Receipt #' + String(orderNo).padStart(4, "0") + "</strong>" +
        '<div class="tscroll"><table><thead><tr><th>Item</th><th class="r">Qty</th><th class="r">Price</th><th class="r">Subtotal</th></tr></thead><tbody>' + rows +
        '<tr class="total-row"><td colspan="3">Total</td><td class="r total">' + peso(total) + "</td></tr></tbody></table></div>" +
        (surged ? '<p class="tagline">Smog day pricing applied to bottle air.</p>' : "") +
        '<p class="tagline">Thank you for breathing with O\'Hare\'s.</p></div>';
    renderMenu();
}

/* ----- wiring ----- */
$("tabSku").addEventListener("click", function () { showView("sku"); });
$("tabOrder").addEventListener("click", function () { showView("order"); });
$("genBtn").addEventListener("click", generate);
$("orderBtn").addEventListener("click", createOrder);
$("inventory").addEventListener("click", function (e) {
    var b = e.target.closest("[data-remove]");
    if (b) removeProduct(b.getAttribute("data-remove"));
});
$("menu").addEventListener("change", function (e) {
    if (e.target.matches("input[type=checkbox]")) {
        e.target.closest(".menu-item").querySelector(".qty").disabled = !e.target.checked;
    }
});

load();
save();
showView("sku");
