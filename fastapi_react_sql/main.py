from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import psycopg2

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_connection():
    return psycopg2.connect(
        host="localhost",
        port="5432",
        database="product_store",
        user="postgres",
        password="Admin@123"
    )

class Product(BaseModel):
    id: int
    name: str
    price: float
    image: str


@app.get("/products")
def get_products():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, price, image
        FROM products
        ORDER BY id
    """)

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    products = []

    for row in rows:
        products.append({
            "id": row[0],
            "name": row[1],
            "price": float(row[2]),
            "image": row[3]
        })

    return products

@app.post("/product_add")
def create_product(product: Product):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO products(id, name, price, image)
        VALUES(%s, %s, %s, %s)
        """,
        (
            product.id,
            product.name,
            product.price,
            product.image
        )
    )

    conn.commit()

    cursor.close()
    conn.close()

    return {
        "message": "Product added successfully"
    }

@app.put("/products/{product_id}")
def update_product(product_id: int, product: Product):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE products
        SET name=%s,
            price=%s,
            image=%s
        WHERE id=%s
        """,
        (
            product.name,
            product.price,
            product.image,
            product_id
        )
    )

    if cursor.rowcount == 0:
        cursor.close()
        conn.close()
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    conn.commit()

    cursor.close()
    conn.close()

    return {
        "message": "Product updated successfully"
    }
@app.delete("/products/{product_id}")
def delete_product(product_id: int):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM products
        WHERE id=%s
        """,
        (product_id,)
    )

    if cursor.rowcount == 0:
        cursor.close()
        conn.close()
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    conn.commit()

    cursor.close()
    conn.close()

    return {
        "message": "Product deleted successfully"
    }
