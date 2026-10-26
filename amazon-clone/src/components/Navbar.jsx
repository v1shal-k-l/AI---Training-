import { Link } from "react-router-dom";
import { useContext } from "react";
import { CartContext } from "../context/CartContext";

function Navbar() {
  const { cart } = useContext(CartContext);

  return (
    <>
      <nav className="navbar">
        <Link to="/" className="logo">
          amazon
        </Link>

        <input
          className="navbar-search"
          placeholder="Search Amazon"
        />

        <div className="nav-right">
          <Link to="/login">Sign In</Link>

          <Link to="/cart" className="cart-link">
            🛒 Cart
            <span className="cart-badge">
              {cart.length}
            </span>
          </Link>
          <Link to="/" className="logo">
            🛒 amazon
          </Link>
        </div>
      </nav>

      <div className="sub-navbar">
        <span>All</span>
        <span>Today's Deals</span>
        <span>Electronics</span>
        <span>Mobiles</span>
        <span>Fashion</span>
        <span>Prime</span>
      </div>
    </>
  );
}

export default Navbar;