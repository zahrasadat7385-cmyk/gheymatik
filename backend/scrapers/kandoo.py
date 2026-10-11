from playwright.async_api import async_playwright
import re
from urllib.parse import urljoin


# =========================
# تنظیمات
# =========================

URL = "http://021021.ir/Index?p=1&c=14"

BASE_URL = "http://021021.ir/"

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"


# =========================
# تبدیل اعداد فارسی به انگلیسی
# =========================

def persian_to_english(text):

    translation = str.maketrans(
        "۰۱۲۳۴۵۶۷۸۹",
        "0123456789"
    )

    return text.translate(translation)


# =========================
# استخراج قیمت
# =========================

def extract_price(text):

    text = persian_to_english(text)

    match = re.search(
        r"قیمت\s*:\s*([\d,]+)\s*تومان",
        text
    )

    if not match:
        return None

    price = match.group(1)

    price = price.replace(",", "")

    return int(price)


# =========================
# دریافت محصولات شیر
# =========================

async def get_products(page):

    await page.goto(
        URL,
        wait_until="domcontentloaded",
        timeout=30000
    )

    await page.wait_for_timeout(2000)

    links = page.locator("a")

    count = await links.count()

    products = []

    for i in range(count):

        link = links.nth(i)

        name = (
            await link.inner_text()
        ).strip()

        href = await link.get_attribute(
            "href"
        )

        if not name or not href:
            continue

        if not href.startswith(
            "product/"
        ):
            continue

        product_url = urljoin(
            BASE_URL,
            href
        )

        products.append({
            "name": name,
            "url": product_url
        })

    return products


# =========================
# دریافت قیمت محصول
# =========================

async def get_product_price(
    page,
    product
):

    try:

        await page.goto(
            product["url"],
            wait_until="domcontentloaded",
            timeout=30000
        )

        await page.wait_for_timeout(800)

        text = await page.locator(
            "body"
        ).inner_text()

        price = extract_price(
            text
        )

        product["price"] = price

    except Exception as e:

        print(
            "خطا در دریافت محصول:"
        )

        print(
            product["name"]
        )

        print(e)

        product["price"] = None

    return product


# =========================
# اجرای کامل اسکریپر
# =========================

async def get_all_products():

    async with async_playwright() as p:

        browser = await p.chromium.launch(
            executable_path=CHROME_PATH,
            headless=True
        )

        page = await browser.new_page(
            locale="fa-IR"
        )

        print(
            "در حال دریافت محصولات کندو..."
        )

        products = await get_products(
            page
        )

        print(
            "تعداد محصولات:",
            len(products)
        )

        results = []

        for product in products:

            result = await get_product_price(
                page,
                product
            )

            results.append(result)

        await browser.close()

        return results