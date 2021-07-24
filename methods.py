import sqlite3 as sl

DATABASE = 'database.db'


def connect_to_db():
    db = None
    db = sl.connect(DATABASE)
    return db


def query_db(query, use_row_factory = False):
    conn = connect_to_db()

    if use_row_factory:
        conn.row_factory = sl.Row

    cur = conn.execute(query)
    conn.commit()
    rows = cur.fetchall()
    cur.close()
    conn.close()

    return rows


class Colleague:
    """class that represents a colleague"""
    def __init__(self, name, email, manager_id, colleague_id=None):
        self.name = name
        self.email = email
        self.manager_id = manager_id
        if colleague_id is not None:
            self.colleague_id = colleague_id

    def create(self):
        query = f"""
                    INSERT INTO colleague (name,email,manager_id) VALUES 
                    ('{self.name}','{self.email}','{self.manager_id}');
                """
        query_db(query)

    def edit(self):
        if self.colleague_id is not None:
            query = f"""
                        UPDATE colleague
                         SET name    = '{self.name}'
                            ,email   = '{self.email}'
                            ,manager_id = '{self.manager_id}'
                        WHERE id = '{self.colleague_id}';
                    """
            query_db(query)


class LeaveRequest:
    """class that represents a colleague"""
    def __init__(self, colleague, start_date, end_date, leave_type):
        self.colleague = colleague
        self.start_date = start_date
        self.end_date = end_date
        self.leave_type = leave_type

    def create(self):
        query = f"""
                    INSERT INTO leave_request (colleague_id,start_date,end_date,leave_type_id,status_id) VALUES 
                    ('{self.colleague}','{self.start_date}','{self.end_date}','{self.leave_type}',1);
                """
        query_db(query)


class LeaveAllocation:
    """class that represents a colleague"""
    def __init__(self, colleague_id, year, allocated_days):
        self.colleague_id = colleague_id
        self.year = year
        self.allocated_days = allocated_days

    def create(self):
        query = f"""
                    INSERT INTO annual_leave_allocation (colleague_id,year,allocated_days) VALUES 
                    ('{self.colleague_id}','{self.year}','{self.allocated_days}');
                """
        query_db(query)


def get_colleague_list():
    query = f"""
                SELECT id,name
                FROM colleague
                ORDER BY LOWER(name);
            """
    colleagues = query_db(query)
    return colleagues


def get_colleague(id):
    query = f"""
                SELECT name 
                     , email
                     , manager_id
                FROM colleague
                WHERE id = '{id}';
            """
    colleague = query_db(query)
    return colleague


def get_leave_types():
    query = f"""
                SELECT id, name
                FROM leave_type;
            """
    leave_types = query_db(query)
    return leave_types


def get_leave_requests(colleague_id):
    query = f"""
                SELECT 
                     r.id           id
                    ,c.name         name
                    ,r.start_date   start_date
                    ,r.end_date     end_date
                    ,t.name         leave_type
                    ,s.name         status
                FROM leave_request r
                JOIN colleague  c ON c.id = r.colleague_id
                JOIN leave_type t ON t.id = r.leave_type_id
                JOIN status     s ON s.id = r.status_id
                WHERE r.colleague_id = {colleague_id}
                ORDER BY r.start_date ASC;
            """
    leave_requests = query_db(query, use_row_factory=True)

    return leave_requests


def get_colleagues():
    query = f"""
                SELECT c.id     id
                      ,c.name   name
                      ,c.email  email
                      ,m.name   manager_name
                FROM colleague c
                JOIN colleague m ON m.id = c.manager_id
                ORDER BY LOWER(c.name);
            """
    colleagues = query_db(query, use_row_factory=True)
    return colleagues