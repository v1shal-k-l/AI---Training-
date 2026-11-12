import json
from pathlib import Path

DATA_FILE = (
    Path(__file__).resolve().parent
    / "products.json"
)


def load_products():

    with open(
        DATA_FILE,
        encoding="utf-8"
    ) as file:

        return json.load(file)


def search_products(
    keyword
):

    keyword = keyword.lower()

    matches = [

        product

        for product
        in load_products()

        if (
            keyword
            in product["name"].lower()

            or

            keyword
            in product["category"].lower()
        )
    ]

    if not matches:

        return {
            "success": False,
            "message":
            "No matching products found."
        }

    return {
        "success": True,
        "products": matches
    }


def calculate_order_total(
    product_id,
    quantity
):

    if quantity <= 0:

        return {
            "success": False,
            "message":
            "Quantity must be greater than zero."
        }

    product = next(

        (
            item

            for item
            in load_products()

            if item["id"].upper()
            == product_id.upper()
        ),

        None
    )

    if product is None:

        return {
            "success": False,
            "message":
            "Product not found."
        }

    if quantity > product["stock"]:

        return {
            "success": False,
            "message":
            "Insufficient stock."
        }

    total = (
        product["price_inr"]
        * quantity
    )

    return {
        "success": True,
        "product_id":
        product["id"],

        "product_name":
        product["name"],

        "quantity":
        quantity,

        "price_inr":
        product["price_inr"],

        "total_cost":
        total,

        "rating":
        product["rating"]
    }