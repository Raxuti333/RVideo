CREATE TABLE profile ( pid INTEGER PRIMARY KEY, username TEXT, password TEXT, timestamp INTEGER, date TEXT );
CREATE TABLE video ( vid INTEGER PRIMARY KEY, pid INTEGER, views INTEGER, name TEXT, description TEXT, timestamp INTEGER, date TEXT, tags TEXT, FOREIGN KEY(pid) REFERENCES profile(pid) );
CREATE TABLE comment ( cid INTEGER PRIMARY KEY, vid INTEGER, pid INTEGER, text TEXT, timestamp INTEGER, date TEXT, FOREIGN KEY(vid) REFERENCES video(vid), FOREIGN KEY(pid) REFERENCES profile(pid) );
