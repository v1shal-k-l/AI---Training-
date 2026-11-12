import axios from "../api/axios";

export const getTasks = async () => {

    const response = await axios.get(
        "/tasks"
    );

    return response.data;
};

export const createTask = async (
    payload
) => {

    const response = await axios.post(
        "/tasks",
        payload
    );

    return response.data;
};