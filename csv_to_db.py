""" 
CSV to DB (SQLite3)
A simple converter that converts a csv into a (SQLite3) database file.
    
### Features
- Converts the csv into a database file *(sqlite3)*
- Auto-adds and increments ID
- Auto-infers column types
- Highly optimized for larger CSVs
- Errors handled like a pro!
- Easy to use
- That's it, it's not facebook or something..!!
        
    
Requirement for usage:
    ** CSV must have a header line for the column names **


#### Author: Anas Shakeel

"""

# Built-in Libraries
import re
import os
import sys
from time import time
import sqlite3
from sqlparse.keywords import KEYWORDS_COMMON
from csv import DictReader, Error as csv_error
# Third-party Libraries
from tqdm import tqdm
from colorama import just_fix_windows_console
from termcolor import colored

# Defining colors
COLORS = {
    "error": "red",
    "success": "green",
    "info": "light_blue",
    "warning": "yellow",
    'dim': "dark_grey"
}

# All Available Statuses
STATUSES = ['info', 'suggestion', 'success', 'warning', 'error']

# Will store all metadata during program execution
META = {}


def main():
    # Fix windows console for termcolor
    just_fix_windows_console()

    # Get the csv path, dir, & name
    META['csv_path'] = get_csvpath()
    META['csv_directory'], META['csv_name'] = os.path.split(META['csv_path'])

    # MESSAGE: csv found...
    message(f"""CSV found: '{META["csv_name"]}'\n""", 'success')

    # Create/GET the Database path/name
    META['db_name'], META['db_path'] = get_db_or_quit(META['csv_directory'],
                                                      META['csv_name'])

    # ASK FOR TABLE NAME
    META['table_name'] = get_table_name_or_quit()

    # Create the database and connect to it
    con = sqlite3.connect(META['db_path'])
    cur = con.cursor()

    try:
        # Get the Fields from the csv headers
        fields = get_fields(META['csv_path'])

        # Create & Execute a table query
        create_table(cur, META['table_name'], fields)

        # COUNT the lines in csv before conversion (for TQDM progressbar)
        META['csv_lines'] = count_csv_lines(META['csv_path'], True)

        # TRANSACTION (SQL thing, for performance. don't know)
        with con:
            # Open the CSV file to read the data
            with open(META['csv_path'], errors='ignore', newline='') as csvfile:
                reader = DictReader(csvfile, quotechar='"')

                insert_query = create_insert_query(META['table_name'],
                                                   reader.fieldnames)

                # INSERT the data INTO the database
                response = insert_data(
                    cur, reader, insert_query, META['csv_lines'])
                con.commit()

        # SUCCESS Message
        message("Database has been written.", 'success')

        META['rows_written'] = response[0]
        META['rows_skipped'] = response[1]
        META['time_taken'] = response[2]

        # Print INFO
        print(colored(create_info_string(), COLORS['dim']))

        if META['rows_skipped'] > 0:
            message(f"{META['rows_skipped']} rows were skipped due to unclean data in the CSV.",
                    'warning')

    except KeyboardInterrupt:
        # DELETE the database & QUIT
        con.close()
        delete_file(META['db_path'])
        sys.exit(1)

    finally:
        try:
            # just TRY to commit
            con.commit()
        except sqlite3.ProgrammingError:
            pass
        con.close()


# Returns a valid csv_path OR closes the program itself
def get_csvpath() -> (str | None):
    # If more commands given than needed
    if len(sys.argv) > 2:
        message("Invalid arguments: args_count exceeded", 'error', True)

    csv_path: str = ""
    if len(sys.argv) == 2:
        # Get the cmd-arg
        csv_path = sys.argv[1]
    else:
        # If no args given, get csv manually
        try:
            csv_path = input("Enter path to CSV file: ")
        except KeyboardInterrupt:
            sys.exit(1)

    # Validate the filename
    if not validate_csv(csv_path):
        message(f"CSV '{csv_path}' not found.", 'error', True)

    return os.path.normpath(csv_path)


def validate_csv(path: str):
    """
    Validate CSV
    Validates the `path` to check if valid existing csv.
    Returns `False` if invalid, `True` otherwise.
    """
    # If path is csv & exists
    if "csv" == os.path.basename(path).split(".")[-1]:
        return os.path.exists(path)

    # If path not csv
    return False


def get_db_or_quit(path: str, csvname: str):
    """
    ### Get DB
    Returns a valid `db name` and `db full path` or quits the program.
    """
    db_name = csvname.replace(".csv", ".db")
    db_path = os.path.join(path, db_name)

    # If DATABASE ALREADY EXISTS, QUIT!!!
    if os.path.exists(db_path):
        message(f"'{db_name}' already exists.", 'warning')
        ans = get_option(["1. connect to existing database.",
                         "2. create a new one.", "3. exit."])
        if ans == 2:
            # Create a new db name+path
            db_name, db_path = get_new_db_name(path)
            message(f"New database '{db_path}' has been created.", "success")
        elif ans == 3:
            sys.exit(0)
        else:
            # connect to existing one
            pass

    return (db_name, db_path)


def get_new_db_name(path: str):
    """
    ### Get New DB Name
    Gets the database name and returns it after validating.
    it also joins the `path` with dbname and checks if that exists.
    """
    dbname = input("Type a name for new database (with extension '.db'): ")
    # Validate db name
    if (not dbname) or (not dbname.endswith(".db")):
        message("Invalid database name. (make sure name ends with .db)",
                "error", quit_=True)

    dbpath = os.path.join(path, dbname)
    if os.path.exists(dbpath):
        message(f"'{dbname}' exists too. you know what, I'M DONE!",
                "error", quit_=True)

    return dbname, dbpath


def get_option(options: list):
    total_options = len(options)
    # Print the options
    for op in options:
        print(op)

    # Get the options as input
    try:
        option = int(input("Choose from above: "))
        if option > total_options or option < 1:
            raise ValueError
        else:
            return option
    except ValueError:
        message("Invalid option!", 'error', True)
    except KeyboardInterrupt:
        sys.exit(1)


def get_table_name_or_quit() -> str:
    """ 
    ### Get Table Name or Quit
    Returns a `valid` table name, or quits the program if `invalid`.

    Rules for validation:
        - Alphanumeric (letters and numbers only)
        - Underscore allowed
        - No Leading digits
        - No Special characters or whitespaces
        - less than 100 characters length
        - No SQL Keywords

    """
    # Validation REGEX pattern
    pattern = r"^[a-zA-Z_][a-zA-Z0-9_]{0,100}$"

    try:
        tname = input("Enter table name: ")
    except KeyboardInterrupt:
        sys.exit(0)

    if not re.match(pattern, tname):
        # REGEX Validation failed!
        message("Invalid table name. (only letters, digits, and underscores allowed)",
                "error", quit_=True)

    if tname.upper() in KEYWORDS_COMMON.keys():
        # It is a SQL Keyword
        message(f"'{tname}' is a SQL Reserved Keyword, Hence invalid.",
                "error", quit_=True)

    return tname


def get_fields(csvpath):
    """ 
    ### Get Fields
    Reads the csv at `csvpath` and fetches the header and
    assigns SQL types to columns in header. Returns a dictionary
    containing fieldnames as keys & their SQL types as values.

    ```
    # Output structure
    {"column name": "column SQL type"}
    # Output example
    {
        "quote":"TEXT",
        "author":"TEXT",
        "category":"TEXT"
    }
    ```
    """

    fields = {}

    with open(csvpath, errors='ignore', newline='') as csvfile:
        reader = DictReader(csvfile, quotechar='"')
        # Get the first row after header
        sample_data = next(reader)

        # Infer the field type
        for field in sample_data.keys():
            fields[field] = infer_type(sample_data[field])

    return fields


def infer_type(value: str):
    """ 
    ### Infer Type
    Figure out the type of `value` from three SQL
    types `TEXT`,`INT`, or `REAL`.

    ```
    # Output example
    >> infer_type('11')
    "INT"
    >> infer_type('11.52')
    "REAL"
    >> infer_type('11a')
    "TEXT"

    ```
    """
    value_type: str = ""
    try:
        # IF int
        int(value)
        value_type = "INT"
    except ValueError:
        try:
            # IF float
            float(value)
            value_type = "REAL"
        except ValueError:
            # IF any other
            value_type = "TEXT"

    return value_type


def count_csv_lines(csv_path, skip_header=True):
    """ 
    Count CSV Lines
    Reads csv at `csv_path` and counts & returns the number of total lines.
    if `skip_header` is True, it skips the header (first line).
    """

    with open(csv_path, "r", newline='', encoding='utf-8', errors='ignore') as file:
        if skip_header:
            next(file)
        return sum(1 for _ in file)


def create_table_query(table_name: str, fields: dict):
    """
    ### Create Table Query
    Returns a `CREATE TABLE` sql query with fields.

    ```
    # OUTPUT Example:
    CREATE TABLE table_name
        (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        field1 TEXT, field2 TEXT, ...,fieldn TEXT)
    ```
    """
    # Create definitions for fields/columns in table
    id_def = "id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT"
    field_defs = ", ".join([f"{f} {ftype}" for f, ftype in fields.items()])

    # Join definitions together & RETURN.
    return f"CREATE TABLE IF NOT EXISTS {table_name} ({id_def}, {field_defs})"


def create_insert_query(table_name: str, fields: list):
    """
    ### Create Insert Query
    Returns a `INSERT INTO` sql query with fields and VALUES placeholders `?`.

    ```
    # OUTPUT Example:
    >> fields = ['quote', 'author', 'category']
    >> create_insert_query('quotes', fields)
    "INSERT INTO quotes (quote, author, category) VALUES(?, ?, ?)"
    ```
    """
    values = ", ".join(fields)
    placeholders = ", ".join(["?"] * len(fields))

    return f"INSERT INTO {table_name} ({values}) VALUES({placeholders})"


def create_table(cursor: sqlite3.Cursor, table_name: str, fields: dict):
    """
    ### Create Table
    Creates a table in database with `fields`.
    """
    # Create a `CREATE TABLE` query
    table_query = create_table_query(table_name, fields)

    # Execute the query
    try:
        cursor.execute(table_query)
        message(f"Table '{table_name}' has been created.\n", 'info')
    except sqlite3.Error as e:
        message(f"Cannot create table: {e}", "error", quit_=True)


def insert_data(cursor, reader: DictReader, query: str, total: int):
    """ 
    ### Insert Data
    Inserts the data into the database provided. 
    Returns `rows_written`, `rows_skipped`, and `time_taken` values.
    `total` is the total number of lines in the csv.
    """
    skip_count, wrote_count = 0, 0
    time_taken = time()

    # Insert data into the table
    for row in tqdm(reader, desc="Processing", unit="r", unit_scale=True, total=total, colour='#2cc295'):
        try:
            # Write the row into the database
            cursor.execute(query, list(row.values()))
            wrote_count += 1
        except (sqlite3.ProgrammingError, sqlite3.OperationalError):
            skip_count += 1
        except csv_error:
            pass
    time_taken = time() - time_taken

    return wrote_count, skip_count, time_taken


def message(message: str, status: str, quit_=False):
    """
    ### Message
    Prints a `message` according to `status` provided. When `quit_` is True,
    it closes the program after printing the message.

    #### Supported Statuses:
    `INFO`, `SUGGESTION`, `SUCCESS`, `WARNING`, `ERROR`
    """
    if status.lower() in STATUSES:
        print(colored(f"[{status.upper()}] {message}", COLORS[status]))
        if quit_:
            sys.exit(0)


def delete_file(filepath: str):
    """
    ### Delete File
    Deletes the given `filepath` file
    """
    # if file doesn't exists, raise valueError
    if not os.path.isfile(filepath):
        raise ValueError("file does not exist")

    # delete file
    os.remove(filepath)


def get_file_size(filepath: str, formatted=True):
    """
    ### Get File Size
    Returns the file size of `filepath`

    ```
    >> fm.get_file_size('C:\\File.txt', formatted=False)
    2248

    >> fm.get_file_size('C:\\File.txt', formatted=True)
    (2.2, 'KB', '2.2 KB')
    ```
    """

    # size of 'filepath' in bytes
    size = os.path.getsize(filepath)

    # returning decision ? formatted or not?
    if not formatted:
        return size

    # return formatted size otherwise
    return _from_bytes(size)[-1]


def _from_bytes(_bytes: int):
    """
    ### Bytes Converter
    Converts `bytes` to other data storage units

    ```
    >> fm._from_bytes(1024)
    (1.0, 'KB', '1.0 KB')

    >> fm._from_bytes(104815200)
    (99.95, 'MB', '99.95 MB')
    ```
    """

    # ? if _bytes is zero, Return
    if _bytes == 0:
        # if size is zero
        return (0.0, 'B', '0.0 B')

    # Unit Factors
    factors = {
        "B": 1,
        "KB": 1024,
        "MB": 1024 ** 2,
        "GB": 1024 ** 3,
        "TB": 1024 ** 4,
        "PB": 1024 ** 5
    }

    # ? one by one calculates each fact in factors
    for fact in factors.keys():
        # calculate bytes into new unit (kb or mb or other)
        new_unit = round(_bytes / factors[fact], 2)

        # if bewteen 1-1024, return it
        if int(new_unit) in range(1, 1024):
            # returning values in (tuple)
            return (new_unit, fact, f"{new_unit} {fact}")


def create_info_string():
    return f"""
    ** INFO **
    Database name: {META['db_name']}
    Database size: {get_file_size(META['db_path'])}
    Table name   : {META['table_name']}
    Time taken   : {META['time_taken']:.2f} seconds
    Rows written : {META['rows_written']:,}
    Rows skipped : {META['rows_skipped']:,}
    """.replace("    ", "")


if __name__ == "__main__":
    main()
