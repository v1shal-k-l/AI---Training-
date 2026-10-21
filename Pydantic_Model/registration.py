import json
import logging
from pydantic import BaseModel, ValidationError
from typing import Literal


# Logging
logging.basicConfig(
    filename="registration.log",
    level=logging.INFO,
    format="%(levelname)s - %(message)s"
)


class Registration(BaseModel):
    registration_id: str
    name: str
    email: str
    age: int
    ticket_type: Literal["Standard", "Premium", "VIP"]
    amount: float


valid_records = []
total = 0
invalid = 0

try:
    with open("registrations.json", "r") as file:
        data = json.load(file)

    total = len(data)

    for record in data:
        try:
            reg = Registration(**record)

            if reg.age < 18:
                raise ValueError("Age must be at least 18")

            if reg.amount <= 0:
                raise ValueError("Amount must be greater than 0")

            valid_records.append(reg)

            logging.info(
                f"Registration {reg.registration_id} validated successfully"
            )

            if reg.ticket_type == "VIP":
                logging.warning(
                    f"Registration {reg.registration_id} has VIP ticket"
                )

        except (ValidationError, ValueError) as e:
            invalid += 1

            print(
                f"Registration ID: {record['registration_id']}"
            )
            print("Error:", e)

            logging.error(
                f"Registration {record['registration_id']} failed validation"
            )

except FileNotFoundError:
    print("registrations.json not found")
    logging.error("registrations.json not found")

except json.JSONDecodeError:
    print("Invalid JSON file")
    logging.error("Invalid JSON file")

else:
    print("\nValid Registrations")

    for reg in valid_records:
        print(reg)

    # Dictionary
    if valid_records:
        print("\nDictionary:")
        print(valid_records[1].model_dump())

        # JSON
        print("\nJSON:")
        print(valid_records[0].model_dump_json(indent=4))

    # Save valid registrations
    with open("valid_registrations.json", "w") as file:
        json.dump(
            [r.model_dump() for r in valid_records],
            file,
            indent=4
        )

    print("\nSummary")
    print("Total records:", total)
    print("Valid records:", len(valid_records))
    print("Invalid records:", invalid)