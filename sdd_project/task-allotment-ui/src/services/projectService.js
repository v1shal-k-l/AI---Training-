import axios from "../api/axios";

export const getProjects = async () => {

    const response = await axios.get(
        "/projects"
    );

    return response.data;
};

export const createProject = async (
    payload
) => {

    const response = await axios.post(
        "/projects",
        payload
    );

    return response.data;
};
