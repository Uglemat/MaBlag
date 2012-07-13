DROP TABLE IF EXISTS post;
DROP TABLE IF EXISTS comment;
DROP TABLE IF EXISTS about;
DROP TABLE IF EXISTS draft;

CREATE TABLE post (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       title STRING NOT NULL,
       text STRING NOT NULL,
       removed INTEGER NOT NULL,
       unixtime INTEGER NOT NULL,  -- Time of publication
       lastedit INTEGER,    	   -- Last edit, 0 if never edited
       timeofremoval INTEGER
);
CREATE TABLE draft (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       title STRING NOT NULL,
       text STRING NOT NULL,
       removed INTEGER NOT NULL,
       lastedit INTEGER NOT NULL,   -- Last edit. There's always a last edit.
       timeofremoval INTEGER
);
CREATE TABLE about (
       text STRING NOT NULL,
       unixtime INTEGER NOT NULL -- Last edit or 0 if never edited
);
CREATE TABLE comment (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       commentpage INTEGER NOT NULL, -- The id of the post
       commenttext STRING NOT NULL,
       nickname STRING NOT NULL,
       removed INTEGER NOT NULL,
       unixtime INTEGER NOT NULL, -- Time of creation
       isadmin INTEGER NOT NULL, -- 1 if admin comment, else 0
       ip STRING NOT NULL,
       website STRING,
       email STRING,
       publicemail INTEGER NOT NULL,
       timeofremoval INTEGER
);

INSERT INTO about VALUES ("",0);
