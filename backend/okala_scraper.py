import json
import re
import time
from urllib.parse import quote

from playwright.sync_api import sync_playwright


# =========================================================
# تنظیمات
# =========================================================

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

BASE_URL = "https://www.okala.com"

DAIRY_URL = "https://www.okala.com/browse/dairy-products"

SEARCHES = {
    "مربا": "مربا",
    "تخم مرغ": "تخم مرغ",
}


# =========================================================
# توابع کمکی
# =========================================================

def normalize_text(text):
    if not text:
        return ""

    text = text.replace("ي", "ی")
    text = text.replace("ى", "ی")
    text = text.replace("ك", "ک")
    text = text.replace("ۀ", "ه")
    text = text.replace("ة", "ه")

    text = re.sub(r"\s+", " ", text)

    return text.strip()


def detect_category(name):
    name = normalize_text(name)

    if "تخم مرغ" in name or "تخم‌مرغ" in name:
        return "تخم مرغ"

    if "مربا" in name:
        return "مربا"

    if "کره" in name:
        return "کره"

    if "پنیر" in name:
        return "پنیر"

    if "شیر" in name:
        return "شیر"

    return None


def is_invalid_product(name):

    name = normalize_text(name)

    invalid_words = [
        "بستنی",
        "کیک",
        "بیسکویت",
        "شکلات",
        "دسر",
        "پودینگ",
        "خامه قنادی",
        "شیرینی",
        "سس",
        "قهوه",
        "کافی",
        "پودر",
        "کاپوچینو",
    ]

    for word in invalid_words:
        if word in name:
            return True

    return False


def clean_price(text):

    if not text:
        return None

    text = text.replace("٬", "")
    text = text.replace(",", "")
    text = text.replace("،", "")

    numbers = re.findall(r"\d+", text)

    prices = []

    for number in numbers:

        try:
            value = int(number)

            # قیمت‌های منطقی محصولات سوپرمارکتی
            if 10_000 <= value <= 5_000_000:
                prices.append(value)

        except:
            pass

    if not prices:
        return None

    return prices[-1]


# =========================================================
# استخراج محصولات از صفحه
# =========================================================

def extract_products(page):

    print("در حال پیدا کردن محصولات...")

    # کمی صبر برای اجرای JavaScript
    page.wait_for_timeout(5000)

    # اسکرول چند مرحله‌ای
    for i in range(8):

        page.mouse.wheel(0, 2500)

        page.wait_for_timeout(1200)

        print(f"اسکرول {i + 1}/8")

    # لینک‌های محصول
    links = page.locator("a").all()

    print()
    print("در حال بررسی لینک‌های محصول...")

    products = []

    seen_urls = set()

    for link in links:

        try:

            href = link.get_attribute("href")

            if not href:
                continue

            if "/product/" not in href:
                continue

            if href.startswith("/"):
                url = BASE_URL + href
            else:
                url = href

            if url in seen_urls:
                continue

            seen_urls.add(url)

            text = link.inner_text(timeout=2000)

            text = normalize_text(text)

            if not text:
                continue

            category = detect_category(text)

            if not category:
                continue

            if is_invalid_product(text):
                continue

            price = clean_price(text)

            # اگر قیمت داخل خود لینک نبود،
            # فعلاً قیمت را None می‌گذاریم
            # و در مرحله بعد از صفحه محصول می‌گیریم.

            product = {
                "product": text,
                "category": category,
                "price": price,
                "store": "اکالا",
                "url": url
            }

            products.append(product)

            print(
                f"[{category}] "
                f"{text}"
            )

        except:
            continue

    return products


# =========================================================
# استخراج قیمت واقعی از صفحه محصول
# =========================================================

def get_real_prices(page, products):

    print()
    print("در حال بررسی قیمت محصولات...")
    print("------------------------------------")

    final_products = []

    for index, product in enumerate(products):

        try:

            print(
                f"{index + 1}/{len(products)} "
                f"{product['product']}"
            )

            page.goto(
                product["url"],
                wait_until="domcontentloaded",
                timeout=30000
            )

            page.wait_for_timeout(1500)

            body_text = page.locator("body").inner_text(
                timeout=10000
            )

            body_text = normalize_text(body_text)

            # قیمت‌هایی که کنار تومان آمده‌اند
            matches = re.findall(
                r"([\d٬,]+)\s*تومان",
                body_text
            )

            prices = []

            for match in matches:

                price = clean_price(match)

                if price:
                    prices.append(price)

            if prices:

                # معمولاً آخرین قیمت قابل مشاهده
                # قیمت فعلی محصول است
                product["price"] = prices[-1]

            else:

                # اگر تومان پیدا نشد
                # قیمت قبلی را نگه می‌داریم
                pass

            if product["price"]:

                print(
                    f"    قیمت: "
                    f"{product['price']:,} تومان"
                )

                final_products.append(product)

        except Exception as e:

            print(
                f"    خطا: {str(e)[:100]}"
            )

            continue

    return final_products


# =========================================================
# حذف تکراری‌ها
# =========================================================

def remove_duplicates(products):

    unique = {}

    for product in products:

        name = normalize_text(product["product"])

        key = (
            name,
            product["category"]
        )

        if key not in unique:

            unique[key] = product

    return list(unique.values())


# =========================================================
# اجرای اصلی
# =========================================================

def main():

    all_products = []

    with sync_playwright() as p:

        print("باز کردن Chrome...")

        browser = p.chromium.launch(
            headless=False,
            executable_path=CHROME_PATH,
            args=[
                "--disable-blink-features=AutomationControlled"
            ]
        )

        context = browser.new_context(
            viewport={
                "width": 1440,
                "height": 900
            },
            locale="fa-IR"
        )

        page = context.new_page()

        # =================================================
        # 1. لبنیات
        # =================================================

        print()
        print("====================================")
        print("مرحله 1: محصولات لبنی")
        print("====================================")

        print()
        print("در حال بررسی:")
        print(DAIRY_URL)
        print("------------------------------------")

        try:

            page.goto(
                DAIRY_URL,
                wait_until="domcontentloaded",
                timeout=60000
            )

            page.wait_for_timeout(5000)

            dairy_products = extract_products(page)

            print()
            print(
                f"محصولات استخراج شده لبنیات: "
                f"{len(dairy_products)}"
            )

            # قیمت‌ها
            dairy_products = get_real_prices(
                page,
                dairy_products
            )

            all_products.extend(
                dairy_products
            )

        except Exception as e:

            print("خطا در بخش لبنیات:")
            print(e)

        # =================================================
        # 2. مربا و تخم مرغ
        # =================================================

        for category, search_text in SEARCHES.items():

            print()
            print("====================================")
            print(f"مرحله: {category}")
            print("====================================")

            search_url = (
                BASE_URL
                + "/search?search="
                + quote(search_text)
            )

            print()
            print("در حال بررسی:")
            print(search_url)
            print("------------------------------------")

            try:

                page.goto(
                    search_url,
                    wait_until="domcontentloaded",
                    timeout=60000
                )

                page.wait_for_timeout(5000)

                search_products = extract_products(
                    page
                )

                # فقط همان دسته‌ای که می‌خواهیم
                search_products = [
                    p
                    for p in search_products
                    if p["category"] == category
                ]

                print()
                print(
                    f"{category}: "
                    f"{len(search_products)} محصول"
                )

                search_products = get_real_prices(
                    page,
                    search_products
                )

                all_products.extend(
                    search_products
                )

            except Exception as e:

                print(
                    f"خطا در بخش {category}:"
                )

                print(e)

        browser.close()

    # =====================================================
    # حذف تکراری‌ها
    # =====================================================

    print()
    print("====================================")

    print(
        "تعداد کل قبل از حذف تکراری‌ها:",
        len(all_products)
    )

    all_products = remove_duplicates(
        all_products
    )

    print(
        "تعداد بعد از حذف تکراری‌ها:",
        len(all_products)
    )

    # =====================================================
    # آمار
    # =====================================================

    counts = {
        "شیر": 0,
        "پنیر": 0,
        "کره": 0,
        "مربا": 0,
        "تخم مرغ": 0
    }

    for product in all_products:

        category = product["category"]

        if category in counts:
            counts[category] += 1

    print()
    print("====================================")
    print("آمار نهایی محصولات اکالا")
    print("====================================")

    print("شیر:", counts["شیر"])
    print("پنیر:", counts["پنیر"])
    print("کره:", counts["کره"])
    print("مربا:", counts["مربا"])
    print("تخم مرغ:", counts["تخم مرغ"])

    print(
        "مجموع:",
        len(all_products)
    )

    # =====================================================
    # ذخیره JSON
    # =====================================================

    with open(
        "okala.json",
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            all_products,
            file,
            ensure_ascii=False,
            indent=2
        )

    print()
    print("فایل okala.json ذخیره شد.")


# =========================================================
# START
# =========================================================

if __name__ == "__main__":
    main()