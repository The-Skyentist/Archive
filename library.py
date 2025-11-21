import sqlite3

conn = sqlite3.connect("library.db")
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS genres (
        id INTEGER PRIMARY KEY,
        type TEXT NOT NULL
    );
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS books (
        id PRIMARY KEY,
        title TEXT NOT NULL,
        author TEXT NOT NULL,
        pub_year INTEGER,
        genre TEXT,
        ISBN INTEGER,
        FOREIGN KEY (genre)
        REFERENCES genres(type)
    );
''')