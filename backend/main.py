from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
import os

app = FastAPI(
    title="Saffron Price API",
    description="API مقایسه قیمت محصولات فروشگاه‌ها",
    version="1.0.0"
)

# ==============================
# اجازه دسترسی Frontend
# ==============================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "http://127.0.0.1:5501",
        "http://localhost:5501",
        "https://zahrasadat7385-cmyk.github.io",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==============================
# مسیر فایل‌ها
# ==============================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PRICE_FILE = os.path.join(
    BASE_DIR,
    "price_comparison.json"
)

BRAND_FILE = os.path.join(
    BASE_DIR,
    "brand_comparison.json"
)

# ==============================
# صفحه اصلی API
# ==============================

@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "Saffron Price API works!"
    }

# ==============================
# محصولات شیر
# ==============================

@app.get("/products")
def get_products():
    try:
        with open(
            PRICE_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            products = json.load(file)

        return products

    except FileNotFoundError:

        return {
            "error": "فایل price_comparison.json پیدا نشد."
        }

# ==============================
# تعداد محصولات شیر
# ==============================

@app.get("/products/count")
def get_products_count():
    try:
        with open(
            PRICE_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            products = json.load(file)

        return {
            "count": len(products)
        }

    except FileNotFoundError:

        return {
            "count": 0
        }

# ==============================
# محصولات پنیر، کره، مربا، تخم مرغ
# ==============================

@app.get("/brand-products")
def get_brand_products():
    try:
        with open(
            BRAND_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            products = json.load(file)

        return products

    except FileNotFoundError:

        return {
            "error": "فایل brand_comparison.json پیدا نشد."
        }

# ==============================
# تعداد محصولات هر دسته
# ==============================

@app.get("/brand-products/count")
def get_brand_products_count():

    try:
        with open(
            BRAND_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            products = json.load(file)

        result = {}

        for category, brands in products.items():

            count = 0

            for brand, items in brands.items():

                count += len(items)

            result[category] = count

        return result

    except FileNotFoundError:

        return {
            "error": "فایل brand_comparison.json پیدا نشد."
        }