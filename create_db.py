import sqlite3 as sl

"""build database and insert default values"""


def create_new_db(run):

    if run:
        con = sl.connect('database.db')

        with con:
            con.execute("""
                CREATE TABLE colleague (
                    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    manager_id INTEGER,
                    FOREIGN KEY(manager_id) REFERENCES colleague(id)
                );
            """)
            con.execute("""
                CREATE TABLE leave_type (
                    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL
                );
            """)
            con.execute("""
                CREATE TABLE status (
                    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL
                );
            """)
            con.execute("""
                CREATE TABLE annual_leave_allocation (
                    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    colleague_id INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    allocated_days INTEGER NOT NULL,
                    FOREIGN KEY(colleague_id) REFERENCES colleague(id)
                );
            """)
            con.execute("""
                CREATE TABLE leave_request (
                    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    colleague_id INTEGER NOT NULL,
                    start_date TEXT NOT NULL,
                    end_date TEXT,
                    leave_type_id INTEGER NOT NULL,
                    status_id INTEGER NOT NULL DEFAULT 1,
                    FOREIGN KEY(colleague_id) REFERENCES colleague(id),
                    FOREIGN KEY(leave_type_id) REFERENCES leave_type(id),
                    FOREIGN KEY(status_id) REFERENCES status(id)
                );
            """)
            con.execute("""
                INSERT INTO status (name) VALUES 
                ('pending'),
                ('approved'),
                ('cancelled');
            """)
            con.execute("""
                INSERT INTO leave_type (name) VALUES 
                ('full day'),
                ('half day');
            """)
    else:
        print("No DB Created")


create_new_db(False)