
CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE IF NOT EXISTS users (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    telegram_id BIGINT NOT NULL UNIQUE,
    username VARCHAR(255),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS categories (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS reports (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    user_id BIGINT NOT NULL
        REFERENCES users(id) ON DELETE CASCADE,

    category_id BIGINT NOT NULL
        REFERENCES categories(id),

    report_type VARCHAR(10) NOT NULL
        CHECK (report_type IN ('lost', 'found')),

    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,

    event_date TIMESTAMPTZ NOT NULL,
    location GEOGRAPHY(POINT, 4326) NOT NULL,
    address TEXT,

    status VARCHAR(10) NOT NULL DEFAULT 'active'
        CHECK (status IN ('active', 'resolved')),

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_reports_category
    ON reports(category_id);

CREATE INDEX IF NOT EXISTS idx_reports_type_status
    ON reports(report_type, status);

CREATE INDEX IF NOT EXISTS idx_reports_event_date
    ON reports(event_date);

CREATE INDEX IF NOT EXISTS idx_reports_location
    ON reports USING GIST(location);

INSERT INTO categories (name) VALUES
    ('Документы'),
    ('Ключи'),
    ('Электроника'),
    ('Одежда'),
    ('Сумки'),
    ('Другое')
ON CONFLICT (name) DO NOTHING;
