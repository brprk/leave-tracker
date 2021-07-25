import sqlite3 as sl
from numpy import busday_count
from datetime import date, timedelta
from dateutil import parser


DATABASE = 'database.db'
WORKING_DAYS = '1111100'
PUBLIC_HOLIDAYS = [
    '2020-01-01',
    '2020-04-10',
    '2020-04-13',
    '2020-05-08',
    '2020-05-25',
    '2020-08-31',
    '2020-12-25',
    '2020-12-28',
    '2021-01-01',
    '2021-04-02',
    '2021-04-05',
    '2021-05-03',
    '2021-05-31',
    '2021-08-30',
    '2021-12-27',
    '2021-12-28'
]


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


class LeaveRequestTableElement:
    """class that represents a request table element"""
    def __init__(self, id, colleague_name, start_date, end_date, leave_type_name, status_name):
        self.id = id
        self.colleague_name = colleague_name
        self.start_date = start_date
        self.end_date = end_date
        self.leave_type_name = leave_type_name
        self.status_name = status_name



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


def get_leave_requests_table(colleague_id):
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

    result_list = []

    for r in leave_requests:
        result_list.append(LeaveRequestTableElement(id=r['id'],
                                                    colleague_name=r['name'],
                                                    start_date=r['start_date'],
                                                    end_date=r['end_date'],
                                                    leave_type_name=r['leave_type'],
                                                    status_name=r['status']))

    return result_list


def get_colleagues_table():
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


def calculate_net_leave_days(leave_start_date, leave_end_date, year):

    # must convert YYYY-MM-DD to datetime.date
    leave_start_date = parser.parse(leave_start_date).date()
    leave_end_date = parser.parse(leave_end_date).date()

    year_start = date(year, 1, 1)
    year_end = date(year, 12, 31)

    # leave days are only required for the
    # year being considered
    if leave_start_date <= year_start:
        leave_start_date = year_start
    else:
        leave_start_date = leave_start_date

    if leave_end_date >= year_end:
        leave_end_date = year_end
    else:
        leave_end_date = leave_end_date

    # busday_count excludes the end day
    # so we offset by one day
    leave_end_date += timedelta(days=1)

    # must convert YYYY-MM-DD to datetime.date
    for d in PUBLIC_HOLIDAYS:
        parser.parse(d).date()

    leave_days = busday_count(leave_start_date, leave_end_date, weekmask=WORKING_DAYS, holidays=PUBLIC_HOLIDAYS)

    return leave_days


def get_colleague_leave_requests(colleague_id, year):
    query = f"""
                SELECT
                    start_date,
                    end_date,
                    leave_type_id,
                    status_id
                FROM leave_request
                WHERE  colleague_id = {colleague_id}
                  AND  status_id IN (1, 2) -- pending or approved
                  AND (CAST(strftime('%Y', start_date) as integer) = {year} OR
                       CAST(strftime('%Y', end_date)   as integer) = {year});
            """

    leave_requests = query_db(query, use_row_factory=True)

    result_list = []

    for r in leave_requests:
        result_list.append(dict(start_date=r['start_date'],
                                end_date=r['end_date'],
                                leave_type_id=r['leave_type_id'],
                                status_id=r['status_id']
                                ))

    return result_list


def calc_total_leave_days(leave_requests, year):
    total_leave_taken = 0
    for l in leave_requests:
        if not l['start_date'] > l['end_date']:
            if l['leave_type_id'] == 2:  # half day
                total_leave_taken += 0.5
            else:
                total_leave_taken += calculate_net_leave_days(l['start_date'],
                                                              l['end_date'],
                                                              year)
    return total_leave_taken


def colleague_taken_leave_days(colleague_id, year):
    leave_requests = get_colleague_leave_requests(colleague_id, year)
    taken_leave_days = calc_total_leave_days(leave_requests, year)

    return taken_leave_days
