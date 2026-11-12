import { useContext } from "react";
import Navbar from "../components/Navbar";
import { CartContext } from "../context/CartContext";
import { useNavigate } from "react-router-dom";

export default function Cart() {

  const { cart, removeFromCart } =
    useContext(CartContext);

  const navigate = useNavigate();

  const total = cart.reduce(
    (sum,item)=>
    sum + item.price * item.quantity,
    0
  );

  const checkout = () => {

    const token = localStorage.getItem("token");

    if(!token){
      navigate("/login");
    }
    else{
      navigate("/payment");
    }
  };

  return (
    <>
      <Navbar />

      <div style={{ padding:"20px" }}>

        <h2>Shopping Cart</h2>

        {cart.map(item=>(
          <div key={item.id}>
            <h3>{item.name}</h3>
            <p>Qty : {item.quantity}</p>
            <p>₹{item.price}</p>

            <button
              onClick={()=>
                removeFromCart(item.id)
              }
            >
              Remove
            </button>

            <hr />
          </div>
        ))}

        <h2>Total : ₹{total}</h2>

        <button onClick={checkout}>
          Proceed To Payment
        </button>

      </div>
    </>
  );
}