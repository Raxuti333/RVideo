CREATE INDEX IF NOT EXISTS idx_vid_timestamp ON comment(vid, timestamp);
CREATE INDEX IF NOT EXISTS idx_vid_private ON video(vid, private);
CREATE INDEX IF NOT EXISTS idx_pid_private ON video(pid, private);
CREATE INDEX IF NOT EXISTS  idx_text ON tag(text);