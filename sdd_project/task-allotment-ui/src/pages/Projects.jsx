import {
    useEffect,
    useState
} from "react";

import {
    getProjects
} from "../services/projectService";

export default function Projects() {

    const [projects, setProjects] =
        useState([]);

    useEffect(() => {

        loadProjects();

    }, []);

    const loadProjects = async () => {

        const data =
            await getProjects();

        setProjects(data);
    };

    return (

        <div>

            <h2>Projects</h2>

            <table border="1">

                <thead>
                <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Status</th>
                </tr>
                </thead>

                <tbody>

                {projects.map(p => (

                    <tr key={p.id}>
                        <td>{p.id}</td>
                        <td>{p.project_name}</td>
                        <td>{p.status}</td>
                    </tr>

                ))}

                </tbody>

            </table>

        </div>

    );
}