-- Run these queries in Supabase SQL Editor

-- 1. Add new columns to users table
ALTER TABLE users ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'pending';
ALTER TABLE users ADD COLUMN IF NOT EXISTS approved_by VARCHAR(50);
ALTER TABLE users ADD COLUMN IF NOT EXISTS approved_at TIMESTAMP;

-- 2. Update existing users to active status
UPDATE users SET status = 'active' WHERE username IN ('admin', 'bhargav');

-- 3. Verify the changes
SELECT * FROM users;
