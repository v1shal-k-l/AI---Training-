import axios from "../api/axios";

export const login = async (payload) => {
    const response = await axios.post(
        "/login",
        payload
    );

    return response.data;
};