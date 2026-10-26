import { useNavigate } from "react-router-dom";

function Payment() {

  const navigate = useNavigate();

  const handlePayment = (e) => {

    e.preventDefault();

    localStorage.removeItem("cart");

    navigate("/success");
  };

  return (
    <div className="payment-container">

      <h2>Payment Details</h2>

      <form onSubmit={handlePayment}>

        <input
          className="form-control"
          placeholder="Card Number"
          required
        />

        <input
          className="form-control"
          placeholder="Card Holder Name"
          required
        />

        <input
          className="form-control"
          placeholder="Expiry Date"
          required
        />

        <input
          className="form-control"
          placeholder="CVV"
          required
        />

        <button
          className="btn"
          type="submit"
        >
          Pay Now
        </button>

      </form>

    </div>
  );
}

export default Payment;