import json
from pathlib import Path

DATA_FILE = (
    Path(__file__).resolve().parent
    / "restaurants.json"
)


def load_restaurants():

    with open(
        DATA_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def search_restaurants(keyword):

    keyword = keyword.lower()

    matches = []

    for restaurant in load_restaurants():

        if (
            keyword in restaurant["name"].lower()
            or keyword in restaurant["cuisine"].lower()
            or keyword in restaurant["location"].lower()
        ):

            matches.append(
                restaurant
            )

    if not matches:

        return {
            "success": False,
            "message":
                "No matching restaurants found."
        }

    return {
        "success": True,
        "restaurants": matches
    }


def calculate_dining_cost(
    restaurant_id,
    guests
):

    restaurant = next(

        (
            restaurant

            for restaurant
            in load_restaurants()

            if restaurant["id"].upper()
            == restaurant_id.upper()
        ),

        None
    )

    if restaurant is None:

        return {
            "success": False,
            "message":
                "Restaurant not found."
        }

    total_cost = (
        restaurant["price_per_person"]
        * guests
    )

    return {

        "success": True,

        "restaurant_id":
        restaurant["id"],

        "restaurant_name":
        restaurant["name"],

        "cuisine":
        restaurant["cuisine"],

        "location":
        restaurant["location"],

        "guests":
        guests,

        "price_per_person":
        restaurant["price_per_person"],

        "estimated_cost":
        total_cost,

        "available_seats":
        restaurant["available_seats"]
    }