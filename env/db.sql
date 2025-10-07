CREATE TABLE IF NOT EXISTS profile 
( 
    pid INTEGER PRIMARY KEY, 
    username TEXT NOT NULL UNIQUE, 
    password TEXT, 
    timestamp INTEGER, 
    date TEXT
);

CREATE TABLE IF NOT EXISTS video 
( 
    vid INTEGER PRIMARY KEY,
    pid INTEGER NOT NULL,
    private INTEGER NOT NULL,
    views INTEGER,
    name TEXT, 
    description TEXT,
    timestamp INTEGER NOT NULL, 
    date TEXT,
    FOREIGN KEY(pid) REFERENCES profile(pid)
);

CREATE TABLE IF NOT EXISTS comment 
( 
    cid INTEGER PRIMARY KEY, 
    vid INTEGER NOT NULL, 
    pid INTEGER NOT NULL, 
    text TEXT, 
    timestamp INTEGER NOT NULL, 
    date TEXT, 
    FOREIGN KEY(vid) REFERENCES video(vid), 
    FOREIGN KEY(pid) REFERENCES profile(pid) 
);

CREATE TABLE IF NOT EXISTS tag
(
    vid INTEGER NOT NULL,
    text TEXT,
    FOREIGN KEY(vid) REFERENCES video(vid)
);