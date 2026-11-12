import { useState, useContext } from "react";
import Navbar from "../components/Navbar";
import { CartContext } from "../context/CartContext";

function Home() {
  const { addToCart } = useContext(CartContext);

  const [search, setSearch] = useState("");

  const products = [
    {
      id: 1,
      name: "Apple iPhone 15 Pro Max",
      price: 149999,
      image:
        "https://m.media-amazon.com/images/I/81dT7CUY6GL._SX679_.jpg",
    },
    {
      id: 2,
      name: "Samsung Galaxy S24 Ultra",
      price: 124999,
      image:
        "https://m.media-amazon.com/images/I/71RVuBs3q9L._SX679_.jpg",
    },
    {
      id: 3,
      name: "Sony WH-1000XM5 Headphones",
      price: 29999,
      image:
        "https://m.media-amazon.com/images/I/61vJtKbAssL._SX679_.jpg",
    },
    {
      id: 4,
      name: "Apple MacBook Air M3",
      price: 114999,
      image:
        "https://m.media-amazon.com/images/I/71jG+e7roXL._SX679_.jpg",
    },
    {
      id: 5,
      name: "Apple Watch Series 9",
      price: 39999,
      image:
        "https://m.media-amazon.com/images/I/71LfnkRgZ4L._SX679_.jpg",
    },
    {
      id: 6,
      name: "boAt Airdopes",
      price: 1999,
      image:
        "https://m.media-amazon.com/images/I/61KNJav3S9L._SX679_.jpg",
    },
    {
      id: 7,
      name: "Dell Inspiron Laptop",
      price: 65999,
      image:
        "https://m.media-amazon.com/images/I/61Dw5Z8LzJL._SX679_.jpg",
    },
    {
      id: 8,
      name: "Noise Smart Watch",
      price: 2999,
      image:
        "https://m.media-amazon.com/images/I/61epn29QG0L._SX679_.jpg",
    },
  ];

  const filteredProducts = products.filter((product) =>
    product.name.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <>
      <Navbar />

      {/* Heading */}
      <div
        style={{
          padding: "20px",
          fontSize: "28px",
          fontWeight: "bold",
          color: "#131921",
        }}
      >
        Today's Deals
      </div>

      {/* Search */}
      <div className="search-container">
        <input
          type="text"
          placeholder="Search products..."
          className="search-input"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      {/* Products */}
      <div className="products-container">
        {filteredProducts.map((product) => (
          <div
            className="product-card"
            key={product.id}
          >
            <img
              src={product.image}
              alt={product.name}
            />

            <h3>{product.name}</h3>

            <p>
              ₹{product.price.toLocaleString()}
            </p>

            <button
              className="btn"
              onClick={() => addToCart(product)}
            >
              Add To Cart
            </button>
          </div>
        ))}
      </div>
    </>
  );
}

export default Home;
