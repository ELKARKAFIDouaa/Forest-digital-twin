-- 1. Création de la base de données
CREATE DATABASE dtdb
    WITH 
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'French_France.1252'
    LC_CTYPE = 'French_France.1252'
    CONNECTION LIMIT = -1;

-- 2. Se connecter à la base DTDB
\c dtdb;

-- 3. Création de la table roles
CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    permissions JSON
);

-- 4. Création de la table users
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(256) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    telephone VARCHAR(15) NOT NULL UNIQUE,
    role VARCHAR(20),
    is_active BOOLEAN DEFAULT true
);

-- 5. Création de la table user_roles (table de liaison)
CREATE TABLE user_roles (
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    role_id INTEGER REFERENCES roles(id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, role_id)
);

-- 6. Création de la table alembic_version (pour les migrations)
CREATE TABLE alembic_version (
    version_num VARCHAR(32) NOT NULL
);

-- 7. Insertion des rôles par défaut
INSERT INTO roles (name, description, permissions) VALUES
('admin', 'Administrateur du système', '["manage_users", "manage_roles", "view_dashboard", "manage_iot"]'),
('forest_agent', 'Agent forestier', '["view_dashboard", "manage_iot", "view_reports"]'),
('researcher', 'Chercheur', '["view_dashboard", "view_reports", "run_predictions"]'),
('viewer', 'Observateur', '["view_dashboard"]');

-- 8. Insertion de l'utilisateur admin par défaut
-- Mot de passe: admin123
INSERT INTO users (email, password_hash, telephone, role, is_active) VALUES
(
    'admin@forest.com',
    'scrypt:32768:8:1$Amh944Zf36Ukgabz$1aa157a1600835bdcb59f5a7ddf68b91542ddd311ea246b0005762d856a4f7aa8b65db52cafe81118b157762491ff6eb8f18ebd53487e5662ad291c970fba459',
    '+123456789',
    'admin',
    true
);

-- 9. Association de l'admin au rôle admin
INSERT INTO user_roles (user_id, role_id)
SELECT u.id, r.id 
FROM users u, roles r 
WHERE u.email = 'admin@forest.com' AND r.name = 'admin';



-

-- 10. Création de la table forests
CREATE TABLE forests (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    location TEXT,
    surface FLOAT
);

-- 11. Création de la table zones
CREATE TABLE zones (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    forest_id INTEGER REFERENCES forests(id) ON DELETE CASCADE,
    coordinates JSONB,
    area FLOAT,
    vegetation_type VARCHAR(50),
    soil_type VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- Table capteurs
CREATE TABLE sensors (
    id SERIAL PRIMARY KEY,
    sensor_id VARCHAR(100) UNIQUE NOT NULL,
    category VARCHAR(50),
    metric VARCHAR(100),
    unit VARCHAR(20),
    min_value FLOAT,
    max_value FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table données reçues
CREATE TABLE sensor_data (
    id SERIAL PRIMARY KEY,
    sensor_id VARCHAR(100) REFERENCES sensors(sensor_id) ON DELETE CASCADE,
    value FLOAT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
