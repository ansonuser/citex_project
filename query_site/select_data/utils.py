# from .forms import InsertForm
# from .models import *
import sqlite3
import os
import datetime

def custom_table(result, all_name_list, product_name_list = ['product_number_id', 'product_amount']):
    info_index = 0
    cum = 0
    respond = []
    store_order_id = {}
    key_ = list(result.keys())
    n = len(result[key_[1]])
    for v in result[key_[0]]:
        info_index += cum

        if v[0] not in store_order_id:
            tmp = {}
            cum = 0
            for k, i in zip(all_name_list, v[1:]):
                if isinstance(i,datetime.date) or isinstance(i,datetime.datetime):
                    i = i.strftime("%Y/%m/%d")
                elif i is None:
                    i = ""
                tmp.update({k:i})

            for index in range(info_index, n):
                if result[key_[1]][index][0] == v[0]:
                    for ll,l in zip(product_name_list, result[key_[1]][index][1:]):
                        tmp[ll]=l
                    
                    # if cum == 1:
                    #     for m in all_name_list:
                    #         tmp.update({m:''})
                    respond.append(tmp.copy())
                    cum += 1
                else:
                    break
            store_order_id.update({v[0]:'added'})
    return respond
        

def tojson(select_result, name_list):
    n = len(select_result)
    result = []
    for i in range(n):
        tmp = {}
        for k,v in zip(name_list, select_result[i]):
            if isinstance(v,datetime.date) or isinstance(v,datetime.datetime):
                v = v.strftime("%Y/%m/%d")
            elif v is None:
                v = ""
            tmp[k] = v
        result.append(tmp.copy())
    return result


def tojsonframe(select_result,  design = None, keys = None):
    n = len(select_result)
    result = {}
    for i in range(n):
        tmp = select_result[i]
        if design is None and keys is None:
            value_list = []
            for j in tmp[1:]:
                if (isinstance(j,datetime.date) or isinstance(j,datetime.datetime)):
                    value_list.append(j.strftime("%Y/%m/%d"))
                elif j is None:
                    value_list.append("")
                else:
                    value_list.append(j)
            result[tmp[0]] = value_list
        elif keys is not None:
            value_list = []
            for j in tmp:
                if (isinstance(j,datetime.date) or isinstance(j,datetime.datetime)):
                    value_list.append(j.strftime("%Y/%m/%d"))
                elif j is None:
                    value_list.append("")
                else:
                    value_list.append(j)
            result[i] = value_list
        else:
            result[tmp[0]] = [j if not  (isinstance(j,datetime.date) or isinstance(j,datetime.datetime)) else j.strftime("%Y/%m/%d") for idx,j in enumerate(tmp[1:]) if idx in design]
    return result    

def make_connection(base_dir = os.path.dirname(os.getcwd() )):
    # cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    # print(os.path.join(base_dir,'db.sqlite3'))
    conn = sqlite3.connect(os.path.join(base_dir,'db.sqlite3'))
    return conn

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
                INSERT INTO {} ({},{})  VALUES ((SELECT MAX({}) + 1 FROM {}),?)
                """.format(update_table, input_id, fe, input_id, update_table), (value_,) )
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