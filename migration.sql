-- Up Migration
CREATE TABLE hotel (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price_per_night DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    location VARCHAR(255),
    rating DECIMAL(2,1) CHECK (rating >= 0 AND rating <= 5),
    available_rooms INTEGER DEFAULT 0,
    amenities TEXT[]
);

-- Indexes
CREATE INDEX idx_hotel_name ON hotel(name);
CREATE INDEX idx_hotel_price ON hotel(price_per_night);
CREATE INDEX idx_hotel_rating ON hotel(rating);

-- Down Migration
DROP INDEX IF EXISTS idx_hotel_rating;
DROP INDEX IF EXISTS idx_hotel_price;
DROP INDEX IF EXISTS idx_hotel_name;
DROP TABLE IF EXISTS hotel;