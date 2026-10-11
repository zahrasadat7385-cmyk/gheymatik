import json
import re
from pathlib import Path

from playwright.sync_api import sync_playwright


# ==========================================
# تنظیمات
# ==========================================

BASE_DIR = Path(__file__).parent
OUTPUT_FILE = BASE_DIR / "digikala.json"

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"


# ==========================================
# جستجوها بر اساس دسته
# ==========================================

SEARCH_QUERIES = {

    # 🥛 شیر
    "شیر": [
        "شیر",
        "شیر کاله",
        "شیر میهن",
        "شیر پگاه",
        "شیر دامداران",
        "شیر پاک",
        "شیر چوپان",
        "شیر رامک",
    ],

    # 🧀 پنیر
    "پنیر": [
        "پنیر",
        "پنیر کاله",
        "پنیر میهن",
        "پنیر پگاه",
        "پنیر دامداران",
        "پنیر پاک",
        "پنیر چوپان",
        "پنیر رامک",
    ],

    # 🧈 کره
    "کره": [
        "کره",
        "کره کاله",
        "کره میهن",
        "کره پگاه",
        "کره پاک",
        "کره رامک",
    ],

    # 🍓 مربا
    "مربا": [
        "مربا",
        "مربا کاله",
        "مربا میهن",
        "مربا پگاه",
        "مربا یک و یک",
        "مربا بهروز",
    ],

    # 🥚 تخم مرغ
    "تخم مرغ": [
        "تخم مرغ",
        "تخم مرغ بسته بندی",
        "تخم مرغ پگاه",
        "تخم مرغ تلاونگ",
        "تخم مرغ کاله",
    ],
}


# ==========================================
# حداکثر تعداد محصول برای هر دسته
# ==========================================

MAX_PRODUCTS_PER_CATEGORY = {

    "شیر": 30,
    "پنیر": 25,
    "کره": 20,
    "مربا": 20,
    "تخم مرغ": 20,
}


# ==========================================
# تبدیل اعداد فارسی و عربی
# ==========================================

def normalize_digits(text):

    translation = str.maketrans(
        "۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩",
        "01234567890123456789"
    )

    return text.translate(translation)


# ==========================================
# استخراج قیمت اصلی
# ==========================================

def extract_main_price(body_text):

    lines = [
        normalize_digits(line.strip())
        for line in body_text.splitlines()
        if line.strip()
    ]

    # --------------------------------------
    # روش اول: اطراف «فروشنده»
    # --------------------------------------

    for i, line in enumerate(lines):

        if line == "فروشنده":

            for next_line in lines[i + 1:i + 21]:

                numbers = re.findall(
                    r"\b\d[\d,]*\b",
                    next_line
                )

                for number in numbers:

                    clean_number = number.replace(",", "")

                    if clean_number.isdigit():

                        price = int(clean_number)

                        if 10000 <= price <= 1000000000:
                            return price

    # --------------------------------------
    # روش دوم: اطراف «افزودن به سبد»
    # --------------------------------------

    for i, line in enumerate(lines):

        if "افزودن به سبد" in line:

            start = max(0, i - 5)

            for previous_line in reversed(lines[start:i]):

                numbers = re.findall(
                    r"\b\d[\d,]*\b",
                    previous_line
                )

                for number in numbers:

                    clean_number = number.replace(",", "")

                    if clean_number.isdigit():

                        price = int(clean_number)

                        if 10000 <= price <= 1000000000:
                            return price

    return None


# ==========================================
# تشخیص دسته محصول
# ==========================================

def is_product_in_category(name, category):

    name = normalize_digits(name).lower()

    # --------------------------------------
    # 🥛 شیر
    # --------------------------------------

    if category == "شیر":

        return (
            "شیر" in name
            and "پنیر" not in name
            and "کره" not in name
            and "مربا" not in name
            and "تخم مرغ" not in name
            and "تخم‌مرغ" not in name
        )

    # --------------------------------------
    # 🧀 پنیر
    # --------------------------------------

    if category == "پنیر":

        return (
            "پنیر" in name
            and "پودر آب پنیر" not in name
            and "آب پنیر" not in name
        )

    # --------------------------------------
    # 🧈 کره
    # --------------------------------------

    if category == "کره":

        return (
            "کره" in name
            and "کره بادام" not in name
            and "کره بادام زمینی" not in name
        )

    # --------------------------------------
    # 🍓 مربا
    # --------------------------------------

    if category == "مربا":

        return "مربا" in name

    # --------------------------------------
    # 🥚 تخم مرغ
    # --------------------------------------

    if category == "تخم مرغ":

        return (
            "تخم مرغ" in name
            or "تخم‌مرغ" in name
            or "تخممرغ" in name
        )

    return False


# ==========================================
# دریافت محصولات از صفحه جستجو
# ==========================================

def get_search_products(page, query, category):

    url = (
        "https://www.digikala.com/search/?q="
        + query.replace(" ", "%20")
    )

    print()
    print("====================================")
    print(f"دسته: {category}")
    print(f"جستجو در دیجی‌کالا: {query}")
    print("====================================")

    page.goto(
        url,
        wait_until="domcontentloaded",
        timeout=60000
    )

    page.wait_for_timeout(5000)

    products = []

    elements = page.locator("h3")

    count = elements.count()

    print(
        f"تعداد عنوان‌های پیدا شده: {count}"
    )

    for i in range(count):

        try:

            element = elements.nth(i)

            name = element.inner_text().strip()

            if not name:
                continue

            # فقط محصولات همین دسته
            if not is_product_in_category(
                name,
                category
            ):
                continue

            link = element.locator(
                "xpath=ancestor::a[1]"
            )

            if link.count() == 0:
                continue

            href = link.get_attribute("href")

            if not href:
                continue

            if href.startswith("/"):

                href = (
                    "https://www.digikala.com"
                    + href
                )

            products.append({

                "name": name,

                "url": href,

                "category": category

            })

        except Exception:

            continue

    print(
        f"محصولات معتبر این جستجو: "
        f"{len(products)}"
    )

    return products


# ==========================================
# دریافت قیمت محصول
# ==========================================

def get_product_price(page, product):

    try:

        print()
        print(
            f"در حال بررسی: {product['name']}"
        )

        page.goto(
            product["url"],
            wait_until="domcontentloaded",
            timeout=60000
        )

        page.wait_for_timeout(7000)

        body_text = page.locator(
            "body"
        ).inner_text()

        price = extract_main_price(
            body_text
        )

        if price is not None:

            print(
                f"✓ قیمت: {price:,} تومان"
            )

        else:

            print(
                "✗ قیمت پیدا نشد"
            )

        return price

    except Exception as error:

        print(
            f"✗ خطا: {error}"
        )

        return None


# ==========================================
# اجرای اصلی
# ==========================================

def main():

    print("====================================")
    print("شروع دریافت محصولات دیجی‌کالا")
    print("====================================")

    print("دسته‌ها:")

    print("🥛 شیر")
    print("🧀 پنیر")
    print("🧈 کره")
    print("🍓 مربا")
    print("🥚 تخم‌مرغ")

    print("====================================")

    all_products = []

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=True,
            executable_path=CHROME_PATH
        )

        page = browser.new_page(
            viewport={
                "width": 1366,
                "height": 900
            }
        )

        # ==================================
        # جستجوی هر دسته به صورت جداگانه
        # ==================================

        for category, queries in SEARCH_QUERIES.items():

            print()
            print()
            print("####################################")
            print(f"شروع دسته: {category}")
            print("####################################")

            category_products = []

            # ------------------------------
            # جستجوی کلمات مختلف دسته
            # ------------------------------

            for query in queries:

                try:

                    products = get_search_products(
                        page,
                        query,
                        category
                    )

                    category_products.extend(
                        products
                    )

                except Exception as error:

                    print(
                        f"خطا در جستجوی {query}: "
                        f"{error}"
                    )

            # ------------------------------
            # حذف تکراری‌ها
            # ------------------------------

            unique_category_products = {}

            for product in category_products:

                unique_category_products[
                    product["url"]
                ] = product

            unique_category_products = list(
                unique_category_products.values()
            )

            # ------------------------------
            # محدود کردن تعداد هر دسته
            # ------------------------------

            max_products = (
                MAX_PRODUCTS_PER_CATEGORY[
                    category
                ]
            )

            unique_category_products = (
                unique_category_products[
                    :max_products
                ]
            )

            print()
            print(
                f"تعداد محصولات یکتای دسته "
                f"{category}: "
                f"{len(unique_category_products)}"
            )

            print(
                f"حداکثر مجاز: "
                f"{max_products}"
            )

            # ------------------------------
            # دریافت قیمت‌ها
            # ------------------------------

            for product in unique_category_products:

                price = get_product_price(
                    page,
                    product
                )

                if price is None:
                    continue

                all_products.append({

                    "name": product["name"],

                    "price": price,

                    "url": product["url"],

                    "store": "دیجی‌کالا",

                    "category": product["category"]

                })

        browser.close()

    # ======================================
    # حذف نهایی محصولات تکراری
    # ======================================

    unique_final_products = {}

    for product in all_products:

        unique_final_products[
            product["url"]
        ] = product

    final_products = list(
        unique_final_products.values()
    )

    # ======================================
    # ذخیره
    # ======================================

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            final_products,
            file,
            ensure_ascii=False,
            indent=4
        )

    # ======================================
    # آمار نهایی
    # ======================================

    category_counts = {

        "شیر": 0,
        "پنیر": 0,
        "کره": 0,
        "مربا": 0,
        "تخم مرغ": 0

    }

    for product in final_products:

        category = product.get(
            "category"
        )

        if category in category_counts:

            category_counts[
                category
            ] += 1

    print()
    print()
    print("====================================")
    print("پایان دریافت اطلاعات")
    print("====================================")

    print(
        f"تعداد کل محصولات ذخیره شده: "
        f"{len(final_products)}"
    )

    print()

    print(
        f"🥛 شیر: "
        f"{category_counts['شیر']}"
    )

    print(
        f"🧀 پنیر: "
        f"{category_counts['پنیر']}"
    )

    print(
        f"🧈 کره: "
        f"{category_counts['کره']}"
    )

    print(
        f"🍓 مربا: "
        f"{category_counts['مربا']}"
    )

    print(
        f"🥚 تخم مرغ: "
        f"{category_counts['تخم مرغ']}"
    )

    print()
    print(
        f"فایل خروجی: {OUTPUT_FILE}"
    )

    print("====================================")


if __name__ == "__main__":
    main()