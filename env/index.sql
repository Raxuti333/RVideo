CREATE INDEX idx_vid_timestamp ON comment(vid, timestamp);
CREATE INDEX idx_vid_private ON video(vid, private);
CREATE INDEX idx_pid_private ON video(pid, private);