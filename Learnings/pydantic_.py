from pydantic import BaseModel, ValidationError, Field
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s - %(message)s"
)

# Pydantic model
class Employee(BaseModel):
    name: str
    age: int = Field(gt=18)
    email: str
    salary: float = Field(gt=0)

data = {
    "name" : "Joe",
    "age" : 24,
    "email" : "",
    "salary" : 1000000
}
try :
    employee = Employee(**data)
    logging.info("Employee data validated successfully")
    print(employee)