# CSV to DB (SQLite3)

`CSV to DB (SQLite3)` is a python based converter that converts any valid `csv` file into a file-based database file. It basically reads the `csv` and copies each row into the table of a database file with the same name.

### Demo

Down below is the demo run of the program which converts `demo.csv` into `demo.db`. It writes all rows from `demo.csv` into `demo.db` in a table called `t`.

```shell
PS G:\csv_to_db> python .\csv_to_db.py .\demo.csv
[SUCCESS] CSV found: 'demo.csv'

Enter table name: t
[INFO] Table 't' has been created.

Processing: 100%|████████████████████████████████████████████████| 8.00/8.00 [00:00<?, ?r/s]
[SUCCESS] Database has been written.

** INFO **
Database name: demo.db
Database size: 12.0 KB
Table name   : t
Time taken   : 0.07 seconds
Rows written : 8
Rows skipped : 0
```

### Features

- Converts the `csv` into a database file *(`sqlite3`)*

- Auto-adds and increments `ID`

- Auto-infers `column` types

- Highly optimized for larger CSVs

- Errors handled like a pro!

- Easy to use

- That's it, it's not facebook or something..!!

### Setup & Installation

Setting up this application in your pc is very easy. just follow below steps and you'll be fine.

> ##### Installing Python 3.x
> 
> - Go to [python.org](https://www.python.org/downloads/) and download latest python.
> 
> - Install `python` into your pc and add `path` to enviroment variables. *(follow a youtube video if stuck!)*
> 
> - Open terminal and run `python --version` to check if python is installed correctly!
> 
> ###### Installing Dependencies
> 
> - Open terminal in the project's directory.
> 
> - Run `pip install -r requirements.txt` command.
> 
> - It will install all libraries listed in the `requirements.txt` file.

### Setting up CSV

Before conversion, make sure your csv is valid, clean, and contains a header line.

> ###### What is Header in a csv?
> 
> Header line in a csv is the first line which contains the names of the columns in the csv *(separated by commas)*.
> 
> ###### CSV file without header
> 
> ```csv
> Python,1991,Guido van Rossum
> JavaScript,1995,Brendan Eich
> C,1972,Dennis Ritchie
> ```
> 
> ###### CSV file with header
> 
> ```csv
> title,appeared,creators
> Python,1991,Guido van Rossum
> JavaScript,1995,Brendan Eich
> C,1972,Dennis Ritchie
> ```

### Using the Program

Once you've followed the steps above, using this program should be a piece of cake!

> - Open terminal in the project directory.
> 
> - Run `python .\csv_to_db.py [csv_path\csv_name.csv]`
>   
>   > ```shell
>   > PS G:\csv_to_db> python .\csv_to_db.py .\test.csv
>   > [SUCCESS] CSV found: 'demo.csv'
>   > 
>   > ```
> 
> - If csv is found, it'll ask you for a `table` name. *(Remember to abide the SQL rules for naming tables)*
>   
>   > ```shell
>   > Enter table name: test
>   > [INFO] Table 'test' has been created.
>   > ```
> 
> - If the name is valid, it'll create a table of that name and starts the writing process.
>   
>   > ```shell
>   > Processing: 100%|████████████████████████████████████████████████| 8.00/8.00 [00:00<?, ?r/s]
>   > [SUCCESS] Database has been written.
>   > ```
>   > 
>   > `r/s` in the progressbar mean `rows per second`.
> 
> - If all goes well, it'll write the csv into the `.db` file and show info like below
>   
>   > ```shell
>   > ** INFO **
>   > Database name: demo.db
>   > Database size: 12.0 KB
>   > Table name   : t
>   > Time taken   : 0.07 seconds
>   > Rows written : 8
>   > Rows skipped : 0
>   > ```
> 
> - Congratulations! you've successfully converted a csv into a database file.



### Overview of the project

> ##### Libraries used in the project
> 
> 10 libraries were used in this project. Only last 3 are `third-party` libraries.
> 
> `os` `re` `sys` `time` `sqlite3` `sqlparse` `csv` `tqdm` `colorama` `termcolor`
> 
> ##### Project's Root Directory
> 
> There are only 3 files in the project's root directory.
> 
> `csv_to_db.py` `README.md` `requirements.txt`



---

You are free to use this program however you like! No need to give credits to the developer *(Well, not if you don't want to...)*

##### Developer: Anas Shakeel