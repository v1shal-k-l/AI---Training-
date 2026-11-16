-- =====================================
-- Database: travel_db
-- Project: AI Travel & Weather Advisor
-- =====================================

DROP TABLE IF EXISTS trips;

CREATE TABLE trips (

    trip_id SERIAL PRIMARY KEY,

    employee_id VARCHAR(50) NOT NULL,

    destination VARCHAR(100) NOT NULL,

    start_date DATE NOT NULL,

    end_date DATE NOT NULL,

    purpose TEXT,

    status VARCHAR(20) DEFAULT 'ACTIVE',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================
-- Sample Records
-- =====================================

INSERT INTO trips
(
    employee_id,
    destination,
    start_date,
    end_date,
    purpose,
    status
)
VALUES
(
    'EMP101',
    'Jaipur',
    '2026-11-25',
    '2026-11-28',
    'Client Meeting',
    'ACTIVE'
);

INSERT INTO trips
(
    employee_id,
    destination,
    start_date,
    end_date,
    purpose,
    status
)
VALUES
(
    'EMP102',
    'Mumbai',
    '2026-12-01',
    '2026-12-04',
    'Sales Presentation',
    'ACTIVE'
);

INSERT INTO trips
(
    employee_id,
    destination,
    start_date,
    end_date,
    purpose,
    status
)
VALUES
(
    'EMP103',
    'Bangalore',
    '2026-12-10',
    '2026-12-12',
    'Internal Workshop',
    'ACTIVE'
);