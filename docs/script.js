const PRODUCTS_API = "https://gheymatik.onrender.com/products";
const BRANDS_API = "https://gheymatik.onrender.com/brand-products";

const productsContainer = document.getElementById("productsContainer");
const productCount = document.getElementById("productCount");
const searchInput = document.getElementById("searchInput");
const searchButton = document.getElementById("searchButton");
const categoryButtons = document.getElementById("categoryButtons");

let milkProducts = [];
let brandProducts = {};
let currentCategory = "شیر";
let comparisonGroupsByCategory = {};

const WEIGHT_TOLERANCE = 0.20;


// ===============================
// ابزارهای عمومی
// ===============================

function formatNumber(number) {
    return new Intl.NumberFormat("fa-IR").format(number);
}

function formatPrice(price) {
    return formatNumber(Math.round(Number(price) || 0));
}

function normalizeText(text) {
    return String(text ?? "")
        .toLowerCase()
        .replace(/ي/g, "ی")
        .replace(/ى/g, "ی")
        .replace(/ك/g, "ک")
        .replace(/ۀ/g, "ه")
        .replace(/ة/g, "ه")
        .replace(/\u200c/g, " ")
        .replace(/\s+/g, " ")
        .trim();
}

function normalizeDigits(text) {
    const persian = "۰۱۲۳۴۵۶۷۸۹";
    const arabic = "٠١٢٣٤٥٦٧٨٩";

    return String(text ?? "")
        .replace(/[۰-۹]/g, d => persian.indexOf(d))
        .replace(/[٠-٩]/g, d => arabic.indexOf(d));
}

function escapeHtml(text) {
    return String(text ?? "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function parseNumber(value) {
    if (typeof value === "number") {
        return value;
    }

    const cleaned = normalizeDigits(value)
        .replace(/,/g, "")
        .replace(/٫/g, ".")
        .replace(/[^\d.]/g, "");

    const result = Number(cleaned);

    return Number.isFinite(result) ? result : null;
}

function getQuantity(product) {
    const value = parseNumber(product?.quantity);

    return value && value > 0 ? value : null;
}

function getCount(product) {
    const value = parseNumber(product?.count);

    return value && value > 0 ? value : null;
}

function getPrice(product) {
    return parseNumber(product?.price) || 0;
}


// ===============================
// تخم مرغ
// ===============================

function extractCountFromName(name) {
    const text = normalizeDigits(
        normalizeText(name)
    );

    const patterns = [
        /([0-9]+)\s*عددی/,
        /([0-9]+)\s*عدد/,
        /([0-9]+)\s*تایی/,
        /([0-9]+)\s*قطعه/
    ];

    for (const pattern of patterns) {
        const match = text.match(pattern);

        if (match) {
            return Number(match[1]);
        }
    }

    return null;
}

function extractEggGrade(name) {
    const text = normalizeText(name);

    const match =
        text.match(/گرید\s*([a-z])/i) ||
        text.match(/grade\s*([a-z])/i);

    if (!match) {
        return "";
    }

    return match[1].toUpperCase();
}


// ===============================
// مربا
// ===============================

function getJamFlavor(name) {
    const text = normalizeText(name);

    const flavors = [
        ["توت فرنگی", ["توت فرنگی", "توتفرنگی"]],
        ["آلبالو", ["آلبالو"]],
        ["بالنگ", ["بالنگ"]],
        ["گل محمدی", ["گل محمدی"]],
        ["هویج", ["هویج"]],
        ["تمشک", ["تمشک"]],
        ["انجیر", ["انجیر"]],
        ["به", ["مربای به"]],
        ["هلو", ["هلو"]],
        ["زردآلو", ["زردآلو"]],
        ["آناناس", ["آناناس"]],
        ["سیب", ["سیب"]],
        ["آلو", ["آلو"]],
        ["چهار میوه", ["چهار میوه"]],
        ["مخلوط", ["مخلوط"]]
    ];

    for (const [label, words] of flavors) {
        if (words.some(word => text.includes(word))) {
            return label;
        }
    }

    return null;
}


// ===============================
// پنیر
// ===============================

function getCheeseType(name) {
    const text = normalizeText(name);

    const types = [
        ["موزارلا", ["موزارلا"]],
        ["پارمسان", ["پارمسان"]],
        ["کممبر", ["کممبر"]],
        ["چدار", ["چدار"]],
        ["کبابی", ["کبابی"]],
        ["لبنه", ["لبنه"]],
        ["لیقوان", ["لیقوان"]],
        ["سفید", ["سفید"]],
        ["صبحانه", ["صبحانه"]],
        ["لاکتیکی", ["لاکتیکی"]],
        ["خامه‌ای", ["خامه ای", "خامه‌ای"]]
    ];

    for (const [label, words] of types) {
        if (words.some(word => text.includes(word))) {
            return label;
        }
    }

    return null;
}

function getCheeseFat(name) {
    const text = normalizeText(name);

    if (text.includes("کم چرب")) {
        return "کم چرب";
    }

    if (
        text.includes("پرچرب") ||
        text.includes("پر چرب")
    ) {
        return "پرچرب";
    }

    return "";
}


// ===============================
// کره
// ===============================

function getButterType(name) {
    const text = normalizeText(name);

    if (text.includes("روغن کره")) {
        return "روغن کره";
    }

    if (text.includes("غیر لاکتیکی")) {
        return "غیر لاکتیکی";
    }

    if (text.includes("لاکتیکی")) {
        return "لاکتیکی";
    }

    if (text.includes("حیوانی")) {
        return "حیوانی";
    }

    if (text.includes("بدون نمک")) {
        return "بدون نمک";
    }

    return "کره";
}


// ===============================
// آماده‌سازی محصول
// ===============================

function prepareProduct(category, product, brand) {

    if (!product || !brand || brand === "سایر") {
        return null;
    }

    const name = normalizeText(product.product);

    const prepared = {
        ...product,
        brand,
        price: getPrice(product),
        quantity: getQuantity(product),
        count: getCount(product),
        category
    };


    // پنیر
    if (category === "پنیر") {

        const type = getCheeseType(name);
        const fat = getCheeseFat(name);

        if (!type || !prepared.quantity) {
            return null;
        }

        prepared.signature =
            `${type}|${fat || "نامشخص"}`;

        prepared.title =
            `پنیر ${type}${fat ? ` ${fat}` : ""}`;

        prepared.unitPrice =
            (prepared.price / prepared.quantity) * 100;

        return prepared;
    }


    // کره
    if (category === "کره") {

        const type = getButterType(name);

        if (!prepared.quantity) {
            return null;
        }

        prepared.signature = type;

        prepared.title = `کره ${type}`;

        prepared.unitPrice =
            (prepared.price / prepared.quantity) * 100;

        return prepared;
    }


    // مربا
    if (category === "مربا") {

        const flavor = getJamFlavor(name);

        if (!flavor || !prepared.quantity) {
            return null;
        }

        prepared.signature = flavor;

        prepared.title = `مربای ${flavor}`;

        prepared.unitPrice =
            (prepared.price / prepared.quantity) * 100;

        return prepared;
    }


    // تخم مرغ
    if (category === "تخم مرغ") {

        const count =
            prepared.count ||
            extractCountFromName(name);

        const grade =
            extractEggGrade(name);

        if (!count || !grade) {
            return null;
        }

        if (
            name.includes("مایع") ||
            name.includes("سفیده")
        ) {
            return null;
        }

        prepared.count = count;
        prepared.grade = grade;

        prepared.signature =
            `${grade}|${count}`;

        prepared.title =
            `تخم‌مرغ گرید ${grade} ${count} عددی`;

        prepared.unitPrice =
            prepared.price / count;

        return prepared;
    }

    return null;
}


// ===============================
// گروه‌بندی وزن
// ===============================

function clusterByQuantity(items) {

    const sorted = [...items]
        .filter(item => item.quantity)
        .sort(
            (a, b) =>
                a.quantity - b.quantity
        );

    const clusters = [];

    for (const item of sorted) {

        const last =
            clusters[clusters.length - 1];

        if (!last) {

            clusters.push({
                baseQuantity: item.quantity,
                items: [item]
            });

            continue;
        }

        const difference =
            Math.abs(
                item.quantity -
                last.baseQuantity
            ) / last.baseQuantity;

        if (difference <= WEIGHT_TOLERANCE) {
            last.items.push(item);
        } else {
            clusters.push({
                baseQuantity: item.quantity,
                items: [item]
            });
        }
    }

    return clusters;
}


// ===============================
// بهترین محصول هر برند
// ===============================

function chooseBestPerBrand(items) {

    const byBrand = {};

    items.forEach(item => {

        if (!byBrand[item.brand]) {
            byBrand[item.brand] = [];
        }

        byBrand[item.brand].push(item);
    });

    return Object.values(byBrand).map(products => {

        products.sort(
            (a, b) =>
                a.unitPrice - b.unitPrice ||
                a.price - b.price
        );

        return products[0];
    });
}


// ===============================
// ساخت گروه‌های مقایسه
// ===============================

function buildComparisonGroups(
    category,
    categoryData
) {

    const prepared = [];

    Object.entries(
        categoryData || {}
    ).forEach(([brand, products]) => {

        if (brand === "سایر") {
            return;
        }

        (products || []).forEach(product => {

            const preparedProduct =
                prepareProduct(
                    category,
                    product,
                    brand
                );

            if (preparedProduct) {
                prepared.push(preparedProduct);
            }
        });
    });


    const map = {};

    prepared.forEach(product => {

        if (!map[product.signature]) {
            map[product.signature] = [];
        }

        map[product.signature].push(product);
    });


    const groups = [];


    Object.values(map).forEach(items => {

        // تخم مرغ
        if (category === "تخم مرغ") {

            const selected =
                chooseBestPerBrand(items);

            if (selected.length >= 2) {

                groups.push({
                    category,
                    title: selected[0].title,
                    items: selected
                });
            }

            return;
        }


        // مربا
        if (category === "مربا") {

            const selected =
                chooseBestPerBrand(items);

            if (selected.length >= 2) {

                groups.push({
                    category,
                    title: selected[0].title,
                    items: selected
                });
            }

            return;
        }


        // پنیر و کره
        const clusters =
            clusterByQuantity(items);

        clusters.forEach(cluster => {

            const selected =
                chooseBestPerBrand(
                    cluster.items
                );

            if (selected.length < 2) {
                return;
            }

            const quantities =
                selected.map(
                    item => item.quantity
                );

            groups.push({
                category,
                title: selected[0].title,
                items: selected,
                minQuantity: Math.min(...quantities),
                maxQuantity: Math.max(...quantities)
            });
        });

    });


    groups.sort((a, b) => {

        const aPrice =
            Math.min(
                ...a.items.map(
                    item => item.unitPrice
                )
            );

        const bPrice =
            Math.min(
                ...b.items.map(
                    item => item.unitPrice
                )
            );

        return aPrice - bPrice;
    });

    return groups;
}


// ===============================
// نمایش مقدار
// ===============================

function getQuantityLabel(group) {

    if (group.category === "تخم مرغ") {

        return `${formatNumber(
            group.items[0].count
        )} عدد`;
    }


    const quantities =
        group.items.map(
            item => item.quantity
        );

    const min =
        Math.min(...quantities);

    const max =
        Math.max(...quantities);

    if (min === max) {

        return `${formatNumber(min)} گرم`;
    }

    return `${formatNumber(min)} تا ${formatNumber(max)} گرم`;
}


// ===============================
// قیمت واحد
// ===============================

function getUnitPriceLabel(
    product,
    category
) {

    if (category === "تخم مرغ") {

        return `هر عدد: ${formatPrice(
            product.unitPrice
        )} تومان`;
    }

    return `هر ۱۰۰ گرم: ${formatPrice(
        product.unitPrice
    )} تومان`;
}


// ===============================
// کارت مقایسه
// ===============================

function createComparisonCard(group) {

    const card =
        document.createElement("div");

    card.className = "product-card";


    const sorted =
        [...group.items].sort(
            (a, b) =>
                a.unitPrice - b.unitPrice
        );


    const cheapest = sorted[0];

    const mostExpensive =
        sorted[sorted.length - 1];


    const priceDifference =
        mostExpensive.price -
        cheapest.price;


    const rows =
        sorted.map((product, index) => {

            let medal = "🔹";

            if (index === 0) {
                medal = "🥇";
            } else if (index === 1) {
                medal = "🥈";
            } else if (index === 2) {
                medal = "🥉";
            }


            const quantityText =
                group.category === "تخم مرغ"
                    ? `${formatNumber(product.count)} عدد`
                    : `${formatNumber(product.quantity)} گرم`;


            return `
                <div class="store-row">
                    <span class="store-name">
                        ${medal}
                        ${escapeHtml(product.brand)}
                    </span>

                    <span class="store-price">
                        ${formatPrice(product.price)}
                        تومان
                    </span>
                </div>

                <div class="saving">
                    📦 ${quantityText}
                    &nbsp; | &nbsp;
                    ${getUnitPriceLabel(
                        product,
                        group.category
                    )}
                </div>

                <a
                    href="${escapeHtml(product.url || "#")}"
                    target="_blank"
                    rel="noopener noreferrer"
                    class="product-button"
                >
                    مشاهده محصول
                    ${escapeHtml(product.brand)}
                </a>
            `;
        }).join("");


    const cheapestText =
        `🏆 ارزان‌ترین: ${escapeHtml(
            cheapest.brand
        )}`;


    const savingText =
        priceDifference > 0
            ? `💵 اختلاف با گران‌ترین: ${formatPrice(
                priceDifference
            )} تومان`
            : "⚖️ قیمت‌ها برابر است";


    card.innerHTML = `
        <div class="product-name">
            ${escapeHtml(group.title)}
        </div>

        <div class="saving">
            📦 مقدار قابل مقایسه:
            ${getQuantityLabel(group)}
        </div>

        ${rows}

        <div class="cheapest">
            ${cheapestText}
        </div>

        <div class="saving">
            ${savingText}
        </div>
    `;

    return card;
}


// ===============================
// نمایش گروه‌های مقایسه
// ===============================

function displayComparisonGroups(groups) {

    productsContainer.innerHTML = "";

    productCount.textContent =
        `${formatNumber(groups.length)} مقایسه`;


    if (!groups.length) {

        productsContainer.innerHTML = `
            <div class="loading">
                فعلاً محصول مشابه از حداقل دو برند پیدا نشد.
                <br><br>
                با دریافت محصولات بیشتر،
                گروه‌های مقایسه‌ای بیشتری ساخته می‌شود.
            </div>
        `;

        return;
    }


    groups.forEach(group => {

        productsContainer.appendChild(
            createComparisonCard(group)
        );
    });
}


// ===============================
// کارت شیر
// ===============================

function createMilkCard(product) {

    const card =
        document.createElement("div");

    card.className = "product-card";


    let cheapestText = "";

    if (product.cheaper_store === "دیجی‌کالا") {

        cheapestText =
            "💰 دیجی‌کالا ارزان‌تر است";

    } else if (
        product.cheaper_store === "اکالا"
    ) {

        cheapestText =
            "💰 اکالا ارزان‌تر است";

    } else {

        cheapestText =
            "⚖️ قیمت‌ها برابر است";
    }


    card.innerHTML = `
        <div class="product-name">
            ${escapeHtml(product.product)}
        </div>

        <div class="store-row">
            <span class="store-name">
                🔵 دیجی‌کالا
            </span>

            <span class="store-price">
                ${formatPrice(
                    product.digikala.price
                )}
                تومان
            </span>
        </div>

        <div class="store-row">
            <span class="store-name">
                🟢 اکالا
            </span>

            <span class="store-price">
                ${formatPrice(
                    product.okala.price
                )}
                تومان
            </span>
        </div>

        <div class="cheapest">
            ${cheapestText}
        </div>

        <div class="saving">
            💵 صرفه‌جویی:
            ${formatPrice(product.saving)}
            تومان
        </div>

        <div class="saving">
            📊 درصد صرفه‌جویی:
            ${product.saving_percent}%
        </div>

        <a
            href="${escapeHtml(
                getMilkStoreUrl(product)
            )}"
            target="_blank"
            rel="noopener noreferrer"
            class="product-button"
        >
            مشاهده محصول
        </a>
    `;

    return card;
}


// ===============================
// لینک محصول شیر
// ===============================

function getMilkStoreUrl(product) {

    if (product.cheaper_store === "دیجی‌کالا") {
        return product.digikala.url;
    }

    if (product.cheaper_store === "اکالا") {
        return product.okala.url;
    }

    return product.digikala.url;
}


// ===============================
// نمایش شیر
// ===============================

function displayMilkProducts(products) {

    productsContainer.innerHTML = "";

    productCount.textContent =
        `${formatNumber(products.length)} محصول`;


    if (!products.length) {

        productsContainer.innerHTML = `
            <div class="loading">
                محصولی پیدا نشد.
            </div>
        `;

        return;
    }


    products.forEach(product => {

        productsContainer.appendChild(
            createMilkCard(product)
        );
    });
}


// ===============================
// دریافت اطلاعات از API
// ===============================

async function loadProducts() {

    try {

        productsContainer.innerHTML = `
            <div class="loading">
                در حال دریافت محصولات...
            </div>
        `;


        // دریافت شیر
        const milkResponse =
            await fetch(PRODUCTS_API);

        if (!milkResponse.ok) {
            throw new Error(
                "خطا در دریافت اطلاعات شیر"
            );
        }

        milkProducts =
            await milkResponse.json();


        // دریافت محصولات برندها
        const brandResponse =
            await fetch(BRANDS_API);

        if (!brandResponse.ok) {
            throw new Error(
                "خطا در دریافت اطلاعات برندها"
            );
        }

        brandProducts =
            await brandResponse.json();


        // ساخت گروه‌های مقایسه
        comparisonGroupsByCategory = {};


        [
            "پنیر",
            "کره",
            "مربا",
            "تخم مرغ"
        ].forEach(category => {

            comparisonGroupsByCategory[category] =
                buildComparisonGroups(
                    category,
                    brandProducts[category]
                );

            console.log(
                category,
                comparisonGroupsByCategory[category]
            );
        });


        // نمایش اولیه
        showCategory("شیر");


    } catch (error) {

        console.error(error);

        productsContainer.innerHTML = `
            <div class="loading">
                ❌ دریافت اطلاعات با مشکل مواجه شد.
                <br><br>
                مطمئن شوید FastAPI در حال اجراست.
            </div>
        `;

        productCount.textContent =
            "خطا در دریافت اطلاعات";
    }
}


// ===============================
// انتخاب دسته
// ===============================

function showCategory(category) {

    currentCategory = category;


    document
        .querySelectorAll(".category-button")
        .forEach(button => {

            button.classList.toggle(
                "active",
                button.dataset.category === category
            );
        });


    if (category === "شیر") {

        displayMilkProducts(
            milkProducts
        );

        return;
    }


    const groups =
        comparisonGroupsByCategory[
            category
        ] || [];


    displayComparisonGroups(groups);
}


// ===============================
// جستجو
// ===============================

function searchProducts() {

    const query =
        normalizeText(
            searchInput.value
        );


    if (!query) {

        showCategory(
            currentCategory
        );

        return;
    }


    // جستجوی شیر
    if (currentCategory === "شیر") {

        const results =
            milkProducts.filter(
                product =>
                    normalizeText(
                        product.product
                    ).includes(query)
            );


        displayMilkProducts(results);

        return;
    }


    // جستجوی سایر دسته‌ها
    const groups =
        comparisonGroupsByCategory[
            currentCategory
        ] || [];


    const results =
        groups.filter(group => {

            if (
                normalizeText(
                    group.title
                ).includes(query)
            ) {
                return true;
            }


            return group.items.some(
                item =>
                    normalizeText(
                        item.product
                    ).includes(query) ||

                    normalizeText(
                        item.brand
                    ).includes(query)
            );
        });


    displayComparisonGroups(results);
}


// ===============================
// دکمه‌های دسته‌بندی
// ===============================

categoryButtons
    .querySelectorAll(".category-button")
    .forEach(button => {

        button.addEventListener(
            "click",
            function () {

                searchInput.value = "";

                showCategory(
                    this.dataset.category
                );
            }
        );
    });


// ===============================
// دکمه جستجو
// ===============================

searchButton.addEventListener(
    "click",
    searchProducts
);


// ===============================
// جستجو با Enter
// ===============================

searchInput.addEventListener(
    "keydown",
    function (event) {

        if (event.key === "Enter") {
            searchProducts();
        }
    }
);


// ===============================
// اجرای اولیه
// ===============================

loadProducts();