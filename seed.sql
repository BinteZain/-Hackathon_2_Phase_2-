-- Seed data for users
INSERT INTO "user" (id, email, username, password_hash, email_verified, created_at, updated_at, last_login_at, is_active) VALUES
('123e4567-e89b-12d3-a456-426614174000', 'admin@example.com', 'admin', '$2b$12$abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ123456', true, '2023-01-01 00:00:00', '2023-01-01 00:00:00', '2023-01-01 00:00:00', true),
('123e4567-e89b-12d3-a456-426614174001', 'user1@example.com', 'user1', '$2b$12$abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ123456', true, '2023-01-02 00:00:00', '2023-01-02 00:00:00', '2023-01-02 00:00:00', true),
('123e4567-e89b-12d3-a456-426614174002', 'user2@example.com', 'user2', '$2b$12$abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ123456', true, '2023-01-03 00:00:00', '2023-01-03 00:00:00', '2023-01-03 00:00:00', true);

-- Seed data for tasks
INSERT INTO task (id, user_id, title, description, status, priority, due_date, created_at, updated_at, completed_at) VALUES
('123e4567-e89b-12d3-a456-426614175000', '123e4567-e89b-12d3-a456-426614174000', 'Setup development environment', 'Install necessary tools and configure the development environment', 'completed', 'high', '2023-01-15 00:00:00', '2023-01-01 00:00:00', '2023-01-05 00:00:00', '2023-01-05 00:00:00'),
('123e4567-e89b-12d3-a456-426614175001', '123e4567-e89b-12d3-a456-426614174000', 'Design database schema', 'Create the initial database schema for the application', 'completed', 'high', '2023-01-20 00:00:00', '2023-01-02 00:00:00', '2023-01-10 00:00:00', '2023-01-10 00:00:00'),
('123e4567-e89b-12d3-a456-426614175002', '123e4567-e89b-12d3-a456-426614174000', 'Implement authentication', 'Create login and registration functionality', 'in-progress', 'high', '2023-02-01 00:00:00', '2023-01-10 00:00:00', '2023-01-15 00:00:00', NULL),
('123e4567-e89b-12d3-a456-426614175003', '123e4567-e89b-12d3-a456-426614174000', 'Create task management API', 'Develop endpoints for CRUD operations on tasks', 'pending', 'medium', '2023-02-15 00:00:00', '2023-01-15 00:00:00', '2023-01-15 00:00:00', NULL),
('123e4567-e89b-12d3-a456-426614175004', '123e4567-e89b-12d3-a456-426614174001', 'Write documentation', 'Document the API endpoints and usage', 'pending', 'low', '2023-03-01 00:00:00', '2023-01-20 00:00:00', '2023-01-20 00:00:00', NULL),
('123e4567-e89b-12d3-a456-426614175005', '123e4567-e89b-12d3-a456-426614174001', 'Implement frontend components', 'Create React components for the UI', 'in-progress', 'medium', '2023-02-10 00:00:00', '2023-01-25 00:00:00', '2023-01-28 00:00:00', NULL),
('123e4567-e89b-12d3-a456-426614175006', '123e4567-e89b-12d3-a456-426614174002', 'Setup CI/CD pipeline', 'Configure continuous integration and deployment', 'pending', 'high', '2023-02-05 00:00:00', '2023-01-30 00:00:00', '2023-01-30 00:00:00', NULL);