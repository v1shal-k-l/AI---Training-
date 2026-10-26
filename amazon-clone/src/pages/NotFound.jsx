import { Link } from "react-router-dom";

export default function NotFound() {

  return (
    <div
      style={{
        textAlign:"center",
        marginTop:"100px"
      }}
    >
      <h1>404</h1>

      <h2>
        Page Not Found
      </h2>

      <Link to="/">
        Go Back Home
      </Link>
    </div>
  );
}
