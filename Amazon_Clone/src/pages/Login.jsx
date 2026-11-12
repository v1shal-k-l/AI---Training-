import { useNavigate } from "react-router-dom";

function Login() {

  const navigate = useNavigate();

  const handleLogin = () => {

    localStorage.setItem(
      "token",
      "loggedin"
    );

    navigate("/payment");
  };

  return (
    <div className="login-container">

      <h2>Login</h2>

      <input
        className="form-control"
        placeholder="Email"
      />

      <input
        className="form-control"
        placeholder="Password"
        type="password"
      />

      <button
        className="btn"
        onClick={handleLogin}
      >
        Login
      </button>

    </div>
  );
}

export default Login;