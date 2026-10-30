import {
    Drawer,
    List,
    ListItem,
    ListItemButton,
    ListItemText
} from "@mui/material";

import {
    Link
} from "react-router-dom";

export default function Sidebar() {

    const role =
        localStorage.getItem("role");

    return (
        <Drawer
            variant="permanent"
        >
            <List>

                <ListItem disablePadding>
                    <ListItemButton
                        component={Link}
                        to="/dashboard"
                    >
                        <ListItemText
                            primary="Dashboard"
                        />
                    </ListItemButton>
                </ListItem>

                {role !== "Employee" && (

                    <ListItem disablePadding>
                        <ListItemButton
                            component={Link}
                            to="/projects"
                        >
                            <ListItemText
                                primary="Projects"
                            />
                        </ListItemButton>
                    </ListItem>

                )}

                <ListItem disablePadding>
                    <ListItemButton
                        component={Link}
                        to="/tasks"
                    >
                        <ListItemText
                            primary="Tasks"
                        />
                    </ListItemButton>
                </ListItem>

                {role === "Admin" && (

                    <ListItem disablePadding>
                        <ListItemButton
                            component={Link}
                            to="/users"
                        >
                            <ListItemText
                                primary="Users"
                            />
                        </ListItemButton>
                    </ListItem>

                )}

            </List>
        </Drawer>
    );
}