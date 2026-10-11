import json
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

INPUT_FILE = os.path.join(BASE_DIR, "matched_products.json")
OUTPUT_FILE = os.path.join(BASE_DIR, "price_comparison.json")


def calculate_comparison():

    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        products = json.load(file)

    results = []

    for product in products:

        digikala = product.get("digikala", {})
        okala = product.get("okala", {})

        digi_price = digikala.get("price")
        okala_price = okala.get("price")

        if digi_price is None or okala_price is None:
            continue

        try:
            digi_price = int(digi_price)
            okala_price = int(okala_price)
        except (ValueError, TypeError):
            continue

        # تعیین فروشگاه ارزان‌تر
        if digi_price < okala_price:
            cheaper_store = "دیجی‌کالا"
            saving = okala_price - digi_price

        elif okala_price < digi_price:
            cheaper_store = "اکالا"
            saving = digi_price - okala_price

        else:
            cheaper_store = "برابر"
            saving = 0

        # درصد صرفه‌جویی
        if saving > 0:
            higher_price = max(digi_price, okala_price)
            saving_percent = round((saving / higher_price) * 100, 2)
        else:
            saving_percent = 0

        result = {
            "product": product.get("product"),

            "digikala": {
                "price": digi_price,
                "url": digikala.get("url")
            },

            "okala": {
                "price": okala_price,
                "url": okala.get("url")
            },

            "cheaper_store": cheaper_store,
            "saving": saving,
            "saving_percent": saving_percent
        }

        results.append(result)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(
            results,
            file,
            ensure_ascii=False,
            indent=2
        )

    print("=" * 50)
    print("مقایسه قیمت‌ها انجام شد")
    print("=" * 50)
    print(f"تعداد محصولات: {len(results)}")
    print(f"فایل خروجی: {OUTPUT_FILE}")
    print()

    for i, item in enumerate(results, 1):

        print(f"#{i}")
        print(f"محصول: {item['product']}")

        print(
            f"دیجی‌کالا: "
            f"{item['digikala']['price']:,} تومان"
        )

        print(
            f"اکالا: "
            f"{item['okala']['price']:,} تومان"
        )

        print(f"ارزان‌تر: {item['cheaper_store']}")
        print(f"صرفه‌جویی: {item['saving']:,} تومان")
        print(f"درصد: {item['saving_percent']}%")
        print("-" * 40)


if __name__ == "__main__":
    calculate_comparison()