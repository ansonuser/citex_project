import sqlite3
import os
import datetime
from .models import Product

def make_connection(base_dir = os.path.dirname(os.getcwd() )):
    conn = sqlite3.connect(os.path.join(base_dir,'db.sqlite3'))
    return conn

def update(conn, table_list, modified_table):

    conn = make_connection()
    cursor = conn.cursor()
    return 0

def delete(conn, name_list):
    for name in name_list:
        Product(pk = name).delete()
    return True