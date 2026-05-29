CREATE TABLE users (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    full_name VARCHAR(100),
    email VARCHAR(150) UNIQUE,
    phone VARCHAR(20),
    password_hash VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE chat_sessions (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT,
    title VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE messages (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    session_id BIGINT,
    sender ENUM('user', 'bot'),
    message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES chat_sessions(id)
);

CREATE TABLE itineraries (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    session_id BIGINT,
    user_id BIGINT,

    title VARCHAR(255),

    destination VARCHAR(255),

    start_date DATE,
    end_date DATE,

    total_days INT,

    budget DECIMAL(12,2),

    travelers_count INT,

    trip_type VARCHAR(100),

    ai_summary TEXT,

    status ENUM(
        'draft',
        'customized',
        'approved',
        'booked'
    ) DEFAULT 'draft',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (session_id) REFERENCES chat_sessions(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE itinerary_days (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,

    itinerary_id BIGINT,

    day_number INT,

    title VARCHAR(255),

    description TEXT,

    hotel_name VARCHAR(255),

    transport_mode VARCHAR(100),

    estimated_cost DECIMAL(10,2),

    FOREIGN KEY (itinerary_id)
    REFERENCES itineraries(id)
);

CREATE TABLE activities (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,

    itinerary_day_id BIGINT,

    activity_name VARCHAR(255),

    location VARCHAR(255),

    activity_time VARCHAR(100),

    cost DECIMAL(10,2),

    notes TEXT,

    FOREIGN KEY (itinerary_day_id)
    REFERENCES itinerary_days(id)
);

CREATE TABLE preferences (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,

    user_id BIGINT,

    preferred_budget_type ENUM(
        'low',
        'medium',
        'luxury'
    ),

    preferred_transport VARCHAR(100),

    preferred_hotel_rating INT,

    favorite_destinations TEXT,

    food_preferences TEXT,

    FOREIGN KEY (user_id)
    REFERENCES users(id)
);

CREATE TABLE destinations (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,

    country VARCHAR(100),

    city VARCHAR(100),

    description TEXT,

    avg_budget_per_day DECIMAL(10,2),

    best_season VARCHAR(100)
);