import json
from pathlib import Path

from langchain.tools import tool

WORKSHOP_FILE = Path("workshops.json")
COUPON_FILE = Path("coupons.json")


def load_workshops():

    with open(
        WORKSHOP_FILE,
        encoding="utf-8"
    ) as file:

        return json.load(file)


def load_coupons():

    with open(
        COUPON_FILE,
        encoding="utf-8"
    ) as file:

        return json.load(file)


@tool
def list_all_workshops():
    """
    Return all workshops.
    """

    return json.dumps(
        load_workshops(),
        indent=2
    )


@tool
def find_cheapest_workshop():
    """
    Return cheapest workshop.
    """

    workshop = min(
        load_workshops(),
        key=lambda x:
        x["fee_per_person_inr"]
    )

    return json.dumps(
        workshop,
        indent=2
    )


@tool
def search_workshops(keyword: str):
    """
    Search workshops by keyword.
    """

    results = [

        workshop

        for workshop in load_workshops()

        if keyword.lower()
        in workshop["title"].lower()

    ]

    return json.dumps(
        results,
        indent=2
    )


@tool
def calculate_workshop_fee(
        workshop_id: str,
        participants: int):

    """
    Calculate fee.
    """

    workshop = next(

        (
            workshop

            for workshop
            in load_workshops()

            if workshop["id"]
            == workshop_id
        ),

        None
    )

    if workshop is None:

        return "Workshop not found."

    total_fee = (
        workshop["fee_per_person_inr"]
        * participants
    )

    return json.dumps(
        {
            "workshop":
                workshop["title"],

            "participants":
                participants,

            "total_fee":
                total_fee
        },
        indent=2
    )


@tool
def apply_coupon(
        workshop_id: str,
        participants: int,
        coupon_code: str):

    """
    Apply coupon.
    """

    workshop = next(

        (
            workshop

            for workshop
            in load_workshops()

            if workshop["id"]
            == workshop_id
        ),

        None
    )

    if not workshop:

        return "Workshop not found."

    coupon = next(

        (
            coupon

            for coupon
            in load_coupons()

            if coupon["code"].upper()
            == coupon_code.upper()
        ),

        None
    )

    if not coupon:

        return "Invalid coupon."

    total_fee = (
        workshop["fee_per_person_inr"]
        * participants
    )

    discount = (
        total_fee
        * coupon["discount"]
        / 100
    )

    final_amount = (
        total_fee
        - discount
    )

    return json.dumps(
        {
            "workshop":
                workshop["title"],

            "participants":
                participants,

            "coupon":
                coupon_code,

            "discount":
                discount,

            "final_amount":
                final_amount
        },
        indent=2
    )
