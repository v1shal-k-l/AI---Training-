import {
    useEffect,
    useState
} from "react";

import axios from "../api/axios";

export default function Dashboard() {

    const [data, setData] =
        useState(null);

    useEffect(() => {

        loadDashboard();

    }, []);

    const loadDashboard = async () => {

        const response =
            await axios.get(
                "/dashboard/summary"
            );

        setData(response.data);
    };

    if (!data) {

        return <h2>Loading...</h2>;
    }

    return (

        <div>

            <h2>Dashboard</h2>

            <h3>
                Total Users:
                {data.total_users}
            </h3>

            <h3>
                Total Projects:
                {data.total_projects}
            </h3>

            <h3>
                Total Tasks:
                {data.total_tasks}
            </h3>

        </div>

    );
}