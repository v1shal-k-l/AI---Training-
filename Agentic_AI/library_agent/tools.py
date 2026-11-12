import json
from pathlib import Path

BOOKS_FILE = Path("books.json")
RESERVATIONS_FILE = Path("reservations.json")


def load_books():

    with open(
        BOOKS_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def save_books(data):

    with open(
        BOOKS_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=4
        )


def load_reservations():

    with open(
        RESERVATIONS_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def save_reservations(data):

    with open(
        RESERVATIONS_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=4
        )


def search_books(keyword):

    books = load_books()

    keyword = keyword.lower()

    matches = []

    for book in books:

        if (
            keyword in book["title"].lower()
            or keyword in book["category"].lower()
            or keyword in book["author"].lower()
        ):

            matches.append(book)

    return matches


def reserve_book(
        book_id,
        customer_name
):

    books = load_books()

    for book in books:

        if book["id"] == book_id:

            if book["available_copies"] <= 0:

                return {
                    "success": False,
                    "message":
                        "No copies available."
                }

            confirmation = input(
                f"\nReserve "
                f"{book['title']} "
                f"for {customer_name}? "
                f"(yes/no): "
            )

            if confirmation.lower() != "yes":

                return {
                    "success": False,
                    "message":
                        "Reservation cancelled."
                }

            book["available_copies"] -= 1

            reservation = {
                "customer":
                    customer_name,
                "book_id":
                    book_id,
                "title":
                    book["title"]
            }

            save_books(books)

            reservations = load_reservations()

            reservations.append(
                reservation
            )

            save_reservations(
                reservations
            )

            return {
                "success": True,
                "reservation":
                    reservation
            }

    return {
        "success": False,
        "message": "Book not found."
    }