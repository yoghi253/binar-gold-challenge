import sqlite3

conn =sqlite3.connect('gold_binar2.db')
print("opened database successfuly")

conn.execute('''CREATE TABLE users (id INTEGER PRIMARY KEY, text varchar(255), clean_text varchar(255));''')
print("Table created successfully")

conn.commit()
print("Record created successfuly")
conn.close()