-- Add unique constraint to device_logs
ALTER TABLE device_logs ADD CONSTRAINT device_logs_device_id_key UNIQUE (device_id);
