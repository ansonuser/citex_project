# from .forms import InsertForm
# from .models import *
import sqlite3
import os
import datetime
def make_connection(base_dir = os.path.dirname(os.getcwd() )):
    # cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    conn = sqlite3.connect(os.path.join(base_dir,'db.sqlite3'))
    return conn

make_connection()
def utils_insert_single(conn, insert_form, 
        fes = ['company_name', 'product_name'], 
        update_tables = ['select_data_company', 'select_data_product']):
    """
    fes = ['company_name', 'product_name']
    update_tables = ['select_data_company', 'select_data_product']
    given insert form and check if current value is already in give columns(fe) of update_tables
    """
    
    current_id_dict = {}
    cursor = conn.cursor()
    for fe,update_table in zip(fes, update_tables):
        value_ = insert_form[fe].value()
        command =  f"""SELECT {fe} FROM {update_table}
                """
        cursor.execute(command)
        respond = cursor.fetchall()
        result = [i[0] for i in respond]
        input_id = update_table.split('_')[-1] + '_id'

        if value_ not in result:
            cursor.execute("""
                INSERT INTO ({},{}) {} VALUES (?,)
                """.format(input_id, fe, update_table), (value_,) )
            conn.commit()
        cursor.execute("""
            SELECT {} FROM {}
            WHERE {} = ?
            """.format(input_id, update_table, fe), (value_,) )

        current_id = cursor.fetchall()[0][0]
        # conn.close()
        current_id_dict[input_id] =  current_id
    return current_id_dict

def utils_insert_relation(conn, insert_form, 
        current_id_dict,
        fes = ["factory_site", "people_name", "get_date", "po_num", "product_amount", "other_command", "expect_date"]):
    """
    mapping:
    factory_site => company_id, factory_id
    people_name => factory_id, people_name (select_data_people) => out: custom_id
    get_date, po_num => get_order_date, po_num (select_data_get_order) => out: order_id
    product_amount,  product_id, expect_date, other_command => product_id, order_id, custom_id, product_num, other_command (select_data_order_detail)

    fes = [factory_site, people_name, get_date, po_num, product_amount, other_command, expect_date]
    """
    keys = current_id_dict.keys()
    keys = [k for k in keys]
    # factory_site
    name_ = insert_form[fes[0]].value()
    cursor = conn.cursor()
    cursor.execute("SELECT factory_site FROM select_data_factory WHERE company_id_id = ?", (current_id_dict[keys[0]],))
    respond = cursor.fetchall()
    result = [i[0] for i in respond]
    if name_ not in result:
        cursor.execute("INSERT INTO select_data_factory (company_id_id, factory_site) VALUES (?, ?)", (current_id_dict[keys[0]], name_,))
        conn.commit()
    cursor.execute("SELECT factory_id FROM select_data_factory WHERE factory_site = ?", (name_,))
    current_id = cursor.fetchall()[0][0]
    current_id_dict['factory_id'] = current_id
    # people_name
    name_ = insert_form[fes[1]].value()
    cursor.execute("SELECT people_name FROM select_data_people WHERE factory_id_id = ?", (current_id,))
    respond = cursor.fetchall()
    result = [i[0] for i in respond]
    if name_ not in result:
        cursor.execute("INSERT INTO select_data_people (factory_id_id, people_name) VALUES (?, ?)", (current_id, name_))
        conn.commit()
    cursor.execute("SELECT people_id FROM select_data_people WHERE people_name = ?", (name_,))
    current_id = cursor.fetchall()[0][0]
    current_id_dict['people_id'] = current_id

    # po_num, get_date
    get_date = insert_form[fes[2]].value()
    # print("get_date:", get_date)
    # print(type(get_date))
    po_num = insert_form['product_demand'].value()
    cursor.execute("INSERT INTO select_data_order_get (get_order_date, po_num, finished) VALUES (?, ?, ?)", (get_date, po_num, 0))
    conn.commit()

    cursor.execute("SELECT MAX(order_id) FROM select_data_order_get")
    current_id = cursor.fetchall()[0][0]
    current_id_dict['order_id'] = current_id

    # product_amount,  product_id, expect_date, other_command
    product_amount = insert_form[fes[4]].value()
    other_command = insert_form["note"].value()
    if other_command is None:
        other_command = "No command"
    expect_date = insert_form[fes[6]].value()
    # print("Expect_date:", expect_date)
    # print(type(expect_date))
    cursor.execute("INSERT INTO select_data_order_detail (product_id_id, order_id_id, custom_id_id, expected_ship_date, product_num, other_command, last_modified) VALUES (?, ?, ?, ?, ?, ?, ?)",
    (current_id_dict['product_id'], current_id_dict['order_id'], current_id_dict['people_id'], expect_date, product_amount, other_command, datetime.datetime.now()))
    conn.commit()
    return 1