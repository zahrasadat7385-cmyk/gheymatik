const PRODUCTS_API = "http://127.0.0.1:8002/products";
const BRANDS_API = "http://127.0.0.1:8002/brand-products";

const productsContainer = document.getElementById("productsContainer");
const productCount = document.getElementById("productCount");
const searchInput = document.getElementById("searchInput");
const searchButton = document.getElementById("searchButton");
const categoryButtons = document.getElementById("categoryButtons");

let milkProducts = [];
let brandProducts = {};
let allProducts = [];
let currentCategory = "شیر";


// ===============================
// تبدیل قیمت به عدد فارسی
// ===============================

function formatPrice(price) {
    return new Intl.NumberFormat("fa-IR").format(price);
}


// ===============================
// دریافت اطلاعات
// ===============================

async function loadProducts() {

    try {

        productsContainer.innerHTML = `
            <div class="loading">
                در حال دریافت محصولات...
            </div>
        `;

        // دریافت شیر
        const milkResponse = await fetch(PRODUCTS_API);

        if (!milkResponse.ok) {
            throw new Error("خطا در دریافت اطلاعات شیر");
        }

        milkProducts = await milkResponse.json();


        // دریافت پنیر، کره، مربا و تخم مرغ
        const brandResponse = await fetch(BRANDS_API);

        if (!brandResponse.ok) {
            throw new Error("خطا در دریافت اطلاعات برندها");
        }

        brandProducts = await brandResponse.json();


        // همه محصولات برای جستجو
        allProducts = [
            ...milkProducts
        ];

        Object.values(brandProducts).forEach(category => {

            Object.values(category).forEach(products => {

                allProducts.push(...products);

            });

        });


        // نمایش شیر در شروع
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

        productCount.textContent = "خطا در دریافت اطلاعات";

    }

}


// ===============================
// انتخاب دسته
// ===============================

function showCategory(category) {

    currentCategory = category;

    // فعال کردن دکمه دسته
    document.querySelectorAll(".category-button").forEach(button => {

        button.classList.remove("active");

        if (button.dataset.category === category) {
            button.classList.add("active");
        }

    });


    // شیر
    if (category === "شیر") {

        displayMilkProducts(milkProducts);

        return;
    }


    // سایر دسته‌ها
    const categoryData = brandProducts[category];

    if (!categoryData) {

        productsContainer.innerHTML = `
            <div class="loading">
                محصولی برای این دسته پیدا نشد.
            </div>
        `;

        productCount.textContent = "۰ محصول";

        return;
    }


    displayBrandProducts(categoryData);

}


// ===============================
// نمایش شیر
// ===============================

function displayMilkProducts(products) {

    productsContainer.innerHTML = "";

    productCount.textContent =
        `${formatNumber(products.length)} محصول`;


    if (products.length === 0) {

        productsContainer.innerHTML = `
            <div class="loading">
                محصولی پیدا نشد.
            </div>
        `;

        return;
    }


    products.forEach(product => {

        const card = createMilkCard(product);

        productsContainer.appendChild(card);

    });

}


// ===============================
// کارت شیر
// ===============================

function createMilkCard(product) {

    const card = document.createElement("div");

    card.className = "product-card";


    let cheapestText = "";

    if (product.cheaper_store === "دیجی‌کالا") {

        cheapestText = "💰 دیجی‌کالا ارزان‌تر است";

    } else if (product.cheaper_store === "اکالا") {

        cheapestText = "💰 اکالا ارزان‌تر است";

    } else {

        cheapestText = "⚖️ قیمت‌ها برابر است";

    }


    card.innerHTML = `

        <div class="product-name">
            ${product.product}
        </div>


        <div class="store-row">

            <span class="store-name">
                🔵 دیجی‌کالا
            </span>

            <span class="store-price">
                ${formatPrice(product.digikala.price)}
                تومان
            </span>

        </div>


        <div class="store-row">

            <span class="store-name">
                🟢 اکالا
            </span>

            <span class="store-price">
                ${formatPrice(product.okala.price)}
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
            href="${getMilkStoreUrl(product)}"
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
// لینک شیر
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
// نمایش محصولات برندها
// ===============================

function displayBrandProducts(categoryData) {

    productsContainer.innerHTML = "";

    let totalProducts = 0;


    // هر برند
    Object.entries(categoryData).forEach(
        ([brand, products]) => {

            totalProducts += products.length;

            // عنوان برند
            const brandSection = document.createElement("div");

            brandSection.className = "brand-section";

            brandSection.innerHTML = `

                <div class="brand-title">

                    <h3>
                        ${brand}
                    </h3>

                    <span>
                        ${formatNumber(products.length)}
                        محصول
                    </span>

                </div>

            `;


            // گرید محصولات برند
            const brandGrid = document.createElement("div");

            brandGrid.className = "products-grid";


            products.forEach(product => {

                const card = createBrandCard(
                    product,
                    brand
                );

                brandGrid.appendChild(card);

            });


            brandSection.appendChild(brandGrid);

            productsContainer.appendChild(brandSection);

        }
    );


    productCount.textContent =
        `${formatNumber(totalProducts)} محصول`;
}


// ===============================
// کارت محصولات برند
// ===============================

function createBrandCard(product, brand) {

    const card = document.createElement("div");

    card.className = "product-card";


    let quantityText = "";

    if (product.quantity) {

        quantityText =
            `${formatNumber(product.quantity)} گرم`;

    } else if (product.count) {

        quantityText =
            `${formatNumber(product.count)} عدد`;

    }


    card.innerHTML = `

        <div class="product-name">

            ${product.product}

        </div>


        <div class="store-row">

            <span class="store-name">
                🏪 فروشگاه
            </span>

            <span class="store-price">
                دیجی‌کالا
            </span>

        </div>


        <div class="store-row">

            <span class="store-name">
                🏷️ برند
            </span>

            <span class="store-price">
                ${brand}
            </span>

        </div>


        <div class="store-row">

            <span class="store-name">
                📦 مقدار
            </span>

            <span class="store-price">
                ${quantityText}
            </span>

        </div>


        <div class="saving">

            💰 قیمت:

            ${formatPrice(product.price)}
            تومان

        </div>


        <a
            href="${product.url}"
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
// تبدیل عدد به فارسی
// ===============================

function formatNumber(number) {

    return new Intl.NumberFormat("fa-IR")
        .format(number);

}


// ===============================
// جستجوی محصولات
// ===============================

function searchProducts() {

    const query =
        searchInput.value.trim().toLowerCase();


    // اگر جستجو خالی بود
    if (!query) {

        showCategory(currentCategory);

        return;

    }


    const results = allProducts.filter(product => {

        return product.product
            .toLowerCase()
            .includes(query);

    });


    displaySearchResults(results);

}


// ===============================
// نمایش نتیجه جستجو
// ===============================

function displaySearchResults(results) {

    productsContainer.innerHTML = "";

    productCount.textContent =
        `${formatNumber(results.length)} نتیجه`;


    if (results.length === 0) {

        productsContainer.innerHTML = `
            <div class="loading">

                محصولی با این نام پیدا نشد.

            </div>
        `;

        return;
    }


    results.forEach(product => {

        // شیر
        if (
            product.digikala &&
            product.okala
        ) {

            productsContainer.appendChild(
                createMilkCard(product)
            );

        }

        // سایر محصولات
        else {

            productsContainer.appendChild(
                createBrandCard(
                    product,
                    detectBrand(product.product)
                )
            );

        }

    });

}


// ===============================
// تشخیص تقریبی برند
// ===============================

function detectBrand(productName) {

    const brands = [

        "کاله",
        "دامداران",
        "روزانه",
        "پگاه",
        "هراز",
        "آلیما",
        "میهن",
        "کالین",
        "دهناد",
        "ماهوند",
        "فدک",
        "سحرانا",
        "کامور",
        "اصالت",
        "شانا",
        "تلاونگ",
        "fresh",
        "سیمرغ",
        "فرش"

    ];


    const found =
        brands.find(brand =>
            productName.toLowerCase()
                .includes(brand.toLowerCase())
        );


    return found || "سایر";
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

                const category =
                    this.dataset.category;

                searchInput.value = "";

                showCategory(category);

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
    function(event) {

        if (event.key === "Enter") {

            searchProducts();

        }

    }
);


// ===============================
// اجرای اولیه
// ===============================

loadProducts();