from playwright.async_api import async_playwright
import re


# =========================
# تنظیمات
# =========================

URL = "https://fazinoo.ir/%D8%B4%DB%8C%D8%B1"

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"


# =========================
# استخراج قیمت
# =========================

def clean_price(text):

    match = re.search(
        r"([\d,]+)\s*تومان",
        text
    )

    if not match:
        return None

    price_text = match.group(1).replace(",", "")

    return int(price_text)


# =========================
# تشخیص برند
# =========================

def detect_brand(name):

    brands = [
        "دومینو",
        "دامداران",
        "چوپان",
        "روزانه",
        "رامک",
        "میهن",
        "هراز",
        "کاله",
        "پگاه",
        "عالیس",
        "پاک"
    ]

    for brand in brands:

        if re.search(
            rf"(?<![آ-ی]){re.escape(brand)}(?![آ-ی])",
            name
        ):
            return brand

    return "نامشخص"


# =========================
# تشخیص حجم
# =========================

def detect_volume(name):

    patterns = [
        r"\d+\s*لیتر",
        r"\d+\s*لیتری",
        r"\d+\s*سی\s*سی",
        r"\d+\s*cc"
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            name
        )

        if match:
            return match.group(0)

    return "نامشخص"


# =========================
# دریافت محصولات
# =========================

async def get_products():

    async with async_playwright() as p:

        browser = await p.chromium.launch(
            executable_path=CHROME_PATH,
            headless=True
        )

        page = await browser.new_page(
            locale="fa-IR"
        )

        print(
            "در حال دریافت اطلاعات فازینو..."
        )

        await page.goto(
            URL,
            wait_until="domcontentloaded",
            timeout=30000
        )

        await page.wait_for_timeout(3000)

        products = []

        h3s = page.locator("h3")

        count = await h3s.count()

        print(
            "تعداد محصولات:",
            count
        )

        for i in range(count):

            item = h3s.nth(i)

            name = (
                await item.inner_text()
            ).strip()

            if not name:
                continue

            parent = item.locator(
                "xpath=.."
            )

            card_text = (
                await parent.inner_text()
            ).strip()

            price = clean_price(
                card_text
            )

            brand = detect_brand(
                name
            )

            volume = detect_volume(
                name
            )

            product_url = await item.evaluate(
                """
                (el) => {

                    let current = el;

                    for (
                        let i = 0;
                        i < 6 && current;
                        i++
                    ) {

                        if (
                            current.tagName === 'A'
                            && current.href
                        ) {
                            return current.href;
                        }

                        const link =
                            current.querySelector(
                                "a[href]"
                            );

                        if (
                            link
                            && link.href
                        ) {
                            return link.href;
                        }

                        current =
                            current.parentElement;
                    }

                    return null;
                }
                """
            )

            products.append({
                "name": name,
                "price": price,
                "brand": brand,
                "volume": volume,
                "url": product_url
            })

        await browser.close()

        return products