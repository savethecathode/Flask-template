
'''
    Here we want to properly use the connection and cursor objects as context managers.
    Think:
    1. Using connection and cursor as context manager only commit() but do not close().
    2. You always want to close a cursor once you are done with it (prevents memory leaks).
        - use contextlib.closing()
    3. You do not necessarily want to close the connection.
    Registration System: store registrants in a SQLite database....
    (...)
    3-Previous Version of Code:
    BUG: sqlite3.ProgrammingError: SQLite objects created in a thread can only be used in that same thread.
    FIX: 
        conn = sqlite3.connect(db_file, check_same_thread=False)
    FOLLOW UP: does this suffice?
    2-Previous Version:
    Access row fields by column name in registrants.html
    In templ_sqlite.py

        conn = sqlite3.connect(detect_types = PARSE_DECLTYPES | PARSE_COLNAMES) # not sure what this does but keep it for now...
        conn.row_factory = sqlite3.Row # to access fields by name
    FOLLOW UP: can row_factory be set when connection is being established?

    The current version investigates if the cursor and connection be closed after command is completed? what is a good way to do this? ie: use contextlib and contextmanager?
'''

from contextlib import closing
from flask import Flask, render_template, request, redirect
from templ_sqlite import create_connection, create_table

app = Flask(__name__)

# Registrants database, need a connection, a table, and a function to create users.
conn = create_connection(r"registrants.db")
create_table(conn, """ CREATE TABLE registrants (id INTEGER PRIMARY KEY, name TEXT NOT NULL, sport TEXT NOT NULL); """)

# Append registrant to registrants list
def create_registrant(conn, registrant):
    """
    Create a new project into the projects table
    :param conn:
    :param registrant:
    :return: registrant id
    """
    sql = ''' INSERT INTO registrants(name, sport)
              VALUES(?, ?) '''
    with conn:
        with closing(conn.cursor()) as cur:
            cur.execute(sql, registrant)
            return cur.lastrowid

# Implement SQL query
def select_all_registrants(conn):
    """
    Query
    :param conn: the Connection object
    :return: data
    """
    sql = ''' SELECT * FROM registrants; '''
    with closing(conn.cursor()) as cur:
        cur.execute(sql)
        return cur.fetchall()

TRADITIONAL_SPORTS = [
    "Baseball",
    "Basket Ball",
    "Foot Ball",
    "Tennis",
    "Volleyball",
]

HOBBY_SPORTS = [
    "Table Tennis",
    "Bungee Jumping",
    "Rock Climbing",
    "Squirrel Suit"
]

SCHOOL_SPORTS = [
    "Dodgeball",
    "Four Square"
]

SPORTS = TRADITIONAL_SPORTS + HOBBY_SPORTS + SCHOOL_SPORTS


@app.route("/")
def index():
    return render_template("index.html", sports=SPORTS)

@app.route("/register", methods=["POST"])
def register():
    name = request.form.get("name")
    if not name:
        return render_template("error.html", message="Missing name")
    sport = request.form.get("sport")
    if not sport:
        return render_template("error.html", message="Missing sport")
    if sport not in SPORTS:
        return render_template("error.html", message="Invalid sport")

    create_registrant(conn, (name, sport))

    return redirect("/registrants")

@app.route("/registrants")
def registrants():
    registrants = select_all_registrants(conn)    ### Implement SQL SELECT statement on database ...
    return render_template("registrants.html", registrants=registrants)

