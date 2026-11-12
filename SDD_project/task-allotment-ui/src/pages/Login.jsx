import {
    Button,
    Container,
    TextField
} from "@mui/material";

import {
    useState
} from "react";

import {
    useNavigate
} from "react-router-dom";

import {
    login
} from "../services/authService";

export default function Login() {

    const navigate = useNavigate();

    const [form, setForm] = useState({
        email: "",
        password: ""
    });

    const handleLogin = async () => {

        try {

            const result =
                await login(form);

            localStorage.setItem(
                "token",
                result.access_token
            );

            localStorage.setItem(
                "role",
                result.role
            );

            navigate("/dashboard");

        } catch (error) {

            alert(
                "Invalid Credentials"
            );
        }
    };

    return (
        <Container
            maxWidth="sm"
            sx={{ mt: 10 }}
        >

            <TextField
                fullWidth
                label="Email"
                margin="normal"
                onChange={(e) =>
                    setForm({
                        ...form,
                        email: e.target.value
                    })
                }
            />

            <TextField
                fullWidth
                type="password"
                label="Password"
                margin="normal"
                onChange={(e) =>
                    setForm({
                        ...form,
                        password: e.target.value
                    })
                }
            />

            <Button
                fullWidth
                variant="contained"
                onClick={handleLogin}
            >
                Login
            </Button>

        </Container>
    );
}