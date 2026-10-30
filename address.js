/* ============================================================
   address.js — Delivery address module for Dot & Key
   ------------------------------------------------------------
   Self-contained. Exposes one global object: window.DKAddress
   Nothing else in the project is modified by this file.
   ============================================================ */

(function () {
    "use strict";

    var STORE_KEY = "dk_addresses";

    var STATES = [
        "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
        "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
        "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram",
        "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu",
        "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal",
        "Andaman and Nicobar Islands", "Chandigarh",
        "Dadra and Nagar Haveli and Daman and Diu", "Delhi", "Jammu and Kashmir",
        "Ladakh", "Lakshadweep", "Puducherry"
    ];

    function currentUser() {
        try { return localStorage.getItem("dk_current_user") || ""; }
        catch (e) { return ""; }
    }

    function readStore() {
        try { return JSON.parse(localStorage.getItem(STORE_KEY) || "{}"); }
        catch (e) { return {}; }
    }

    function writeStore(store) {
        try { localStorage.setItem(STORE_KEY, JSON.stringify(store)); }
        catch (e) { /* storage unavailable */ }
    }

    function esc(s) {
        return String(s == null ? "" : s)
            .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;").replace(/'/g, "&#39;");
    }

    function get() {
        var user = currentUser();
        if (!user) return null;
        var addr = readStore()[user];
        return addr && addr.fullName ? addr : null;
    }

    function save(addr) {
        var user = currentUser();
        if (!user) return;
        var store = readStore();
        store[user] = addr;
        writeStore(store);
    }

    function format(a) {
        if (!a) return "";
        var parts = [
            a.flat,
            a.area,
            a.landmark ? "Landmark: " + a.landmark : "",
            [a.city, a.state].filter(Boolean).join(", "),
            a.pincode ? "PIN " + a.pincode : ""
        ];
        return parts.filter(Boolean).join(", ");
    }

    function formatHtml(a) {
        if (!a) return "";
        return '<span class="addr-name">' + esc(a.fullName) +
               (a.type ? ' <span class="addr-tag">' + esc(a.type) + '</span>' : '') +
               '</span>' +
               '<span class="addr-line">' + esc(format(a)) + '</span>' +
               '<span class="addr-phone">Phone: ' + esc(a.mobile) + '</span>';
    }

    var RULES = {
        fullName: function (v) {
            if (!v.trim()) return "Full name is required";
            if (v.trim().length < 3) return "Name looks too short";
            return "";
        },
        mobile: function (v) {
            if (!v.trim()) return "Mobile number is required";
            if (!/^[6-9]\d{9}$/.test(v.trim())) return "Enter a valid 10-digit mobile number";
            return "";
        },
        pincode: function (v) {
            if (!v.trim()) return "Pincode is required";
            if (!/^[1-9]\d{5}$/.test(v.trim())) return "Enter a valid 6-digit pincode";
            return "";
        },
        flat: function (v) {
            if (!v.trim()) return "Flat / House no. and building name are required";
            return "";
        },
        area: function (v) {
            if (!v.trim()) return "Area / street / locality is required";
            return "";
        },
        city: function (v) {
            if (!v.trim()) return "City / town is required";
            return "";
        },
        state: function (v) {
            if (!v.trim()) return "Please select a state";
            return "";
        },
        landmark: function () { return ""; }
    };

    function buildModal(innerHtml, className) {
        var overlay = document.createElement("div");
        overlay.className = "addr-overlay " + (className || "");
        overlay.innerHTML = '<div class="addr-modal">' + innerHtml + '</div>';
        document.body.appendChild(overlay);

        overlay.addEventListener("click", function (e) {
            if (e.target === overlay) close();
        });

        function close() {
            if (overlay.parentNode) overlay.parentNode.removeChild(overlay);
            document.body.classList.remove("addr-modal-open");
        }

        document.body.classList.add("addr-modal-open");
        return { overlay: overlay, close: close };
    }

    function openForm(opts) {
        opts = opts || {};
        var existing = opts.existing || {};

        function field(name, label, placeholder, attrs, optional) {
            return '' +
                '<label class="addr-field">' +
                    '<span class="addr-label">' + esc(label) +
                        (optional ? ' <em>(optional)</em>' : '') + '</span>' +
                    '<input type="text" name="' + name + '" ' + (attrs || '') +
                        ' placeholder="' + esc(placeholder) + '"' +
                        ' value="' + esc(existing[name] || "") + '">' +
                    '<span class="addr-error" data-for="' + name + '"></span>' +
                '</label>';
        }

        var stateOptions = '<option value="">Select state</option>' +
            STATES.map(function (s) {
                var sel = (existing.state === s) ? ' selected' : '';
                return '<option value="' + esc(s) + '"' + sel + '>' + esc(s) + '</option>';
            }).join("");

        var types = ["Home", "Work", "Other"];
        var typeChips = types.map(function (t) {
            var checked = ((existing.type || "Home") === t) ? ' checked' : '';
            return '<label class="addr-chip">' +
                       '<input type="radio" name="type" value="' + t + '"' + checked + '>' +
                       '<span>' + t + '</span>' +
                   '</label>';
        }).join("");

        var html =
            '<div class="addr-modal-head">' +
                '<h3>' + esc(opts.title || "Add delivery address") + '</h3>' +
                '<button type="button" class="addr-close" aria-label="Close">&times;</button>' +
            '</div>' +
            '<form class="addr-form" novalidate>' +
                field("fullName", "Full name", "Name of the person receiving the order",
                      'autocomplete="name"') +
                field("mobile", "Mobile number", "10-digit mobile number",
                      'inputmode="numeric" maxlength="10" autocomplete="tel"') +
                field("pincode", "Pincode", "6-digit PIN code",
                      'inputmode="numeric" maxlength="6" autocomplete="postal-code"') +
                field("flat", "Flat / House no., Building, Apartment", "e.g. Flat 402, Sai Residency",
                      'autocomplete="address-line1"') +
                field("area", "Area, Street, Sector, Village", "e.g. Hi-Tech City Road, Madhapur",
                      'autocomplete="address-line2"') +
                field("landmark", "Landmark", "e.g. Near Cyber Towers", '', true) +
                field("city", "Town / City", "e.g. Hyderabad",
                      'autocomplete="address-level2"') +
                '<label class="addr-field">' +
                    '<span class="addr-label">State</span>' +
                    '<select name="state" autocomplete="address-level1">' + stateOptions + '</select>' +
                    '<span class="addr-error" data-for="state"></span>' +
                '</label>' +
                '<div class="addr-field">' +
                    '<span class="addr-label">Address type</span>' +
                    '<div class="addr-chips">' + typeChips + '</div>' +
                '</div>' +
                '<div class="addr-actions">' +
                    '<button type="button" class="addr-btn-ghost addr-cancel">Cancel</button>' +
                    '<button type="submit" class="addr-btn">Save address</button>' +
                '</div>' +
            '</form>';

        var modal = buildModal(html, "addr-overlay-form");
        var form = modal.overlay.querySelector(".addr-form");

        function cancel() {
            modal.close();
            if (opts.onCancel) opts.onCancel();
        }
        modal.overlay.querySelector(".addr-close").addEventListener("click", cancel);
        modal.overlay.querySelector(".addr-cancel").addEventListener("click", cancel);

        ["mobile", "pincode"].forEach(function (name) {
            var input = form.querySelector('[name="' + name + '"]');
            input.addEventListener("input", function () {
                input.value = input.value.replace(/\D/g, "");
            });
        });

        function showError(name, message) {
            var slot = form.querySelector('.addr-error[data-for="' + name + '"]');
            var input = form.querySelector('[name="' + name + '"]');
            if (slot) slot.textContent = message;
            if (input) input.classList.toggle("has-error", !!message);
        }

        Object.keys(RULES).forEach(function (name) {
            var input = form.querySelector('[name="' + name + '"]');
            if (!input) return;
            input.addEventListener("blur", function () {
                showError(name, RULES[name](input.value));
            });
        });

        form.addEventListener("submit", function (e) {
            e.preventDefault();

            var values = {};
            var firstBad = null;

            Object.keys(RULES).forEach(function (name) {
                var input = form.querySelector('[name="' + name + '"]');
                var value = input ? input.value.trim() : "";
                values[name] = value;
                var error = RULES[name](value);
                showError(name, error);
                if (error && !firstBad) firstBad = input;
            });

            if (firstBad) {
                firstBad.focus();
                return;
            }

            var typeEl = form.querySelector('input[name="type"]:checked');
            values.type = typeEl ? typeEl.value : "Home";
            values.savedAt = new Date().toISOString();

            save(values);
            modal.close();
            if (opts.onSave) opts.onSave(values);
        });

        form.querySelector('[name="fullName"]').focus();
        return modal;
    }

    function openConfirm(addr, onConfirm) {
        var html =
            '<div class="addr-modal-head">' +
                '<h3>Confirm delivery address</h3>' +
                '<button type="button" class="addr-close" aria-label="Close">&times;</button>' +
            '</div>' +
            '<p class="addr-confirm-note">Your order will be delivered to this address. ' +
                'Please check it carefully before continuing.</p>' +
            '<div class="addr-card">' + formatHtml(addr) + '</div>' +
            '<div class="addr-actions">' +
                '<button type="button" class="addr-btn-ghost addr-change">Change address</button>' +
                '<button type="button" class="addr-btn addr-confirm">Deliver here &amp; continue</button>' +
            '</div>';

        var modal = buildModal(html, "addr-overlay-confirm");

        modal.overlay.querySelector(".addr-close").addEventListener("click", modal.close);

        modal.overlay.querySelector(".addr-change").addEventListener("click", function () {
            modal.close();
            openForm({
                existing: addr,
                title: "Edit delivery address",
                onSave: function (updated) { openConfirm(updated, onConfirm); }
            });
        });

        modal.overlay.querySelector(".addr-confirm").addEventListener("click", function () {
            modal.close();
            if (onConfirm) onConfirm(addr);
        });
    }

    function requireAddress(onReady) {
        var addr = get();
        if (addr) {
            openConfirm(addr, onReady);
        } else {
            openForm({
                title: "Add delivery address",
                onSave: function (saved) { openConfirm(saved, onReady); }
            });
        }
    }

    function renderAccount() {
        var box = document.querySelector("#savedAddressBox");
        if (!box) return;

        var addr = get();

        if (!addr) {
            box.innerHTML =
                '<p class="addr-empty">No delivery address saved yet. ' +
                'You can add one here, or when you place your first order.</p>' +
                '<button type="button" class="addr-btn" id="addrAddBtn">Add address</button>';
            box.querySelector("#addrAddBtn").addEventListener("click", function () {
                openForm({ title: "Add delivery address", onSave: renderAccount });
            });
            return;
        }

        box.innerHTML =
            '<div class="addr-card">' + formatHtml(addr) + '</div>' +
            '<button type="button" class="addr-btn-ghost" id="addrEditBtn">Edit address</button>';

        box.querySelector("#addrEditBtn").addEventListener("click", function () {
            openForm({
                existing: addr,
                title: "Edit delivery address",
                onSave: renderAccount
            });
        });
    }

    window.DKAddress = {
        get: get,
        save: save,
        format: format,
        formatHtml: formatHtml,
        openForm: openForm,
        requireAddress: requireAddress,
        renderAccount: renderAccount
    };

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", renderAccount);
    } else {
        renderAccount();
    }
})();