import json
import re


# =========================================================
# تنظیمات
# =========================================================

DIGIKALA_FILE = "digikala.json"
OKALA_FILE = "okala.json"

OUTPUT_FILE = "matched_products.json"
BRAND_OUTPUT_FILE = "brand_comparison.json"

MIN_SCORE = 80


# =========================================================
# نرمال‌سازی متن
# =========================================================

def normalize_text(text):

    if not text:
        return ""

    text = str(text).lower()

    replacements = {
        "ي": "ی",
        "ى": "ی",
        "ك": "ک",
        "ة": "ه",
        "ۀ": "ه",
        "ؤ": "و",
        "إ": "ا",
        "أ": "ا",
        "ئ": "ی",
        "‌": " ",
        "ـ": " ",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    persian_digits = "۰۱۲۳۴۵۶۷۸۹"
    arabic_digits = "٠١٢٣٤٥٦٧٨٩"

    for i in range(10):
        text = text.replace(
            persian_digits[i],
            str(i)
        )
        text = text.replace(
            arabic_digits[i],
            str(i)
        )

    text = text.replace("٬", "")
    text = text.replace(",", "")
    text = text.replace("،", " ")

    text = re.sub(r"\s+", " ", text)

    return text.strip()


# =========================================================
# نام محصول
# =========================================================

def get_product_name(product):

    name = product.get("name")

    if name:
        return normalize_text(name)

    name = product.get("product")

    if name:
        return normalize_text(name)

    return ""


# =========================================================
# تشخیص دسته
# =========================================================

def detect_category(name):

    name = normalize_text(name)

    if "تخم مرغ" in name or "تخممرغ" in name:
        return "تخم مرغ"

    if "مربا" in name or "مربای" in name:
        return "مربا"

    if "کره" in name:
        return "کره"

    if "پنیر" in name:
        return "پنیر"

    if "شیر" in name:
        return "شیر"

    return "سایر"


# =========================================================
# محصولات نامعتبر
# =========================================================

EXCLUDED_KEYWORDS = [

    # کره‌های غیرخوراکی
    "کره بدن",
    "کره جغرافیایی",
    "کره نارگیل",
    "کره پسته",
    "کره بادام",
    "کره بادام زمینی",
    "شی باتر",
    "body butter",

    # تخم مرغ‌های غیرخوراکی
    "تخم مرغ تزیینی",
    "تخم مرغ تزئینی",
    "تخم مرغ پلاستیکی",
    "تخم مرغ سفالی",
    "تخم مرغ پز",
    "تخممرغ پز",
    "ظرف تخم مرغ",
    "جا تخم مرغ",
    "جا تخممرغ",

    # شیرهای غیرخوراکی / نامرتبط
    "پودر آب پنیر",
    "آب پنیر",
    "پودر شیر",
    "شیر خشک",
    "شیر عسل",
    "شیر تغلیظ شده",

    # محصولات آرایشی
    "lotion",
    "cream",
    "shampoo",
    "soap",
]


def is_valid_food(name):

    name = normalize_text(name)

    for word in EXCLUDED_KEYWORDS:

        if normalize_text(word) in name:
            return False

    return True


# =========================================================
# برندها
# =========================================================

BRANDS = [

    "کاله",
    "پگاه",
    "میهن",
    "دامداران",
    "پاک",
    "چوپان",
    "رامک",
    "ماهشام",
    "مانیزان",
    "هراز",
    "دوشه",

    "کالین",
    "دهناد",
    "آلیما",
    "آنا",
    "روزانه",

    "تلاونگ",
    "سیمرغ",
    "فرش",
    "fresh",

    "ماهوند",
    "فدک",
    "سحرانا",
    "کامور",
    "شانا",
    "اصالت",

    "یک و یک",
    "یک‌ویک",
    "یکویک",

    "بهروز",
    "پاکبان",
]


def extract_brand(name):

    name = normalize_text(name)

    # برندهای چندکلمه‌ای
    multi_brands = [
        "یک و یک",
        "یکویک",
    ]

    for brand in multi_brands:

        if normalize_text(brand) in name:
            return brand

    # برندهای معمولی
    for brand in BRANDS:

        normalized_brand = normalize_text(brand)

        if normalized_brand in name:
            return brand

    return "سایر"


# =========================================================
# حجم محصول
# =========================================================

def extract_quantity(name):

    name = normalize_text(name)

    patterns = [

        # لیتر
        (
            r"(\d+(?:\.\d+)?)\s*(?:لیتر|لیتری|l)\b",
            "liter"
        ),

        # میلی لیتر
        (
            r"(\d+(?:\.\d+)?)\s*(?:میلی\s*لیتر|میلی\s*لیتری|ml|میل)\b",
            "ml"
        ),

        # کیلو
        (
            r"(\d+(?:\.\d+)?)\s*(?:کیلوگرم|کیلو|kg)\b",
            "kg"
        ),

        # گرم
        (
            r"(\d+(?:\.\d+)?)\s*(?:گرم|گرمی|g)\b",
            "g"
        ),
    ]

    for pattern, unit in patterns:

        match = re.search(pattern, name)

        if match:

            value = float(match.group(1))

            if unit == "liter":
                return value * 1000

            if unit == "kg":
                return value * 1000

            return value

    return None


# =========================================================
# تعداد محصول
# =========================================================

def extract_count(name):

    name = normalize_text(name)

    patterns = [

        r"بسته\s*(\d+)\s*عدد",
        r"(\d+)\s*عدد",
        r"مجموعه\s*(\d+)\s*عدد",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            name
        )

        if match:
            return int(match.group(1))

    return 1


# =========================================================
# درصد چربی
# =========================================================

def extract_fat_percent(name):

    name = normalize_text(name)

    patterns = [

        r"(\d+(?:\.\d+)?)\s*%\s*چربی",

        r"(\d+(?:\.\d+)?)\s*درصد\s*چربی",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            name
        )

        if match:
            return float(match.group(1))

    return None


# =========================================================
# نوع چربی
# =========================================================

def extract_fat_type(name):

    name = normalize_text(name)

    if "کم چرب" in name:
        return "کم چرب"

    if "پر چرب" in name or "پرچرب" in name:
        return "پر چرب"

    return None


# =========================================================
# نوع شیر
# =========================================================

def extract_milk_type(name):

    name = normalize_text(name)

    if "شیر کاکائو" in name:
        return "کاکائو"

    if "شیر موز" in name:
        return "موز"

    if "شیر قهوه" in name:
        return "قهوه"

    if "شیر توت فرنگی" in name:
        return "توت فرنگی"

    if "شیر وانیلی" in name:
        return "وانیل"

    if "شیر سنتی" in name:
        return "سنتی"

    if "esl" in name or "ای اس ال" in name:
        return "esl"

    if "فرادما" in name:
        return "فرادما"

    return "ساده"


# =========================================================
# ویژگی‌های محصول
# =========================================================

FEATURE_GROUPS = {

    "cocoa": [
        "کاکائو",
        "شیر کاکائو",
    ],

    "banana": [
        "موز",
        "شیر موز",
    ],

    "strawberry": [
        "توت فرنگی",
    ],

    "vanilla": [
        "وانیل",
    ],

    "coffee": [
        "قهوه",
    ],

    "lactose": [
        "بدون لاکتوز",
        "لاکتوز",
    ],

    "protein": [
        "پروتئین",
    ],

    "traditional": [
        "سنتی",
    ],

    "esl": [
        "esl",
        "ای اس ال",
    ],

    "ultra": [
        "فرادما",
    ],

    "pasteurized": [
        "پاستوریزه",
    ],

    "sterilized": [
        "استریل",
        "استریلیزه",
    ],

    "feta": [
        "فتا",
    ],

    "labneh": [
        "لبنه",
    ],

    "halloumi": [
        "هالومی",
    ],

    "kebabi": [
        "کبابی",
    ],

    "mozzarella": [
        "موزارلا",
    ],

    "cheddar": [
        "چدار",
    ],

    "parmesan": [
        "پارمزان",
    ],

    "white": [
        "سفید",
    ],

    "breakfast": [
        "صبحانه",
    ],

    "spread": [
        "اسپرد",
    ],

    "salted": [
        "نمک",
        "نمکی",
    ],

    "unsalted": [
        "بدون نمک",
    ],

    "animal": [
        "حیوانی",
    ],

    "vegetable": [
        "گیاهی",
    ],

    "lactic": [
        "لاکتیکی",
    ],

    "grated": [
        "رنده",
        "رنده شده",
    ],

    "sliced": [
        "ورقه",
        "ورقه‌ای",
    ],
}


def get_features(name):

    name = normalize_text(name)

    result = set()

    for group, keywords in FEATURE_GROUPS.items():

        for keyword in keywords:

            if normalize_text(keyword) in name:

                result.add(group)

                break

    return result


# =========================================================
# بررسی حجم
# =========================================================

def quantity_compatible(q1, q2):

    if q1 is None or q2 is None:
        return True

    if q1 <= 0 or q2 <= 0:
        return False

    difference = abs(q1 - q2)

    average = (q1 + q2) / 2

    percentage = difference / average

    return percentage <= 0.10


# =========================================================
# بررسی تعداد
# =========================================================

def count_compatible(c1, c2):

    if c1 is None or c2 is None:
        return True

    return c1 == c2


# =========================================================
# بررسی نوع شیر
# =========================================================

def milk_type_compatible(name1, name2):

    type1 = extract_milk_type(name1)
    type2 = extract_milk_type(name2)

    return type1 == type2


# =========================================================
# بررسی چربی شیر
# =========================================================

def milk_fat_compatible(name1, name2):

    fat_type1 = extract_fat_type(name1)
    fat_type2 = extract_fat_type(name2)

    if fat_type1 and fat_type2:

        if fat_type1 != fat_type2:
            return False

    fat1 = extract_fat_percent(name1)
    fat2 = extract_fat_percent(name2)

    if fat1 is not None and fat2 is not None:

        if abs(fat1 - fat2) > 0.7:
            return False

    return True


# =========================================================
# ویژگی‌های عمومی
# =========================================================

def features_compatible(name1, name2):

    features1 = get_features(name1)
    features2 = get_features(name2)

    strict_features = [

        "cocoa",
        "banana",
        "strawberry",
        "vanilla",
        "coffee",
        "lactose",

        "feta",
        "labneh",
        "halloumi",
        "mozzarella",
        "cheddar",
        "parmesan",
    ]

    for feature in strict_features:

        if feature in features1 and feature not in features2:
            return False

        if feature in features2 and feature not in features1:
            return False

    return True


# =========================================================
# محاسبه امتیاز
# =========================================================

def calculate_score(
    product1,
    product2
):

    name1 = get_product_name(product1)
    name2 = get_product_name(product2)

    if not name1 or not name2:
        return 0

    # محصول معتبر
    if not is_valid_food(name1):
        return 0

    if not is_valid_food(name2):
        return 0

    # دسته
    category1 = detect_category(name1)
    category2 = detect_category(name2)

    if category1 != category2:
        return 0

    # فقط Match بین فروشگاه‌ها برای شیر
    if category1 != "شیر":
        return 0

    score = 50

    # =====================================================
    # برند
    # =====================================================

    brand1 = extract_brand(name1)
    brand2 = extract_brand(name2)

    # اگر حداقل یکی برند مشخص داشته باشد،
    # برند طرف مقابل نیز باید همان باشد.
    if brand1 != "سایر" or brand2 != "سایر":

        if normalize_text(brand1) != normalize_text(brand2):
            return 0

        score += 20

    # =====================================================
    # نوع شیر
    # =====================================================

    if not milk_type_compatible(
        name1,
        name2
    ):
        return 0

    score += 10

    # =====================================================
    # چربی
    # =====================================================

    if not milk_fat_compatible(
        name1,
        name2
    ):
        return 0

    score += 5

    # =====================================================
    # ویژگی‌ها
    # =====================================================

    if not features_compatible(
        name1,
        name2
    ):
        return 0

    score += 5

    # =====================================================
    # حجم
    # =====================================================

    q1 = extract_quantity(name1)
    q2 = extract_quantity(name2)

    if not quantity_compatible(
        q1,
        q2
    ):
        return 0

    if q1 is not None and q2 is not None:
        score += 10

    # =====================================================
    # تعداد
    # =====================================================

    c1 = extract_count(name1)
    c2 = extract_count(name2)

    if not count_compatible(
        c1,
        c2
    ):
        return 0

    return score


# =========================================================
# تطبیق محصولات
# =========================================================

def match_products(
    digikala_products,
    okala_products
):

    matches = []

    used_okala = set()

    digi_milk = []
    okala_milk = []

    # -----------------------------------------------------
    # شیرهای دیجی‌کالا
    # -----------------------------------------------------

    for product in digikala_products:

        name = get_product_name(product)

        if detect_category(name) == "شیر":

            if is_valid_food(name):

                digi_milk.append(product)

    # -----------------------------------------------------
    # شیرهای اکالا
    # -----------------------------------------------------

    for product in okala_products:

        name = get_product_name(product)

        if detect_category(name) == "شیر":

            if is_valid_food(name):

                okala_milk.append(product)

    print()
    print(
        "تعداد شیر دیجی‌کالا:",
        len(digi_milk)
    )

    print(
        "تعداد شیر اکالا:",
        len(okala_milk)
    )

    print()

    # -----------------------------------------------------
    # Match
    # -----------------------------------------------------

    for digi in digi_milk:

        best_match = None
        best_score = 0
        best_index = None

        for index, okala in enumerate(
            okala_milk
        ):

            if index in used_okala:
                continue

            score = calculate_score(
                digi,
                okala
            )

            if (
                score >= MIN_SCORE
                and score > best_score
            ):

                best_score = score
                best_match = okala
                best_index = index

        # -------------------------------------------------
        # ذخیره Match
        # -------------------------------------------------

        if best_match is not None:

            used_okala.add(
                best_index
            )

            digi_name = get_product_name(
                digi
            )

            okala_name = get_product_name(
                best_match
            )

            matches.append({

                "product": digi_name,

                "category": "شیر",

                "digikala": {

                    "product": digi_name,

                    "price": digi.get(
                        "price"
                    ),

                    "url": digi.get(
                        "url"
                    )
                },

                "okala": {

                    "product": okala_name,

                    "price": best_match.get(
                        "price"
                    ),

                    "url": best_match.get(
                        "url"
                    )
                },

                "match_score": best_score
            })

    return matches


# =========================================================
# مقایسه برندهای دیجی‌کالا
# =========================================================

def create_brand_comparison(
    digikala_products
):

    comparison = {}

    allowed_categories = {
        "پنیر",
        "کره",
        "مربا",
        "تخم مرغ",
    }

    for product in digikala_products:

        name = get_product_name(
            product
        )

        category = detect_category(
            name
        )

        if category not in allowed_categories:
            continue

        if not is_valid_food(name):
            continue

        brand = extract_brand(name)

        if category not in comparison:

            comparison[category] = {}

        if brand not in comparison[category]:

            comparison[category][brand] = []

        comparison[category][brand].append({

            "product": name,

            "price": product.get(
                "price"
            ),

            "quantity": extract_quantity(
                name
            ),

            "count": extract_count(
                name
            ),

            "url": product.get(
                "url"
            ),

            "store": "دیجی‌کالا"
        })

    return comparison


# =========================================================
# MAIN
# =========================================================

def main():

    # =====================================================
    # خواندن دیجی‌کالا
    # =====================================================

    print(
        "در حال خواندن محصولات دیجی‌کالا..."
    )

    with open(
        DIGIKALA_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        digikala = json.load(file)

    print(
        "تعداد محصولات دیجی‌کالا:",
        len(digikala)
    )

    # =====================================================
    # خواندن اکالا
    # =====================================================

    print()

    print(
        "در حال خواندن محصولات اکالا..."
    )

    with open(
        OKALA_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        okala = json.load(file)

    print(
        "تعداد محصولات اکالا:",
        len(okala)
    )

    # =====================================================
    # مرحله اول
    # =====================================================

    print()

    print("=" * 50)

    print(
        "مرحله ۱: تطبیق شیر"
    )

    print("=" * 50)

    matches = match_products(
        digikala,
        okala
    )

    print()

    print(
        "تعداد شیرهای Match شده:",
        len(matches)
    )

    # =====================================================
    # نمایش Matchها
    # =====================================================

    for index, match in enumerate(
        matches,
        start=1
    ):

        print()

        print(
            f"#{index}"
        )

        print(
            "دیجی‌کالا:",
            match["digikala"]["product"]
        )

        print(
            "اکالا:",
            match["okala"]["product"]
        )

        print(
            "امتیاز:",
            match["match_score"]
        )

    # =====================================================
    # ذخیره matched_products
    # =====================================================

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            matches,
            file,
            ensure_ascii=False,
            indent=4
        )

    # =====================================================
    # مرحله دوم
    # =====================================================

    print()

    print("=" * 50)

    print(
        "مرحله ۲: مقایسه برندهای دیجی‌کالا"
    )

    print("=" * 50)

    brand_comparison = create_brand_comparison(
        digikala
    )

    # =====================================================
    # نمایش برندها
    # =====================================================

    for category, brands in brand_comparison.items():

        print()

        print(
            f"📦 {category}"
        )

        for brand, products in brands.items():

            print(
                f"   🏷️ {brand}: {len(products)} محصول"
            )

    # =====================================================
    # ذخیره brand_comparison
    # =====================================================

    with open(
        BRAND_OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            brand_comparison,
            file,
            ensure_ascii=False,
            indent=4
        )

    # =====================================================
    # پایان
    # =====================================================

    print()

    print("=" * 50)

    print(
        "تمام شد."
    )

    print("=" * 50)

    print(
        "✓ matched_products.json"
    )

    print(
        "✓ brand_comparison.json"
    )


# =========================================================
# اجرای برنامه
# =========================================================

if __name__ == "__main__":

    main()