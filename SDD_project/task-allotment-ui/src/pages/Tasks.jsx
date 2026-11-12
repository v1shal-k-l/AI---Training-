import {
    useEffect,
    useState
} from "react";

import {
    getTasks
} from "../services/taskService";

export default function Tasks() {

    const [tasks, setTasks] =
        useState([]);

    useEffect(() => {

        loadTasks();

    }, []);

    const loadTasks = async () => {

        const data =
            await getTasks();

        setTasks(data);
    };

    return (

        <div>

            <h2>Tasks</h2>

            <table border="1">

                <thead>
                <tr>
                    <th>ID</th>
                    <th>Task</th>
                    <th>Status</th>
                </tr>
                </thead>

                <tbody>

                {tasks.map(t => (

                    <tr key={t.id}>
                        <td>{t.id}</td>
                        <td>{t.task_name}</td>
                        <td>{t.status}</td>
                    </tr>

                ))}

                </tbody>

            </table>

        </div>

    );
}