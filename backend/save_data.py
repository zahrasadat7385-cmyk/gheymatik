import asyncio
import json

from scrapers.fazineo import get_products as get_fazineo_products
from scrapers.kandoo import get_all_products as get_kandoo_products


async def main():

    print("=" * 50)
    print("شروع دریافت اطلاعات فروشگاه‌ها")
    print("=" * 50)

    # =========================
    # فازینو
    # =========================

    print("\n🟣 دریافت محصولات فازینو...")

    fazineo_products = await get_fazineo_products()

    print(
        f"✅ {len(fazineo_products)} محصول از فازینو دریافت شد."
    )

    # =========================
    # ذخیره فازینو
    # =========================

    with open(
        "fazineo.json",
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            fazineo_products,
            file,
            ensure_ascii=False,
            indent=4
        )

    print("💾 اطلاعات فازینو ذخیره شد.")


    # =========================
    # کندو
    # =========================

    print("\n🟢 دریافت محصولات کندو...")

    kandoo_products = await get_kandoo_products()

    print(
        f"✅ {len(kandoo_products)} محصول از کندو دریافت شد."
    )

    # =========================
    # ذخیره کندو
    # =========================

    with open(
        "kandoo.json",
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            kandoo_products,
            file,
            ensure_ascii=False,
            indent=4
        )

    print("💾 اطلاعات کندو ذخیره شد.")


    # =========================
    # پایان
    # =========================

    print("\n")
    print("=" * 50)
    print("🎉 اطلاعات هر دو فروشگاه ذخیره شد.")
    print("=" * 50)


asyncio.run(main())
